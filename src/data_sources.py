from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


CKAN_PACKAGE_SEARCH_URL = "https://data.gov.il/api/3/action/package_search"
CKAN_DATASTORE_SEARCH_URL = "https://data.gov.il/api/3/action/datastore_search"
CKAN_PACKAGE_SHOW_URL = "https://data.gov.il/api/3/action/package_show"

MAVAT_URL = "https://mavat.iplan.gov.il/"
GOVMAP_URBAN_RENEWAL_URL = "https://www.govmap.gov.il/?lay=200720"
XPLAN_URL = "https://ags.iplan.gov.il/xplan/"
XPLAN_SERVICE_REFERENCE_URL = (
    "https://ags.iplan.gov.il/services/"
    "?f=PlanningPublic&s=ttl_all_blue_lines%2FMapServer"
)
XPLAN_REST_CANDIDATES = (
    "https://ags.iplan.gov.il/arcgis/rest/services/"
    "PlanningPublic/ttl_all_blue_lines/MapServer",
    "https://ags.iplan.gov.il/arcgis/rest/services/"
    "PlanningPublic/AllPlans/MapServer",
)


URBAN_RENEWAL_SEARCH_TERMS = (
    "התחדשות עירונית",
    "פינוי בינוי",
    "פינוי-בינוי",
    'תמ"א 38',
    "תמא 38",
    "מתחמי התחדשות",
    "מתחמים מוכרזים",
    "רשות ממשלתית להתחדשות עירונית",
    "urban renewal",
    "gis_urban_renewal",
)

NORMALIZATION_SEARCH_TERMS = (
    "רשימת יישובים",
    "סמלי יישובים",
    "יישובים בישראל",
    "רשימת רחובות",
    "רחובות בישראל",
)

SUPPORTED_RESOURCE_FORMATS = {
    "CSV",
    "XLS",
    "XLSX",
    "JSON",
    "GEOJSON",
    "ZIP",
    "SHP",
}

STRICT_RENEWAL_TERMS = (
    "התחדשות עירונית",
    "פינוי בינוי",
    "פינוי-בינוי",
    'תמ"א 38',
    "תמא 38",
    "מתחמי התחדשות",
    "urban renewal",
    "gis_urban_renewal",
)


@dataclass(frozen=True)
class SourceReference:
    source_name: str
    source_url: str
    source_type: str
    priority: int
    source_role: str
    access_method: str
    resource_id: str | None = None
    package_id: str | None = None
    expected_format: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


KNOWN_DATA_SOURCES = (
    SourceReference(
        source_name="data.gov.il — מתחמי התחדשות עירונית",
        source_url=(
            "https://data.gov.il/he/datasets/ministry_of_housing/"
            "urban_renewal/f65a0daf-f737-49c5-9424-d378d52104f5"
        ),
        source_type="government_open_data_resource",
        priority=1,
        source_role="urban_renewal_records",
        access_method="ckan_datastore_search",
        resource_id="f65a0daf-f737-49c5-9424-d378d52104f5",
        expected_format="CSV",
        notes="Official Ministry of Housing urban-renewal complexes resource.",
    ),
    SourceReference(
        source_name="data.gov.il — מתחמי התחדשות עירונית מוכרזים",
        source_url=(
            "https://data.gov.il/he/datasets/ministry_of_housing/"
            "gis_urban_renewal/ceb7bbb0-e2db-4e87-8a6c-0a250f5de001"
        ),
        source_type="government_open_data_gis_resource",
        priority=1,
        source_role="urban_renewal_records",
        access_method="ckan_discovery_then_direct_download",
        resource_id="ceb7bbb0-e2db-4e87-8a6c-0a250f5de001",
        package_id="gis_urban_renewal",
        expected_format="ZIP",
        notes=(
            "High-priority official GIS resource. Its page UUID is retained even "
            "when CKAN DataStore access is unavailable."
        ),
    ),
)

