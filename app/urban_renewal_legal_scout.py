from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


GITHUB_URL = "https://github.com/guyluzon64/kaos-urban-renewal"

TEXT = {
    "he": {
        "site_name": "כאוס עירוני",
        "subtitle": "עושים סדר בהתחדשות עירונית בעזרת מידע ציבורי בלבד.",
        "secondary_phrase": "בניין, מה נסגר?",
        "microcopy": "בקיצור: זה מצפן, לא פסק דין.",
        "hero_kicker": "מיזם ציבורי ללא מטרות רווח · {phrase}",
        "important": "חשוב לדעת:",
        "top_disclaimer": (
            "המידע באתר מוצג כפי שנמצא במקורות ציבוריים ורשמיים, ועלול להיות "
            "חלקי, לא מעודכן או שגוי. האתר אינו נותן ייעוץ משפטי, תכנוני, "
            "שמאי או נדל״ני, ואינו מחליף בדיקה מול עורך דין, העירייה, מינהל "
            "התכנון או הגורם הרשמי הרלוונטי."
        ),
        "stage_disclaimer": (
            "השלב הציבורי המזוהה מתאר רק את מה שנמצא ברשומות ציבוריות. הוא "
            "אינו תחזית, אינו קביעה משפטית או תכנונית, ואינו מחליף בדיקה "
            "במקור הרשמי."
        ),
        "non_profit_short": "מידע ציבורי, מוסבר בפשטות.",
        "non_profit_credit": "ללא מטרות רווח · גיא לוזון",
        "records": "רשומות",
        "sources": "מקורות",
        "legend_title": "איך קוראים את זה?",
        "legend_subtitle": (
            "האתר מציג שלב ציבורי מזוהה — כלומר מה אפשר להבין מהרשומות "
            "הציבוריות, לא הבטחה לגבי מה שיקרה."
        ),
        "source_caution": (
            "מקור ציבורי אינו מבטיח שהמידע מלא, עדכני או סופי מבחינה משפטית."
        ),
        "chip_declared": "מתחם מוכרז",
        "chip_plan": "תכנית",
        "chip_deposit": "הפקדה",
        "chip_permit": "היתר",
        "chip_source": "מקור ציבורי",
        "steps_title": "שלושה צעדים, בלי תואר בתכנון ערים",
        "step_1": "חפשו עיר, רחוב, מתחם או מספר תכנית.",
        "step_2": "בדקו את השלב הציבורי המזוהה.",
        "step_3": "פתחו את המקור הרשמי ובדקו את הפרטים.",
        "freshness_title": "מתי המידע נטען לאחרונה?",
        "site_last_refreshed": "האתר רוענן לאחרונה",
        "source_latest_update": "העדכון האחרון שמופיע במקורות הציבוריים",
        "freshness_caution": (
            "גם אם האתר רוענן היום, ייתכן שהמקור הציבורי עצמו כולל מידע ישן יותר."
        ),
        "refresh_details": "פרטי רענון למי שרוצה לבדוק",
        "refresh_report": (
            "נרשמו {attempts:,} ניסיונות מקור; {failed:,} מהם הסתיימו "
            "בשגיאה או במצב הפניה בלבד."
        ),
        "refresh_unavailable": "דוח הרענון המפורט אינו זמין כרגע.",
        "search_label": "חפשו עיר, רחוב, שם מתחם או מספר תכנית",
        "search_placeholder": (
            "לדוגמה: חולון, ארלוזורוב, מתחם ההסתדרות, 507-..."
        ),
        "search_help": (
            "החיפוש עובר על פרטי המקום, שם המתחם, מספר התכנית והטקסט "
            "שהתקבל מהמקור הציבורי."
        ),
        "filters": "סינון",
        "filters_caption": "אפשר להשאיר מסנן ריק כדי לראות את כל הרשומות.",
        "city": "עיר",
        "stage": "שלב ציבורי מזוהה",
        "renewal_type": "סוג התחדשות",
        "source": "מקור",
        "data_completeness": "שלמות המידע",
        "city_help": "שם היישוב כפי שנמצא במקור הציבורי, לאחר ניקוי בסיסי.",
        "stage_help": (
            "תיאור של השלב שניתן לזהות ברשומות ציבוריות, לא תחזית."
        ),
        "renewal_help": "המסלול או סוג ההתחדשות כפי שנכתב במקור.",
        "source_help": "הגוף או מאגר המידע הציבורי שממנו התקבלה הרשומה.",
        "completeness_help": (
            "כמה שדות תיעוד בסיסיים נמצאו ברשומה. זה אינו מדד לתכנית עצמה."
        ),
        "stage_format": "{stage} מתוך 9",
        "records_found": "רשומות שנמצאו",
        "cities": "ערים",
        "public_sources": "מקורות ציבוריים",
        "with_plan": "עם מספר תכנית",
        "empty_title": "לא מצאנו התאמה במידע הציבורי שנטען כרגע.",
        "empty_body": (
            "זה לא אומר שאין פרויקט — רק שלא מצאנו רשומה מתאימה במקורות "
            "שהאתר בדק."
        ),
        "empty_suggestion": (
            "נסו לחפש שם עיר בלבד, שם רחוב בלי מספר בית, או מספר תכנית "
            "אם יש לכם."
        ),
        "results_title": "מה נמצא במידע הציבורי",
        "open_record": "פתחו רשומה",
        "choose_record": "בחרו מתחם או תכנית",
        "choose_record_help": (
            "הבחירה פותחת סיכום וקישורים למקורות הציבוריים."
        ),
        "unnamed_record": "רשומה ללא שם",
        "not_available": "לא זמין",
        "identified_stage": "שלב ציבורי מזוהה: {stage} מתוך {total}",
        "plan_number": "מספר תכנית",
        "open_source": "פתח מקור רשמי",
        "check_mavat": "בדוק במבא״ת",
        "open_map": "פתח מפה",
        "no_public_link": "לא נמצא קישור ציבורי תקין לרשומה הזאת.",
        "technical_details": "מידע טכני למי שאוהב טבלאות",
        "raw_status": "סטטוס כפי שנכתב במקור",
        "normalized_status": "סטטוס מנורמל",
        "stage_basis": "בסיס לזיהוי השלב",
        "source_type": "סוג מקור",
        "source_update": "מועד עדכון במקור",
        "refresh_status": "מצב רענון המקור",
        "data_quality": "הערת איכות נתונים",
        "internal_fields_note": (
            "שדות טכניים ישנים מוצגים כאן רק לשקיפות. הם אינם תחזית, "
            "אינם דירוג ציבורי ואינם חלק מהשלב הציבורי המזוהה."
        ),
        "glossary_title": "מילון קצר: מה המילים האלה אומרות בכלל?",
        "why_title": "למה האתר הזה קיים?",
        "why_body": (
            "כי בהתחדשות עירונית יש הרבה רעש: שמועות, קבוצות וואטסאפ, "
            "מסמכים, יזמים, עירייה, תכניות ומילים שאף אחד לא באמת הסביר. "
            "האתר מנסה לעשות דבר אחד פשוט: להראות בצורה ברורה מה נמצא "
            "במקורות ציבוריים — ומה לא."
        ),
        "non_profit": (
            "האתר הוא מיזם ללא מטרות רווח ומתבסס על מידע ציבורי בלבד."
        ),
        "credit": "נבנה ופותח על ידי גיא לוזון",
        "credit_description": (
            "פרויקט עצמאי ללא מטרות רווח, שנועד להנגיש מידע ציבורי על "
            "התחדשות עירונית לציבור הרחב."
        ),
        "credit_role": "פיתוח, דאטה ועיצוב מוצר",
        "footer_caution": (
            "אם פרט מסוים חשוב לכם, מומלץ לפתוח את המקור הרשמי ולבדוק את "
            "המסמכים והתאריך שמופיעים בו."
        ),
        "missing_data_file": (
            "עדיין אין קובץ נתונים ציבורי להצגה. הריצו משורש הפרויקט: "
            "`python scripts/update_public_data.py`"
        ),
        "table_city": "עיר",
        "table_street": "רחוב / אזור",
        "table_complex": "שם מתחם",
        "table_plan": "מספר תכנית",
        "table_renewal": "סוג התחדשות",
        "table_stage": "שלב ציבורי מזוהה",
        "table_standing": "איפה זה עומד?",
        "table_completeness": "שלמות המידע",
        "table_source": "מקור",
        "table_updated": "עודכן לאחרונה",
        "table_stage_help": "מיקום תיאורי לפי הרשומה הציבורית בלבד.",
        "table_completeness_help": "כמה פרטי תיעוד בסיסיים נמצאו ברשומה.",
        "table_plan_help": "מזהה תכנית, כאשר הוא מופיע במקור.",
        "confidence_high": "תיעוד ציבורי מלא יחסית",
        "confidence_medium": "תיעוד ציבורי חלקי",
        "confidence_low": "תיעוד ציבורי מצומצם",
    },
    "en": {
        "site_name": "Urban Chaos",
        "subtitle": "Making sense of urban renewal using public information only.",
        "secondary_phrase": "What is happening with the building?",
        "microcopy": "In short: it’s a compass, not a verdict.",
        "hero_kicker": "Non-profit public-interest project · {phrase}",
        "important": "Important:",
        "top_disclaimer": (
            "The information shown on this site is based on public and official "
            "sources as found, and may be incomplete, outdated, or incorrect. "
            "This site does not provide legal, planning, appraisal, or real-estate "
            "advice, and does not replace verification with a lawyer, municipality, "
            "planning authority, or the relevant official source."
        ),
        "stage_disclaimer": (
            "The identified public stage only describes what was found in public "
            "records. It is not a forecast, not a legal or planning determination, "
            "and does not replace checking the official source."
        ),
        "non_profit_short": "Public information, explained simply.",
        "non_profit_credit": "Non-profit · Guy Luzon",
        "records": "Records",
        "sources": "Sources",
        "legend_title": "How should I read this?",
        "legend_subtitle": (
            "The site shows an identified public stage: what can be understood "
            "from public records, not a promise about what will happen."
        ),
        "source_caution": (
            "A public source does not mean the information is complete, current, "
            "or legally final."
        ),
        "chip_declared": "Declared area",
        "chip_plan": "Plan",
        "chip_deposit": "Deposit",
        "chip_permit": "Permit",
        "chip_source": "Public source",
        "steps_title": "Three steps, no planning degree required",
        "step_1": "Search by city, street, complex, or plan number.",
        "step_2": "Review the identified public stage.",
        "step_3": "Open the official source and check the details.",
        "freshness_title": "When was the information loaded?",
        "site_last_refreshed": "Site last refreshed",
        "source_latest_update": "Latest update reported by public sources",
        "freshness_caution": (
            "Even if the site was refreshed today, the public source itself may "
            "contain older information."
        ),
        "refresh_details": "Refresh details",
        "refresh_report": (
            "{attempts:,} source attempts were recorded; {failed:,} ended with "
            "an error or reference-only status."
        ),
        "refresh_unavailable": "The detailed refresh report is not available.",
        "search_label": "Search by city, street, complex name, or plan number",
        "search_placeholder": (
            "For example: Holon, Arlozorov, renewal complex, 507-..."
        ),
        "search_help": (
            "Search covers location details, complex names, plan numbers, and "
            "text received from the public source."
        ),
        "filters": "Filters",
        "filters_caption": "Leave a filter empty to include all records.",
        "city": "City",
        "stage": "Identified public stage",
        "renewal_type": "Renewal type",
        "source": "Source",
        "data_completeness": "Data completeness",
        "city_help": "The locality name as shown in the public source.",
        "stage_help": (
            "A description of the stage identified in public records, not a forecast."
        ),
        "renewal_help": "The renewal route or type as written in the source.",
        "source_help": "The public body or dataset that supplied the record.",
        "completeness_help": (
            "How many basic documentation fields were found. This does not rate "
            "the plan itself."
        ),
        "stage_format": "{stage} of 9",
        "records_found": "Records found",
        "cities": "Cities",
        "public_sources": "Public sources",
        "with_plan": "With a plan number",
        "empty_title": (
            "No matching record was found in the public information currently loaded."
        ),
        "empty_body": (
            "This does not mean there is no project — only that no matching public "
            "record was found in the sources checked by the site."
        ),
        "empty_suggestion": (
            "Try a city name only, a street without a building number, or a plan "
            "number if you have one."
        ),
        "results_title": "What was found in public information",
        "open_record": "Open a record",
        "choose_record": "Choose a complex or plan",
        "choose_record_help": (
            "The selection opens a summary and links to public sources."
        ),
        "unnamed_record": "Unnamed record",
        "not_available": "Not available",
        "identified_stage": "Identified public stage: {stage} of {total}",
        "plan_number": "Plan number",
        "open_source": "Open official source",
        "check_mavat": "Check in Mavat",
        "open_map": "Open map",
        "no_public_link": "No valid public link was found for this record.",
        "technical_details": "Technical details for table lovers",
        "raw_status": "Status as written in the source",
        "normalized_status": "Normalized status",
        "stage_basis": "Basis for the identified stage",
        "source_type": "Source type",
        "source_update": "Source update date",
        "refresh_status": "Source refresh status",
        "data_quality": "Data-quality note",
        "internal_fields_note": (
            "Legacy technical fields are shown only for transparency. They are "
            "not forecasts, public ratings, or part of the identified public stage."
        ),
        "glossary_title": "Short glossary: what do these terms mean?",
        "why_title": "Why does this site exist?",
        "why_body": (
            "Urban renewal comes with a lot of noise: rumors, WhatsApp groups, "
            "documents, developers, municipalities, plans, and terms that are "
            "rarely explained. This site tries to do one simple thing: show clearly "
            "what appears in public sources — and what does not."
        ),
        "non_profit": (
            "This is a non-profit public-interest project based only on public information."
        ),
        "credit": "Built and developed by Guy Luzon",
        "credit_description": (
            "An independent non-profit project created to make public urban-renewal "
            "information easier to understand."
        ),
        "credit_role": "Development, data, and product design",
        "footer_caution": (
            "If a detail matters to you, check the official source, its documents, "
            "and the date shown there."
        ),
        "missing_data_file": (
            "The public data file is not available. Run from the project root: "
            "`python scripts/update_public_data.py`"
        ),
        "table_city": "City",
        "table_street": "Street / Area",
        "table_complex": "Complex name",
        "table_plan": "Plan number",
        "table_renewal": "Renewal type",
        "table_stage": "Identified public stage",
        "table_standing": "Where it stands",
        "table_completeness": "Data completeness",
        "table_source": "Source",
        "table_updated": "Last updated",
        "table_stage_help": "A descriptive position based on the public record only.",
        "table_completeness_help": "How many basic documentation details were found.",
        "table_plan_help": "A plan identifier, when shown in the source.",
        "confidence_high": "Relatively complete public documentation",
        "confidence_medium": "Partial public documentation",
        "confidence_low": "Limited public documentation",
    },
}

