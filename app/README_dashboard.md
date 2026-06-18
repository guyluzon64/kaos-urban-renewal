# בניין, מה נסגר?

יישום Streamlit ציבורי ופשוט לחיפוש מידע רשמי על התחדשות עירונית.

הקלט נוצר אוטומטית בנתיב:

`data/processed/urban_renewal_public.csv`

הרצה:

```powershell
pip install -r requirements.txt
python scripts/update_public_data.py
streamlit run app/urban_renewal_legal_scout.py
```

האתר אינו נותן ייעוץ או תחזית. הוא מציג את המידע כפי שנמצא במקורות
ציבוריים ומפנה בחזרה למקור.
