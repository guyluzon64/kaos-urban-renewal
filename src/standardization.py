from __future__ import annotations

import hashlib
import re
from typing import Any, Iterable
from urllib.parse import quote

import pandas as pd

from src.data_sources import GOVMAP_URBAN_RENEWAL_URL, MAVAT_URL, XPLAN_URL


EMPTY_MARKERS = {"", "nan", "none", "null", "n/a", "na", "-", "--", "<na>"}

STANDARD_COLUMNS = [
    "record_id",
    "source_record_id",
    "city",
    "city_code",
    "neighborhood",
    "street_or_area",
    "complex_name",
    "plan_number",
    "renewal_type",
    "planning_status_raw",
    "planning_status_normalized",
    "declared_complex",
    "existing_units",
    "additional_units",
    "proposed_units",
    "permits_total",
    "declaration_date",
    "validity_year",
    "in_execution",
    "mavat_url",
    "map_url",
    "source_name",
    "source_url",
    "source_type",
    "original_resource_id",
    "last_updated",
    "confidence_level",
    "data_confidence_score",
    "data_quality_flag",
    "mavat_lookup_url",
    "govmap_lookup_url",
    "xplan_lookup_url",
    "source_refresh_status",
    "source_refresh_error",
    "pipeline_last_run",
]


FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "source_record_id": (
        "source_record_id",
        "MisparMitham",
        "_id",
        "OBJECTID",
        "ObjectID",
        "מזהה",
        "מפתח לפוליגון תכנית",
    ),
    "city": (
        "city",
        "Yeshuv",
        "יישוב",
        "ישוב",
        "שם יישוב",
        "שם ישוב",
        "SHEM_YISHUV",
        "SETL_NAME",
        "CITY_NAME",
    ),
    "city_code": (
        "city_code",
        "SemelYeshuv",
        "סמל יישוב",
        "סמל ישוב",
        "SEMEL_YISHUV",
        "SETL_CODE",
    ),
    "neighborhood": (
        "neighborhood",
        "שכונה",
        "שם שכונה",
        "NEIGHBORHOOD",
    ),
    "street_or_area": (
        "street_or_area",
        "רחוב",
        "כתובת",
        "אזור",
        "תיאור מיקום",
        "STREET",
        "ADDRESS",
        "LOCATION",
    ),
    "complex_name": (
        "complex_name",
        "ShemMitcham",
        "שם מתחם",
        "שם תוכנית",
        "שם תכנית",
        "PLAN_NAME",
        "PL_NAME",
        "NAME",
    ),
    "plan_number": (
        "plan_number",
        "MisparTochnit",
        "מספר תוכנית",
        "מספר תכנית",
        "PLAN_NUM",
        "PL_NUMBER",
        "PLAN_NUMBER",
    ),
    "renewal_type": (
        "renewal_type",
        "Maslul",
        "מסלול",
        "סוג התחדשות",
        "סוג תכנית",
        "PLAN_TYPE",
    ),
    "planning_status_raw": (
        "planning_status_raw",
        "Status",
        "סטטוס",
        "שלב תכנוני",
        "מצב תכנית",
        "PLAN_STATUS",
        "STATUS",
    ),
    "existing_units": (
        "existing_units",
        "YachadKayam",
        'יח"ד קיימות',
        "יחידות קיימות",
        "EXISTING_UNITS",
    ),
    "additional_units": (
        "additional_units",
        "YachadTosafti",
        'יח"ד תוספתיות',
        "יחידות תוספתיות",
        "ADDITIONAL_UNITS",
    ),
    "proposed_units": (
        "proposed_units",
        "YachadMutza",
        'יח"ד מוצעות',
        "יחידות מוצעות",
        "יחד פוטנציאל לשיווק",
        "PROPOSED_UNITS",
    ),
    "permits_total": (
        "permits_total",
        "SachHeterim",
        "סך היתרים",
        "מספר היתרים",
        "PERMITS",
    ),
    "declaration_date": (
        "declaration_date",
        "TaarichHachraza",
        "תאריך הכרזה",
        "DECLARATION_DATE",
    ),
    "validity_year": (
        "validity_year",
        "ShnatMatanTokef",
        "שנת מתן תוקף",
        "שנת תוקף",
        "VALIDITY_YEAR",
    ),
    "in_execution": (
        "in_execution",
        "Bebitzua",
        "בביצוע",
        "במימוש",
        "IN_EXECUTION",
    ),
    "mavat_url": (
        "mavat_url",
        "KishurLatar",
        "קישור לאתר מנהל תכנון",
        "קישור למבא״ת",
        "קישור למבא\"ת",
        "MAVAT_URL",
    ),
    "map_url": (
        "map_url",
        "KishurLaMapa",
        "קישור למפה",
        "MAP_URL",
    ),
}


