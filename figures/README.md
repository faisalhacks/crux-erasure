# figures/

Run (miniconda Python, isolated): `C:/Users/intel/miniconda3/python.exe -I make_figures.py [--in DIR] [--out DIR]`
Default input `dummy/` (from `make_dummy_results.py`, invented numbers, `kind: "dummy"`), default output `dummy_out/`.
Any input with `kind` in dummy/synthetic/shuffled gets a "DUMMY DATA" watermark and a `DUMMY_` file prefix.
No numbers are hard-coded; each figure writes PDF + PNG (220 dpi) + sidecar JSON (input sha256) and `captions.md`.
Still to do before real use: append a run_log.jsonl line per run (not wired yet), and look at each render.

| Fig | Input file | Schema (keys read) |
|---|---|---|
| 1 gate-1 | gate1.json | analysis/gate1.py output: kappa.{primary,primary_ci_info_only,cutoff,n_shared,unsure_L1,unsure_L2}, balanced_accuracy.{ba,lo,hi,n_used,n_unsure_excluded}, verdict |
| 2 A2 forest | a2.json | a2_within_round.py output: controlled.{erasure,length,clarity}.{est,lo,hi}, uncontrolled.erasure, n_clusters, B, seed |
| 3 N1 | n1.json | n1_winner_vs_mean.py output: erasure/length/clarity.{est,lo,hi}, n_clusters, B, seed |
| 4 Tier 2 | a2.json + optional a4.json (a2 format, second scorer), a3.json / n3.json (`{n_clusters, erasure:{est,lo,hi}}`), n4.json (`{minority:{est,lo,hi}, majority:{...}}`) | missing optional files are labelled "not available" |
| 5 N2 grid | n2.json | `{measure, cells:{"<sys>|<user>":{mean,lo,hi,n_clusters}}}`, sys in keep_all_satisfied/accurate_differences, user in common_ground/show_disagreement |
| 6 schematic | none | static, no data |

The a3/n3/n4/n2 schemas are PROPOSED by the figure maker (stats coder has not written those scripts yet); align the scripts to them or edit the readers in make_figures.py.
