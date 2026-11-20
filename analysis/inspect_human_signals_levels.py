"""Step 1 (D49a): levels of the human signals. Counts and array shapes only.
No scores are loaded; ranks are not read (only their presence is counted).
Output: analysis/human_signals_levels.json
"""
import json, os
from collections import Counter
import pandas as pd

D = os.path.join(os.path.dirname(__file__), "..", "..", "data", "habermas_gcs")
OUT = os.path.join(os.path.dirname(__file__), "human_signals_levels.json")
r = {}

cc = pd.read_parquet(os.path.join(D, "hm_all_candidate_comparisons.parquet"),
                     columns=["iteration_index", "metadata.provenance", "critique.metadata.provenance",
                              "critique.metadata.status", "critique.text", "ratings.agreement",
                              "ratings.quality", "rankings.explanation", "launch_id", "round_id"])
hum = cc[cc["metadata.provenance"] == "HUMAN_CITIZEN"]
r["cc_rows_human"] = int(len(hum))
r["cc_human_by_iteration"] = {str(k): int(v) for k, v in hum["iteration_index"].value_counts().items()}
crit = hum[(hum["critique.metadata.provenance"] == "HUMAN_CITIZEN") & (hum["critique.metadata.status"] == "COMPLETED")]
r["critiques_human_completed_by_iteration"] = {str(k): int(v) for k, v in crit["iteration_index"].value_counts().items()}
r["critiques_human_completed_rounds"] = int(crit["round_id"].nunique())
r["critiques_human_completed_launches"] = int(crit["launch_id"].nunique())
r["agreement_array_len"] = dict(Counter(int(len(a)) for a in hum["ratings.agreement"] if a is not None))
r["agreement_values_sample"] = sorted({str(x) for a in hum["ratings.agreement"].head(3000) if a is not None for x in a})[:20]
r["quality_array_len"] = dict(Counter(int(len(a)) for a in hum["ratings.quality"] if a is not None))
r["quality_values_sample"] = sorted({str(x) for a in hum["ratings.quality"].head(3000) if a is not None for x in a})[:20]
ex = hum["rankings.explanation"].dropna()
ex = ex[ex.astype(str).str.len() > 0]
r["ranking_explanations_human_nonempty"] = int(len(ex))
r["ranking_explanations_by_iteration"] = {str(k): int(v) for k, v in hum.loc[ex.index, "iteration_index"].value_counts().items()}

ps = pd.read_parquet(os.path.join(D, "hm_all_position_statement_ratings.parquet"))
psh = ps[ps["metadata.provenance"] == "HUMAN_CITIZEN"]
r["position_rows_human"] = int(len(psh))
r["position_by_rating_index"] = {str(k): int(v) for k, v in psh["rating_index"].value_counts().items()}
r["position_by_question_index"] = {str(k): int(v) for k, v in psh["question_index"].value_counts().items()}
r["position_agreement_array_len"] = dict(Counter(int(len(a)) for a in psh["ratings.agreement"] if a is not None))
r["position_agreement_values"] = sorted({str(x) for a in psh["ratings.agreement"].head(5000) if a is not None for x in a})[:20]
r["position_launches"] = int(psh["launch_id"].nunique())
r["position_participants"] = int(psh["metadata.participant_id"].nunique())

sv = pd.read_parquet(os.path.join(D, "hm_all_round_survey_responses.parquet"))
svh = sv[sv["metadata.provenance"] == "HUMAN_CITIZEN"]
r["survey_rows_human"] = int(len(svh))
for c in ["best_expression", "own_influence", "unwanted_pressure", "view_change", "view_movement",
          "candidate.metadata.provenance"]:
    r[f"survey_{c}"] = {str(k): int(v) for k, v in svh[c].value_counts().items()}
r["survey_view_explanation_nonempty"] = int(svh["view_explanation"].dropna().astype(str).str.len().gt(0).sum())
json.dump(r, open(OUT, "w", encoding="utf-8"), indent=1)
print(json.dumps(r, indent=1))
