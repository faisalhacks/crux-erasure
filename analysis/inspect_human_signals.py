"""Step 1 (D49): inventory of existing human signals in the Habermas Machine data.
Schema/level description only: column names, dtypes, row counts, key cardinalities,
non-null counts and value sets of small categorical columns. No join with scores,
no relation to rankings is computed. Output: analysis/human_signals_inventory.json
"""
import hashlib, json, os, sys
import pandas as pd

D = os.path.join(os.path.dirname(__file__), "..", "..", "data", "habermas_gcs")
OUT = os.path.join(os.path.dirname(__file__), "human_signals_inventory.json")
res = {}
for f in sorted(os.listdir(D)):
    if not f.endswith(".parquet"):
        continue
    p = os.path.join(D, f)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    df = pd.read_parquet(p)
    cols = {}
    for c in df.columns:
        s = df[c]
        info = {"dtype": str(s.dtype), "non_null": int(s.notna().sum())}
        try:
            nu = s.nunique(dropna=True)
            info["n_unique"] = int(nu)
            if nu <= 12:
                info["values"] = [str(v) for v in s.dropna().unique()[:12]]
            elif s.dtype == object:
                ex = s.dropna().astype(str)
                info["example_len_chars_median"] = float(ex.str.len().median())
        except TypeError:
            info["n_unique"] = "unhashable"
            info["example_type"] = type(s.dropna().iloc[0]).__name__ if s.notna().any() else None
        cols[c] = info
    res[f] = {"sha256": h, "rows": int(len(df)), "columns": cols}
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
for f, r in res.items():
    print(f"== {f} rows={r['rows']}")
    for c, i in r["columns"].items():
        extra = i.get("values", i.get("example_len_chars_median", i.get("example_type", "")))
        print(f"   {c}: {i['dtype']} nn={i['non_null']} uniq={i.get('n_unique')} {extra}")
