# models.py

import random
from otree.api import BaseConstants, BaseSubsession, BaseGroup, BasePlayer, models, widgets

class Constants(BaseConstants):
    name_in_url = 'investment'
    players_per_group = None
    # Total rounds/pages:
    # 1 Consent + 1 Instructions + 20 Investment + 1 Survey
    # + 1 Numeracy Intro + 10 Numeracy + 1 Thank You = 35
    num_rounds = 35

# --- Numeracy Test Questions ---
NUMERACY_QUESTIONS = [
    "25% of 80 students passed an exam. How many students is that?",
    "A product costs €200. A 50% discount is applied. What is the discount amount?",
    "8 out of 40 bulbs are faulty. What percentage are faulty?",
    "A fair 6-sided die is rolled 60 times. How many times is a 6 expected?",
    "A train is on time 19 days out of 20. Over 100 days, how many days is it late?",
    "If 6 out of 30 raffle tickets win a prize, how many winning tickets are expected out of 150?",
    "4 out of 100 deliveries arrive late. If the company improves its service and cuts the delay rate in half, how many late deliveries are expected out of 100?",
    "A city has 2,000 buses. 15% are electric. How many buses are not electric?",
    "60% of people have smartphones. Of those, 50% use Android. What percent of all people use Android?",
    "In a survey of 1,000 people, 40% drink coffee. Of those, 25% prefer espresso. How many people prefer espresso?",
]

# --- Scenario Definitions (5 scenarios, each yields 5 frames per block, 4 blocks total = 20 decision rounds) ---
SCENARIOS = [
    {
        "name": "Scenario 1",
        "PROBS": {
            "crypto": (0.20, 0.10, 0.70),
            "equity": (0.50, 0.20, 0.30),
            "bond":   (0.80, 0.10, 0.10),
        },
        "PAYMENTS": {
            "crypto": (9.50, -2.00, -0.50),
            "equity": (4.00, -1.80, -0.50),
            "bond":   (2.50,  0.00, -0.50),
        },
    },
    {
        "name": "Scenario 2",
        "PROBS": {
            "bond":   (0.80, 0.10, 0.10),
            "equity": (0.50, 0.30, 0.20),
            "crypto": (0.15, 0.10, 0.75),
        },
        "PAYMENTS": {
            "bond":   (2.60,  -0.40, -0.20),
            "equity": (3.80,  -1.80, -0.50),
            "crypto": (10.50, -2.50, -0.50),
        },
    },
    {
        "name": "Scenario 3",
        "PROBS": {
            "bond":   (0.85, 0.10, 0.05),
            "equity": (0.50, 0.30, 0.20),
            "crypto": (0.15, 0.10, 0.75),
        },
        "PAYMENTS": {
            "bond":   (2.40,   0.00, -0.50),
            "equity": (4.00,  -1.50, -0.50),
            "crypto": (10.00, -2.50, -0.50),
        },
    },
    {
        "name": "Scenario 4",
        "PROBS": {
            "bond":   (0.90, 0.05, 0.05),
            "equity": (0.45, 0.30, 0.25),
            "crypto": (0.10, 0.15, 0.75),
        },
        "PAYMENTS": {
            "bond":   (2.20,   0.00, -0.50),
            "equity": (4.50,  -1.80, -0.50),
            "crypto": (11.00, -2.00, -0.50),
        },
    },
    {
        "name": "Scenario 5",
        "PROBS": {
            "bond":   (0.75, 0.20, 0.05),
            "equity": (0.50, 0.30, 0.20),
            "crypto": (0.15, 0.10, 0.75),
        },
        "PAYMENTS": {
            "bond":   (2.50,   0.00, -0.50),
            "equity": (3.80,  -1.80, -0.50),
            "crypto": (10.50, -2.50, -0.50),
        },
    },
]

# --- Fixed multipliers for Rounds 6–10 & 16–20 ---
MULTIPLIERS = [0.25, 2, 5, 7, 9.5]

assert len(SCENARIOS) == len(MULTIPLIERS), "SCENARIOS and MULTIPLIERS must be the same length"

# --- Label pools for named frames ---
LABELS = {
    "crypto": [
        "Zypherium (ZPH, Cryptocurrency)",
        "Quantacoin (QTC, Cryptocurrency)",
        "Nebulite (NBL, Cryptocurrency)",
        "Fintara (FTR, Cryptocurrency)",
        "OrbisX (OBX, Cryptocurrency)",
    ],
    "equity": [
        "Luminex Corp. (LMX, Equity)",
        "Vireon Systems (VRN, Equity)",
        "Heliox Dynamics (HLX, Equity)",
        "Trionex Ltd. (TRX, Equity)",
        "Aurelia Group (AUR, Equity)",
    ],
    "bond": [
        "Bayern 12Y (Bayern, Bond)",
        "Sachsen 6Y (Sachsen, Bond)",
        "Hessen 3Y (Hessen, Bond)",
        "Nordrhein-Westfalen 9Y (Nordrhein-Westfalen, Bond)",
        "Berlin 5Y (Berlin, Bond)",
    ],
}

ASSET_LABEL_MAP = {
    "crypto": "Asset A",
    "equity": "Asset B",
    "bond":   "Asset C",
}


def init_participant(pid, seed=None):
    rng = random.Random(seed or pid)
    label_bags = {k: rng.sample(v, len(v)) for k, v in LABELS.items()}
    frame_order = rng.choice([("blind", "named"), ("named", "blind")])
    return {"rng": rng, "label_bags": label_bags, "frame_order": frame_order}


