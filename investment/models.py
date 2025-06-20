import random
from otree.api import BaseConstants, BaseSubsession, BaseGroup, BasePlayer, models, widgets

class Constants(BaseConstants):
    name_in_url       = 'investment'
    players_per_group = None
    # 20 investment frames + 1 survey + 10 numeracy + 1 thank you = 32 rounds
    num_rounds        = 32

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

# --- Baseline PROBS & PAYMENTS ---
PROBS_BASE = {
    "crypto": (0.20, 0.10, 0.70),
    "equity": (0.50, 0.20, 0.30),
    "bond":   (0.80, 0.10, 0.10),
}
PAYMENTS_BASE = {
    "crypto": (9.50, -2.00, -0.50),
    "equity": (4.00, -1.80, -0.50),
    "bond":   (2.50,  0.00, -0.50),
}

# --- Your Four Additional Scenarios ---
SCENARIOS = [
    {
        "name": "Baseline",
        "PROBS": PROBS_BASE,
        "PAYMENTS": PAYMENTS_BASE,
    },
    {
        "name": "Szenario 1",
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
        "name": "Szenario 2",
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
        "name": "Szenario 3",
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
        "name": "Szenario 4",
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

# --- Label maps ---
ASSET_LABEL_MAP = {
    "crypto": "Asset A",
    "equity": "Asset B",
    "bond":   "Asset C",
}
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


def init_participant(pid, seed=None):
    rng = random.Random(seed or pid)
    label_bags = {k: rng.sample(v, len(v)) for k, v in LABELS.items()}
    return {"rng": rng, "label_bags": label_bags}


def next_label(state, ac):
    bag = state["label_bags"][ac]
    if not bag:
        bag[:] = state["rng"].sample(LABELS[ac], len(LABELS[ac]))
    return bag.pop()


def make_frames(state):
    rng = state["rng"]
    frames = []

    # 1) Blind, no scale (5 rounds)
    for scen in SCENARIOS:
        order = rng.sample(list(scen["PROBS"].keys()), k=3)
        cols = [{
            "asset_class": ac,
            "display_name": ASSET_LABEL_MAP[ac],
            "probs":        scen["PROBS"][ac],
            "payoffs":      scen["PAYMENTS"][ac],
        } for ac in order]
        frames.append({"frame": "blind", "columns": cols})

    # 2) Blind, scale (5 rounds)
    for scen, m in zip(SCENARIOS, MULTIPLIERS):
        order = rng.sample(list(scen["PROBS"].keys()), k=3)
        cols = [{
            "asset_class": ac,
            "display_name": ASSET_LABEL_MAP[ac],
            "probs":        scen["PROBS"][ac],
            "payoffs":      tuple(round(x * m, 2) for x in scen["PAYMENTS"][ac]),
        } for ac in order]
        frames.append({"frame": "blind", "columns": cols})

    # 3) Named, no scale (5 rounds)
    for scen in SCENARIOS:
        order = rng.sample(list(scen["PROBS"].keys()), k=3)
        cols = [{
            "asset_class": ac,
            "display_name": f"{next_label(state, ac)} ({ac.title()})",
            "probs":        scen["PROBS"][ac],
            "payoffs":      scen["PAYMENTS"][ac],
        } for ac in order]
        frames.append({"frame": "named", "columns": cols})

    # 4) Named, scale (5 rounds)
    for scen, m in zip(SCENARIOS, MULTIPLIERS):
        order = rng.sample(list(scen["PROBS"].keys()), k=3)
        cols = [{
            "asset_class": ac,
            "display_name": f"{next_label(state, ac)} ({ac.title()})",
            "probs":        scen["PROBS"][ac],
            "payoffs":      tuple(round(x * m, 2) for x in scen["PAYMENTS"][ac]),
        } for ac in order]
        frames.append({"frame": "named", "columns": cols})

    # Assign round numbers 1–20
    for i, f in enumerate(frames, start=1):
        f["round"] = i

    return frames


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
    choice      = models.StringField()

    fam_crypto  = models.IntegerField(
        label="How familiar are you with cryptocurrencies?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal)
    fam_equity  = models.IntegerField(
        label="How familiar are you with equities (e.g., stocks)?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal)
    fam_bond    = models.IntegerField(
        label="How familiar are you with bonds (e.g., government or corporate)?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal)
    risk_crypto = models.IntegerField(
        label="How financially risky do you consider cryptocurrencies to be?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal)
    risk_equity = models.IntegerField(
        label="How financially risky do you consider equities to be?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal)
    risk_bond   = models.IntegerField(
        label="How financially risky do you consider bonds to be?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal)

    # Numeracy fields
    numq_1   = models.IntegerField(blank=True)
    numq_2   = models.IntegerField(blank=True)
    numq_3   = models.IntegerField(blank=True)
    numq_4   = models.IntegerField(blank=True)
    numq_5   = models.IntegerField(blank=True)
    numq_6   = models.IntegerField(blank=True)
    numq_7   = models.IntegerField(blank=True)
    numq_8   = models.IntegerField(blank=True)
    numq_9   = models.IntegerField(blank=True)
    numq_10  = models.IntegerField(blank=True)