REFERENCE_ONLY_SOURCES = (
    SourceReference(
        source_name="GovMap — שכבת התחדשות עירונית",
        source_url=GOVMAP_URBAN_RENEWAL_URL,
        source_type="government_map_portal",
        priority=2,
        source_role="map_reference",
        access_method="reference_only_unless_documented_api_is_available",
        notes="The visual portal is not scraped.",
    ),
    SourceReference(
        source_name="XPLAN — שירותי תכנון ציבוריים",
        source_url=XPLAN_SERVICE_REFERENCE_URL,
        source_type="government_planning_gis",
        priority=2,
        source_role="planning_reference",
        access_method="arcgis_rest_detection",
        notes="Only a documented ArcGIS JSON/query endpoint may be ingested.",
    ),
    SourceReference(
        source_name='מבא"ת — מידע תכנוני',
        source_url=MAVAT_URL,
        source_type="government_planning_portal",
        priority=2,
        source_role="planning_reference",
        access_method="reference_only",
        notes="No aggressive scraping; public lookup links are generated locally.",
    ),
)


def source_registry() -> list[dict[str, Any]]:
    """Return the human-readable source registry used by scripts and notebooks."""
    rows = [source.to_dict() for source in KNOWN_DATA_SOURCES]
    rows.extend(source.to_dict() for source in REFERENCE_ONLY_SOURCES)
    rows.append(
        {
            "source_name": "data.gov.il — חיפוש CKAN דינמי",
            "source_url": CKAN_PACKAGE_SEARCH_URL,
            "source_type": "government_open_data_api",
            "priority": 1,
            "source_role": "source_discovery",
            "access_method": "package_search_paginated",
            "resource_id": None,
            "package_id": None,
            "expected_format": "JSON",
            "notes": "Searches all configured urban-renewal terms on every refresh.",
        }
    )
    rows.append(
        {
            "source_name": "data.gov.il — רשימות יישובים ורחובות",
            "source_url": CKAN_PACKAGE_SEARCH_URL,
            "source_type": "government_open_data_api",
            "priority": 1,
            "source_role": "normalization_reference",
            "access_method": "package_search_paginated",
            "resource_id": None,
            "package_id": None,
            "expected_format": "CSV/XLSX/JSON",
            "notes": "Used only to improve normalization and search quality.",
        }
    )
    return rows


def metadata_blob(package: dict[str, Any], resource: dict[str, Any]) -> str:
    organization = package.get("organization") or {}
    values = [
        package.get("title"),
        package.get("name"),
        package.get("notes"),
        organization.get("title"),
        organization.get("name"),
        resource.get("name"),
        resource.get("description"),
        resource.get("url"),
    ]
    return " ".join(str(value or "") for value in values).lower()


def is_strict_urban_renewal_resource(
    package: dict[str, Any], resource: dict[str, Any]
) -> bool:
    resource_id = str(resource.get("id") or "")
    if resource_id in {source.resource_id for source in KNOWN_DATA_SOURCES}:
        return True
    # Notes and descriptions can mention urban renewal only as one possible
    # use of a broad housing/planning dataset. Automatic inclusion therefore
    # requires the dataset/resource identity itself to be renewal-specific.
    blob = " ".join(
        str(value or "")
        for value in (
            package.get("title"),
            package.get("name"),
            resource.get("name"),
            resource.get("url"),
        )
    ).lower()
    return any(term.lower() in blob for term in STRICT_RENEWAL_TERMS)


def normalized_resource_format(resource: dict[str, Any]) -> str:
    value = str(resource.get("format") or "").strip().upper()
    if value == "GEOJSON":
        return value
    url = str(resource.get("url") or "").split("?", 1)[0].lower()
    extension_map = {
        ".csv": "CSV",
        ".xlsx": "XLSX",
        ".xls": "XLS",
        ".json": "JSON",
        ".geojson": "GEOJSON",
        ".zip": "ZIP",
        ".shp": "SHP",
    }
    for suffix, inferred in extension_map.items():
        if url.endswith(suffix):
            return inferred
    return value
