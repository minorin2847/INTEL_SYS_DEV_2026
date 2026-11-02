#!/usr/bin/env python3
# Agent 02: Q-learning seller vs rule-based seller. Changes to the reference code are documented in report/agent02.tex.

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

# ----------------------------------------------------------------------------
# 1. Settings and paths
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class Settings:
    """All tunable numbers of the study in one place."""

    # training
    num_episodes: int = 5000
    horizon: int = 20                # steps per episode
    lr: float = 0.10                 # learning rate (alpha)
    gamma: float = 0.90              # discount factor of future profit
    eps_start: float = 0.20
    eps_floor: float = 0.02
    eps_decay: float = 0.995

    # market
    list_price: float = 10.0
    unit_cost: float = 5.0
    discount_pct: float = 0.20       # price cut when a seller discounts
    quiet_customers: int = 10        # demand level 0
    busy_customers: int = 20         # demand level 1

    # evaluation / bookkeeping
    base_seed: int = 42
    eval_episodes: int = 500
    smooth_window: int = 100         # K episodes per point on learning curves


SEEDS = [11, 22, 33, 44, 55, 66, 77, 88, 99, 110]
EVAL_SEED_SHIFT = 800_000

PROJECT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT / "results"
FIGURES = RESULTS / "figures"
TABLES = RESULTS / "tables"

KEEP, CUT = 0, 1                     # the two possible actions
SELL_FULL = "no discount"
SELL_CUT = "discount"


# ----------------------------------------------------------------------------
# 2. The market
# ----------------------------------------------------------------------------


class PriceWarMarket:
    """Two sellers, one product.

    observation of seller i : (demand, rival's action at the previous step)
    action                  : 0 = keep the price, 1 = give the discount
    reward                  : profit = sales * (price paid - unit cost)
    """

    def __init__(self, settings: Settings, seed: int | None = None):
        self.cfg = settings
        self.rng = np.random.default_rng(settings.base_seed if seed is None else seed)
        self.demand = 0
        self.last_moves = [0, 0]

    # -- helpers ---------------------------------------------------------
    def _customers(self) -> int:
        c = self.cfg
        return c.quiet_customers if self.demand == 0 else c.busy_customers

    def observations(self):
        return [(self.demand, self.last_moves[1]),
                (self.demand, self.last_moves[0])]

    # -- gym-like API ----------------------------------------------------
    def reset(self):
        self.demand = int(self.rng.integers(0, 2))
        self.last_moves = [0, 0]
        return self.observations()

    def step(self, moves):
        if len(moves) != 2:
            raise ValueError("Exactly two actions are required.")
        if any(m not in (0, 1) for m in moves):
            raise ValueError("Actions must be 0 or 1.")

        crowd = self._customers()
        profits, sold, conv = [], [], []
        for me in range(2):
            mine, theirs = moves[me], moves[1 - me]
            p_buy = float(np.clip(0.30 + 0.25 * self.demand
                                  + 0.15 * mine - 0.10 * theirs, 0.05, 0.95))
            n_sold = int(self.rng.binomial(crowd, p_buy))
            paid = self.cfg.list_price * (1.0 - self.cfg.discount_pct * mine)
            profits.append(float(n_sold * (paid - self.cfg.unit_cost)))
            sold.append(n_sold)
            conv.append(p_buy)

        self.last_moves = list(moves)
        self.demand = int(self.rng.integers(0, 2))
        details = {"sales": sold, "conversion": conv, "customers": crowd}
        return self.observations(), profits, details


def expected_profit(cfg: Settings, demand: int, mine: int, theirs: int) -> float:
    """Analytic one-step expectation  N * p * margin  (analysis only)."""
    crowd = cfg.quiet_customers if demand == 0 else cfg.busy_customers
    p_buy = np.clip(0.30 + 0.25 * demand + 0.15 * mine - 0.10 * theirs, 0.05, 0.95)
    margin = cfg.list_price * (1 - cfg.discount_pct * mine) - cfg.unit_cost
    return crowd * p_buy * margin


# ----------------------------------------------------------------------------
# 3. Sellers
# ----------------------------------------------------------------------------


class TabularQSeller:
    """Q-learning with a table  Q[demand, rival_last, action].

    ``step_rule="constant"`` is the reference learner (fixed lr);
    ``step_rule="visit"`` uses lr = 1 / N(s, a), the sample-average rule of the
    improved agent (question 10).
    """

    learns = True

    def __init__(self, lr=0.10, gamma=0.90, epsilon=0.20, seed=123,
                 step_rule="constant"):
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.step_rule = step_rule
        self.rng = np.random.default_rng(seed)
        self.q = np.zeros((2, 2, 2))
        self.visits = np.zeros((2, 2, 2), dtype=int)

    def choose(self, obs, explore=True):
        demand, rival_last = obs
        if explore and self.rng.random() < self.epsilon:
            return int(self.rng.integers(0, 2))
        row = self.q[demand, rival_last]
        ties = np.flatnonzero(np.isclose(row, np.max(row)))
        return int(self.rng.choice(ties))

    def update(self, obs, action, reward, next_obs, done=False):
        d, c = obs
        nd, nc = next_obs
        current = self.q[d, c, action]
        bootstrap = 0.0 if done else self.gamma * np.max(self.q[nd, nc])
        target = reward + bootstrap

        self.visits[d, c, action] += 1
        rate = 1.0 / self.visits[d, c, action] if self.step_rule == "visit" else self.lr
        self.q[d, c, action] = current + rate * (target - current)

    def new_episode(self):
        """The reference learner keeps no per-episode memory."""

    def greedy_policy(self):
        return {(d, c): int(np.argmax(self.q[d, c]))
                for d in range(2) for c in range(2)}

    def policy_code(self):
        """Greedy policy of the 4 states packed in one integer (to count flips)."""
        pol = self.greedy_policy()
        return pol[(0, 0)] + 2 * pol[(0, 1)] + 4 * pol[(1, 0)] + 8 * pol[(1, 1)]