def clean_text(value: Any) -> Any:
    if pd.isna(value):
        return pd.NA
    text = re.sub(r"\s+", " ", str(value)).strip()
    if text.lower() in EMPTY_MARKERS:
        return pd.NA
    return text


def clean_identifier(value: Any) -> Any:
    text = clean_text(value)
    if pd.isna(text):
        return pd.NA
    text = str(text)
    return text[:-2] if re.fullmatch(r"\d+\.0", text) else text


def clean_url(value: Any) -> Any:
    text = clean_text(value)
    if pd.isna(text):
        return pd.NA
    return text if str(text).lower().startswith(("http://", "https://")) else pd.NA


def parse_number(value: Any) -> Any:
    text = clean_text(value)
    if pd.isna(text):
        return pd.NA
    cleaned = re.sub(r"[^\d.\-]", "", str(text).replace(",", ""))
    if cleaned in {"", "-", ".", "-."}:
        return pd.NA
    number = pd.to_numeric(cleaned, errors="coerce")
    if pd.isna(number):
        return pd.NA
    number = float(number)
    return int(number) if number.is_integer() else number


def parse_boolean(value: Any) -> Any:
    text = clean_text(value)
    if pd.isna(text):
        return pd.NA
    normalized = str(text).lower()
    if normalized in {"כן", "true", "1", "yes", "y", "בביצוע", "במימוש"}:
        return True
    if normalized in {"לא", "false", "0", "no", "n"}:
        return False
    return pd.NA


def first_available_series(
    frame: pd.DataFrame, aliases: Iterable[str]
) -> pd.Series:
    result = pd.Series(pd.NA, index=frame.index, dtype="object")
    for alias in aliases:
        if alias not in frame.columns:
            continue
        candidate = frame[alias]
        missing = result.isna() | result.astype("string").str.strip().isin(
            list(EMPTY_MARKERS)
        )
        result.loc[missing] = candidate.loc[missing]
    return result


def normalize_plan_number(value: Any) -> Any:
    text = clean_identifier(value)
    if pd.isna(text):
        return pd.NA
    return re.sub(r"\s+", "", str(text)).replace("–", "-").replace("—", "-")


def normalize_status(raw_status: Any, in_execution: Any) -> str:
    text_value = clean_text(raw_status)
    text = str(text_value).lower() if not pd.isna(text_value) else ""
    if parse_boolean(in_execution) is True:
        return "CONSTRUCTION"
    if any(term in text for term in ("הושלם", "הסתיים", "completed")):
        return "COMPLETED"
    if any(
        term in text
        for term in ("בביצוע", "במימוש", "בנייה", "בניה", "construction")
    ):
        return "CONSTRUCTION"
    if any(
        term in text
        for term in (
            "היתר אושר",
            "היתר בנייה",
            "היתר בניה",
            "אחרי רישוי",
            "permit approved",
        )
    ):
        return "PERMIT_APPROVED"
    if any(
        term in text
        for term in ("בקשה להיתר", "רישוי", "permit requested")
    ):
        return "PERMIT_REQUESTED"
    if any(
        term in text
        for term in (
            "מאושרת",
            "מאושר",
            "מתן תוקף",
            "פורסם לאישור",
            "approved",
        )
    ):
        return "PLAN_APPROVED"
    if any(
        term in text
        for term in ("מופקדת", "הופקדה", "הפקדה", "deposited")
    ):
        return "PLAN_DEPOSITED"
    if any(
        term in text
        for term in (
            "תכנון סטטוטורי",
            "תכנון ראשוני",
            "תנאי סף",
            "בתכנון",
            "בהכנה",
            "דיון",
            "in progress",
        )
    ):
        return "PLAN_IN_PROGRESS"
    if any(term in text for term in ("מתחם מוכרז", "הכרזה", "declared")):
        return "DECLARED_COMPLEX"
    if any(term in text for term in ("מדיניות", "אזור", "policy")):
        return "POLICY_AREA_ONLY"
    return "UNKNOWN"


def extract_city_vocabulary(
    normalization_frames: Iterable[pd.DataFrame] | None,
) -> dict[str, str]:
    vocabulary: dict[str, str] = {}
    likely_columns = {
        "יישוב",
        "ישוב",
        "שם יישוב",
        "שם ישוב",
        "שם_ישוב",
        "city",
        "CITY_NAME",
        "SETL_NAME",
    }
    for frame in normalization_frames or []:
        for column in frame.columns:
            if str(column).strip() not in likely_columns:
                continue
            for value in frame[column].dropna().head(100_000):
                canonical = clean_text(value)
                if pd.isna(canonical):
                    continue
                key = re.sub(r"[\s\-־]+", "", str(canonical)).lower()
                vocabulary.setdefault(key, str(canonical))
    return vocabulary


