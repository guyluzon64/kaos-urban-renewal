from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion_utils import (  # noqa: E402
    collect_public_sources,
    relative_inventory_paths,
    utc_now_iso,
)
from src.stage_mapping import add_public_stage_fields  # noqa: E402
from src.standardization import standardize_records  # noqa: E402


DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"

SOURCE_INVENTORY_PATH = METADATA_DIR / "source_inventory.csv"
REFRESH_REPORT_PATH = METADATA_DIR / "latest_refresh_report.csv"
RAW_COLLECTED_PATH = PROCESSED_DIR / "urban_renewal_raw_collected.csv"
STANDARDIZED_PATH = PROCESSED_DIR / "urban_renewal_standardized.csv"
PUBLIC_PATH = PROCESSED_DIR / "urban_renewal_public.csv"


def read_existing_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    for encoding in ("utf-8-sig", "utf-8", "cp1255"):
        try:
            return pd.read_csv(path, encoding=encoding, low_memory=False)
        except Exception:
            continue
    return pd.DataFrame()


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def fallback_inventory_row(run_at: str, message: str) -> dict[str, object]:
    return {
        "source_name": "Previous checked-in public data",
        "source_url": pd.NA,
        "source_type": "local_pipeline_fallback",
        "source_role": "urban_renewal_records",
        "priority": 1,
        "package_id": pd.NA,
        "package_name": pd.NA,
        "package_title": pd.NA,
        "organization": pd.NA,
        "resource_id": pd.NA,
        "resource_name": pd.NA,
        "resource_format": "CSV",
        "resource_url": pd.NA,
        "last_modified": pd.NA,
        "access_method": "reuse_previous_checked_in_output",
        "refresh_status": "fallback_previous_data",
        "http_status": pd.NA,
        "rows_loaded": 0,
        "file_path": str(RAW_COLLECTED_PATH.relative_to(PROJECT_ROOT)),
        "included_in_public_records": True,
        "error_message": message,
        "checked_at": run_at,
    }


def build_refresh_report(
    inventory: pd.DataFrame,
    *,
    run_at: str,
    raw_rows: int,
    standardized_rows: int,
    public_rows: int,
) -> pd.DataFrame:
    report_columns = [
        "pipeline_last_run",
        "report_type",
        "source_name",
        "source_url",
        "source_role",
        "refresh_status",
        "rows_loaded",
        "error_message",
        "raw_rows",
        "standardized_rows",
        "public_rows",
        "output_path",
    ]
    rows: list[dict[str, object]] = []
    for _, item in inventory.iterrows():
        rows.append(
            {
                "pipeline_last_run": run_at,
                "report_type": "source",
                "source_name": item.get("source_name"),
                "source_url": item.get("source_url"),
                "source_role": item.get("source_role"),
                "refresh_status": item.get("refresh_status"),
                "rows_loaded": item.get("rows_loaded"),
                "error_message": item.get("error_message"),
                "raw_rows": pd.NA,
                "standardized_rows": pd.NA,
                "public_rows": pd.NA,
                "output_path": item.get("file_path"),
            }
        )
    rows.append(
        {
            "pipeline_last_run": run_at,
            "report_type": "pipeline_summary",
            "source_name": "update_public_data",
            "source_url": pd.NA,
            "source_role": "pipeline",
            "refresh_status": "succeeded" if public_rows else "completed_without_rows",
            "rows_loaded": public_rows,
            "error_message": pd.NA,
            "raw_rows": raw_rows,
            "standardized_rows": standardized_rows,
            "public_rows": public_rows,
            "output_path": str(PUBLIC_PATH.relative_to(PROJECT_ROOT)),
        }
    )
    return pd.DataFrame(rows, columns=report_columns)


def main() -> int:
    for folder in (RAW_DIR, PROCESSED_DIR, METADATA_DIR):
        folder.mkdir(parents=True, exist_ok=True)

    run_at = utc_now_iso()
    previous_raw = read_existing_csv(RAW_COLLECTED_PATH)
    previous_standardized = read_existing_csv(STANDARDIZED_PATH)
    previous_public = read_existing_csv(PUBLIC_PATH)

    try:
        raw_collected, inventory, normalization_frames = collect_public_sources(
            PROJECT_ROOT
        )
    except Exception as exc:
        raw_collected = pd.DataFrame()
        normalization_frames = []
        inventory = pd.DataFrame(
            [
                fallback_inventory_row(
                    run_at,
                    f"Unexpected collection error: {type(exc).__name__}: {exc}",
                )
            ]
        )

    if raw_collected.empty and not previous_raw.empty:
        raw_collected = previous_raw.copy()
        raw_collected["source_refresh_status"] = "fallback_previous_data"
        raw_collected["source_refresh_error"] = (
            "No source produced rows during this refresh; previous checked-in "
            "public data was retained."
        )
        raw_collected["pipeline_last_run"] = run_at
        inventory = pd.concat(
            [
                inventory,
                pd.DataFrame(
                    [
                        fallback_inventory_row(
                            run_at,
                            "No live source produced rows; previous checked-in "
                            "raw collection retained.",
                        )
                    ]
                ),
            ],
            ignore_index=True,
            sort=False,
        )

    write_csv(raw_collected, RAW_COLLECTED_PATH)

    standardized = standardize_records(
        raw_collected,
        normalization_frames=normalization_frames,
        pipeline_run=run_at,
    )
    if standardized.empty and not previous_standardized.empty:
        standardized = previous_standardized.copy()
        standardized["source_refresh_status"] = "fallback_previous_data"
        standardized["source_refresh_error"] = (
            "Current standardization produced no rows; previous output retained."
        )
        standardized["pipeline_last_run"] = run_at
    write_csv(standardized, STANDARDIZED_PATH)

    public = add_public_stage_fields(standardized)
    if public.empty and not previous_public.empty:
        public = previous_public.copy()
        public["source_refresh_status"] = "fallback_previous_data"
        public["source_refresh_error"] = (
            "Current public output produced no rows; previous output retained."
        )
        public["pipeline_last_run"] = run_at
    write_csv(public, PUBLIC_PATH)

    inventory = relative_inventory_paths(inventory, PROJECT_ROOT)
    write_csv(inventory, SOURCE_INVENTORY_PATH)

    refresh_report = build_refresh_report(
        inventory,
        run_at=run_at,
        raw_rows=len(raw_collected),
        standardized_rows=len(standardized),
        public_rows=len(public),
    )
    write_csv(refresh_report, REFRESH_REPORT_PATH)

    source_rows = inventory[
        ~inventory["source_role"].isin(["source_discovery"])
    ].copy()
    attempted = len(source_rows)
    succeeded = int((source_rows["refresh_status"] == "succeeded").sum())
    failed = int(
        source_rows["refresh_status"]
        .fillna("")
        .astype(str)
        .str.contains("failed", case=False)
        .sum()
    )

    print("Public data refresh complete")
    print(f"Rows loaded: {len(public):,}")
    print(f"Sources attempted: {attempted:,}")
    print(f"Sources succeeded: {succeeded:,}")
    print(f"Sources failed: {failed:,}")
    print(f"Output CSV: {PUBLIC_PATH.relative_to(PROJECT_ROOT)}")
    print(
        "Dashboard: "
        f"{(PROJECT_ROOT / 'app' / 'urban_renewal_legal_scout.py').relative_to(PROJECT_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