class MemoryQSeller(TabularQSeller):
    """Improved learner for question 10: the state also contains the seller's own
    previous action, so the rival's delayed reaction becomes observable
    (2 x 2 x 2 x 2 = 16 Q-values)."""

    def __init__(self, gamma=0.90, epsilon=0.20, seed=123, step_rule="visit", lr=0.10):
        super().__init__(lr, gamma, epsilon, seed, step_rule)
        self.q = np.zeros((2, 2, 2, 2))
        self.visits = np.zeros((2, 2, 2, 2), dtype=int)
        self.new_episode()

    def new_episode(self):
        self.own_last = 0
        self._seen = (0, 0, 0)

    def choose(self, obs, explore=True):
        full = (obs[0], obs[1], self.own_last)
        if explore and self.rng.random() < self.epsilon:
            move = int(self.rng.integers(0, 2))
        else:
            row = self.q[full]
            move = int(self.rng.choice(np.flatnonzero(np.isclose(row, row.max()))))
        self._seen = full
        self.own_last = move
        return move

    def update(self, obs, action, reward, next_obs, done=False):
        here = self._seen
        there = (next_obs[0], next_obs[1], action)
        target = reward if done else reward + self.gamma * np.max(self.q[there])
        idx = here + (action,)
        self.visits[idx] += 1
        rate = 1.0 / self.visits[idx] if self.step_rule == "visit" else self.lr
        self.q[idx] += rate * (target - self.q[idx])

    def greedy_policy(self):
        return {(d, c, p): int(np.argmax(self.q[d, c, p]))
                for d in range(2) for c in range(2) for p in range(2)}

    def policy_code(self):
        return sum(a << i for i, a in enumerate(self.greedy_policy().values()))


class FixedSeller:
    """Base class of every seller that does not learn."""

    learns = False
    label = "Rule-based"

    def choose(self, obs, explore=True):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        return None

    def new_episode(self):
        return None


class RuleSeller(FixedSeller):
    """Reference rule: discount only if demand is high AND the rival discounted
    at the previous step."""

    def choose(self, obs, explore=True):
        demand, rival_last = obs
        if demand == 0:
            return KEEP
        if rival_last == 1:
            return CUT
        return KEEP


class AggressiveSeller(FixedSeller):
    """Question 9 rival: discounts whenever demand is high."""

    label = "Aggressive"

    def choose(self, obs, explore=True):
        return CUT if obs[0] == 1 else KEEP


class MirrorSeller(FixedSeller):
    """Tit-for-tat: repeats the rival's previous action."""

    label = "Tit-for-tat"

    def choose(self, obs, explore=True):
        return obs[1]


class ConstantSeller(FixedSeller):
    def __init__(self, action, label):
        self.action = action
        self.label = label

    def choose(self, obs, explore=True):
        return self.action


class CoinFlipSeller(FixedSeller):
    label = "Random (p=0.5)"

    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)

    def choose(self, obs, explore=True):
        return int(self.rng.integers(0, 2))


RIVAL_FACTORIES = {
    "rule": lambda seed: RuleSeller(),
    "aggressive": lambda seed: AggressiveSeller(),
    "tit_for_tat": lambda seed: MirrorSeller(),
    "always_discount": lambda seed: ConstantSeller(CUT, "Always discount"),
    "never_discount": lambda seed: ConstantSeller(KEEP, "Never discount"),
    "random": lambda seed: CoinFlipSeller(seed + 30_000),
}


def build_rival(kind: str, seed: int = 0):
    return RIVAL_FACTORIES[kind](seed)


# ----------------------------------------------------------------------------
# 4. Training and (separate) evaluation
# ----------------------------------------------------------------------------


def epsilon_for(episode: int, schedule) -> float:
    start, floor, decay = schedule
    return max(floor, start * decay ** episode)


def train(cfg: Settings, seed: int, lr=None, schedule=None, opponent="rule",
          step_rule="constant", opponent_pool=None, memory=False):
    """Train the seller in seat 0 and return ``(seat0, seat1, log)``.

    ``opponent``      name of the rival, or ``"rl"`` for a second Q-learner that
                      learns at the same time;
    ``opponent_pool`` list of rival names; one is drawn per episode (question 10);
    ``log``           one dict per episode.
    """
    lr = cfg.lr if lr is None else lr
    schedule = schedule or (cfg.eps_start, cfg.eps_floor, cfg.eps_decay)

    market = PriceWarMarket(cfg, seed=seed)
    if memory:
        hero = MemoryQSeller(cfg.gamma, schedule[0], seed + 10_000, step_rule, lr)
    else:
        hero = TabularQSeller(lr, cfg.gamma, schedule[0], seed + 10_000, step_rule)

    draw = np.random.default_rng(seed + 40_000)
    if opponent_pool:
        roster = [build_rival(k, seed) for k in opponent_pool]
        rival = roster[0]
    elif opponent == "rl":
        rival = TabularQSeller(lr, cfg.gamma, schedule[0], seed + 20_000)
    else:
        rival = build_rival(opponent, seed)

    log = []
    horizon = cfg.horizon
    for ep in range(cfg.num_episodes):
        eps = epsilon_for(ep, schedule)
        hero.epsilon = eps
        if rival.learns:
            rival.epsilon = eps
        if opponent_pool:
            rival = roster[int(draw.integers(0, len(roster)))]

        obs = market.reset()
        hero.new_episode()
        rival.new_episode()
        earned = [0.0, 0.0]
        cuts = [0, 0]
        for t in range(horizon):
            moves = [hero.choose(obs[0], explore=True),
                     rival.choose(obs[1], explore=True)]
            nxt, rewards, _ = market.step(moves)
            last = t == horizon - 1
            hero.update(obs[0], moves[0], rewards[0], nxt[0], last)
            rival.update(obs[1], moves[1], rewards[1], nxt[1], last)
            for i in range(2):
                earned[i] += rewards[i]
                cuts[i] += moves[i]
            obs = nxt

        log.append({
            "episode": ep + 1,
            "rl_episode_reward": earned[0],
            "opponent_episode_reward": earned[1],
            "rl_mean_reward_per_step": earned[0] / horizon,
            "opponent_mean_reward_per_step": earned[1] / horizon,
            "rl_discount_rate": cuts[0] / horizon,
            "opponent_discount_rate": cuts[1] / horizon,
            "epsilon": eps,
            "alpha": lr,
            "rl_policy": hero.policy_code(),
            "opponent_policy": rival.policy_code() if rival.learns else -1,
        })
    return hero, rival, log