def normalize_city(value: Any, vocabulary: dict[str, str]) -> Any:
    text = clean_text(value)
    if pd.isna(text):
        return pd.NA
    compact = re.sub(r"[\s\-־]+", "", str(text)).lower()
    return vocabulary.get(compact, text)


def infer_declared_complex(row: pd.Series) -> Any:
    if row.get("planning_status_normalized") == "DECLARED_COMPLEX":
        return True
    if not pd.isna(row.get("source_record_id")) and "MisparMitham" in str(
        row.get("_mapping_basis", "")
    ):
        return True
    if not pd.isna(row.get("declaration_date")):
        return True
    source = " ".join(
        str(row.get(column) or "")
        for column in ("source_name", "source_url", "source_type")
    ).lower()
    if "מתחמי התחדשות עירונית" in source or "urban_renewal" in source:
        return True
    return pd.NA


def data_quality_flags(row: pd.Series) -> str:
    flags: list[str] = []
    if pd.isna(row.get("city")):
        flags.append("MISSING_CITY")
    if pd.isna(row.get("complex_name")):
        flags.append("MISSING_COMPLEX_NAME")
    if row.get("planning_status_normalized") == "UNKNOWN":
        flags.append("MISSING_OR_UNCLEAR_STATUS")
    if pd.isna(row.get("source_url")):
        flags.append("MISSING_SOURCE_URL")
    existing = row.get("existing_units")
    proposed = row.get("proposed_units")
    if not pd.isna(existing) and not pd.isna(proposed) and proposed < existing:
        flags.append("UNIT_LOGIC_ANOMALY")
    for column in (
        "existing_units",
        "additional_units",
        "proposed_units",
        "permits_total",
    ):
        value = row.get(column)
        if not pd.isna(value) and value < 0:
            flags.append("NEGATIVE_VALUE")
            break
    return "|".join(dict.fromkeys(flags)) if flags else "OK"


def confidence_score(row: pd.Series) -> int:
    score = 20
    source_blob = " ".join(
        str(row.get(column) or "")
        for column in ("source_name", "source_url", "source_type")
    ).lower()
    if ".gov.il" in source_blob or "government" in source_blob:
        score += 20
    if not pd.isna(row.get("city")):
        score += 10
    if not pd.isna(row.get("complex_name")):
        score += 10
    if not pd.isna(row.get("plan_number")):
        score += 10
    if row.get("planning_status_normalized") != "UNKNOWN":
        score += 15
    if not pd.isna(row.get("source_url")):
        score += 10
    if not pd.isna(row.get("last_updated")):
        score += 5
    if row.get("data_quality_flag") != "OK":
        score -= 20
    return max(0, min(100, int(score)))


def confidence_level(score: Any) -> str:
    if pd.isna(score):
        return "LOW"
    if int(score) >= 80:
        return "HIGH"
    if int(score) >= 50:
        return "MEDIUM"
    return "LOW"


def stable_record_id(row: pd.Series) -> str:
    parts = [
        row.get("original_resource_id"),
        row.get("source_record_id"),
        row.get("city"),
        row.get("complex_name"),
        row.get("plan_number"),
    ]
    raw = "|".join("" if pd.isna(value) else str(value) for value in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]


def _mavat_lookup(plan_number: Any, existing_url: Any) -> Any:
    existing = clean_url(existing_url)
    if not pd.isna(existing):
        return existing
    if pd.isna(plan_number):
        return pd.NA
    return MAVAT_URL


def _govmap_lookup(city: Any, complex_name: Any, existing_url: Any) -> Any:
    existing = clean_url(existing_url)
    if not pd.isna(existing):
        return existing
    if pd.isna(city) and pd.isna(complex_name):
        return GOVMAP_URBAN_RENEWAL_URL
    query = " ".join(
        str(value) for value in (city, complex_name) if not pd.isna(value)
    )
    return f"{GOVMAP_URBAN_RENEWAL_URL}&q={quote(query)}"


def is_relevant_public_row(raw_row: pd.Series) -> bool:
    if not pd.isna(raw_row.get("MisparMitham")) or not pd.isna(
        raw_row.get("ShemMitcham")
    ):
        return True
    role = str(raw_row.get("source_role") or "")
    if role == "urban_renewal_records":
        return True
    source_blob = " ".join(
        str(raw_row.get(column) or "")
        for column in ("source_name", "source_url", "source_type")
    ).lower()
    return any(
        term in source_blob
        for term in (
            "התחדשות עירונית",
            "פינוי בינוי",
            "urban renewal",
            "urban_renewal",
        )
    )


