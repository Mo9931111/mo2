# KSA Car Makes & Models (GitHub-ready)

ينتج ملفات `ksa_makes_models.csv` و`ksa_makes_models.xlsx` باستخدام CarQuery API مع تصفية ماركات منتشرة في السعودية وإمكانية حصر السنوات.

## تشغيل محلي
```bash
pip install -r requirements.txt
python ksa_carquery_dump.py
```

## تحديث تلقائي عبر GitHub Actions
- الملف `.github/workflows/update-car-data.yml` يحدّث الملفات أسبوعيًا.
- فعّل قسم **Actions** في المستودع ثم نفّذ **Run workflow** يدويًا أول مرة.

## تخصيص
- عدّل مجموعة `KSA_MAKES` داخل `ksa_carquery_dump.py`.
- غيّر `MIN_YEAR` و`MAX_YEAR` حسب حاجتك.