def evaluate(cfg: Settings, seat0, seat1, seed: int, episodes: int | None = None):
    """Play two *frozen* sellers against each other (no learning, no exploration)
    in a fresh market built from ``seed``.

    Returns ``(per_seat_summary, mean_reward_per_step_of_each_episode)``.
    """
    episodes = cfg.eval_episodes if episodes is None else episodes
    market = PriceWarMarket(cfg, seed=seed)
    seats = [seat0, seat1]
    horizon = cfg.horizon

    per_episode = np.zeros((episodes, 2))
    action_count = np.zeros((2, 2), dtype=int)
    for ep in range(episodes):
        obs = market.reset()
        for s in seats:
            s.new_episode()
        for _ in range(horizon):
            moves = [seats[i].choose(obs[i], explore=False) for i in range(2)]
            obs, rewards, _ = market.step(moves)
            for i in range(2):
                per_episode[ep, i] += rewards[i]
                action_count[i, moves[i]] += 1

    steps = episodes * horizon
    total = per_episode.sum(axis=0)
    summary = [{
        "seat": i,
        "total_reward": float(total[i]),
        "mean_reward_per_step": float(total[i] / steps),
        "episode_std_of_mean_reward": float(np.std(per_episode[:, i] / horizon, ddof=1)),
        "no_discount_actions": int(action_count[i, 0]),
        "discount_actions": int(action_count[i, 1]),
        "discount_action_rate": float(action_count[i, 1] / steps),
    } for i in range(2)]
    return summary, per_episode / horizon


# ----------------------------------------------------------------------------
# 5. Small utilities (files, statistics, formatting)
# ----------------------------------------------------------------------------


def save_csv(path, records):
    if not records:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)


def save_latex_table(path, header, body, align):
    lines = [r"\begin{tabular}{" + align + "}", r"\toprule",
             " & ".join(header) + r" \\", r"\midrule"]
    lines += [" & ".join(str(cell) for cell in row) + r" \\" for row in body]
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def q_table_report(title, seller):
    lines = [title,
             "Q[demand, rival_last_action, action]; action 0 = no discount, 1 = discount"]
    for d in range(2):
        for c in range(2):
            q_keep, q_cut = seller.q[d, c]
            n_keep, n_cut = seller.visits[d, c]
            lines.append(
                f"  state=({d}, {c}) | Q0={q_keep:9.4f} | Q1={q_cut:9.4f} | "
                f"visits=({n_keep}, {n_cut}) | "
                f"greedy={'DISCOUNT' if q_cut > q_keep else 'NO DISCOUNT'}")
    return "\n".join(lines) + "\n\n"


def append_text(path, text):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(text)


def block_means(values, k):
    """Mean of consecutive non-overlapping blocks of k episodes."""
    arr = np.asarray(values, dtype=float)
    n_blocks = len(arr) // k
    return arr[: n_blocks * k].reshape(n_blocks, k).mean(axis=1)


def mean_std(values):
    arr = np.asarray(values, dtype=float)
    return float(arr.mean()), (float(arr.std(ddof=1)) if len(arr) > 1 else 0.0)


def count_policy_changes(codes):
    codes = np.asarray(codes)
    return int(np.count_nonzero(codes[1:] != codes[:-1]))


def never_discounts(seller):
    return all(a == KEEP for a in seller.greedy_policy().values())


def fmt2(x):
    return f"{x:.2f}"


def fmt3(x):
    return f"{x:.3f}"


def heading(text, char="-", width=72):
    print(f"\n{char * width}\n {text}\n{char * width}")


# ----------------------------------------------------------------------------
# 6. Plot style
# ----------------------------------------------------------------------------

TEAL, CORAL, INDIGO, AMBER, SLATE = "#0f766e", "#e4572e", "#4c4ccf", "#e0a100", "#64748b"
SERIES = [TEAL, CORAL, INDIGO, AMBER, SLATE]
BENCHMARK = 35.0   # expected reward per step when nobody ever discounts

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 170, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": "#cbd5e1",
    "grid.linewidth": 0.7, "axes.axisbelow": True,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.labelcolor": "#334155", "xtick.color": "#475569", "ytick.color": "#475569",
    "legend.frameon": False,
})


def finish(fig, filename):
    fig.tight_layout()
    fig.savefig(FIGURES / filename)
    plt.close(fig)


def episode_axis(values, k):
    return (np.arange(len(values)) + 1) * k


# ----------------------------------------------------------------------------
# 7. One configuration over all seeds
# ----------------------------------------------------------------------------


def run_config(cfg, label, seeds=SEEDS, **train_kwargs):
    """Train + greedily evaluate one configuration for every seed.

    Returns (per-seed rows, stacked windowed training curves, trained sellers).
    """
    opponent = train_kwargs.get("opponent", "rule")
    rows, curves, sellers = [], [], []
    for seed in seeds:
        hero, _, log = train(cfg, seed, **train_kwargs)
        rival = build_rival("rule" if opponent == "rl" else opponent, seed)
        result, _ = evaluate(cfg, hero, rival, seed + EVAL_SEED_SHIFT)
        rewards = [r["rl_mean_reward_per_step"] for r in log]
        rows.append({
            "configuration": label,
            "seed": seed,
            "train_mean_reward_per_step": np.mean(rewards),
            "train_last500_mean_reward_per_step": np.mean(rewards[-500:]),
            "eval_mean_reward_per_step": result[0]["mean_reward_per_step"],
            "eval_discount_rate": result[0]["discount_action_rate"],
            "never_discount_policy": int(never_discounts(hero)),
            "policy_flips_during_training": count_policy_changes(
                [r["rl_policy"] for r in log]),
        })
        curves.append(block_means(rewards, cfg.smooth_window))
        sellers.append(hero)
    return rows, np.array(curves), sellers


def aggregate(label, rows):
    ev_mean, ev_std = mean_std([r["eval_mean_reward_per_step"] for r in rows])
    tr_mean, tr_std = mean_std([r["train_mean_reward_per_step"] for r in rows])
    disc, _ = mean_std([r["eval_discount_rate"] for r in rows])
    return {
        "configuration": label,
        "n_seeds": len(rows),
        "eval_mean_reward": ev_mean, "eval_std_across_seeds": ev_std,
        "train_mean_reward": tr_mean, "train_std_across_seeds": tr_std,
        "eval_discount_rate": disc,
        "seeds_with_never_discount_policy": sum(r["never_discount_policy"] for r in rows),
        "mean_policy_flips": float(np.mean(
            [r["policy_flips_during_training"] for r in rows])),
    }


def rule_as_seat0(cfg, opponent="rule", seeds=SEEDS):
    """Hand-written rule in seat 0 against the same rival / evaluation seeds."""
    rows = []
    for seed in seeds:
        result, _ = evaluate(cfg, RuleSeller(), build_rival(opponent, seed),
                             seed + EVAL_SEED_SHIFT)
        rows.append({
            "configuration": "Rule-based",
            "seed": seed,
            "train_mean_reward_per_step": float("nan"),
            "train_last500_mean_reward_per_step": float("nan"),
            "eval_mean_reward_per_step": result[0]["mean_reward_per_step"],
            "eval_discount_rate": result[0]["discount_action_rate"],
            "never_discount_policy": 0,
            "policy_flips_during_training": 0,
        })
    return rows