def next_label(state, asset_class):
    bag = state["label_bags"][asset_class]
    if not bag:
        bag[:] = state["rng"].sample(LABELS[asset_class], len(LABELS[asset_class]))
    return bag.pop()


def make_frames(state):
    rng = state["rng"]
    blind_noscale = []
    blind_scale = []
    named_noscale = []
    named_scale = []

    # 1) Blind, no scale
    for scen in SCENARIOS:
        order = rng.sample(list(scen["PROBS"].keys()), 3)
        cols = [{
            "asset_class": ac,
            "display_name": ASSET_LABEL_MAP[ac],
            "probs": scen["PROBS"][ac],
            "payoffs": scen["PAYMENTS"][ac],
        } for ac in order]
        blind_noscale.append({
            "frame":            "blind",
            "scenario_name":    scen["name"],
            "scale_multiplier": 1.0,
            "columns":          cols,
        })

    # 2) Blind, scaled
    for scen, m in zip(SCENARIOS, MULTIPLIERS):
        order = rng.sample(list(scen["PROBS"].keys()), 3)
        cols = [{
            "asset_class": ac,
            "display_name": ASSET_LABEL_MAP[ac],
            "probs": scen["PROBS"][ac],
            "payoffs": tuple(round(x * m, 2) for x in scen["PAYMENTS"][ac]),
        } for ac in order]
        blind_scale.append({
            "frame":            "blind",
            "scenario_name":    scen["name"],
            "scale_multiplier": m,
            "columns":          cols,
        })

    # 3) Named, no scale
    for scen in SCENARIOS:
        order = rng.sample(list(scen["PROBS"].keys()), 3)
        cols = [{
            "asset_class": ac,
            "display_name": next_label(state, ac),
            "probs": scen["PROBS"][ac],
            "payoffs": scen["PAYMENTS"][ac],
        } for ac in order]
        named_noscale.append({
            "frame":            "named",
            "scenario_name":    scen["name"],
            "scale_multiplier": 1.0,
            "columns":          cols,
        })

    # 4) Named, scaled
    for scen, m in zip(SCENARIOS, MULTIPLIERS):
        order = rng.sample(list(scen["PROBS"].keys()), 3)
        cols = [{
            "asset_class": ac,
            "display_name": next_label(state, ac),
            "probs": scen["PROBS"][ac],
            "payoffs": tuple(round(x * m, 2) for x in scen["PAYMENTS"][ac]),
        } for ac in order]
        named_scale.append({
            "frame":            "named",
            "scenario_name":    scen["name"],
            "scale_multiplier": m,
            "columns":          cols,
        })

    first, second = state["frame_order"]
    block_map = {
        "blind": blind_noscale + blind_scale,
        "named": named_noscale + named_scale,
    }
    combined = block_map[first] + block_map[second]

    # assign display rounds 1–20
    for i, frame in enumerate(combined, start=1):
        frame["round"] = i

    return combined


def generate_participant_tables(pid, seed=None):
    state = init_participant(pid, seed)
    return make_frames(state)


class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            p.participant.vars["frame_data"] = generate_participant_tables(
                p.participant.id_in_session
            )


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choice = models.StringField()

    # New metadata fields for CSV export
    scenario_name    = models.StringField()
    scale_multiplier = models.FloatField()
    frame_type       = models.StringField()

    def choice_choices(self):
        frame_index = self.round_number - 3
        frames = self.participant.vars.get("frame_data", [])
        if 0 <= frame_index < len(frames):
            frame = frames[frame_index]
            return [(col["asset_class"], col["display_name"]) for col in frame["columns"]]
        return []

    fam_crypto = models.IntegerField(
        label="How familiar are you with cryptocurrencies?",
        choices=list(range(1, 8)),
        widget=widgets.RadioSelectHorizontal,
    )
    fam_equity = models.IntegerField(
        label="How familiar are you with equities (e.g., stocks)?",
        choices=list(range(1, 8)),
        widget=widgets.RadioSelectHorizontal,
    )
    fam_bond = models.IntegerField(
        label="How familiar are you with bonds (e.g., government or corporate)?",
        choices=list(range(1, 8)),
        widget=widgets.RadioSelectHorizontal,
    )
    risk_crypto = models.IntegerField(
        label="How financially risky do you consider cryptocurrencies to be?",
        choices=list(range(1, 8)),
        widget=widgets.RadioSelectHorizontal,
    )
    risk_equity = models.IntegerField(
        label="How financially risky do you consider equities to be?",
        choices=list(range(1, 8)),
        widget=widgets.RadioSelectHorizontal,
    )
    risk_bond = models.IntegerField(
        label="How financially risky do you consider bonds to be?",
        choices=list(range(1, 8)),
        widget=widgets.RadioSelectHorizontal,
    )

    numq_1  = models.IntegerField(blank=True)
    numq_2  = models.IntegerField(blank=True)
    numq_3  = models.IntegerField(blank=True)
    numq_4  = models.IntegerField(blank=True)
    numq_5  = models.IntegerField(blank=True)
    numq_6  = models.IntegerField(blank=True)
    numq_7  = models.IntegerField(blank=True)
    numq_8  = models.IntegerField(blank=True)
    numq_9  = models.IntegerField(blank=True)
    numq_10 = models.IntegerField(blank=True)
