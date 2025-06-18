import random
from otree.api import (
    BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    models, widgets
)

class Constants(BaseConstants):
    name_in_url       = 'investment'
    players_per_group = None
    num_rounds        = 34  # 10 blind + 10 named + 1 survey + 10 numeracy + 1 thank you

# Basic lottery parameters
PROBS = {
    "crypto": (0.20, 0.10, 0.70),
    "equity": (0.50, 0.20, 0.30),
    "bond":   (0.80, 0.10, 0.10),
}
PAYMENTS = {
    "crypto": (9.50, 2.00, 0.50),
    "equity": (4.00, 1.80, 0.50),
    "bond":   (2.50, 1.00, 0.50),
}
LABELS = {
    "crypto": ["Bitcoin","Ethereum","Solana","Avalanche","Dogecoin"],
    "equity": ["AAPL","NVDA","MSFT","TSLA","AMZN"],
    "bond":   ["US Treasury 10 Y","Bund 5 Y","UK Gilt 2 Y","OAT 8 Y","JGB 3 Y"],
}

ASSET_LABEL_MAP = {
    "crypto": "Asset A",
    "equity": "Asset B",
    "bond":   "Asset C",
}

# Numeracy questions
NUMERACY_QUESTIONS = [
    "Out of 100 people, 5% have a rare disease. How many people is that?",
    "Out of 1,000 passengers, 2% have a ticket. How many passengers is that?",
    "In an urn there are 50 balls, 20% of them are red. How many red balls?",
    "A test has a hit rate of 90%. How many correct results out of 100 tests?",
    "5% of €200 is how many euros?",
    "20% of 150 is how much?",
    "Out of 500 participants, 10% remain. How many participants?",
    "If 0.5% of the population is 1% of a group, how many percent remain?",
    "8% of 125 equals how much?",
    "Out of 250 people, 4% have blue eyes. How many people?"
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
    """Build 10 rounds of lottery specs (first 5 fixed, next 5 scaled)."""
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
    # Rounds 6–10: scaled payoffs
    for _ in range(5):
        s = rng.uniform(0.85, 1.20)
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
    """
    First build 10 blind frames (random order but fixed Asset A/B/C labels),
    then 10 named frames (random order with real labels).
    """
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
    # Investment choice
    choice      = models.StringField()

    # Post-experiment survey
    fam_crypto  = models.IntegerField(
        label="How familiar are you with Crypto?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal
    )
    fam_equity  = models.IntegerField(
        label="How familiar are you with Equities?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal
    )
    fam_bond    = models.IntegerField(
        label="How familiar are you with Bonds?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal
    )
    risk_crypto = models.IntegerField(
        label="How do you assess the risk of Crypto?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal
    )
    risk_equity = models.IntegerField(
        label="How do you assess the risk of Equities?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal
    )
    risk_bond   = models.IntegerField(
        label="How do you assess the risk of Bonds?",
        choices=list(range(1, 8)), widget=widgets.RadioSelectHorizontal
    )

    # Numeracy test
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