# ----------------------------------------------------------------------------
# 8. Experiments
# ----------------------------------------------------------------------------


def run_expected_profit(cfg):
    heading("Model analysis: expected one-step profit")
    rows = []
    for d in range(2):
        for c in range(2):
            row = {"demand": d, "competitor_current_action": c}
            for a in range(2):
                row[f"E_profit_action_{a}"] = expected_profit(cfg, d, a, c)
            row["myopic_best_action"] = int(row["E_profit_action_1"]
                                            > row["E_profit_action_0"])
            rows.append(row)
            print(row)
    save_csv(RESULTS / "expected_profit_table.csv", rows)
    save_latex_table(
        TABLES / "expected_profit.tex",
        ["Demand $d$", "Rival's current action", r"$E[r\mid a=0]$",
         r"$E[r\mid a=1]$", "Better action"],
        [["low" if r["demand"] == 0 else "high",
          "discount" if r["competitor_current_action"] else "no discount",
          fmt2(r["E_profit_action_0"]), fmt2(r["E_profit_action_1"]),
          "discount" if r["myopic_best_action"] else "no discount"] for r in rows],
        "llrrl")


def run_baseline(cfg):
    heading("Experiments A and B: baseline run (seed 42)")
    hero, _, log = train(cfg, cfg.base_seed)
    save_csv(RESULTS / "baseline_episode_rewards.csv", log)

    eval_seed = cfg.base_seed + 500_000
    rl_result, rl_eps = evaluate(cfg, hero, RuleSeller(), eval_seed)
    rule_result, rule_eps = evaluate(cfg, RuleSeller(), RuleSeller(), eval_seed)

    table = []
    for match, result in (("RL vs Rule", rl_result), ("Rule vs Rule", rule_result)):
        for entry in result:
            who = "RL" if (match == "RL vs Rule" and entry["seat"] == 0) else "Rule-based"
            table.append({"match": match, "agent": who, **entry})
    save_csv(RESULTS / "baseline_evaluation.csv", table)
    save_csv(RESULTS / "baseline_evaluation_episodes.csv", [
        {"episode": i + 1, "rl_seat0_vs_rule": rl_eps[i, 0],
         "rule_seat1": rl_eps[i, 1], "rule_seat0_vs_rule": rule_eps[i, 0]}
        for i in range(len(rl_eps))])
    (RESULTS / "q_tables.txt").write_text(
        q_table_report("Baseline RL agent (seed 42), trained against the rule-based agent",
                       hero), encoding="utf-8")

    for r in table:
        print(f"{r['match']:<13} seat {r['seat']}  {r['agent']:<10} "
              f"total={r['total_reward']:>9,.0f}  mean/step={r['mean_reward_per_step']:.3f}  "
              f"discounts={r['discount_actions']}  keeps={r['no_discount_actions']}")
    print(q_table_report("Baseline Q-table", hero))

    # totals collected while training (with exploration)
    totals = {
        "rl_total_training_reward": sum(r["rl_episode_reward"] for r in log),
        "rule_total_training_reward": sum(r["opponent_episode_reward"] for r in log),
        "rl_training_discount_actions": int(round(
            sum(r["rl_discount_rate"] for r in log) * cfg.horizon)),
        "rule_training_discount_actions": int(round(
            sum(r["opponent_discount_rate"] for r in log) * cfg.horizon)),
        "total_training_steps": cfg.num_episodes * cfg.horizon,
        "rl_policy_flips": count_policy_changes([r["rl_policy"] for r in log]),
    }
    save_csv(RESULTS / "baseline_training_totals.csv", [totals])
    print(totals)

    save_latex_table(
        TABLES / "baseline_eval.tex",
        ["Match (seat 0 vs seat 1)", "Agent", "Total reward", "Mean reward/step",
         "Discounts", "No discounts", "Discount rate"],
        [[r["match"], f"{r['agent']} (seat {r['seat']})", f"{r['total_reward']:,.0f}",
          fmt3(r["mean_reward_per_step"]), r["discount_actions"],
          r["no_discount_actions"], fmt3(r["discount_action_rate"])] for r in table],
        "llrrrrr")
    save_latex_table(
        TABLES / "baseline_qtable.tex",
        ["State $(d, c)$", "$Q(s, 0)$", "$Q(s, 1)$", "Visits $(a{=}0, a{=}1)$",
         "Greedy action"],
        [[f"({d}, {c})", fmt2(hero.q[d, c, 0]), fmt2(hero.q[d, c, 1]),
          f"({hero.visits[d, c, 0]:,}, {hero.visits[d, c, 1]:,})",
          "discount" if hero.q[d, c, 1] > hero.q[d, c, 0] else "no discount"]
         for d in range(2) for c in range(2)],
        "lrrrl")

    plot_baseline_training(cfg, log)
    plot_baseline_eval(rl_eps[:, 0], rule_eps[:, 0], cfg.eval_episodes)
    return hero


def plot_baseline_training(cfg, log):
    k = cfg.smooth_window
    raw = np.array([r["rl_mean_reward_per_step"] for r in log])
    n_blocks = len(raw) // k
    blocks = raw[: n_blocks * k].reshape(n_blocks, k)
    rule_w = block_means([r["opponent_mean_reward_per_step"] for r in log], k)
    disc_w = block_means([r["rl_discount_rate"] for r in log], k)
    codes = np.array([r["rl_policy"] for r in log])
    changed = np.r_[0, codes[1:] != codes[:-1]].astype(int)
    changes_per_block = changed[: n_blocks * k].reshape(n_blocks, k).sum(axis=1)
    x = episode_axis(blocks.mean(axis=1), k)

    fig, (top, bottom) = plt.subplots(2, 1, figsize=(8.6, 6.4), sharex=True,
                                      gridspec_kw={"height_ratios": [3, 2]})
    top.fill_between(x, blocks.min(axis=1), blocks.max(axis=1), color=TEAL, alpha=0.12,
                     label="range of single episodes (RL)")
    top.fill_between(x, np.percentile(blocks, 25, axis=1), np.percentile(blocks, 75, axis=1),
                     color=TEAL, alpha=0.30, label="middle 50% of episodes (RL)")
    top.plot(x, blocks.mean(axis=1), color=TEAL, lw=2.2, label="RL block mean")
    top.plot(x, rule_w, color=CORAL, lw=1.8, ls="--", label="rule-based block mean")
    top.axhline(BENCHMARK, color=SLATE, lw=1, ls=":")
    top.text(x[-1], BENCHMARK + 0.5, "35 = nobody ever discounts", ha="right",
             color=SLATE, fontsize=8)
    top.set_ylabel("reward per step")
    top.set_title(f"Reward spread inside each block of {k} training episodes")
    top.legend(loc="lower right", fontsize=8)

    bottom.bar(x, changes_per_block, width=k * 0.8, color=INDIGO, alpha=0.85)
    bottom.set_ylabel("greedy-policy changes\nper block", color=INDIGO)
    bottom.set_xlabel("training episode")
    bottom.set_title("Instability: how often the greedy policy flipped (bars) "
                     "and how often RL discounted (line)")
    twin = bottom.twinx()
    twin.plot(x, disc_w, color=CORAL, lw=1.8, marker="o", ms=3)
    twin.set_ylabel("discount share", color=CORAL)
    twin.grid(False)
    finish(fig, "fig_baseline_training.png")