STAGE_GUIDE = {
    0: {
        "he": ("לא נמצא שלב ברור", "המידע חלקי או לא מספיק לזיהוי שלב."),
        "en": ("No clear stage found", "The information is insufficient to identify a clear stage."),
    },
    1: {
        "he": ("אזור או מדיניות בלבד", "נמצא מידע כללי על אזור, לא בהכרח על פרויקט מסוים."),
        "en": ("Area or policy only", "General area or policy information was found, not necessarily a specific project."),
    },
    2: {
        "he": ("מתחם מוכרז", "נמצאה רשומה רשמית ראשונית על מתחם."),
        "en": ("Declared renewal area", "An initial official record for a renewal area was found."),
    },
    3: {
        "he": ("קיימת תכנית או מספר תכנית", "נמצא מספר תכנית או חיווי לתהליך תכנוני."),
        "en": ("Plan or plan number exists", "A plan number or public indication of a planning process was found."),
    },
    4: {
        "he": ("תכנית בתהליך", "נמצא חיווי ציבורי לתהליך תכנוני פעיל."),
        "en": ("Plan in process", "A public indication of an active planning process was found."),
    },
    5: {
        "he": ("תכנית הופקדה", "התכנית פורסמה להפקדה, אך אינה בהכרח מאושרת."),
        "en": ("Plan deposited", "The plan was published for deposit, but is not necessarily approved."),
    },
    6: {
        "he": ("תכנית אושרה", "נמצא חיווי ציבורי לאישור; עדיין יש לבדוק תנאים והיתרים."),
        "en": ("Plan approved", "A public indication of approval was found; conditions and permits still need checking."),
    },
    7: {
        "he": ("בקשה להיתר", "נמצא חיווי לבקשה; אין בכך אישור שהיתר ניתן."),
        "en": ("Permit request", "A permit-request indication was found; this does not mean a permit was granted."),
    },
    8: {
        "he": ("היתר או ביצוע", "נמצא חיווי ציבורי מתקדם הקשור להיתר או לביצוע."),
        "en": ("Permit or construction", "An advanced public indication related to a permit or construction was found."),
    },
    9: {
        "he": ("הושלם", "נמצא חיווי ציבורי לכך שהפרויקט הושלם."),
        "en": ("Completed", "A public indication that the project was completed was found."),
    },
}

