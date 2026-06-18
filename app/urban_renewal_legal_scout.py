from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


SITE_NAME = "כאוס עירוני"
SITE_SUBTITLE = "עושים סדר בהתחדשות עירונית בעזרת מידע ציבורי בלבד."
SECONDARY_PHRASE = "בניין, מה נסגר?"
GITHUB_URL = "https://github.com/guyluzon64/kaos-urban-renewal"

TOP_DISCLAIMER = (
    "המידע באתר מוצג כפי שנמצא במקורות ציבוריים ורשמיים, ועלול להיות חלקי, "
    "לא מעודכן או שגוי. האתר אינו נותן ייעוץ משפטי, תכנוני, שמאי או נדל״ני, "
    "ואינו מחליף בדיקה מול עורך דין, העירייה, מינהל התכנון או הגורם הרשמי "
    "הרלוונטי."
)
MICROCOPY = "בקיצור: זה מצפן, לא פסק דין."
DETAIL_DISCLAIMER = (
    "השלב הציבורי המזוהה מתאר רק את מה שנמצא ברשומות ציבוריות. הוא אינו "
    "תחזית, אינו קביעה משפטית או תכנונית, ואינו מחליף בדיקה במקור הרשמי."
)

STAGE_GUIDE = {
    0: (
        "לא נמצא שלב ברור",
        "המידע חלקי או לא מספיק לזיהוי שלב.",
    ),
    1: (
        "אזור או מדיניות בלבד",
        "נמצא מידע כללי על אזור, לא בהכרח על פרויקט מסוים.",
    ),
    2: (
        "מתחם מוכרז",
        "נמצאה רשומה רשמית ראשונית על מתחם.",
    ),
    3: (
        "קיימת תכנית או מספר תכנית",
        "נמצא מספר תכנית או חיווי לתהליך תכנוני.",
    ),
    4: (
        "תכנית בתהליך",
        "נמצא חיווי ציבורי לתהליך תכנוני פעיל.",
    ),
    5: (
        "תכנית הופקדה",
        "התכנית פורסמה להפקדה, אך אינה בהכרח מאושרת.",
    ),
    6: (
        "תכנית אושרה",
        "נמצא חיווי לאישור; עדיין יש לבדוק תנאים והיתרים.",
    ),
    7: (
        "בקשה להיתר",
        "נמצא חיווי לבקשה; אין בכך אישור שהיתר ניתן.",
    ),
    8: (
        "היתר או ביצוע",
        "נמצא חיווי ציבורי מתקדם הקשור להיתר או לביצוע.",
    ),
    9: (
        "הושלם",
        "נמצא חיווי ציבורי לכך שהפרויקט הושלם.",
    ),
}

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
    :root {
        --kaos-accent: #1d8a70;
        --kaos-accent-dark: #12634f;
        --kaos-warm: #d97706;
        --kaos-border: rgba(127, 127, 127, .24);
        --kaos-muted: rgba(127, 127, 127, .13);
    }
    html, body, [class*="css"], .stApp {
        direction: rtl;
        text-align: right;
        font-family: "Segoe UI", "Rubik", Arial, "Noto Sans Hebrew", sans-serif;
        line-height: 1.65;
    }
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] * {
        direction: rtl;
        text-align: right;
    }
    .block-container {
        max-width: 1260px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        position: relative;
        overflow: hidden;
        padding: clamp(1.55rem, 4vw, 2.7rem);
        border-radius: 28px;
        background:
            radial-gradient(circle at 8% 15%, rgba(217, 119, 6, .16), transparent 25%),
            linear-gradient(135deg, rgba(29, 138, 112, .16), rgba(29, 138, 112, .04));
        border: 1px solid var(--kaos-border);
        margin-bottom: 1.1rem;
        box-shadow: 0 18px 50px rgba(15, 23, 42, .07);
    }
    .hero h1 {
        margin: 0 0 .3rem 0;
        font-size: clamp(2.45rem, 7vw, 4.8rem);
        line-height: 1;
        color: var(--text-color);
        letter-spacing: -.045em;
    }
    .hero p {
        margin: 0;
        max-width: 820px;
        font-size: clamp(1rem, 2.2vw, 1.25rem);
        color: var(--text-color);
        opacity: .82;
        font-weight: 600;
    }
    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        margin-bottom: .8rem;
        padding: .28rem .72rem;
        border-radius: 999px;
        background: rgba(29, 138, 112, .13);
        color: var(--text-color);
        font-size: .88rem;
        font-weight: 800;
    }
    .microcopy {
        display: inline-block;
        margin-top: 1rem;
        padding: .42rem .8rem;
        border-radius: 10px;
        background: rgba(217, 119, 6, .12);
        font-weight: 800;
        color: var(--text-color);
    }
    .disclaimer-box {
        padding: 1rem 1.15rem;
        border: 1px solid rgba(217, 119, 6, .32);
        border-inline-start: 5px solid var(--kaos-warm);
        border-radius: 16px;
        background: rgba(217, 119, 6, .08);
        color: var(--text-color);
        margin: .8rem 0 1.25rem;
    }
    .section-intro {
        margin: 2rem 0 .9rem;
    }
    .section-intro h2 {
        margin: 0 0 .25rem;
        font-size: clamp(1.55rem, 3vw, 2.1rem);
        color: var(--text-color);
    }
    .section-intro p {
        margin: 0;
        color: var(--text-color);
        opacity: .74;
        max-width: 920px;
    }
    .legend-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: .72rem;
        margin: .85rem 0 1.15rem;
    }
    .legend-card {
        min-height: 132px;
        padding: .85rem .9rem;
        border: 1px solid var(--kaos-border);
        border-radius: 16px;
        background: var(--secondary-background-color);
        color: var(--text-color);
    }
    .legend-index {
        display: inline-grid;
        place-items: center;
        width: 2.15rem;
        height: 2.15rem;
        margin-bottom: .55rem;
        border-radius: 10px;
        background: rgba(29, 138, 112, .16);
        color: var(--text-color);
        font-weight: 900;
    }
    .legend-card strong {
        display: block;
        line-height: 1.25;
        margin-bottom: .35rem;
    }
    .legend-card small {
        display: block;
        line-height: 1.45;
        opacity: .72;
    }
    .steps-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .8rem;
        margin: .8rem 0 1.25rem;
    }
    .step-card, .info-card, .public-interest-card {
        padding: 1rem 1.05rem;
        border: 1px solid var(--kaos-border);
        border-radius: 17px;
        background: var(--secondary-background-color);
        color: var(--text-color);
    }
    .step-card b {
        color: var(--kaos-accent);
        font-size: 1.25rem;
        margin-inline-end: .35rem;
    }
    .glossary-row {
        display: flex;
        flex-wrap: wrap;
        gap: .48rem;
        margin: .75rem 0 1rem;
    }
    .glossary-chip {
        padding: .35rem .7rem;
        border: 1px solid var(--kaos-border);
        border-radius: 999px;
        background: var(--secondary-background-color);
        color: var(--text-color);
        font-size: .9rem;
        font-weight: 700;
    }
    .stage-card {
        border: 1px solid rgba(29, 138, 112, .32);
        border-radius: 22px;
        padding: clamp(1.15rem, 3vw, 1.7rem);
        background:
            linear-gradient(135deg, rgba(29, 138, 112, .14), transparent 70%),
            var(--secondary-background-color);
        margin: .8rem 0;
        box-shadow: 0 12px 35px rgba(15, 23, 42, .06);
    }
    .stage-number {
        font-size: clamp(1.45rem, 4vw, 2.35rem);
        font-weight: 900;
        color: var(--text-color);
        letter-spacing: -.025em;
    }
    .stage-card h3 {
        margin: .45rem 0 .55rem;
        font-size: 1.4rem;
    }
    .stage-card p {
        margin: 0;
        max-width: 900px;
        font-size: 1.03rem;
        opacity: .84;
    }
    .stage-track {
        height: .65rem;
        margin-top: 1rem;
        border-radius: 999px;
        background: rgba(127, 127, 127, .18);
        overflow: hidden;
    }
    .stage-fill {
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, var(--kaos-accent), #46b89b);
    }
    .credit-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 1.15rem 1.25rem;
        margin-top: 1.2rem;
        border-radius: 18px;
        border: 1px solid var(--kaos-border);
        background: linear-gradient(135deg, rgba(29, 138, 112, .12), transparent);
        color: var(--text-color);
    }
    .credit-card strong {
        display: block;
        font-size: 1.05rem;
    }
    .credit-card span {
        opacity: .74;
    }
    .sidebar-brand {
        padding: .9rem 1rem;
        margin-bottom: 1rem;
        border-radius: 16px;
        border: 1px solid var(--kaos-border);
        background: var(--secondary-background-color);
    }
    .sidebar-brand strong {
        font-size: 1.25rem;
    }
    .sidebar-brand small {
        display: block;
        margin-top: .3rem;
        opacity: .7;
    }
    div[data-testid="stDataFrame"] {
        direction: rtl;
        margin: .7rem 0 1rem;
        border-radius: 16px;
        overflow: hidden;
    }
    div[data-testid="stMetric"] {
        border: 1px solid var(--kaos-border);
        border-radius: 16px;
        padding: .85rem;
        background: var(--secondary-background-color);
    }
    div[data-testid="stLinkButton"] a {
        border-radius: 12px;
        font-weight: 800;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 14px;
        min-height: 3.15rem;
    }
    div[data-testid="stExpander"] {
        border-radius: 14px;
        border-color: var(--kaos-border);
    }
    a { font-weight: 700; }
    @media (max-width: 980px) {
        .legend-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .steps-grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 620px) {
        .block-container { padding-top: 1rem; }
        .legend-grid { grid-template-columns: 1fr; }
        .legend-card { min-height: 0; }
        .credit-card { align-items: flex-start; flex-direction: column; }
    }
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
    "last_updated_display": "עודכן לאחרונה",
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