def plot_baseline_eval(rl_values, rule_values, n):
    fig, ax = plt.subplots(figsize=(5.4, 5.0))
    lo = min(rl_values.min(), rule_values.min()) - 1
    hi = max(rl_values.max(), rule_values.max()) + 1
    ax.plot([lo, hi], [lo, hi], color=SLATE, ls="--", lw=1, label="equal reward")
    ax.scatter(rule_values, rl_values, s=16, color=TEAL, alpha=0.6, label="one evaluation episode")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    gap = float(np.abs(np.asarray(rl_values) - np.asarray(rule_values)).max())
    ax.set_xlabel("rule-based seller, reward per step")
    ax.set_ylabel("RL seller, reward per step")
    ax.set_title(f"Same demand, episode by episode (largest gap {gap:.2f})")
    ax.grid(axis="x", alpha=1.0)
    ax.legend(fontsize=8, loc="upper left")
    finish(fig, "fig_baseline_eval_paired.png")


def plot_learning_rate(cfg, curves, results):
    k = cfg.smooth_window
    labels = [rf"$\alpha$ = {lr}" for lr in curves]
    mat = np.vstack([curves[lr].mean(axis=0) for lr in curves])
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.4, 3.9),
                                      gridspec_kw={"width_ratios": [3, 2]})
    im = left.imshow(mat, aspect="auto", cmap="YlGnBu", extent=(0, mat.shape[1] * k, len(mat), 0))
    left.set_yticks(np.arange(len(mat)) + 0.5, labels)
    left.set_xlabel("training episode")
    left.set_title(f"Training reward per step, block of {k} episodes (mean of 10 seeds)")
    left.grid(False)
    fig.colorbar(im, ax=left, pad=0.01, shrink=0.9)

    flips = [np.mean([r["policy_flips_during_training"] for r in results[lr]]) for lr in results]
    bars = right.bar(labels, flips, color=SERIES[: len(flips)], width=0.55)
    right.set_yscale("log")
    for b, v in zip(bars, flips):
        right.text(b.get_x() + b.get_width() / 2, v * 1.12, f"{v:,.0f}", ha="center", fontsize=9)
    right.set_ylim(top=max(flips) * 3)
    right.set_ylabel("greedy-policy changes per run (log)")
    right.set_title("Stability: policy changes")
    finish(fig, "fig_learning_rate.png")


def plot_exploration(results):
    labels = [label for label, _ in EXPLORATION_SETTINGS]
    short = ["decay\n0.20→0.02", "fixed\nε=0.05", "fixed\nε=0.30", "greedy\nε=0"]
    grid = np.array([[r["eval_mean_reward_per_step"] for r in results[l]] for l in labels]).T
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.4, 4.6),
                                      gridspec_kw={"width_ratios": [1, 1]})
    im = left.imshow(grid, aspect="auto", cmap="RdYlGn", vmin=24, vmax=36)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            left.text(j, i, f"{grid[i, j]:.1f}", ha="center", va="center", fontsize=8)
    left.set_xticks(range(len(short)), short, fontsize=8)
    left.set_yticks(range(len(SEEDS)), [f"seed {s}" for s in SEEDS], fontsize=8)
    left.set_title("Greedy evaluation reward of every seed")
    left.grid(False)
    fig.colorbar(im, ax=left, pad=0.02, shrink=0.9)

    lo, hi = 25, 37
    right.plot([lo, hi], [lo, hi], color=SLATE, ls="--", lw=1)
    for j, l in enumerate(labels):
        right.scatter([r["train_mean_reward_per_step"] for r in results[l]],
                      [r["eval_mean_reward_per_step"] for r in results[l]],
                      s=34, color=SERIES[j], alpha=0.8, label=short[j].replace("\n", " "))
    right.set_xlabel("reward per step while training (includes exploration)")
    right.set_ylabel("reward per step in greedy evaluation")
    right.set_title("Training vs. evaluation, one dot per seed (above line: eval better)")
    right.grid(axis="x", alpha=1.0)
    right.legend(fontsize=8, loc="lower right")
    finish(fig, "fig_exploration.png")


def plot_gap_to_rule(lineup):
    """Heatmap of (configuration - rule-based) evaluation reward, per seed."""
    names = ["RL α=0.10", "RL α=0.01", "RL α=0.50", "RL ε=0.05", "RL ε=0.30", "RL ε=0"]
    rule = np.array([r["eval_mean_reward_per_step"] for r in lineup[-1][1]])
    gap = np.array([[r["eval_mean_reward_per_step"] for r in rows] - rule
                    for _, rows in lineup[:-1]])
    limit = max(abs(gap).max(), 1.0)
    fig, ax = plt.subplots(figsize=(9.4, 3.9))
    im = ax.imshow(gap, aspect="auto", cmap="RdBu", vmin=-limit, vmax=limit)
    for i in range(gap.shape[0]):
        for j in range(gap.shape[1]):
            txt = "0" if abs(gap[i, j]) < 1e-9 else f"{gap[i, j]:+.1f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8)
    ax.set_xticks(range(len(SEEDS)), [str(s) for s in SEEDS], fontsize=8)
    ax.set_yticks(range(len(names)), names)
    ax.set_xlabel("seed")
    ax.set_title("Reward gap to the rule-based seller, per seed (blue = better, red = worse)")
    ax.grid(False)
    fig.colorbar(im, ax=ax, pad=0.01, shrink=0.9)
    finish(fig, "fig_gap_to_rule.png")