GLOSSARY = {
    "he": {
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
    },
    "en": {
        "Declared renewal area": (
            "An area shown in an official declaration or renewal record. The "
            "declaration alone does not explain what is happening in every building."
        ),
        "Plan": (
            "A planning document that sets instructions for an area. Plans have "
            "stages, documents, and decisions that change over time."
        ),
        "Deposited plan": (
            "A plan published at a stage where the public can review it and the "
            "related proceedings."
        ),
        "Approved plan": (
            "A plan described as approved in the source. Conditions, documents, "
            "and permits may still need to be checked."
        ),
        "Permit": (
            "Authorization for specific work. A permit request is not a granted permit."
        ),
        "Existing units": "The number of housing units reported in the existing situation.",
        "Proposed units": "The number of housing units stated in a proposal or plan.",
        "Public source": "A public-body dataset or website accessible without a login.",
        "Why is information missing?": (
            "Public datasets serve different purposes, update at different rates, "
            "and do not always use the same names or fields."
        ),
    },
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "urban_renewal_public.csv"
)
REFRESH_REPORT_PATH = (
    PROJECT_ROOT / "data" / "metadata" / "latest_refresh_report.csv"
)


def file_mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


st.set_page_config(
    page_title="כאוס עירוני | Urban Chaos",
    page_icon="🏠",
    layout="wide",
    # Keep the familiar expanded desktop layout while Streamlit collapses the
    # sidebar on narrow screens. CSS below fully hides the zero-width mobile
    # sidebar shell that some iPhone in-app browsers otherwise still paint.
    initial_sidebar_state="auto",
)

