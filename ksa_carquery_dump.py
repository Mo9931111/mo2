# requirements: requests pandas tenacity openpyxl
import requests, time
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

BASE = "https://www.carqueryapi.com/api/0.3/"

KSA_MAKES = {
    "toyota","lexus","nissan","infiniti","hyundai","genesis","kia","honda","acura",
    "chevrolet","gmc","cadillac","buick","ford","lincoln","dodge","jeep","ram",
    "bmw","mercedes-benz","audi","volkswagen","porsche","mini","skoda","seat",
    "mitsubishi","mazda","suzuki","subaru",
    "byd","geely","changan","haval","great wall","gwm","gac","mg","jac","jetour","chery",
    "exeed","omoda","jaecoo","hongqi","baic","faw","peugeot","renault","citroen","opel","fiat"
}
MIN_YEAR = 2005
MAX_YEAR = None  # ضع قيمة رقمية إن رغبت بحصر أعلى سنة

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
def cq(cmd, **params):
    p = {"cmd": cmd}; p.update(params)
    r = requests.get(BASE, params=p, timeout=30)
    r.raise_for_status()
    txt = r.text.strip()
    if txt.startswith("var"):
        txt = txt[txt.find("=")+1:].strip().rstrip(";")
    try:
        return r.json()
    except Exception:
        import json; return json.loads(txt)

def get_all_makes():
    data = cq("getMakes")
    makes = data.get("Makes") or data.get("makes") or []
    out=[]
    for m in makes:
        display = m.get("make_display") or m.get("make_name") or m.get("make") or ""
        slug = m.get("make_slug") or display.lower()
        country = m.get("make_country") or ""
        out.append({"display":display, "slug":slug, "country":country})
    return out

def is_ksa_make(display):
    name = display.strip().lower()
    name = name.replace("mercedes benz","mercedes-benz").replace("great wall motors","great wall")
    return any(name==x or name.startswith(x+" ") for x in KSA_MAKES)

def get_models_for_make(slug):
    data = cq("getModels", make=slug, sold_in_us="")
    return data.get("Models") or data.get("models") or []

def year_pass(y):
    if not y: return True
    try: y = int(y)
    except: return True
    if MIN_YEAR and y < MIN_YEAR: return False
    if MAX_YEAR and y > MAX_YEAR: return False
    return True

def main():
    makes = get_all_makes()
    target = [m for m in makes if is_ksa_make(m["display"])]
    rows=[]
    for i, mk in enumerate(target, 1):
        try:
            models = get_models_for_make(mk["slug"])
        except Exception as e:
            print(f"[warn] {mk['display']}: {e}"); time.sleep(1.2); continue
        for m in models:
            ys = m.get("model_start_year") or m.get("model_year")
            ye = m.get("model_end_year")
            if not year_pass(ys): continue
            rows.append({
                "Make": mk["display"],
                "Model": m.get("model_name",""),
                "YearStart": ys or "",
                "YearEnd": ye or "",
                "MakeCountry": mk["country"]
            })
        if i % 10 == 0: time.sleep(1.0)

    df = pd.DataFrame(rows).drop_duplicates().sort_values(["Make","Model","YearStart"], na_position="last")
    df.to_csv("ksa_makes_models.csv", index=False, encoding="utf-8-sig")
    try:
        df.to_excel("ksa_makes_models.xlsx", index=False)
    except Exception as e:
        print("[warn] excel export:", e)
    print(f"done: {len(df):,} rows -> ksa_makes_models.(csv|xlsx)")

if __name__ == "__main__":
    main()