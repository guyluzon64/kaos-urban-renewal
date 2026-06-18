from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


SITE_NAME = "בניין, מה נסגר?"
SITE_SUBTITLE = (
    "בודקים מידע ציבורי על התחדשות עירונית — בלי חליפה, בלי סיסמאות, "
    "ובלי להעמיד פנים שזה ייעוץ משפטי."
)

TOP_DISCLAIMER = (
    "האתר הוא מיזם ללא מטרות רווח. המידע מוצג כפי שנמצא במקורות ציבוריים "
    "ורשמיים, ועלול להיות חלקי, לא מעודכן או שגוי. האתר לא נותן ייעוץ "
    "משפטי, תכנוני, שמאי או נדל״ני, ולא מחליף בדיקה מול עורך דין, העירייה, "
    "מינהל התכנון או הגורם הרשמי הרלוונטי."
)
MICROCOPY = "בקיצור: זה מצפן, לא פסק דין."
DETAIL_DISCLAIMER = (
    "השלב המוצג מתאר רק חיווי שנמצא במידע ציבורי. הוא אינו תחזית, אינו "
    "קביעה משפטית או תכנונית, ואינו מלמד לבדו מה מצב הבניין או מה יקרה בהמשך."
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "urban_renewal_public.csv"
)
REFRESH_REPORT_PATH = (
    PROJECT_ROOT / "data" / "metadata" / "latest_refresh_report.csv"
)