def plot_two_learners(rows_out, log_rl):
    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.2),
                             gridspec_kw={"width_ratios": [1.1, 0.8, 1.2]})
    bars_ax, flips_ax, heat_ax = axes
    x = np.arange(len(rows_out))
    bars_ax.bar(x - 0.2, [r["rl_vs_rl_eval_reward_seat0"] for r in rows_out], 0.4,
                color=TEAL, label="seat 0")
    bars_ax.bar(x + 0.2, [r["rl_vs_rl_eval_reward_seat1"] for r in rows_out], 0.4,
                color=CORAL, label="seat 1")
    bars_ax.axhline(BENCHMARK, color=SLATE, ls=":", lw=1)
    bars_ax.set_ylim(25, 37)
    bars_ax.set_xticks(x, [str(r["seed"]) for r in rows_out], fontsize=8)
    bars_ax.set_xlabel("seed")
    bars_ax.set_ylabel("greedy reward per step")
    bars_ax.set_title("Final RL-vs-RL pair, per seed")
    bars_ax.legend(fontsize=8, loc="lower left")

    fx = [r["policy_flips_vs_rule"] for r in rows_out]
    fy = [r["policy_flips_vs_learning_rl"] for r in rows_out]
    top = max(fx + fy) * 1.1
    flips_ax.plot([0, top], [0, top], color=SLATE, ls="--", lw=1)
    flips_ax.scatter(fx, fy, s=38, color=INDIGO, alpha=0.85)
    flips_ax.set_xlabel("policy changes, learner vs fixed rule")
    flips_ax.set_ylabel("policy changes, learner vs learner")
    flips_ax.set_title("Instability per seed")
    flips_ax.grid(axis="x", alpha=1.0)

    states = ["(0,0)", "(0,1)", "(1,0)", "(1,1)"]
    code0 = np.array([r["rl_policy"] for r in log_rl])
    code1 = np.array([r["opponent_policy"] for r in log_rl])
    grid = np.vstack([((code0 & b) > 0) for b in (1, 2, 4, 8)]
                     + [((code1 & b) > 0) for b in (1, 2, 4, 8)]).astype(int)
    heat_ax.imshow(grid, aspect="auto", interpolation="nearest",
                   cmap=ListedColormap(["#e2e8f0", CORAL]),
                   extent=(0, grid.shape[1], 8, 0))
    heat_ax.axhline(4, color="white", lw=3)
    heat_ax.set_yticks(np.arange(8) + 0.5, [f"A0 {s}" for s in states]
                       + [f"A1 {s}" for s in states], fontsize=7)
    heat_ax.set_xlabel("training episode")
    heat_ax.set_title(f"Greedy action per state, seed {SEEDS[0]} (red = discount)")
    heat_ax.grid(False)
    finish(fig, "fig_two_learners.png")


def run_learning_rate(cfg):
    heading("Experiment C: learning rate")
    results, curves = {}, {}
    for lr in (0.01, 0.10, 0.50):
        label = f"alpha={lr:.2f}"
        rows, c, sellers = run_config(cfg, label, lr=lr)
        results[lr], curves[lr] = rows, c
        print(aggregate(label, rows))
        if lr == 0.50:
            append_text(RESULTS / "q_tables.txt",
                        q_table_report(f"alpha=0.50, seed {SEEDS[0]}", sellers[0]))
    save_csv(RESULTS / "learning_rate_per_seed.csv",
             [r for lr in results for r in results[lr]])
    save_csv(RESULTS / "learning_rate_comparison.csv",
             [{"alpha": lr, **aggregate(f"alpha={lr:.2f}", results[lr])} for lr in results])

    plot_learning_rate(cfg, curves, results)
    return results


EXPLORATION_SETTINGS = [
    ("Reference decay 0.20→0.02", (0.20, 0.02, 0.995)),
    ("Fixed ε = 0.05", (0.05, 0.05, 1.0)),
    ("Fixed ε = 0.30", (0.30, 0.30, 1.0)),
    ("Greedy, ε = 0", (0.0, 0.0, 1.0)),
]


def run_exploration(cfg):
    heading("Experiment D: exploration schedules")
    results, curves = {}, {}
    for label, schedule in EXPLORATION_SETTINGS:
        rows, c, _ = run_config(cfg, label, schedule=schedule)
        results[label], curves[label] = rows, c
        print(aggregate(label, rows))
    save_csv(RESULTS / "exploration_per_seed.csv",
             [r for label in results for r in results[label]])
    save_csv(RESULTS / "exploration_comparison.csv",
             [{"epsilon_start": s[0], "epsilon_min": s[1], "epsilon_decay": s[2],
               **aggregate(label, results[label])} for label, s in EXPLORATION_SETTINGS])

    plot_exploration(results)
    return results


