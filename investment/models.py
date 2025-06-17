import random, math
from otree.api import (
    BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    models, widgets
)

class Constants(BaseConstants):
    name_in_url       = 'investment'
    players_per_group = None
    # 20 Investment + 1 Survey + 10 Numeracy + 1 ThankYou = 32 Runden
    num_rounds        = 32

# Lotterie-Grunddaten
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

# SVG-Einstellungen
SVG_SIZE     = 416
CENTER       = SVG_SIZE/2
RADIUS       = 104
INNER_RADIUS = RADIUS*0.4
OUTCOME_COLORS = ["#2196F3","#FFC107","#9E9E9E"]

# Berlin Numeracy Test Fragen
NUMERACY_QUESTIONS = [
    "Von 100 Personen haben 5 % eine seltene Krankheit. Wie viele Personen sind das?",
    "Aus 1 000 Fahrgästen haben 2 % einen Fahrschein. Wie viele Fahrgäste sind das?",
    "In einer Urne liegen 50 Kugeln, 20 % davon rot. Wie viele rote Kugeln?",
    "Ein Test hat eine Trefferquote von 90 %. Wie viele richtige Ergebnisse bei 100 Tests?",
    "5 % von 200 € sind wie viel Euro?",
    "20 % von 150 sind wie viel?",
    "Aus 500 Teilnehmern bestehen 10 %. Wie viele Teilnehmer?",
    "Wenn 0,5 % der Bevölkerung 1 % einer Gruppe sind, wie viel Prozent bleiben übrig?",
    "8 % von 125 ergeben wie viel?",
    "Von 250 Personen haben 4 % blaue Augen. Wie viele Personen?"
]

def init_participant(pid, seed=None):
    rng = random.Random(seed or pid)
    frame_order = rng.choice([("blind","named"),("named","blind")])
    label_bags = {k:rng.sample(v,len(v)) for k,v in LABELS.items()}
    return {"rng":rng,"frame_order":frame_order,"label_bags":label_bags}

def next_label(state, ac):
    bag = state["label_bags"][ac]
    if not bag:
        bag[:] = state["rng"].sample(LABELS[ac], len(LABELS[ac]))
    return bag.pop()

def build_lotteries(state):
    rng = state["rng"]
    rounds = []
    # Runden 1–5: feste Payoffs
    for _ in range(5):
        row = {
            ac:{
                "probs": PROBS[ac],
                "payoffs": PAYMENTS[ac],
                "label": next_label(state,ac)
            }
            for ac in ("crypto","equity","bond")
        }
        rounds.append(row)
    # Runden 6–10: skalierte Payoffs
    for _ in range(5):
        s = rng.uniform(0.85,1.20)
        row = {
            ac:{
                "probs": PROBS[ac],
                "payoffs": tuple(round(p*s,2) for p in PAYMENTS[ac]),
                "label": next_label(state,ac)
            }
            for ac in ("crypto","equity","bond")
        }
        rounds.append(row)
    return rounds

def make_frames(state, lotteries):
    frames = []
    for idx,spec in enumerate(lotteries, start=1):
        orders = [state["rng"].sample(["crypto","equity","bond"],3) for _ in range(2)]
        for f_idx,frame_name in enumerate(state["frame_order"]):
            cols = []
            for c_i,ac in enumerate(orders[f_idx]):
                cols.append({
                    "asset_class": ac,
                    "display_name": (
                        f"Asset {chr(65+c_i)}"
                        if frame_name=="blind"
                        else f"{spec[ac]['label']} ({ac.title()})"
                    ),
                    "probs": spec[ac]["probs"],
                    "payoffs": spec[ac]["payoffs"],
                })
            frames.append({"round":idx,"frame":frame_name,"columns":cols})
    return frames

def generate_participant_tables(pid, seed=None):
    state = init_participant(pid, seed)
    return make_frames(state, build_lotteries(state))

def get_segments(probs, payoffs):
    segments = []
    start = 0.0
    for i,p in enumerate(probs):
        angle = p*360
        end = start+angle
        sr, er = math.radians(start-90), math.radians(end-90)
        x1 = CENTER+RADIUS*math.cos(sr)
        y1 = CENTER+RADIUS*math.sin(sr)
        x2 = CENTER+RADIUS*math.cos(er)
        y2 = CENTER+RADIUS*math.sin(er)
        large_arc = 1 if angle>=180 else 0
        path = f"M{CENTER},{CENTER} L{x1:.2f},{y1:.2f} A{RADIUS},{RADIUS} 0 {large_arc} 1 {x2:.2f},{y2:.2f} Z"
        mid = start+angle/2
        mr = math.radians(mid-90)
        lx = CENTER+(RADIUS+10)*math.cos(mr)
        ly = CENTER+(RADIUS+10)*math.sin(mr)
        tx = CENTER+(RADIUS+15)*math.cos(mr)
        ty = CENTER+(RADIUS+15)*math.sin(mr)
        anchor = "start" if math.cos(mr)>=0 else "end"
        segments.append({
            "path": path, "color": OUTCOME_COLORS[i],
            "label": f"{int(p*100)}% → €{payoffs[i]:.2f}",
            "line_x": f"{lx:.2f}", "line_y": f"{ly:.2f}",
            "text_x": f"{tx:.2f}", "text_y": f"{ty:.2f}",
            "text_anchor": anchor, "text_color": "#000"
        })
        start = end
    return segments

class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            p.participant.vars["frame_data"] = generate_participant_tables(p.participant.id_in_session)

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    choice      = models.StringField()

    # Survey
    fam_crypto  = models.IntegerField(label="Wie vertraut sind Sie mit Crypto?",
        choices=list(range(1,8)), widget=widgets.RadioSelectHorizontal)
    fam_equity  = models.IntegerField(label="Wie vertraut sind Sie mit Equities?",
        choices=list(range(1,8)), widget=widgets.RadioSelectHorizontal)
    fam_bond    = models.IntegerField(label="Wie vertraut sind Sie mit Bonds?",
        choices=list(range(1,8)), widget=widgets.RadioSelectHorizontal)
    risk_crypto = models.IntegerField(label="Wie schätzen Sie das Risiko von Crypto ein?",
        choices=list(range(1,8)), widget=widgets.RadioSelectHorizontal)
    risk_equity = models.IntegerField(label="Wie schätzen Sie das Risiko von Equities ein?",
        choices=list(range(1,8)), widget=widgets.RadioSelectHorizontal)
    risk_bond   = models.IntegerField(label="Wie schätzen Sie das Risiko von Bonds ein?",
        choices=list(range(1,8)), widget=widgets.RadioSelectHorizontal)

    # Numeracy
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