language_choice = st.selectbox(
    "שפה / Language",
    ["עברית", "English"],
    index=0,
    key="site_language",
    label_visibility="collapsed",
)
lang = "he" if language_choice == "עברית" else "en"
direction = "rtl" if lang == "he" else "ltr"
text_align = "right" if lang == "he" else "left"


def t(key: str, **values: Any) -> str:
    """Return localized UI text, safely falling back to Hebrew or the key."""
    text = TEXT.get(lang, {}).get(key, TEXT["he"].get(key, key))
    if not values:
        return text
    try:
        return text.format(**values)
    except (KeyError, ValueError):
        return text


SITE_NAME = t("site_name")
SITE_SUBTITLE = t("subtitle")
SECONDARY_PHRASE = t("secondary_phrase")
MICROCOPY = t("microcopy")
TOP_DISCLAIMER = t("top_disclaimer")
DETAIL_DISCLAIMER = t("stage_disclaimer")

def inject_mobile_css(direction: str, text_align: str) -> None:
    """Apply responsive, direction-aware styling once near the app entry point."""
    css = """
    <style>
    :root {
        --kaos-accent: #1d8a70;
        --kaos-accent-dark: #12634f;
        --kaos-warm: #d97706;
        --kaos-border: rgba(127, 127, 127, .24);
        --kaos-muted: rgba(127, 127, 127, .13);
    }
    *, *::before, *::after {
        box-sizing: border-box;
    }
    html, body, [class*="css"], .stApp {
        direction: __DIRECTION__;
        text-align: __TEXT_ALIGN__;
        font-family: "Segoe UI", "Rubik", Arial, "Noto Sans Hebrew", sans-serif;
        line-height: 1.65;
        max-width: 100%;
        overflow-wrap: break-word;
        word-break: normal;
    }
    .stApp {
        overflow-x: hidden;
    }
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] * {
        direction: __DIRECTION__;
        text-align: __TEXT_ALIGN__;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        display: none !important;
        overflow: hidden !important;
    }
    .block-container {
        width: 100%;
        max-width: 1260px;
        padding-top: clamp(1rem, 3vw, 2rem);
        padding-inline: clamp(.8rem, 3vw, 2.5rem);
        padding-bottom: max(7rem, calc(env(safe-area-inset-bottom) + 5rem));
        overflow-x: hidden;
    }
    .st-key-site_language {
        width: min(100%, 11rem);
        max-width: 11rem;
        margin: 0 0 .75rem auto;
    }
    .st-key-site_language [data-testid="stSelectbox"] {
        width: 100%;
        min-width: 0;
    }
    .hero {
        width: 100%;
        max-width: 100%;
        min-width: 0;
        overflow: hidden;
        padding: clamp(1.1rem, 4vw, 2.7rem);
        border-radius: 28px;
        background:
            radial-gradient(circle at 8% 15%, rgba(217, 119, 6, .16), transparent 25%),
            linear-gradient(135deg, rgba(29, 138, 112, .16), rgba(29, 138, 112, .04));
        border: 1px solid var(--kaos-border);
        margin-bottom: 1.1rem;
        box-shadow: 0 18px 50px rgba(15, 23, 42, .07);
    }
    .hero, .hero * {
        max-width: 100%;
        min-width: 0;
        white-space: normal;
        overflow-wrap: break-word;
        word-break: normal;
    }
    .hero h1 {
        margin: 0 0 .3rem 0;
        font-size: clamp(2rem, 7vw, 4.8rem);
        line-height: 1.08;
        color: var(--text-color);
        letter-spacing: normal;
    }
    .hero p {
        margin: 0;
        width: 100%;
        max-width: 820px;
        font-size: clamp(.98rem, 2.2vw, 1.25rem);
        color: var(--text-color);
        opacity: .82;
        font-weight: 600;
    }
    .hero-kicker {
        display: inline-block;
        max-width: 100%;
        margin-bottom: .8rem;
        padding: .28rem .72rem;
        border-radius: 999px;
        background: rgba(29, 138, 112, .13);
        color: var(--text-color);
        font-size: .88rem;
        font-weight: 800;
        line-height: 1.45;
    }
    .microcopy {
        display: inline-block;
        max-width: 100%;
        margin-top: 1rem;
        padding: .42rem .8rem;
        border-radius: 10px;
        background: rgba(217, 119, 6, .12);
        font-weight: 800;
        color: var(--text-color);
        line-height: 1.45;
    }
    .disclaimer-box {
        width: 100%;
        max-width: 100%;
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
        width: 100%;
        max-width: 920px;
    }
    .legend-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: .72rem;
        margin: .85rem 0 1.15rem;
    }
    .legend-card {
        min-width: 0;
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
        width: 100%;
        max-width: 100%;
        min-width: 0;
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
        width: 100%;
        max-width: 100%;
        min-width: 0;
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
        width: 100%;
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
        width: 100%;
        max-width: 100%;
        min-width: 0;
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
        direction: __DIRECTION__;
        width: 100%;
        max-width: 100%;
        margin: .7rem 0 1rem;
        border-radius: 16px;
        overflow-x: auto;
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
        white-space: normal;
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
    @media (max-width: 768px) {
        .block-container {
            padding-top: max(3.75rem, calc(env(safe-area-inset-top) + 3.25rem));
            padding-inline: .75rem;
            padding-bottom: max(8rem, calc(env(safe-area-inset-bottom) + 6rem));
        }
        .st-key-site_language {
            width: 9.5rem;
            max-width: calc(100vw - 1.5rem);
            margin-bottom: .55rem;
        }
        .hero {
            padding: clamp(1rem, 4.5vw, 1.35rem);
            border-radius: 20px;
            margin-bottom: .8rem;
        }
        .hero h1 {
            font-size: clamp(1.9rem, 9vw, 2.85rem);
            line-height: 1.12;
        }
        .hero p {
            font-size: clamp(.96rem, 4vw, 1.12rem);
            line-height: 1.55;
        }
        .hero-kicker,
        .microcopy {
            border-radius: 10px;
            font-size: .82rem;
        }
        .section-intro {
            margin-top: 1.45rem;
        }
        .section-intro h2 {
            font-size: clamp(1.35rem, 6vw, 1.8rem);
            line-height: 1.2;
        }
        .legend-grid,
        .steps-grid {
            grid-template-columns: 1fr;
        }
        .credit-card {
            align-items: flex-start;
            flex-direction: column;
        }
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
            gap: .75rem;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 1 1 100% !important;
            width: 100% !important;
            min-width: 0 !important;
        }
        div[data-testid="stLinkButton"],
        div[data-testid="stLinkButton"] a,
        div[data-testid="stDownloadButton"],
        div[data-testid="stDownloadButton"] button {
            width: 100%;
        }
        div[data-testid="stMetric"] {
            width: 100%;
            min-width: 0;
        }
    }
    @media (max-width: 480px) {
        .block-container {
            padding-top: max(3.75rem, calc(env(safe-area-inset-top) + 3.25rem));
            padding-inline: .6rem;
            padding-bottom: max(9rem, calc(env(safe-area-inset-bottom) + 7rem));
        }
        .st-key-site_language {
            width: 8.75rem;
            max-width: calc(100vw - 1.2rem);
        }
        .hero {
            padding: .9rem;
            border-radius: 16px;
            box-shadow: 0 10px 28px rgba(15, 23, 42, .06);
        }
        .hero h1 {
            font-size: clamp(1.75rem, 10vw, 2.35rem);
        }
        .hero p {
            font-size: clamp(.94rem, 4.4vw, 1.05rem);
        }
        .hero-kicker,
        .microcopy {
            display: block;
            width: fit-content;
            max-width: 100%;
        }
        .disclaimer-box,
        .stage-card,
        .step-card,
        .info-card,
        .public-interest-card,
        .credit-card,
        .legend-card {
            padding: .85rem;
            border-radius: 14px;
        }
        .stage-number {
            font-size: clamp(1.25rem, 7vw, 1.75rem);
            line-height: 1.2;
        }
        .glossary-chip {
            max-width: 100%;
            white-space: normal;
        }
        .legend-grid { grid-template-columns: 1fr; }
    }
    </style>
    """
    st.markdown(
        css.replace("__DIRECTION__", direction).replace(
            "__TEXT_ALIGN__", text_align
        ),
        unsafe_allow_html=True,
    )