def standardize_records(
    raw_df: pd.DataFrame,
    *,
    normalization_frames: Iterable[pd.DataFrame] | None = None,
    pipeline_run: str,
) -> pd.DataFrame:
    """Map supported official source schemas into one cautious public schema."""
    if raw_df.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS)
    relevant_mask = raw_df.apply(is_relevant_public_row, axis=1)
    source = raw_df.loc[relevant_mask].copy()
    if source.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    standardized = pd.DataFrame(index=source.index)
    mapping_basis: list[str] = []
    for target, aliases in FIELD_ALIASES.items():
        standardized[target] = first_available_series(source, aliases)
    for aliases in FIELD_ALIASES.values():
        mapping_basis.extend(alias for alias in aliases if alias in source.columns)
    standardized["_mapping_basis"] = "|".join(mapping_basis)

    metadata_columns = (
        "source_name",
        "source_url",
        "source_type",
        "original_resource_id",
        "source_last_modified",
        "source_refresh_status",
        "source_refresh_error",
        "pipeline_last_run",
    )
    for column in metadata_columns:
        standardized[column] = (
            source[column]
            if column in source.columns
            else pd.Series(pd.NA, index=source.index, dtype="object")
        )

    vocabulary = extract_city_vocabulary(normalization_frames)
    standardized["source_record_id"] = standardized["source_record_id"].map(
        clean_identifier
    )
    standardized["city"] = standardized["city"].map(
        lambda value: normalize_city(value, vocabulary)
    )
    standardized["city_code"] = standardized["city_code"].map(clean_identifier)
    for column in (
        "neighborhood",
        "street_or_area",
        "complex_name",
        "renewal_type",
        "planning_status_raw",
        "source_name",
        "source_type",
        "original_resource_id",
        "source_refresh_status",
        "source_refresh_error",
    ):
        standardized[column] = standardized[column].map(clean_text)
    standardized["plan_number"] = standardized["plan_number"].map(
        normalize_plan_number
    )
    for column in (
        "existing_units",
        "additional_units",
        "proposed_units",
        "permits_total",
        "validity_year",
    ):
        standardized[column] = standardized[column].map(parse_number)
        standardized[column] = pd.to_numeric(
            standardized[column], errors="coerce"
        ).astype("Int64")
    standardized["declaration_date"] = pd.to_datetime(
        standardized["declaration_date"], dayfirst=True, errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    standardized["in_execution"] = standardized["in_execution"].map(parse_boolean)
    standardized["mavat_url"] = standardized["mavat_url"].map(clean_url)
    standardized["map_url"] = standardized["map_url"].map(clean_url)
    standardized["source_url"] = standardized["source_url"].map(clean_url)
    standardized["last_updated"] = standardized["source_last_modified"].map(
        clean_text
    )
    standardized["pipeline_last_run"] = standardized["pipeline_last_run"].map(
        clean_text
    ).fillna(pipeline_run)

    standardized["planning_status_normalized"] = standardized.apply(
        lambda row: normalize_status(
            row.get("planning_status_raw"), row.get("in_execution")
        ),
        axis=1,
    )
    standardized["declared_complex"] = standardized.apply(
        infer_declared_complex, axis=1
    )
    standardized["data_quality_flag"] = standardized.apply(
        data_quality_flags, axis=1
    )
    standardized["data_confidence_score"] = standardized.apply(
        confidence_score, axis=1
    )
    standardized["confidence_level"] = standardized[
        "data_confidence_score"
    ].map(confidence_level)

    standardized["mavat_lookup_url"] = standardized.apply(
        lambda row: _mavat_lookup(
            row.get("plan_number"), row.get("mavat_url")
        ),
        axis=1,
    )
    standardized["govmap_lookup_url"] = standardized.apply(
        lambda row: _govmap_lookup(
            row.get("city"), row.get("complex_name"), row.get("map_url")
        ),
        axis=1,
    )
    standardized["xplan_lookup_url"] = standardized["plan_number"].map(
        lambda value: XPLAN_URL if not pd.isna(value) else pd.NA
    )
    standardized["record_id"] = standardized.apply(stable_record_id, axis=1)

    standardized = standardized.drop_duplicates(
        subset=["record_id"], keep="first"
    ).reset_index(drop=True)
    for column in STANDARD_COLUMNS:
        if column not in standardized.columns:
            standardized[column] = pd.NA
    return standardized[STANDARD_COLUMNS]
