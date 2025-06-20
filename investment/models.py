import random
from otree.api import (
    BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    models, widgets
)

class Constants(BaseConstants):
    name_in_url       = 'investment'
    players_per_group = None
    # 10 blind + 10 named + 1 consent + 1 instructions + 1 survey +
    # 1 intro + 10 numeracy + 1 thank you = 35 rounds
    num_rounds        = 35

# Basic lottery parameters
PROBS = {
    "crypto": (0.20, 0.10, 0.70),
    "equity": (0.50, 0.20, 0.30),
    "bond":   (0.80, 0.10, 0.10),
}
PAYMENTS = {
    "crypto": (9.50, -2.00, -0.50),
    "equity": (4.00, -1.80, -0.50),
    "bond":   (2.50, 0.00, -0.50),
}

# Expanded descriptive labels
LABELS = {
    "crypto": [
        "Bitcoin (BTC, Cryptocurrency)",
        "Ethereum (ETH, Cryptocurrency)",
        "Solana (SOL, Cryptocurrency)",
        "Avalanche (AVAX, Cryptocurrency)",
        "Dogecoin (DOGE, Cryptocurrency)",
    ],
    "equity": [
        "Apple Inc. (AAPL, Equity)",
        "NVIDIA Corp. (NVDA, Equity)",
        "Microsoft Corp. (MSFT, Equity)",
        "Tesla Inc. (TSLA, Equity)",
        "Amazon.com Inc. (AMZN, Equity)",
    ],
    "bond": [
        "US Treasury 10Y (US, Bond)",
        "Bund 5Y (Germany, Bond)",
        "UK Gilt 2Y (UK, Bond)",
        "OAT 8Y (France, Bond)",
        "JGB 3Y (Japan, Bond)",
    ],
}

ASSET_LABEL_MAP = {
    "crypto": "Asset A",
    "equity": "Asset B",
    "bond":   "Asset C",
}

# Updated numeracy questions
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
    "In a survey of 1,000 people, 40% drink coffee. Of those, 25% prefer espresso. How many people prefer espresso?"
]

def init_participant(pid, seed=None):
    rng = random.Random(seed or pid)
    label_bags = {k: rng.sample(v, len(v)) for k, v in LABELS.items()}
    return {"rng": rng, "label_bags": label_bags}

def next_label(state, asset_class):
    bag = state["label_bags"][asset_class]
    if not bag:
        bag[:] = state["rng"].sample(LABELS[asset_class], len(LABELS[asset_class]))
    return bag.pop()

def build_lotteries(state):
    rng = state["rng"]
    rounds = []
    # Rounds 1–5: fixed payoffs
    for _ in range(5):
        spec = {
            ac: {
                "probs":   PROBS[ac],
                "payoffs": PAYMENTS[ac],
                "label":   next_label(state, ac),
            }
            for ac in PROBS
        }
        rounds.append(spec)
    # Rounds 6–10: scaled payoffs with fixed multipliers
    for s in [0.25, 2, 5, 7, 9.5]:
        spec = {
            ac: {
                "probs":   PROBS[ac],
                "payoffs": tuple(round(p * s, 2) for p in PAYMENTS[ac]),
                "label":   next_label(state, ac),
            }
            for ac in PROBS
        }
        rounds.append(spec)
    return rounds

def make_frames(state, lotteries):
    frames = []
    rng = state["rng"]

    # 10 blind frames
    for spec in lotteries:
        order = rng.sample(list(PROBS), k=3)
        cols = []
        for ac in order:
            cols.append({
                "asset_class": ac,
                "display_name": ASSET_LABEL_MAP[ac],
                "probs":       spec[ac]["probs"],
                "payoffs":     spec[ac]["payoffs"],
            })
        frames.append({"frame": "blind", "columns": cols})

    # 10 named frames
    for spec in lotteries:
        order = rng.sample(list(PROBS), k=3)
        cols = []
        for ac in order:
            cols.append({
                "asset_class": ac,
                "display_name": f"{spec[ac]['label']} ({ac.title()})",
                "probs":       spec[ac]["probs"],
                "payoffs":     spec[ac]["payoffs"],
            })
        frames.append({"frame": "named", "columns": cols})

    # assign round numbers 1–20
    for i, f in enumerate(frames, start=1):
        f["round"] = i

    return frames

def generate_participant_tables(pid, seed=None):
    state = init_participant(pid, seed)
    lotteries = build_lotteries(state)
    return make_frames(state, lotteries)

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
