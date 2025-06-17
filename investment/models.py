from otree.api import (
    BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    models
)
import random

class Constants(BaseConstants):
    name_in_url = 'investment'
    players_per_group = None
    num_rounds = 20  # 10 Runden × 2 Frames

# Basisdaten
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
    "crypto": ["Bitcoin", "Ethereum", "Solana", "Avalanche", "Dogecoin"],
    "equity": ["AAPL", "NVDA", "MSFT", "TSLA", "AMZN"],
    "bond":   ["US Treasury 10 Y", "Bund 5 Y", "UK Gilt 2 Y", "OAT 8 Y", "JGB 3 Y"],
}

def init_participant(pid, seed=None):
    rng = random.Random(seed or pid)
    frame_order = rng.choice([("blind","named"), ("named","blind")])
    label_bags = {k: rng.sample(v, len(v)) for k, v in LABELS.items()}
    return {"rng": rng, "frame_order": frame_order, "label_bags": label_bags}

def next_label(state, asset_class):
    bag = state["label_bags"][asset_class]
    if not bag:
        bag[:] = state["rng"].sample(LABELS[asset_class], len(LABELS[asset_class]))
    return bag.pop()

def build_lotteries(state):
    rng = state["rng"]
    rounds = []
    # Runden 1–5
    for _ in range(5):
        row = {
            ac: {
                "probs":   PROBS[ac],
                "payoffs": PAYMENTS[ac],
                "label":   next_label(state, ac),
            }
            for ac in ("crypto","equity","bond")
        }
        rounds.append(row)
    # Runden 6–10
    for _ in range(5):
        s = rng.uniform(0.85, 1.20)
        row = {
            ac: {
                "probs":   PROBS[ac],
                "payoffs": tuple(round(p * s, 2) for p in PAYMENTS[ac]),
                "label":   next_label(state, ac),
            }
            for ac in ("crypto","equity","bond")
        }
        rounds.append(row)
    return rounds

def make_frames(state, lotteries):
    rng = state["rng"]
    frames = []
    for round_idx, spec in enumerate(lotteries, start=1):
        orders = [rng.sample(["crypto","equity","bond"], 3) for _ in range(2)]
        for frame_name, order in zip(state["frame_order"], orders):
            cols = []
            for ac in order:
                cols.append({
                    "asset_class":   ac,
                    "display_name": (
                        ac.title()
                        if frame_name == "blind"
                        else spec[ac]["label"]
                    ),
                    "probs":   spec[ac]["probs"],
                    "payoffs": spec[ac]["payoffs"],
                })
            frames.append({
                "round":   round_idx,
                "frame":   frame_name,
                "columns": cols,
            })
    return frames

def generate_participant_tables(pid, seed=None):
    state     = init_participant(pid, seed)
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
    choice = models.StringField()
