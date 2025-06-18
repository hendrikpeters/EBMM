import math
from otree.api import Page
from .models import Constants, NUMERACY_QUESTIONS

class InvestmentDecision(Page):
    form_model = 'player'
    form_fields = ['choice']

    def is_displayed(self):
        return 1 <= self.round_number <= 20

    def vars_for_template(self):
        frame = self.participant.vars['frame_data'][self.round_number - 1]
        display_round = math.ceil(self.round_number / 2)
        progress_pct  = (self.round_number - 1) / Constants.num_rounds * 100
        columns = []
        for opt in frame['columns']:
            labels = [
                f"{int(p * 100)} % – €{pay:.2f}"
                for p, pay in zip(opt['probs'], opt['payoffs'])
            ]
            columns.append({
                'asset_class':    opt['asset_class'],
                'display_label':  opt['display_name'],
                'outcome_labels': labels,
            })
        return {
            'display_round': display_round,
            'frame_name':    frame['frame'],
            'columns':       columns,
            'progress_pct':  f"{progress_pct:.0f}",
        }

class PostExperimentSurvey(Page):
    form_model = 'player'
    form_fields = [
        'fam_crypto','fam_equity','fam_bond',
        'risk_crypto','risk_equity','risk_bond',
    ]

    def is_displayed(self):
        return self.round_number == 21

    def vars_for_template(self):
        pct = (self.round_number - 1) / Constants.num_rounds * 100
        return {'progress_pct': f"{pct:.0f}"}

class NumeracyTest(Page):
    form_model = 'player'
    timeout_seconds = 10
    timer_text      = "Verbleibende Zeit:"
    auto_submit     = True

    def is_displayed(self):
        return 22 <= self.round_number <= 31

    def get_form_fields(self):
        idx = self.round_number - 21
        return [f'numq_{idx}']

    def vars_for_template(self):
        idx = self.round_number - 21
        pct = (self.round_number - 1) / Constants.num_rounds * 100
        return {
            'question_number': idx,
            'question_text':   NUMERACY_QUESTIONS[idx-1],
            'progress_pct':    f"{pct:.0f}"
        }

class ThankYou(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        pct = (self.round_number - 1) / Constants.num_rounds * 100
        return {'progress_pct': f"{pct:.0f}"}

page_sequence = [
    InvestmentDecision,    # Runden 1–20
    PostExperimentSurvey,  # Runde 21
    NumeracyTest,          # Runden 22–31
    ThankYou,              # Runde 32
]
