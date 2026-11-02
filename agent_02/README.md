# Agent 02 - A Q-learning seller against a rule-following seller

Laboratory Experiment 02 (due 29.10.2026), by Bùi Nguyên Hoàng Việt (B23DCDT285). Two shops in a simulated e-commerce market decide at every step whether to give a 20% discount. A tabular Q-learning seller is compared with a fixed rule-based seller. The assignment, reference code and slides are in `material/`.

| Path | Content |
|---|---|
| `code/agent02_experiment.py` | market, all sellers, training, separate evaluation, every experiment (A-E, Q8-Q10) |
| `notebook/agent02_demo.ipynb` | the same experiments step by step, with commentary and extra charts |
| `results/` | CSV results, `q_tables.txt`, `figures/*.png`, `tables/*.tex` (the report `\input`s these tables) |
| `report/agent02.pdf` | the report: model, method, findings, answers to the 10 questions, reflection |

```bash
python -m venv .venv
.venv\Scripts\activate                 # Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
cd code
python agent02_experiment.py           # about 25 min, rewrites ../results/
python agent02_experiment.py --only robustness   # re-run a single extra study
```

The script keeps the reference market, Q-learning update and rule, and adds:

- a paired evaluation: both kinds of seller sit in seat 0 against the same rival, seed and demand sequence;
- 10 seeds per configuration;
- fixed-epsilon and fully greedy exploration settings;
- studies for Q8 (two learners), Q9 (aggressive rival) and Q10 (rival pool, step size 1/N, robustness test).

Main results (greedy evaluation, reward per step):

| Seller | Reference market (10 seeds) | Average over 5 rival types |
|---|---|---|
| Rule-based | 34.97 ± 0.25 | 29.94 |
| Q-learning, reference settings | 34.39 ± 1.24 | 31.08 |
| Q-learning, rival pool + α = 1/N | 34.72 ± 0.77 (robustness test) | 31.59 |
| Best response (model) | 35.00 | 31.80 |