def run_fair_comparison(cfg, lr_results, expl_results):
    heading("Experiment E: paired comparison over 10 seeds")
    rule_rows = rule_as_seat0(cfg)
    save_csv(RESULTS / "rule_based_per_seed.csv", rule_rows)

    lineup = [
        ("RL, baseline ($\\alpha=0.10$, decaying $\\varepsilon$)", lr_results[0.10]),
        ("RL, low learning rate ($\\alpha=0.01$)", lr_results[0.01]),
        ("RL, high learning rate ($\\alpha=0.50$)", lr_results[0.50]),
        ("RL, fixed $\\varepsilon=0.05$", expl_results["Fixed ε = 0.05"]),
        ("RL, fixed $\\varepsilon=0.30$", expl_results["Fixed ε = 0.30"]),
        ("RL, greedy $\\varepsilon=0$", expl_results["Greedy, ε = 0"]),
        ("Rule-based", rule_rows),
    ]
    summary_rows, latex_rows = [], []
    for label, rows in lineup:
        s = aggregate(label, rows)
        summary_rows.append(s)
        latex_rows.append([
            label, fmt3(s["eval_mean_reward"]), fmt3(s["eval_std_across_seeds"]),
            fmt3(s["eval_discount_rate"]),
            "--" if label == "Rule-based"
            else f"{s['seeds_with_never_discount_policy']}/10"])
        print(f"{label:<55} mean={s['eval_mean_reward']:.3f}  "
              f"std={s['eval_std_across_seeds']:.3f}  disc={s['eval_discount_rate']:.3f}")
    save_csv(RESULTS / "multi_seed_summary.csv", summary_rows)
    save_latex_table(
        TABLES / "results_table.tex",
        ["Agent / configuration", "Mean reward", "Std.\\ dev.", "Discount rate",
         "``Never discount'' policy"], latex_rows, "lrrrc")

    gaps = [a["eval_mean_reward_per_step"] - b["eval_mean_reward_per_step"]
            for a, b in zip(lr_results[0.10], rule_rows)]
    m, s = mean_std(gaps)
    print(f"Paired gap RL - Rule: mean={m:.3f}  std={s:.3f}")
    save_csv(RESULTS / "paired_difference_rl_minus_rule.csv",
             [{"seed": sd, "difference": g} for sd, g in zip(SEEDS, gaps)])

    # compact LaTeX tables for learning rate and exploration
    lr_stats = {lr: aggregate("", lr_results[lr]) for lr in (0.01, 0.10, 0.50)}
    save_latex_table(
        TABLES / "learning_rate.tex",
        [r"$\alpha$", "Train reward", "Eval.\\ reward", "Eval.\\ std", "Discount rate",
         "``Never discount''", "Policy changes"],
        [[lr, fmt3(st["train_mean_reward"]), fmt3(st["eval_mean_reward"]),
          fmt3(st["eval_std_across_seeds"]), fmt3(st["eval_discount_rate"]),
          f"{st['seeds_with_never_discount_policy']}/10", f"{st['mean_policy_flips']:.1f}"]
         for lr, st in lr_stats.items()], "rrrrrcr")
    ex_stats = {label: aggregate("", expl_results[label]) for label, _ in EXPLORATION_SETTINGS}
    save_latex_table(
        TABLES / "exploration.tex",
        ["Exploration", "Train reward", "Train std", "Eval.\\ reward", "Eval.\\ std",
         "``Never discount''"],
        [[label.replace("ε", "$\\varepsilon$").replace("→", "$\\to$"),
          fmt3(st["train_mean_reward"]), fmt3(st["train_std_across_seeds"]),
          fmt3(st["eval_mean_reward"]), fmt3(st["eval_std_across_seeds"]),
          f"{st['seeds_with_never_discount_policy']}/10"]
         for label, st in ex_stats.items()], "lrrrrc")

    plot_gap_to_rule(lineup)


def run_two_learners(cfg):
    heading("Question 8: two sellers that both learn")
    rows_out, sample = [], None
    for seed in SEEDS:
        _, _, log_rule = train(cfg, seed, opponent="rule")
        a0, a1, log_rl = train(cfg, seed, opponent="rl")
        if sample is None:
            sample = (a0, a1, log_rl)
        pair, _ = evaluate(cfg, a0, a1, seed + EVAL_SEED_SHIFT)
        policy_rule = [r["rl_policy"] for r in log_rule]
        policy_rl = [r["rl_policy"] for r in log_rl]
        rows_out.append({
            "seed": seed,
            "policy_flips_vs_rule": count_policy_changes(policy_rule),
            "policy_flips_vs_learning_rl": count_policy_changes(policy_rl),
            "rl_vs_rl_eval_reward_seat0": pair[0]["mean_reward_per_step"],
            "rl_vs_rl_eval_reward_seat1": pair[1]["mean_reward_per_step"],
            "rl_vs_rl_discount_rate_seat0": pair[0]["discount_action_rate"],
            "rl_vs_rl_discount_rate_seat1": pair[1]["discount_action_rate"],
            "late_flips_vs_rule": count_policy_changes(policy_rule[-2500:]),
            "late_flips_vs_learning_rl": count_policy_changes(policy_rl[-2500:]),
        })
    save_csv(RESULTS / "rl_vs_rl.csv", rows_out)
    append_text(RESULTS / "q_tables.txt",
                q_table_report(f"RL vs RL, seat 0 (seed {SEEDS[0]})", sample[0])
                + q_table_report(f"RL vs RL, seat 1 (seed {SEEDS[0]})", sample[1]))

    summary = {key: mean_std([r[key] for r in rows_out])
               for key in rows_out[0] if key != "seed"}
    for key, (m, s) in summary.items():
        print(f"{key:<35} mean={m:.3f}  std={s:.3f}")
    save_csv(RESULTS / "rl_vs_rl_summary.csv",
             [{"metric": key, "mean": m, "std": s} for key, (m, s) in summary.items()])

    plot_two_learners(rows_out, sample[2])
    return summary


def run_aggressive_market(cfg):
    heading("Question 9: the rival becomes aggressive")
    rows, _, sellers = run_config(cfg, "RL vs Aggressive", opponent="aggressive")
    rule_rows = rule_as_seat0(cfg, opponent="aggressive")

    # the baseline learner, moved unchanged into the new market
    carried = []
    for seed in SEEDS:
        old_hero, _, _ = train(cfg, seed, opponent="rule")
        r, _ = evaluate(cfg, old_hero, AggressiveSeller(), seed + EVAL_SEED_SHIFT)
        carried.append(r[0]["mean_reward_per_step"])

    append_text(RESULTS / "q_tables.txt",
                q_table_report(f"RL trained against the aggressive competitor "
                               f"(seed {SEEDS[0]})", sellers[0]))

    rl_s = aggregate("RL (retrained)", rows)
    rule_s = aggregate("Rule-based", rule_rows)
    c_mean, c_std = mean_std(carried)
    table = [
        {"agent": "RL retrained against the aggressive competitor",
         "eval_mean": rl_s["eval_mean_reward"], "eval_std": rl_s["eval_std_across_seeds"],
         "discount_rate": rl_s["eval_discount_rate"]},
        {"agent": "RL trained on the reference market (not retrained)",
         "eval_mean": c_mean, "eval_std": c_std, "discount_rate": float("nan")},
        {"agent": "Rule-based", "eval_mean": rule_s["eval_mean_reward"],
         "eval_std": rule_s["eval_std_across_seeds"],
         "discount_rate": rule_s["eval_discount_rate"]},
    ]
    save_csv(RESULTS / "modification_aggressive.csv", table)
    save_csv(RESULTS / "modification_aggressive_per_seed.csv", rows + rule_rows)
    for r in table:
        print(r)
    save_latex_table(
        TABLES / "modification.tex",
        ["Agent in seat 0 (opponent: aggressive competitor)", "Mean reward",
         "Std.\\ dev.", "Discount rate"],
        [[r["agent"], fmt3(r["eval_mean"]), fmt3(r["eval_std"]),
          "--" if np.isnan(r["discount_rate"]) else fmt3(r["discount_rate"])]
         for r in table], "lrrr")
    gaps = [a["eval_mean_reward_per_step"] - b["eval_mean_reward_per_step"]
            for a, b in zip(rows, rule_rows)]
    m, s = mean_std(gaps)
    print(f"Paired gap RL - Rule (aggressive market): mean={m:.3f}  std={s:.3f}")
    save_csv(RESULTS / "modification_paired_difference.csv",
             [{"seed": sd, "difference": g} for sd, g in zip(SEEDS, gaps)])
    return table


