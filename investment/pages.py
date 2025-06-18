import math
from otree.api import Page
from .models import Constants, NUMERACY_QUESTIONS

class Consent(Page):
    """Round 1: Informed consent."""
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        # progress = 0%
        return {'progress_pct': "0"}


class Instructions(Page):
    """Round 2: Brief instructions (no headlines)."""
    def is_displayed(self):
        return self.round_number == 2

    def vars_for_template(self):
        pct = (self.round_number - 1) / Constants.num_rounds * 100
        return {'progress_pct': f"{pct:.0f}"}


class InvestmentDecision(Page):
    form_model = 'player'
    form_fields = ['choice']

    def is_displayed(self):
        # rounds 3–22 inclusive
        return 3 <= self.round_number <= 22

    def vars_for_template(self):
        # display 1–20
        display_round = self.round_number - 2

        # progress from 2 intro pages up to this page
        progress_pct = (self.round_number - 1) / Constants.num_rounds * 100

        frame = self.participant.vars['frame_data'][self.round_number - 3]
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
        'fam_crypto', 'fam_equity', 'fam_bond',
        'risk_crypto', 'risk_equity', 'risk_bond',
    ]

    def is_displayed(self):
        return self.round_number == 23

    def vars_for_template(self):
        pct = (self.round_number - 1) / Constants.num_rounds * 100
        return {'progress_pct': f"{pct:.0f}"}


class NumeracyTest(Page):
    form_model = 'player'
    timeout_seconds = 10
    timer_text      = "Verbleibende Zeit:"
    auto_submit     = True

    def is_displayed(self):
        # rounds 24–33 inclusive
        return 24 <= self.round_number <= 33

    def get_form_fields(self):
        idx = self.round_number - 23
        return [f'numq_{idx}']

    def vars_for_template(self):
        idx = self.round_number - 23
        pct = (self.round_number - 1) / Constants.num_rounds * 100
        return {
            'question_number': idx,
            'question_text':   NUMERACY_QUESTIONS[idx - 1],
            'progress_pct':    f"{pct:.0f}"
        }


class ThankYou(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds  # now 34

    def vars_for_template(self):
        return {'progress_pct': "100"}


page_sequence = [
    Consent,               # 1
    Instructions,          # 2
    InvestmentDecision,    # 3–22 (20 pages)
    PostExperimentSurvey,  # 23
    NumeracyTest,          # 24–33 (10 pages)
    ThankYou,              # 34
]