inject_mobile_css(direction, text_align)


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

CONFIDENCE_LABELS = {
    "HIGH": t("confidence_high"),
    "MEDIUM": t("confidence_medium"),
    "LOW": t("confidence_low"),
}

TABLE_LABELS = {
    "city": t("table_city"),
    "street_or_area": t("table_street"),
    "complex_name": t("table_complex"),
    "plan_number": t("table_plan"),
    "renewal_type": t("table_renewal"),
    "stage_display": t("table_stage"),
    "stage_name_display": t("table_standing"),
    "confidence_display": t("table_completeness"),
    "source_name": t("table_source"),
    "last_updated_display": t("table_updated"),
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


def safe_text(value: Any, fallback: str | None = None) -> str:
    if fallback is None:
        fallback = t("not_available")
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


def stage_copy(stage: int) -> tuple[str, str]:
    stage_entry = STAGE_GUIDE.get(stage, STAGE_GUIDE[0])
    return stage_entry.get(lang, stage_entry["he"])


def render_stage_guide() -> None:
    cards = "".join(
        (
            '<div class="legend-card">'
            f'<span class="legend-index">{stage}</span>'
            f"<strong>{escape(title)}</strong>"
            f"<small>{escape(explanation)}</small>"
            "</div>"
        )
        for stage in STAGE_GUIDE
        for title, explanation in [stage_copy(stage)]
    )
    st.markdown(
        f"""
        <div class="section-intro">
            <h2>{escape(t("legend_title"))}</h2>
            <p>{escape(t("legend_subtitle"))}</p>
        </div>
        """
        f'<div class="legend-grid">{cards}</div>'
        f"""
        <div class="glossary-row">
            <span class="glossary-chip">{escape(t("chip_declared"))}</span>
            <span class="glossary-chip">{escape(t("chip_plan"))}</span>
            <span class="glossary-chip">{escape(t("chip_deposit"))}</span>
            <span class="glossary-chip">{escape(t("chip_permit"))}</span>
            <span class="glossary-chip">{escape(t("chip_source"))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(t("source_caution"))


def render_usage_steps() -> None:
    st.markdown(
        f"""
        <div class="section-intro">
            <h2>{escape(t("steps_title"))}</h2>
        </div>
        <div class="steps-grid">
            <div class="step-card"><b>1</b> {escape(t("step_1"))}</div>
            <div class="step-card"><b>2</b> {escape(t("step_2"))}</div>
            <div class="step-card"><b>3</b> {escape(t("step_3"))}</div>
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
        result["public_stage_index"].map(
            lambda stage: t("stage_format", stage=int(stage))
        )
    )
    result["stage_name_display"] = result["public_stage_index"].map(
        lambda stage: stage_copy(int(stage))[0]
    )
    result["confidence_display"] = (
        result["public_stage_confidence"]
        .fillna("LOW")
        .astype(str)
        .str.upper()
        .map(CONFIDENCE_LABELS)
        .fillna(t("not_available"))
    )
    result["last_updated_display"] = result["last_updated"].map(readable_date)
    return result


@st.cache_data(show_spinner=False)
def load_public_data(language: str, data_mtime: float) -> pd.DataFrame:
    # Language and file modification time are intentionally part of the cache
    # key. Controlled display fields are localized, and refreshed CSV data must
    # be reloaded after an automated update.
    if not PUBLIC_DATA_PATH.exists():
        return pd.DataFrame(columns=DEFAULT_COLUMNS)
    return ensure_columns(
        pd.read_csv(PUBLIC_DATA_PATH, encoding="utf-8-sig", low_memory=False)
    )


@st.cache_data(show_spinner=False)
def load_refresh_report(report_mtime: float) -> pd.DataFrame:
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
    return text or safe_text(row.get("record_id"), t("unnamed_record"))


def render_source_buttons(row: pd.Series) -> None:
    buttons = [
        (t("open_source"), safe_url(row.get("source_url"))),
        (t("check_mavat"), safe_url(row.get("mavat_lookup_url"))),
        (
            t("open_map"),
            safe_url(row.get("govmap_lookup_url"))
            or safe_url(row.get("xplan_lookup_url")),
        ),
    ]
    available = [(label, url) for label, url in buttons if url]
    if not available:
        st.caption(t("no_public_link"))
        return
    columns = st.columns(len(available))
    for column, (label, url) in zip(columns, available):
        column.link_button(label, url, width="stretch")


def render_record_detail(row: pd.Series) -> None:
    stage = int(row.get("public_stage_index") or 0)
    total = int(row.get("public_stage_total") or 9)
    stage_name, stage_explanation = stage_copy(stage)
    progress_width = max(0, min(100, round((stage / total) * 100))) if total else 0
    st.markdown(
        f"""
        <div class="stage-card">
            <div class="stage-number">{escape(t("identified_stage", stage=stage, total=total))}</div>
            <h3>{escape(stage_name)}</h3>
            <p>{escape(stage_explanation)}</p>
            <div class="stage-track" aria-label="{escape(t("identified_stage", stage=stage, total=total))}">
                <div class="stage-fill" style="width: {progress_width}%"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    info_a, info_b, info_c = st.columns(3)
    info_a.metric(t("city"), safe_text(row.get("city")))
    info_b.metric(t("plan_number"), safe_text(row.get("plan_number")))
    info_c.metric(
        t("data_completeness"),
        CONFIDENCE_LABELS.get(
            safe_text(row.get("public_stage_confidence"), "LOW").upper(),
            t("not_available"),
        ),
    )

    st.markdown(f"**{t('source')}:** {escape(safe_text(row.get('source_name')))}")
    render_source_buttons(row)

    with st.expander(t("technical_details")):
        technical_fields = {
            t("raw_status"): row.get("planning_status_raw"),
            t("normalized_status"): row.get("planning_status_normalized"),
            t("stage_basis"): row.get("public_stage_basis"),
            t("source_type"): row.get("source_type"),
            t("source_update"): readable_date(row.get("last_updated")),
            t("refresh_status"): row.get("source_refresh_status"),
            t("data_quality"): row.get("data_quality_flag"),
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
            st.caption(t("internal_fields_note"))
            for column in internal_fields:
                st.write(f"`{column}`: {safe_text(row.get(column))}")

    st.warning(DETAIL_DISCLAIMER)


st.markdown(
    f"""
    <div class="hero">
        <div class="hero-kicker">{escape(t("hero_kicker", phrase=SECONDARY_PHRASE))}</div>
        <h1>{escape(SITE_NAME)}</h1>
        <p>{escape(SITE_SUBTITLE)}</p>
        <div class="microcopy">{escape(MICROCOPY)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    (
        '<div class="disclaimer-box">'
        f"<strong>{escape(t('important'))}</strong> {escape(TOP_DISCLAIMER)}"
        "</div>"
    ),
    unsafe_allow_html=True,
)

data = load_public_data(lang, file_mtime(PUBLIC_DATA_PATH))
refresh_report = load_refresh_report(file_mtime(REFRESH_REPORT_PATH))

if data.empty:
    st.error(t("missing_data_file"))
    st.stop()

st.sidebar.markdown(
    f"""
    <div class="sidebar-brand">
        <strong>{escape(SITE_NAME)}</strong>
        <small>{escape(t("non_profit_short"))}</small>
        <small>{escape(t("non_profit_credit"))}</small>
    </div>
    """,
    unsafe_allow_html=True,
)
sidebar_a, sidebar_b = st.sidebar.columns(2)
sidebar_a.metric(t("records"), f"{len(data):,}")
sidebar_b.metric(t("sources"), f"{data['source_name'].nunique(dropna=True):,}")

render_stage_guide()
render_usage_steps()

pipeline_dates = data["pipeline_last_run"].dropna().astype(str)
source_dates = data["last_updated"].dropna().astype(str)
latest_pipeline = (
    readable_date(pipeline_dates.max())
    if not pipeline_dates.empty
    else t("not_available")
)
latest_source = (
    readable_date(source_dates.max())
    if not source_dates.empty
    else t("not_available")
)
st.markdown(
    f"""
    <div class="section-intro">
        <h2>{escape(t("freshness_title"))}</h2>
    </div>
    <div class="info-card">
        <strong>{escape(t("site_last_refreshed"))}:</strong> {escape(latest_pipeline)}
        &nbsp;·&nbsp;
        <strong>{escape(t("source_latest_update"))}:</strong> {escape(latest_source)}
        <br>
        <small>{escape(t("freshness_caution"))}</small>
    </div>
    """,
    unsafe_allow_html=True,
)
with st.expander(t("refresh_details")):
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
        st.write(t("refresh_report", attempts=len(source_rows), failed=int(failed)))
    else:
        st.write(t("refresh_unavailable"))

search_text = st.text_input(
    t("search_label"),
    placeholder=t("search_placeholder"),
    help=t("search_help"),
)

st.sidebar.markdown(f"## {t('filters')}")
st.sidebar.caption(t("filters_caption"))
selected_cities = st.sidebar.multiselect(
    t("city"),
    options(data, "city"),
    help=t("city_help"),
)
selected_stages = st.sidebar.multiselect(
    t("stage"),
    sorted(data["public_stage_index"].dropna().astype(int).unique().tolist()),
    format_func=lambda value: t("stage_format", stage=value),
    help=t("stage_help"),
)
selected_types = st.sidebar.multiselect(
    t("renewal_type"),
    options(data, "renewal_type"),
    help=t("renewal_help"),
)
selected_sources = st.sidebar.multiselect(
    t("source"),
    options(data, "source_name"),
    help=t("source_help"),
)
selected_confidence = st.sidebar.multiselect(
    t("data_completeness"),
    options(data, "confidence_display"),
    help=t("completeness_help"),
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
metric_a.metric(t("records_found"), f"{len(filtered):,}")
metric_b.metric(t("cities"), f"{filtered['city'].nunique(dropna=True):,}")
metric_c.metric(
    t("public_sources"),
    f"{filtered['source_name'].nunique(dropna=True):,}",
)
metric_d.metric(
    t("with_plan"),
    f"{sum(1 for value in filtered['plan_number'] if has_value(value)):,}",
)

if filtered.empty:
    st.markdown(
        f"""
        <div class="info-card">
            <strong>{escape(t("empty_title"))}</strong><br>
            {escape(t("empty_body"))}
            <br><br>
            <small>{escape(t("empty_suggestion"))}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(f"### {t('results_title')}")
    public_columns = [
        "city",
        "street_or_area",
        "complex_name",
        "plan_number",
        "renewal_type",
        "stage_display",
        "stage_name_display",
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
        column_config={
            t("table_stage"): st.column_config.TextColumn(
                t("table_stage"),
                help=t("table_stage_help"),
            ),
            t("table_completeness"): st.column_config.TextColumn(
                t("table_completeness"),
                help=t("table_completeness_help"),
            ),
            t("table_plan"): st.column_config.TextColumn(
                t("table_plan"),
                help=t("table_plan_help"),
            ),
        },
    )

    st.markdown(f"### {t('open_record')}")
    selected_index = st.selectbox(
        t("choose_record"),
        filtered.index.tolist(),
        format_func=lambda index: selection_label(filtered.loc[index]),
        help=t("choose_record_help"),
    )
    render_record_detail(filtered.loc[selected_index])

with st.expander(t("glossary_title")):
    for term, explanation in GLOSSARY.get(lang, GLOSSARY["he"]).items():
        st.markdown(f"**{term}** — {explanation}")

st.markdown(
    f"""
    <div class="section-intro">
        <h2>{escape(t("why_title"))}</h2>
    </div>
    <div class="public-interest-card">
        {escape(t("why_body"))}
        <br><br>
        <strong>{escape(t("non_profit"))}</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="credit-card">
        <div>
            <strong>{escape(t("credit"))}</strong>
            <span>{escape(t("credit_description"))}</span>
        </div>
        <span>{escape(t("credit_role"))}</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.link_button("GitHub", GITHUB_URL)
st.caption(t("footer_caution"))