ROBUSTNESS_RIVALS = ["rule", "aggressive", "tit_for_tat", "always_discount", "random"]
RIVAL_TITLES = ["Rule", "Aggressive", "Tit-for-tat", "Always discount", "Random"]


def run_robustness(cfg):
    heading("Question 10: robustness against a pool of rivals")
    candidates = {
        "Rule-based": lambda seed: RuleSeller(),
        "RL baseline (trained vs rule)":
            lambda seed: train(cfg, seed, opponent="rule")[0],
        "RL + opponent pool + α=1/N":
            lambda seed: train(cfg, seed, step_rule="visit",
                               opponent_pool=ROBUSTNESS_RIVALS)[0],
        "Improved RL (+ own previous action in state)":
            lambda seed: train(cfg, seed, step_rule="visit",
                               opponent_pool=ROBUSTNESS_RIVALS, memory=True)[0],
    }
    records = []
    for name, build in candidates.items():
        for seed in SEEDS:
            seller = build(seed)
            for rival_name in ROBUSTNESS_RIVALS:
                r, _ = evaluate(cfg, seller, build_rival(rival_name, seed + 1),
                                seed + EVAL_SEED_SHIFT + 1)
                records.append({"agent": name, "seed": seed, "opponent": rival_name,
                                "eval_mean_reward_per_step": r[0]["mean_reward_per_step"],
                                "discount_rate": r[0]["discount_action_rate"]})
    save_csv(RESULTS / "robustness_per_seed.csv", records)

    summary, latex_rows = [], []
    for name in candidates:
        cells, means = [name.replace("α=1/N", "$\\alpha=1/N$")], []
        for rival_name in ROBUSTNESS_RIVALS:
            vals = [r["eval_mean_reward_per_step"] for r in records
                    if r["agent"] == name and r["opponent"] == rival_name]
            m, s = mean_std(vals)
            summary.append({"agent": name, "opponent": rival_name, "mean": m, "std": s})
            cells.append(f"{m:.2f} $\\pm$ {s:.2f}")
            means.append(m)
        cells += [f"{np.mean(means):.2f}", f"{np.min(means):.2f}"]
        latex_rows.append(cells)

    # Best response computed from the model: never discounting is optimal against
    # the three reactive rivals; against stateless ones, maximise per demand level.
    best = [35.0, 30.0, 35.0]
    for p_disc in (1.0, 0.5):                         # always-discount, random
        value = 0.0
        for d in range(2):
            value += 0.5 * max(p_disc * expected_profit(cfg, d, a, 1)
                               + (1 - p_disc) * expected_profit(cfg, d, a, 0)
                               for a in range(2))
        best.append(value)
    latex_rows.append(["Best response (from the model)"] + [f"{b:.2f}" for b in best]
                      + [f"{np.mean(best):.2f}", f"{np.min(best):.2f}"])
    summary += [{"agent": "Best response (model)", "opponent": o, "mean": b, "std": 0.0}
                for o, b in zip(ROBUSTNESS_RIVALS, best)]
    save_csv(RESULTS / "robustness_summary.csv", summary)
    for r in summary:
        print(f"{r['agent']:<46} vs {r['opponent']:<16} {r['mean']:.3f} ± {r['std']:.3f}")
    save_latex_table(
        TABLES / "robustness.tex",
        ["Agent", "Rule", "Aggressive", "Tit-for-tat", "Always disc.", "Random",
         "Average", "Worst"], latex_rows, "lrrrrrrr")
    plot_robustness(summary, list(candidates), best)


def plot_robustness(summary, agent_names, best):
    """Dot plot: mean reward (± std) of every seller against every rival."""
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    short = ["Rule-based", "RL baseline", "RL + pool + α=1/N", "RL + own last action"]
    for j, name in enumerate(agent_names):
        for i, rival in enumerate(ROBUSTNESS_RIVALS):
            entry = next(r for r in summary if r["agent"] == name and r["opponent"] == rival)
            ax.errorbar(entry["mean"], i + (j - 1.5) * 0.17, xerr=entry["std"], fmt="o",
                        color=SERIES[j], ms=6, capsize=2, label=short[j] if i == 0 else None)
    ax.scatter(best, range(len(best)), marker="D", s=70, facecolor="none",
               edgecolor="black", lw=1.4, zorder=4, label="best response (model)")
    ax.set_yticks(range(len(ROBUSTNESS_RIVALS)), RIVAL_TITLES)
    ax.invert_yaxis()
    ax.grid(axis="y", alpha=0.0)
    ax.grid(axis="x", alpha=1.0)
    ax.set_xlabel("reward per step (dot = mean, bar = ± std over 10 seeds)")
    ax.set_title("How close each seller gets to the best response, by rival")
    ax.legend(fontsize=8, loc="lower left")
    finish(fig, "fig_robustness_dots.png")


# ----------------------------------------------------------------------------
# 9. Command line
# ----------------------------------------------------------------------------

OPTIONAL_PARTS = {
    "two_learners": run_two_learners,
    "aggressive": run_aggressive_market,
    "robustness": run_robustness,
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Agent 02: Q-learning seller vs rule-based seller")
    parser.add_argument("--only", nargs="+", choices=sorted(OPTIONAL_PARTS),
                        help="re-run only these extra studies (skips experiments A-E)")
    args = parser.parse_args(argv)

    cfg = Settings()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")     # Windows consoles default to cp1252
    for folder in (RESULTS, FIGURES, TABLES):
        folder.mkdir(parents=True, exist_ok=True)

    heading("AGENT 02 | Q-learning seller vs rule-based seller", "=")
    print(cfg)
    print("seeds:", SEEDS)
    print("results folder:", RESULTS)

    if not args.only:
        (RESULTS / "q_tables.txt").unlink(missing_ok=True)
        run_expected_profit(cfg)
        run_baseline(cfg)
        lr_results = run_learning_rate(cfg)
        expl_results = run_exploration(cfg)
        run_fair_comparison(cfg, lr_results, expl_results)
    for name, part in OPTIONAL_PARTS.items():
        if not args.only or name in args.only:
            part(cfg)

    print("\nDone. Everything was written to", RESULTS)


if __name__ == "__main__":
    main()