st.set_page_config(
    page_title=SITE_NAME,
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"], .stApp {
        direction: rtl;
        text-align: right;
        font-family: "Segoe UI", Arial, "Noto Sans Hebrew", sans-serif;
    }
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] * {
        direction: rtl;
        text-align: right;
    }
    .hero {
        padding: 1.25rem 1.4rem;
        border-radius: 22px;
        background: linear-gradient(135deg, #effaf6 0%, #fffaf0 100%);
        border: 1px solid rgba(20, 83, 70, 0.12);
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin: 0 0 .25rem 0;
        font-size: clamp(2.1rem, 5vw, 3.5rem);
        color: #17453b;
    }
    .hero p {
        margin: 0;
        font-size: 1.08rem;
        color: #385d55;
    }
    .microcopy {
        margin-top: .55rem;
        font-weight: 800;
        color: #8a4b08;
    }
    .stage-card {
        border: 1px solid rgba(20, 83, 70, 0.16);
        border-radius: 18px;
        padding: 1rem 1.2rem;
        background: var(--secondary-background-color);
        margin: .7rem 0;
    }
    .stage-number {
        font-size: 2rem;
        font-weight: 900;
        color: #147a63;
    }
    div[data-testid="stDataFrame"] {
        direction: rtl;
    }
    div[data-testid="stMetric"] {
        border: 1px solid rgba(127, 127, 127, .20);
        border-radius: 16px;
        padding: .75rem;
        background: var(--secondary-background-color);
    }
    a { font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)


DEFAULT_COLUMNS: dict[str, Any] = {
    "record_id": pd.NA,
    "city": pd.NA,
    "street_or_area": pd.NA,
    "complex_name": pd.NA,
    "plan_number": pd.NA,
    "renewal_type": pd.NA,
    "planning_status_raw": pd.NA,
    "planning_status_normalized": "UNKNOWN",
    "existing_units": pd.NA,
    "proposed_units": pd.NA,
    "source_name": pd.NA,
    "source_url": pd.NA,
    "source_type": pd.NA,
    "last_updated": pd.NA,
    "public_stage_index": 0,
    "public_stage_total": 9,
    "public_stage_name_he": "לא נמצא שלב ברור",
    "public_stage_short_explanation_he": (
        "מצאנו מידע חלקי או לא מספיק כדי לזהות שלב ברור."
    ),
    "public_stage_basis": "insufficient_public_information",
    "public_stage_confidence": "LOW",
    "public_friendly_summary_he": pd.NA,
    "public_disclaimer_he": DETAIL_DISCLAIMER,
    "mavat_lookup_url": pd.NA,
    "govmap_lookup_url": pd.NA,
    "xplan_lookup_url": pd.NA,
    "source_refresh_status": pd.NA,
    "source_refresh_error": pd.NA,
    "pipeline_last_run": pd.NA,
    "data_quality_flag": pd.NA,
}

CONFIDENCE_HE = {
    "HIGH": "תיעוד ציבורי מלא יחסית",
    "MEDIUM": "תיעוד ציבורי חלקי",
    "LOW": "תיעוד ציבורי מצומצם",
}

TABLE_LABELS = {
    "city": "עיר",
    "street_or_area": "רחוב / אזור",
    "complex_name": "שם מתחם",
    "plan_number": "מספר תכנית",
    "renewal_type": "סוג התחדשות",
    "stage_display": "שלב ציבורי מזוהה",
    "public_stage_name_he": "איפה זה עומד?",
    "confidence_display": "שלמות המידע",
    "source_name": "מקור",
    "last_updated": "עודכן לאחרונה",
}


def has_value(value: Any) -> bool:
    if pd.isna(value):
        return False
    return str(value).strip().lower() not in {
        "",
        "nan",
        "none",
        "null",
        "<na>",
        "-",
        "--",
    }


def safe_text(value: Any, fallback: str = "לא ידוע") -> str:
    return str(value).strip() if has_value(value) else fallback


def safe_url(value: Any) -> str | None:
    if not has_value(value):
        return None
    url = str(value).strip()
    return url if url.startswith(("https://", "http://")) else None


def ensure_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column, default in DEFAULT_COLUMNS.items():
        if column not in result.columns:
            result[column] = default
    result["public_stage_index"] = (
        pd.to_numeric(result["public_stage_index"], errors="coerce")
        .fillna(0)
        .clip(0, 9)
        .astype(int)
    )
    result["public_stage_total"] = (
        pd.to_numeric(result["public_stage_total"], errors="coerce")
        .fillna(9)
        .astype(int)
    )
    result["stage_display"] = (
        result["public_stage_index"].astype(str)
        + " מתוך "
        + result["public_stage_total"].astype(str)
    )
    result["confidence_display"] = (
        result["public_stage_confidence"]
        .fillna("LOW")
        .astype(str)
        .str.upper()
        .map(CONFIDENCE_HE)
        .fillna("לא ידוע")
    )
    return result


@st.cache_data(show_spinner=False)
def load_public_data() -> pd.DataFrame:
    if not PUBLIC_DATA_PATH.exists():
        return pd.DataFrame(columns=DEFAULT_COLUMNS)
    return ensure_columns(
        pd.read_csv(PUBLIC_DATA_PATH, encoding="utf-8-sig", low_memory=False)
    )


@st.cache_data(show_spinner=False)
def load_refresh_report() -> pd.DataFrame:
    if not REFRESH_REPORT_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(
        REFRESH_REPORT_PATH, encoding="utf-8-sig", low_memory=False
    )


def options(frame: pd.DataFrame, column: str) -> list[str]:
    if column not in frame.columns:
        return []
    values = frame[column].dropna().astype(str).str.strip()
    values = values[~values.str.lower().isin(["", "nan", "none", "null", "<na>"])]
    return sorted(values.unique().tolist())


def apply_filter(
    frame: pd.DataFrame, column: str, selected: list[str]
) -> pd.DataFrame:
    if not selected:
        return frame
    return frame[frame[column].fillna("").astype(str).isin(selected)]


def selection_label(row: pd.Series) -> str:
    parts = [
        safe_text(row.get("city"), ""),
        safe_text(row.get("complex_name"), ""),
        safe_text(row.get("plan_number"), ""),
    ]
    text = " · ".join(part for part in parts if part)
    return text or safe_text(row.get("record_id"), "רשומה ללא שם")


def render_source_buttons(row: pd.Series) -> None:
    buttons = [
        ("פתח מקור רשמי", safe_url(row.get("source_url"))),
        ('בדוק במבא"ת', safe_url(row.get("mavat_lookup_url"))),
        (
            "פתח מפה",
            safe_url(row.get("govmap_lookup_url"))
            or safe_url(row.get("xplan_lookup_url")),
        ),
    ]
    available = [(label, url) for label, url in buttons if url]
    if not available:
        st.caption("לא נמצא קישור ציבורי תקין לרשומה הזאת.")
        return
    columns = st.columns(len(available))
    for column, (label, url) in zip(columns, available):
        column.link_button(label, url, width="stretch")


def render_record_detail(row: pd.Series) -> None:
    stage = int(row.get("public_stage_index") or 0)
    total = int(row.get("public_stage_total") or 9)
    summary = safe_text(
        row.get("public_friendly_summary_he"),
        (
            f"לפי המידע הציבורי שמצאנו, השלב המזוהה הוא "
            f"{stage} מתוך {total}: "
            f"{safe_text(row.get('public_stage_name_he'))}."
        ),
    )
    st.markdown(
        f"""
        <div class="stage-card">
            <div class="stage-number">שלב ציבורי מזוהה: {stage} מתוך {total}</div>
            <h3>{safe_text(row.get("public_stage_name_he"))}</h3>
            <p>{summary}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(stage / total if total else 0)
    st.write(safe_text(row.get("public_stage_short_explanation_he")))

    info_a, info_b, info_c = st.columns(3)
    info_a.metric("עיר", safe_text(row.get("city")))
    info_b.metric("מספר תכנית", safe_text(row.get("plan_number")))
    info_c.metric(
        "שלמות המידע",
        CONFIDENCE_HE.get(
            safe_text(row.get("public_stage_confidence"), "LOW").upper(),
            "לא ידוע",
        ),
    )

    st.markdown(f"**מקור:** {safe_text(row.get('source_name'))}")
    render_source_buttons(row)

    with st.expander("מידע טכני למי שאוהב טבלאות"):
        technical_fields = {
            "סטטוס כפי שנכתב במקור": row.get("planning_status_raw"),
            "סטטוס מנורמל": row.get("planning_status_normalized"),
            "בסיס לזיהוי השלב": row.get("public_stage_basis"),
            "סוג מקור": row.get("source_type"),
            "מועד עדכון במקור": row.get("last_updated"),
            "מצב רענון המקור": row.get("source_refresh_status"),
            "הערת איכות נתונים": row.get("data_quality_flag"),
        }
        for label, value in technical_fields.items():
            st.write(f"**{label}:** {safe_text(value)}")
        internal_fields = [
            column
            for column in (
                "planning_maturity_score",
                "ml_advancement_score",
                "project_momentum_score",
            )
            if column in row.index and has_value(row.get(column))
        ]
        if internal_fields:
            st.divider()
            st.caption(
                "שדות טכניים ישנים מוצגים כאן רק לשקיפות. הם אינם תחזית, "
                "אינם דירוג ציבורי ואינם חלק מהשלב הציבורי המזוהה."
            )
            for column in internal_fields:
                st.write(f"`{column}`: {safe_text(row.get(column))}")

    st.warning(
        safe_text(row.get("public_disclaimer_he"), DETAIL_DISCLAIMER)
    )


st.markdown(
    f"""
    <div class="hero">
        <h1>{SITE_NAME}</h1>
        <p>{SITE_SUBTITLE}</p>
        <div class="microcopy">{MICROCOPY}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.info(TOP_DISCLAIMER)

data = load_public_data()
refresh_report = load_refresh_report()

if data.empty:
    st.error(
        "עדיין אין קובץ נתונים ציבורי להצגה. הריצו משורש הפרויקט: "
        "`python scripts/update_public_data.py`"
    )
    st.stop()

with st.expander("מתי המידע עודכן?"):
    pipeline_dates = data["pipeline_last_run"].dropna().astype(str)
    source_dates = data["last_updated"].dropna().astype(str)
    st.write(
        f"**ריצת העדכון האחרונה:** "
        f"{pipeline_dates.max() if not pipeline_dates.empty else 'לא ידוע'}"
    )
    st.write(
        f"**העדכון המאוחר ביותר שדווח במקור:** "
        f"{source_dates.max() if not source_dates.empty else 'לא ידוע'}"
    )
    if not refresh_report.empty:
        source_rows = refresh_report[
            refresh_report.get("report_type", pd.Series(dtype=str)) == "source"
        ]
        failed = (
            source_rows.get("refresh_status", pd.Series(dtype=str))
            .fillna("")
            .astype(str)
            .str.contains("failed", case=False)
            .sum()
        )
        st.caption(
            f"בדוח הרענון האחרון נרשמו {len(source_rows):,} ניסיונות מקור, "
            f"מהם {int(failed):,} עם שגיאה או גישת עזר בלבד."
        )
    st.caption(
        "גם אם כתוב שהמידע עודכן היום, המקור עצמו יכול להכיל מידע ישן יותר."
    )

search_text = st.text_input(
    "חפשו עיר, רחוב, שם מתחם או מספר תכנית",
    placeholder="לדוגמה: חולון, ארלוזורוב, מתחם ההסתדרות, 507-…",
    help=(
        "החיפוש עובר על פרטי המקום, שם המתחם, מספר התכנית והטקסט "
        "שהתקבל מהמקור הציבורי."
    ),
)

st.sidebar.markdown("## סינון")
st.sidebar.caption("אפשר להשאיר מסנן ריק כדי לראות את כל הרשומות.")
selected_cities = st.sidebar.multiselect(
    "עיר",
    options(data, "city"),
    help="שם היישוב כפי שנמצא במקור הציבורי, לאחר ניקוי בסיסי.",
)
selected_stages = st.sidebar.multiselect(
    "שלב ציבורי מזוהה",
    sorted(data["public_stage_index"].dropna().astype(int).unique().tolist()),
    format_func=lambda value: f"{value} מתוך 9",
    help="תיאור של השלב שניתן לזהות ברשומות ציבוריות, לא תחזית.",
)
selected_types = st.sidebar.multiselect(
    "סוג התחדשות",
    options(data, "renewal_type"),
    help="המסלול או סוג ההתחדשות כפי שנכתב במקור.",
)
selected_sources = st.sidebar.multiselect(
    "מקור",
    options(data, "source_name"),
    help="הגוף או מאגר המידע הציבורי שממנו התקבלה הרשומה.",
)
selected_confidence = st.sidebar.multiselect(
    "שלמות המידע",
    options(data, "confidence_display"),
    help="כמה שדות תיעוד בסיסיים נמצאו ברשומה. זה אינו מדד לתכנית עצמה.",
)

filtered = data.copy()
filtered = apply_filter(filtered, "city", selected_cities)
if selected_stages:
    filtered = filtered[
        filtered["public_stage_index"].isin(selected_stages)
    ]
filtered = apply_filter(filtered, "renewal_type", selected_types)
filtered = apply_filter(filtered, "source_name", selected_sources)
filtered = apply_filter(filtered, "confidence_display", selected_confidence)

if search_text.strip():
    search_columns = [
        "city",
        "street_or_area",
        "complex_name",
        "plan_number",
        "renewal_type",
        "planning_status_raw",
        "source_name",
    ]
    haystack = (
        filtered[search_columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.lower()
    )
    filtered = filtered[
        haystack.str.contains(search_text.strip().lower(), regex=False, na=False)
    ]

metric_a, metric_b, metric_c, metric_d = st.columns(4)
metric_a.metric("רשומות שנמצאו", f"{len(filtered):,}")
metric_b.metric("ערים", f"{filtered['city'].nunique(dropna=True):,}")
metric_c.metric(
    "מקורות ציבוריים",
    f"{filtered['source_name'].nunique(dropna=True):,}",
)
metric_d.metric(
    "עם מספר תכנית",
    f"{int(filtered['plan_number'].map(has_value).sum()):,}",
)

if filtered.empty:
    st.warning("לא נמצאו רשומות לפי החיפוש הזה. נסו ניסוח קצר יותר או פחות מסננים.")
else:
    st.markdown("### מה נמצא במידע הציבורי")
    public_columns = [
        "city",
        "street_or_area",
        "complex_name",
        "plan_number",
        "renewal_type",
        "stage_display",
        "public_stage_name_he",
        "confidence_display",
        "source_name",
        "last_updated",
    ]
    table = filtered[public_columns].rename(columns=TABLE_LABELS)
    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        height=480,
        column_config={
            "שלב ציבורי מזוהה": st.column_config.TextColumn(
                "שלב ציבורי מזוהה",
                help="מיקום תיאורי לפי הרשומה הציבורית בלבד.",
            ),
            "שלמות המידע": st.column_config.TextColumn(
                "שלמות המידע",
                help="כמה פרטי תיעוד בסיסיים נמצאו ברשומה.",
            ),
            "מספר תכנית": st.column_config.TextColumn(
                "מספר תכנית",
                help="מזהה תכנית, כאשר הוא מופיע במקור.",
            ),
        },
    )

    st.markdown("### פתחו רשומה")
    selected_index = st.selectbox(
        "בחרו מתחם או תכנית",
        filtered.index.tolist(),
        format_func=lambda index: selection_label(filtered.loc[index]),
        help="הבחירה פותחת סיכום וקישורים למקורות הציבוריים.",
    )
    render_record_detail(filtered.loc[selected_index])

with st.expander("מה המילים האלה אומרות בכלל?"):
    glossary = {
        "מתחם מוכרז": (
            "מתחם שמופיע ברשומה רשמית כהכרזה או כמתחם התחדשות. ההכרזה "
            "לבדה אינה מספרת מה קורה בכל בניין."
        ),
        "תכנית": (
            "מסמך תכנוני שמגדיר הוראות לאזור. לתכניות יש שלבים, מסמכים "
            "והחלטות שמתעדכנים לאורך זמן."
        ),
        "תכנית מופקדת": (
            "תכנית שפורסמה בשלב שבו הציבור יכול לעיין בה ובהליכים הנלווים."
        ),
        "תכנית מאושרת": (
            "תכנית שקיבלה אישור תכנוני לפי המקור. ייתכן שעדיין נדרשים "
            "תנאים, מסמכים והיתרים."
        ),
        "היתר": "אישור לביצוע עבודות מסוימות. בקשה להיתר אינה היתר שניתן.",
        "יחידות קיימות": "מספר יחידות הדיור שדווחו במצב הקיים.",
        "יחידות מוצעות": "מספר יחידות הדיור שנכתב בהצעה או בתכנית.",
        "מקור ציבורי": "מאגר או אתר של גוף ציבורי שניתן לפתוח ללא התחברות.",
        "למה יש מידע חסר?": (
            "מאגרים ציבוריים נבנו למטרות שונות, מתעדכנים בקצב שונה ולא "
            "תמיד משתמשים באותם שמות ושדות."
        ),
    }
    for term, explanation in glossary.items():
        st.markdown(f"**{term}** — {explanation}")

st.caption(
    "האתר מציג מידע ציבורי בלבד. אם משהו חשוב לכם, פתחו את המקור הרשמי "
    "ובדקו את המסמכים והתאריך שמופיעים בו."
)