def readable_date(value: Any) -> str:
    if not has_value(value):
        return ""
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return safe_text(value, "")
    return parsed.strftime("%d.%m.%Y")


def render_stage_guide() -> None:
    cards = "".join(
        (
            '<div class="legend-card">'
            f'<span class="legend-index">{stage}</span>'
            f"<strong>{escape(title)}</strong>"
            f"<small>{escape(explanation)}</small>"
            "</div>"
        )
        for stage, (title, explanation) in STAGE_GUIDE.items()
    )
    st.markdown(
        """
        <div class="section-intro">
            <h2>איך קוראים את זה?</h2>
            <p>
                האתר מציג שלב ציבורי מזוהה — כלומר מה אפשר להבין מהרשומות
                הציבוריות, לא הבטחה לגבי מה שיקרה.
            </p>
        </div>
        """
        f'<div class="legend-grid">{cards}</div>'
        """
        <div class="glossary-row">
            <span class="glossary-chip">מתחם מוכרז</span>
            <span class="glossary-chip">תכנית</span>
            <span class="glossary-chip">הפקדה</span>
            <span class="glossary-chip">היתר</span>
            <span class="glossary-chip">מקור ציבורי</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "מקור ציבורי אינו מבטיח שהמידע מלא, עדכני או סופי מבחינה משפטית."
    )


def render_usage_steps() -> None:
    st.markdown(
        """
        <div class="section-intro">
            <h2>שלושה צעדים, בלי תואר בתכנון ערים</h2>
        </div>
        <div class="steps-grid">
            <div class="step-card"><b>1</b> חפשו עיר, רחוב, מתחם או מספר תכנית.</div>
            <div class="step-card"><b>2</b> בדקו את השלב הציבורי המזוהה.</div>
            <div class="step-card"><b>3</b> פתחו את המקור הרשמי ובדקו את הפרטים.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    result["last_updated_display"] = result["last_updated"].map(readable_date)
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
    stage_name = safe_text(
        row.get("public_stage_name_he"),
        STAGE_GUIDE.get(stage, STAGE_GUIDE[0])[0],
    )
    stage_explanation = safe_text(
        row.get("public_stage_short_explanation_he"),
        STAGE_GUIDE.get(stage, STAGE_GUIDE[0])[1],
    )
    progress_width = max(0, min(100, round((stage / total) * 100))) if total else 0
    st.markdown(
        f"""
        <div class="stage-card">
            <div class="stage-number">שלב ציבורי מזוהה: {stage} מתוך {total}</div>
            <h3>{escape(stage_name)}</h3>
            <p>{escape(stage_explanation)}</p>
            <div class="stage-track" aria-label="שלב {stage} מתוך {total}">
                <div class="stage-fill" style="width: {progress_width}%"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    st.markdown(f"**מקור:** {escape(safe_text(row.get('source_name')))}")
    render_source_buttons(row)

    with st.expander("מידע טכני למי שאוהב טבלאות"):
        technical_fields = {
            "סטטוס כפי שנכתב במקור": row.get("planning_status_raw"),
            "סטטוס מנורמל": row.get("planning_status_normalized"),
            "בסיס לזיהוי השלב": row.get("public_stage_basis"),
            "סוג מקור": row.get("source_type"),
            "מועד עדכון במקור": readable_date(row.get("last_updated")),
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
        <div class="hero-kicker">מיזם ציבורי ללא מטרות רווח · {SECONDARY_PHRASE}</div>
        <h1>{SITE_NAME}</h1>
        <p>{SITE_SUBTITLE}</p>
        <div class="microcopy">{MICROCOPY}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="disclaimer-box"><strong>חשוב לדעת:</strong> {TOP_DISCLAIMER}</div>',
    unsafe_allow_html=True,
)

data = load_public_data()
refresh_report = load_refresh_report()

if data.empty:
    st.error(
        "עדיין אין קובץ נתונים ציבורי להצגה. הריצו משורש הפרויקט: "
        "`python scripts/update_public_data.py`"
    )
    st.stop()

st.sidebar.markdown(
    f"""
    <div class="sidebar-brand">
        <strong>{SITE_NAME}</strong>
        <small>מידע ציבורי, מוסבר בפשטות.</small>
        <small>ללא מטרות רווח · גיא לוזון</small>
    </div>
    """,
    unsafe_allow_html=True,
)
sidebar_a, sidebar_b = st.sidebar.columns(2)
sidebar_a.metric("רשומות", f"{len(data):,}")
sidebar_b.metric("מקורות", f"{data['source_name'].nunique(dropna=True):,}")

render_stage_guide()
render_usage_steps()

pipeline_dates = data["pipeline_last_run"].dropna().astype(str)
source_dates = data["last_updated"].dropna().astype(str)
latest_pipeline = (
    readable_date(pipeline_dates.max()) if not pipeline_dates.empty else "לא ידוע"
)
latest_source = (
    readable_date(source_dates.max()) if not source_dates.empty else "לא ידוע"
)
st.markdown(
    f"""
    <div class="section-intro">
        <h2>מתי המידע נטען לאחרונה?</h2>
    </div>
    <div class="info-card">
        <strong>ריצת האתר האחרונה:</strong> {escape(latest_pipeline)}
        &nbsp;·&nbsp;
        <strong>עדכון אחרון שדווח במקור:</strong> {escape(latest_source)}
        <br>
        <small>
            גם אם האתר נטען היום, המקור עצמו עשוי להכיל מידע ישן יותר.
        </small>
    </div>
    """,
    unsafe_allow_html=True,
)
with st.expander("פרטי רענון למי שרוצה לבדוק"):
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
        st.write(
            f"נרשמו {len(source_rows):,} ניסיונות מקור; "
            f"{int(failed):,} מהם הסתיימו בשגיאה או במצב הפניה בלבד."
        )
    else:
        st.write("דוח הרענון המפורט אינו זמין כרגע.")

search_text = st.text_input(
    "חפשו עיר, רחוב, שם מתחם או מספר תכנית",
    placeholder="לדוגמה: חולון, ארלוזורוב, מתחם ההסתדרות, 507-...",
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
    f"{sum(1 for value in filtered['plan_number'] if has_value(value)):,}",
)

if filtered.empty:
    st.markdown(
        """
        <div class="info-card">
            <strong>לא מצאנו התאמה במידע הציבורי שנטען כרגע.</strong><br>
            זה לא אומר שאין פרויקט — רק שלא מצאנו רשומה מתאימה במקורות
            שהאתר בדק.
            <br><br>
            <small>
                נסו לחפש שם עיר בלבד, שם רחוב בלי מספר בית, או מספר תכנית
                אם יש לכם.
            </small>
        </div>
        """,
        unsafe_allow_html=True,
    )
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
        "last_updated_display",
    ]
    table = filtered[public_columns].copy()
    for column in table.columns:
        table[column] = table[column].map(
            lambda value: safe_text(value, "")
        )
    table = table.rename(columns=TABLE_LABELS)
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

with st.expander("מילון קצר: מה המילים האלה אומרות בכלל?"):
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

st.markdown(
    """
    <div class="section-intro">
        <h2>למה האתר הזה קיים?</h2>
    </div>
    <div class="public-interest-card">
        כי בהתחדשות עירונית יש הרבה רעש: שמועות, קבוצות וואטסאפ, מסמכים,
        יזמים, עירייה, תכניות ומילים שאף אחד לא באמת הסביר. האתר מנסה לעשות
        דבר אחד פשוט: להראות בצורה ברורה מה נמצא במקורות ציבוריים — ומה לא.
        <br><br>
        <strong>
            האתר הוא מיזם ללא מטרות רווח ומתבסס על מידע ציבורי בלבד.
        </strong>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="credit-card">
        <div>
            <strong>נבנה ופותח על ידי גיא לוזון</strong>
            <span>
                פרויקט עצמאי ללא מטרות רווח, שנועד להנגיש מידע ציבורי על
                התחדשות עירונית לציבור הרחב.
            </span>
        </div>
        <span>פיתוח, דאטה ועיצוב מוצר</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.link_button("GitHub", GITHUB_URL)
st.caption(
    "אם פרט מסוים חשוב לכם, מומלץ לפתוח את המקור הרשמי ולבדוק את המסמכים "
    "והתאריך שמופיעים בו."
)
