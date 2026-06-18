from __future__ import annotations

import io
import json
import re
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import requests

from src.data_sources import (
    CKAN_DATASTORE_SEARCH_URL,
    CKAN_PACKAGE_SEARCH_URL,
    CKAN_PACKAGE_SHOW_URL,
    GOVMAP_URBAN_RENEWAL_URL,
    KNOWN_DATA_SOURCES,
    NORMALIZATION_SEARCH_TERMS,
    REFERENCE_ONLY_SOURCES,
    SUPPORTED_RESOURCE_FORMATS,
    URBAN_RENEWAL_SEARCH_TERMS,
    XPLAN_REST_CANDIDATES,
    XPLAN_SERVICE_REFERENCE_URL,
    is_strict_urban_renewal_resource,
    normalized_resource_format,
)


DEFAULT_HEADERS = {
    "User-Agent": (
        "UrbanRenewalPublicData/1.0 "
        "(non-profit public-data refresh; contact through repository)"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.7",
}

INVENTORY_COLUMNS = [
    "source_name",
    "source_url",
    "source_type",
    "source_role",
    "priority",
    "package_id",
    "package_name",
    "package_title",
    "organization",
    "resource_id",
    "resource_name",
    "resource_format",
    "resource_url",
    "last_modified",
    "access_method",
    "refresh_status",
    "http_status",
    "rows_loaded",
    "file_path",
    "included_in_public_records",
    "error_message",
    "checked_at",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_filename(value: Any, limit: int = 100) -> str:
    text = str(value or "source").strip()
    text = re.sub(r'[\\/:*?"<>|]+', "_", text)
    text = re.sub(r"\s+", "_", text)
    return text.strip("._")[:limit] or "source"


def safe_get(
    session: requests.Session,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    timeout: int = 30,
    attempts: int = 2,
) -> dict[str, Any]:
    """GET a public endpoint and return diagnostics instead of raising."""
    result: dict[str, Any] = {
        "ok": False,
        "status_code": None,
        "response": None,
        "error": None,
    }
    for attempt in range(attempts):
        try:
            response = session.get(url, params=params, timeout=timeout)
            result.update(
                {
                    "ok": 200 <= response.status_code < 400,
                    "status_code": response.status_code,
                    "response": response,
                    "error": (
                        None
                        if 200 <= response.status_code < 400
                        else f"HTTP {response.status_code}"
                    ),
                }
            )
            if result["ok"] or response.status_code < 500:
                return result
        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"
        if attempt + 1 < attempts:
            time.sleep(1.0 + attempt)
    return result


def safe_json(response: requests.Response) -> tuple[Any | None, str | None]:
    try:
        return response.json(), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def read_csv_flexible(source: Path | io.BytesIO) -> pd.DataFrame:
    encodings = ("utf-8-sig", "utf-8", "cp1255", "iso-8859-8")
    last_error: Exception | None = None
    raw_bytes = source.read_bytes() if isinstance(source, Path) else source.getvalue()
    for encoding in encodings:
        try:
            return pd.read_csv(
                io.BytesIO(raw_bytes),
                encoding=encoding,
                sep=None,
                engine="python",
                on_bad_lines="skip",
            )
        except Exception as exc:
            last_error = exc
    raise last_error or ValueError("Could not decode CSV")


def json_to_dataframe(payload: Any) -> pd.DataFrame:
    if isinstance(payload, list):
        return pd.json_normalize(payload)
    if isinstance(payload, dict):
        if payload.get("type") == "FeatureCollection":
            return pd.json_normalize(payload.get("features") or [])
        for key in ("records", "features", "results", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return pd.json_normalize(value)
        return pd.json_normalize(payload)
    raise ValueError("Unsupported JSON structure")


def load_tabular_file(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv_flexible(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix in {".json", ".geojson"}:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        return json_to_dataframe(payload)
    if suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            members = [
                name
                for name in archive.namelist()
                if Path(name).suffix.lower()
                in {".csv", ".xlsx", ".xls", ".json", ".geojson"}
            ]
            if members:
                member = members[0]
                data = archive.read(member)
                member_suffix = Path(member).suffix.lower()
                if member_suffix == ".csv":
                    return read_csv_flexible(io.BytesIO(data))
                if member_suffix in {".xlsx", ".xls"}:
                    return pd.read_excel(io.BytesIO(data))
                return json_to_dataframe(json.loads(data.decode("utf-8-sig")))
        try:
            import geopandas as gpd

            return pd.DataFrame(gpd.read_file(f"zip://{path}"))
        except Exception as exc:
            raise ValueError(
                "ZIP has no tabular member and geopandas could not read it"
            ) from exc
    raise ValueError(f"Unsupported file type: {suffix}")


def _organization_name(package: dict[str, Any]) -> str | None:
    organization = package.get("organization") or {}
    return organization.get("title") or organization.get("name")


def discover_ckan_packages(
    session: requests.Session,
    terms: Iterable[str],
    *,
    rows: int = 100,
    max_pages: int = 10,
    timeout: int = 30,
) -> tuple[list[tuple[str, dict[str, Any]]], list[dict[str, Any]]]:
    discovered: list[tuple[str, dict[str, Any]]] = []
    diagnostics: list[dict[str, Any]] = []
    seen: set[str] = set()
    for term in terms:
        start = 0
        for _ in range(max_pages):
            request = safe_get(
                session,
                CKAN_PACKAGE_SEARCH_URL,
                params={"q": term, "rows": rows, "start": start},
                timeout=timeout,
            )
            diagnostic = {
                "source_name": f"data.gov.il CKAN search: {term}",
                "source_url": CKAN_PACKAGE_SEARCH_URL,
                "source_type": "government_open_data_api",
                "source_role": "source_discovery",
                "priority": 1,
                "package_id": None,
                "package_name": None,
                "package_title": term,
                "organization": None,
                "resource_id": None,
                "resource_name": None,
                "resource_format": "JSON",
                "resource_url": None,
                "last_modified": None,
                "access_method": "package_search_paginated",
                "refresh_status": "failed",
                "http_status": request["status_code"],
                "rows_loaded": 0,
                "file_path": None,
                "included_in_public_records": False,
                "error_message": request["error"],
                "checked_at": utc_now_iso(),
            }
            if not request["ok"] or request["response"] is None:
                diagnostics.append(diagnostic)
                break
            payload, json_error = safe_json(request["response"])
            if json_error or not payload or not payload.get("success"):
                diagnostic["error_message"] = json_error or str(
                    (payload or {}).get("error")
                )
                diagnostics.append(diagnostic)
                break
            result = payload.get("result") or {}
            packages = result.get("results") or []
            diagnostic["refresh_status"] = "discovered"
            diagnostic["rows_loaded"] = len(packages)
            diagnostic["error_message"] = None
            diagnostics.append(diagnostic)
            for package in packages:
                package_id = str(package.get("id") or package.get("name") or "")
                key = f"{term}|{package_id}"
                if key not in seen:
                    seen.add(key)
                    discovered.append((term, package))
            start += len(packages)
            total = int(result.get("count") or 0)
            if not packages or start >= total:
                break
    return discovered, diagnostics


def package_show(
    session: requests.Session, package_id: str, timeout: int = 30
) -> tuple[dict[str, Any] | None, str | None, int | None]:
    request = safe_get(
        session,
        CKAN_PACKAGE_SHOW_URL,
        params={"id": package_id},
        timeout=timeout,
    )
    if not request["ok"] or request["response"] is None:
        return None, request["error"], request["status_code"]
    payload, json_error = safe_json(request["response"])
    if json_error or not payload or not payload.get("success"):
        return None, json_error or str((payload or {}).get("error")), request[
            "status_code"
        ]
    return payload.get("result") or {}, None, request["status_code"]


def datastore_records(
    session: requests.Session,
    resource_id: str,
    *,
    page_size: int = 5000,
    timeout: int = 30,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    offset = 0
    total: int | None = None
    http_status: int | None = None
    while True:
        request = safe_get(
            session,
            CKAN_DATASTORE_SEARCH_URL,
            params={
                "resource_id": resource_id,
                "limit": page_size,
                "offset": offset,
            },
            timeout=timeout,
        )
        http_status = request["status_code"]
        if not request["ok"] or request["response"] is None:
            return {
                "ok": False,
                "records": records,
                "total": total,
                "http_status": http_status,
                "error": request["error"],
            }
        payload, json_error = safe_json(request["response"])
        if json_error or not payload or not payload.get("success"):
            return {
                "ok": False,
                "records": records,
                "total": total,
                "http_status": http_status,
                "error": json_error or str((payload or {}).get("error")),
            }
        result = payload.get("result") or {}
        page = result.get("records") or []
        records.extend(page)
        total = int(result.get("total") or len(records))
        offset += len(page)
        if not page or offset >= total:
            break
    return {
        "ok": True,
        "records": records,
        "total": total,
        "http_status": http_status,
        "error": None,
    }


def save_datastore_resource(
    raw_dir: Path,
    resource_id: str,
    records: list[dict[str, Any]],
) -> tuple[Path, pd.DataFrame]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    stem = f"data_gov_{safe_filename(resource_id)}_records"
    json_path = raw_dir / f"{stem}.json"
    csv_path = raw_dir / f"{stem}.csv"
    write_json(json_path, {"records": records})
    frame = pd.json_normalize(records)
    frame.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path, frame


def download_resource(
    session: requests.Session,
    resource_url: str,
    raw_dir: Path,
    *,
    source_name: str,
    resource_id: str,
    resource_format: str,
    timeout: int = 60,
) -> dict[str, Any]:
    request = safe_get(session, resource_url, timeout=timeout)
    if not request["ok"] or request["response"] is None:
        return {
            "ok": False,
            "file_path": None,
            "dataframe": None,
            "http_status": request["status_code"],
            "error": request["error"],
        }
    response = request["response"]
    content_type = str(response.headers.get("content-type") or "").lower()
    preview = response.content[:500].decode("utf-8", errors="ignore").lower()
    if "text/html" in content_type or "<html" in preview or "<!doctype" in preview:
        return {
            "ok": False,
            "file_path": None,
            "dataframe": None,
            "http_status": response.status_code,
            "error": "The resource URL returned HTML rather than a dataset.",
        }
    suffix_by_format = {
        "CSV": ".csv",
        "XLS": ".xls",
        "XLSX": ".xlsx",
        "JSON": ".json",
        "GEOJSON": ".geojson",
        "ZIP": ".zip",
        "SHP": ".zip",
    }
    url_path = resource_url.split("?", 1)[0].lower()
    suffix = next(
        (
            candidate
            for candidate in (".geojson", ".xlsx", ".xls", ".csv", ".json", ".zip")
            if url_path.endswith(candidate)
        ),
        suffix_by_format.get(resource_format, ".bin"),
    )
    filename = (
        f"data_gov_{safe_filename(source_name)}_"
        f"{safe_filename(resource_id)}{suffix}"
    )
    file_path = raw_dir / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(response.content)
    try:
        dataframe = load_tabular_file(file_path)
    except Exception as exc:
        return {
            "ok": False,
            "file_path": file_path,
            "dataframe": None,
            "http_status": response.status_code,
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {
        "ok": True,
        "file_path": file_path,
        "dataframe": dataframe,
        "http_status": response.status_code,
        "error": None,
    }


def _resource_inventory_row(
    package: dict[str, Any],
    resource: dict[str, Any],
    *,
    source_role: str,
    checked_at: str,
) -> dict[str, Any]:
    return {
        "source_name": package.get("title") or resource.get("name") or "data.gov.il",
        "source_url": (
            resource.get("url")
            or f"https://data.gov.il/dataset/{package.get('name') or package.get('id')}"
        ),
        "source_type": "data.gov.il_ckan_resource",
        "source_role": source_role,
        "priority": 1,
        "package_id": package.get("id"),
        "package_name": package.get("name"),
        "package_title": package.get("title"),
        "organization": _organization_name(package),
        "resource_id": resource.get("id"),
        "resource_name": resource.get("name"),
        "resource_format": normalized_resource_format(resource),
        "resource_url": resource.get("url"),
        "last_modified": (
            resource.get("last_modified")
            or resource.get("metadata_modified")
            or package.get("metadata_modified")
        ),
        "access_method": "ckan_datastore_then_direct_download",
        "refresh_status": "discovered",
        "http_status": None,
        "rows_loaded": 0,
        "file_path": None,
        "included_in_public_records": False,
        "error_message": None,
        "checked_at": checked_at,
    }


def _attach_source_metadata(
    frame: pd.DataFrame,
    row: dict[str, Any],
    pipeline_run: str,
) -> pd.DataFrame:
    result = frame.copy()
    result["source_name"] = row["source_name"]
    result["source_url"] = row["source_url"]
    result["source_type"] = row["source_type"]
    result["source_role"] = row["source_role"]
    result["original_resource_id"] = row["resource_id"]
    result["source_last_modified"] = row["last_modified"]
    result["source_refresh_status"] = row["refresh_status"]
    result["source_refresh_error"] = row["error_message"]
    result["pipeline_last_run"] = pipeline_run
    return result


def _process_resource(
    session: requests.Session,
    package: dict[str, Any],
    resource: dict[str, Any],
    raw_dir: Path,
    *,
    source_role: str,
    pipeline_run: str,
    timeout: int,
) -> tuple[dict[str, Any], pd.DataFrame | None]:
    row = _resource_inventory_row(
        package, resource, source_role=source_role, checked_at=pipeline_run
    )
    resource_id = str(resource.get("id") or "")
    resource_url = str(resource.get("url") or "")
    resource_format = normalized_resource_format(resource)
    if resource_format not in SUPPORTED_RESOURCE_FORMATS:
        row["refresh_status"] = "unsupported_format"
        row["error_message"] = f"Unsupported resource format: {resource_format or 'UNKNOWN'}"
        return row, None

    datastore = datastore_records(session, resource_id, timeout=timeout)
    if datastore["ok"] and datastore["records"]:
        csv_path, frame = save_datastore_resource(
            raw_dir, resource_id, datastore["records"]
        )
        row.update(
            {
                "refresh_status": "succeeded",
                "http_status": datastore["http_status"],
                "rows_loaded": len(frame),
                "file_path": str(csv_path),
                "included_in_public_records": source_role
                == "urban_renewal_records",
                "error_message": None,
                "access_method": "ckan_datastore_search_paginated",
            }
        )
        return row, _attach_source_metadata(frame, row, pipeline_run)

    if not resource_url:
        row["refresh_status"] = "failed"
        row["http_status"] = datastore["http_status"]
        row["error_message"] = datastore["error"] or "Missing resource URL"
        return row, None

    downloaded = download_resource(
        session,
        resource_url,
        raw_dir,
        source_name=str(row["source_name"]),
        resource_id=resource_id,
        resource_format=resource_format,
        timeout=max(timeout, 60),
    )
    if downloaded["ok"] and downloaded["dataframe"] is not None:
        frame = downloaded["dataframe"]
        row.update(
            {
                "refresh_status": "succeeded",
                "http_status": downloaded["http_status"],
                "rows_loaded": len(frame),
                "file_path": str(downloaded["file_path"]),
                "included_in_public_records": source_role
                == "urban_renewal_records",
                "error_message": None,
                "access_method": "direct_resource_download",
            }
        )
        return row, _attach_source_metadata(frame, row, pipeline_run)

    errors = [error for error in (datastore["error"], downloaded["error"]) if error]
    row.update(
        {
            "refresh_status": "failed",
            "http_status": downloaded["http_status"] or datastore["http_status"],
            "file_path": (
                str(downloaded["file_path"])
                if downloaded.get("file_path")
                else None
            ),
            "error_message": " | ".join(errors),
        }
    )
    return row, None


def try_xplan_arcgis(
    session: requests.Session,
    raw_dir: Path,
    pipeline_run: str,
    timeout: int,
) -> tuple[dict[str, Any], pd.DataFrame | None]:
    base_row = {
        "source_name": "XPLAN — קווי תכניות ציבוריים",
        "source_url": XPLAN_SERVICE_REFERENCE_URL,
        "source_type": "government_planning_gis",
        "source_role": "planning_reference",
        "priority": 2,
        "package_id": None,
        "package_name": None,
        "package_title": None,
        "organization": "מינהל התכנון",
        "resource_id": None,
        "resource_name": "ttl_all_blue_lines",
        "resource_format": "ArcGIS REST JSON",
        "resource_url": None,
        "last_modified": None,
        "access_method": "arcgis_rest_detection",
        "refresh_status": "failed_or_reference_only",
        "http_status": None,
        "rows_loaded": 0,
        "file_path": None,
        "included_in_public_records": False,
        "error_message": None,
        "checked_at": pipeline_run,
    }
    errors: list[str] = []
    for candidate in XPLAN_REST_CANDIDATES:
        request = safe_get(
            session, candidate, params={"f": "pjson"}, timeout=timeout
        )
        if not request["ok"] or request["response"] is None:
            errors.append(f"{candidate}: {request['error']}")
            continue
        payload, json_error = safe_json(request["response"])
        if json_error or not isinstance(payload, dict) or payload.get("error"):
            errors.append(
                f"{candidate}: {json_error or (payload or {}).get('error')}"
            )
            continue
        layers = payload.get("layers") or []
        layer_id = (layers[0] or {}).get("id") if layers else None
        query_base = f"{candidate}/{layer_id}" if layer_id is not None else candidate
        query_url = f"{query_base}/query"
        query = safe_get(
            session,
            query_url,
            params={
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "geojson",
                "resultRecordCount": 2000,
            },
            timeout=max(timeout, 60),
        )
        if not query["ok"] or query["response"] is None:
            errors.append(f"{query_url}: {query['error']}")
            continue
        query_payload, query_error = safe_json(query["response"])
        if query_error or not isinstance(query_payload, dict):
            errors.append(f"{query_url}: {query_error}")
            continue
        frame = json_to_dataframe(query_payload)
        geojson_path = raw_dir / "xplan_ttl_all_blue_lines.geojson"
        write_json(geojson_path, query_payload)
        base_row.update(
            {
                "source_url": query_url,
                "resource_url": query_url,
                "resource_id": str(layer_id) if layer_id is not None else None,
                "refresh_status": "succeeded",
                "http_status": query["status_code"],
                "rows_loaded": len(frame),
                "file_path": str(geojson_path),
                "included_in_public_records": False,
                "error_message": None,
            }
        )
        return base_row, _attach_source_metadata(frame, base_row, pipeline_run)
    base_row["error_message"] = " | ".join(errors) or (
        "No stable machine-readable ArcGIS query endpoint was detected."
    )
    return base_row, None


def collect_public_sources(
    project_root: Path,
    *,
    timeout: int = 30,
) -> tuple[pd.DataFrame, pd.DataFrame, list[pd.DataFrame]]:
    """Discover and refresh public sources without allowing one failure to abort."""
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    pipeline_run = utc_now_iso()
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    inventory: list[dict[str, Any]] = []
    public_frames: list[pd.DataFrame] = []
    normalization_frames: list[pd.DataFrame] = []
    processed_ids: set[str] = set()

    discovered, diagnostics = discover_ckan_packages(
        session, URBAN_RENEWAL_SEARCH_TERMS, timeout=timeout
    )
    inventory.extend(diagnostics)

    for known in KNOWN_DATA_SOURCES:
        package: dict[str, Any] = {}
        matched: list[dict[str, Any]] = []
        for _, discovered_package in discovered:
            discovered_resources = discovered_package.get("resources") or []
            discovered_match = [
                resource
                for resource in discovered_resources
                if str(resource.get("id") or "") == known.resource_id
            ]
            if discovered_match:
                package = discovered_package
                matched = discovered_match
                break

        if not package and known.package_id:
            package, package_error, package_http = package_show(
                session, known.package_id, timeout=timeout
            )
            if not package:
                inventory.append(
                    {
                        "source_name": known.source_name,
                        "source_url": known.source_url,
                        "source_type": known.source_type,
                        "source_role": known.source_role,
                        "priority": known.priority,
                        "package_id": known.package_id,
                        "package_name": known.package_id,
                        "package_title": known.source_name,
                        "organization": None,
                        "resource_id": known.resource_id,
                        "resource_name": known.source_name,
                        "resource_format": known.expected_format,
                        "resource_url": known.source_url,
                        "last_modified": None,
                        "access_method": known.access_method,
                        "refresh_status": "discovery_failed",
                        "http_status": package_http,
                        "rows_loaded": 0,
                        "file_path": None,
                        "included_in_public_records": False,
                        "error_message": package_error,
                        "checked_at": pipeline_run,
                    }
                )
        if not matched:
            resources = (package or {}).get("resources") or []
            matched = [
                resource
                for resource in resources
                if str(resource.get("id") or "") == known.resource_id
            ]
        if not matched and known.resource_id:
            matched = [
                {
                    "id": known.resource_id,
                    "name": known.source_name,
                    "format": known.expected_format,
                    "url": None
                    if known.access_method == "ckan_datastore_search"
                    else known.source_url,
                }
            ]
            package = package or {
                "id": known.package_id,
                "name": known.package_id or "known_resource",
                "title": known.source_name,
                "organization": {"title": "משרד הבינוי והשיכון"},
            }
        for resource in matched:
            resource_id = str(resource.get("id") or "")
            if resource_id in processed_ids:
                continue
            processed_ids.add(resource_id)
            row, frame = _process_resource(
                session,
                package,
                resource,
                raw_dir,
                source_role=known.source_role,
                pipeline_run=pipeline_run,
                timeout=timeout,
            )
            row["source_name"] = known.source_name
            row["source_url"] = known.source_url
            row["source_type"] = known.source_type
            if frame is not None:
                for column in ("source_name", "source_url", "source_type"):
                    frame[column] = row[column]
                public_frames.append(frame)
            inventory.append(row)

    for _, package in discovered:
        for resource in package.get("resources") or []:
            resource_id = str(resource.get("id") or "")
            if not resource_id or resource_id in processed_ids:
                continue
            if not is_strict_urban_renewal_resource(package, resource):
                continue
            processed_ids.add(resource_id)
            row, frame = _process_resource(
                session,
                package,
                resource,
                raw_dir,
                source_role="urban_renewal_records",
                pipeline_run=pipeline_run,
                timeout=timeout,
            )
            inventory.append(row)
            if frame is not None:
                public_frames.append(frame)

    reference_packages, reference_diagnostics = discover_ckan_packages(
        session,
        NORMALIZATION_SEARCH_TERMS,
        rows=25,
        max_pages=2,
        timeout=timeout,
    )
    for row in reference_diagnostics:
        row["source_role"] = "normalization_reference"
    inventory.extend(reference_diagnostics)
    reference_resource_budget = 4
    for _, package in reference_packages:
        if reference_resource_budget <= 0:
            break
        for resource in package.get("resources") or []:
            if reference_resource_budget <= 0:
                break
            resource_id = str(resource.get("id") or "")
            resource_format = normalized_resource_format(resource)
            if (
                not resource_id
                or resource_id in processed_ids
                or resource_format not in {"CSV", "XLS", "XLSX", "JSON"}
            ):
                continue
            processed_ids.add(resource_id)
            reference_resource_budget -= 1
            row, frame = _process_resource(
                session,
                package,
                resource,
                raw_dir,
                source_role="normalization_reference",
                pipeline_run=pipeline_run,
                timeout=timeout,
            )
            row["included_in_public_records"] = False
            inventory.append(row)
            if frame is not None:
                normalization_frames.append(frame)

    xplan_row, _ = try_xplan_arcgis(
        session, raw_dir, pipeline_run, timeout=timeout
    )
    inventory.append(xplan_row)

    for reference in REFERENCE_ONLY_SOURCES:
        if reference.source_url == XPLAN_SERVICE_REFERENCE_URL:
            continue
        inventory.append(
            {
                "source_name": reference.source_name,
                "source_url": reference.source_url,
                "source_type": reference.source_type,
                "source_role": reference.source_role,
                "priority": reference.priority,
                "package_id": reference.package_id,
                "package_name": reference.package_id,
                "package_title": reference.source_name,
                "organization": None,
                "resource_id": reference.resource_id,
                "resource_name": None,
                "resource_format": reference.expected_format,
                "resource_url": reference.source_url,
                "last_modified": None,
                "access_method": reference.access_method,
                "refresh_status": "reference_only",
                "http_status": None,
                "rows_loaded": 0,
                "file_path": None,
                "included_in_public_records": False,
                "error_message": None,
                "checked_at": pipeline_run,
            }
        )

    if public_frames:
        raw_collected = pd.concat(public_frames, ignore_index=True, sort=False)
        dedupe_columns = [
            column
            for column in ("original_resource_id", "_id", "MisparMitham")
            if column in raw_collected.columns
        ]
        if dedupe_columns:
            raw_collected = raw_collected.drop_duplicates(
                subset=dedupe_columns, keep="first"
            )
    else:
        raw_collected = pd.DataFrame()

    inventory_frame = pd.DataFrame(inventory)
    for column in INVENTORY_COLUMNS:
        if column not in inventory_frame.columns:
            inventory_frame[column] = pd.NA
    inventory_frame = inventory_frame[INVENTORY_COLUMNS]
    return raw_collected, inventory_frame, normalization_frames


def relative_inventory_paths(inventory: pd.DataFrame, project_root: Path) -> pd.DataFrame:
    result = inventory.copy()
    if "file_path" not in result.columns:
        return result

    def make_relative(value: Any) -> Any:
        if pd.isna(value) or not str(value).strip():
            return pd.NA
        path = Path(str(value))
        try:
            return str(path.resolve().relative_to(project_root.resolve()))
        except Exception:
            return str(path)

    result["file_path"] = result["file_path"].map(make_relative)
    return result
