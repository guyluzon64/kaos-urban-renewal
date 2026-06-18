from __future__ import annotations

from typing import Any

import pandas as pd


PUBLIC_STAGE_TOTAL = 9
PUBLIC_DISCLAIMER_HE = (
    "השלב הציבורי המזוהה מתאר רק את מה שנמצא ברשומות ציבוריות. "
    "הוא אינו תחזית, אינו קביעה משפטית או תכנונית ואינו תחליף לבדיקה "
    "במקור הרשמי."
)

STAGES: dict[int, dict[str, str]] = {
    0: {
        "name": "לא נמצא שלב ברור",
        "explanation": "מצאנו מידע חלקי או לא מספיק כדי לזהות שלב ברור.",
    },
    1: {
        "name": "אזור או מדיניות בלבד",
        "explanation": (
            "קיים מידע כללי על אזור או מדיניות, אבל לא בהכרח פרויקט קונקרטי."
        ),
    },
    2: {
        "name": "מתחם מוכרז או רשומה רשמית ראשונית",
        "explanation": (
            "נמצאה רשומה ציבורית על מתחם, אך אין בכך מידע על מועד ביצוע."
        ),
    },
    3: {
        "name": "קיימת תכנית או מספר תכנית",
        "explanation": (
            "קיים מספר תכנית או סימן לתהליך תכנוני. מומלץ לפתוח את המקור "
            "הרשמי ולקרוא את הפרטים."
        ),
    },
    4: {
        "name": "תכנית בתהליך",
        "explanation": (
            "לפי המידע הציבורי, נראה שקיים תהליך תכנוני פעיל."
        ),
    },
    5: {
        "name": "תכנית הופקדה",
        "explanation": (
            "תכנית שהופקדה נמצאת בשלב תכנוני מתקדם יותר, אך עדיין אינה "
            "בהכרח מאושרת."
        ),
    },
    6: {
        "name": "תכנית אושרה",
        "explanation": (
            "נמצא חיווי ציבורי לכך שהתכנית אושרה. עדיין יש לבדוק תנאים, "
            "מסמכים והיתרים."
        ),
    },
    7: {
        "name": "בקשה להיתר",
        "explanation": (
            "נמצא חיווי ציבורי הקשור לבקשה להיתר. אין בכך אישור שהיתר כבר ניתן."
        ),
    },
    8: {
        "name": "היתר או ביצוע",
        "explanation": (
            "נמצא חיווי ציבורי מתקדם הקשור להיתר או לביצוע."
        ),
    },
    9: {
        "name": "הושלם",
        "explanation": "נמצא חיווי ציבורי שהפרויקט הושלם.",
    },
}


STATUS_STAGE = {
    "POLICY_AREA_ONLY": 1,
    "DECLARED_COMPLEX": 2,
    "PLAN_IN_PROGRESS": 4,
    "PLAN_DEPOSITED": 5,
    "PLAN_APPROVED": 6,
    "PERMIT_REQUESTED": 7,
    "PERMIT_APPROVED": 8,
    "CONSTRUCTION": 8,
    "COMPLETED": 9,
}


def has_value(value: Any) -> bool:
    return not pd.isna(value) and str(value).strip().lower() not in {
        "",
        "nan",
        "none",
        "null",
        "<na>",
    }


def stage_for_row(row: pd.Series) -> tuple[int, str]:
    status = str(row.get("planning_status_normalized") or "UNKNOWN")
    if status in STATUS_STAGE:
        return STATUS_STAGE[status], f"planning_status_normalized={status}"
    if has_value(row.get("plan_number")):
        return 3, "has_plan_number"
    if row.get("declared_complex") is True:
        return 2, "declared_complex"
    return 0, "insufficient_public_information"


def public_confidence(row: pd.Series) -> str:
    level = str(row.get("confidence_level") or "").upper()
    if level in {"HIGH", "MEDIUM", "LOW"}:
        return level
    score = pd.to_numeric(row.get("data_confidence_score"), errors="coerce")
    if pd.isna(score):
        return "LOW"
    if score >= 80:
        return "HIGH"
    if score >= 50:
        return "MEDIUM"
    return "LOW"


def friendly_summary(row: pd.Series, stage: int) -> str:
    city = row.get("city")
    complex_name = row.get("complex_name")
    place_parts = [
        str(value)
        for value in (complex_name, city)
        if has_value(value)
    ]
    place = " ב" + ", ".join(place_parts) if place_parts else ""
    return (
        f"לפי המידע הציבורי שמצאנו{place}, השלב המזוהה הוא "
        f"{stage} מתוך {PUBLIC_STAGE_TOTAL}: {STAGES[stage]['name']}."
    )


def add_public_stage_fields(standardized: pd.DataFrame) -> pd.DataFrame:
    public = standardized.copy()
    stage_pairs = public.apply(stage_for_row, axis=1)
    public["public_stage_index"] = [pair[0] for pair in stage_pairs]
    public["public_stage_total"] = PUBLIC_STAGE_TOTAL
    public["public_stage_name_he"] = public["public_stage_index"].map(
        lambda stage: STAGES[int(stage)]["name"]
    )
    public["public_stage_short_explanation_he"] = public[
        "public_stage_index"
    ].map(lambda stage: STAGES[int(stage)]["explanation"])
    public["public_stage_basis"] = [pair[1] for pair in stage_pairs]
    public["public_stage_confidence"] = public.apply(
        public_confidence, axis=1
    )
    public["public_friendly_summary_he"] = public.apply(
        lambda row: friendly_summary(row, int(row["public_stage_index"])),
        axis=1,
    )
    public["public_stage_disclaimer"] = PUBLIC_DISCLAIMER_HE
    public["public_disclaimer_he"] = PUBLIC_DISCLAIMER_HE
    return public
