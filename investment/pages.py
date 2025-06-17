from otree.api import Page
from .models import NUMERACY_QUESTIONS

class PostExperimentSurvey(Page):
    form_model = 'player'
    form_fields = [
        'fam_crypto', 'fam_equity', 'fam_bond',
        'risk_crypto','risk_equity','risk_bond'
    ]

    def is_displayed(self):
        return self.round_number == 1

class NumeracyTest(Page):
    form_model = 'player'

    timeout_seconds = 10
    # Keine {} mehr – oTree rendert "Verbleibende Zeit: 0:07 Sek."
    timer_text = "Verbleibende Zeit:"
    auto_submit = True

    def get_form_fields(self):
        idx = self.round_number - 1
        return [f'numq_{idx}']

    def is_displayed(self):
        return 2 <= self.round_number <= 11

    def vars_for_template(self):
        idx = self.round_number - 1
        return {
            'question_number': idx,
            'question_text': NUMERACY_QUESTIONS[idx-1],
        }

page_sequence = [
    # InvestmentDecision ausgesetzt
    PostExperimentSurvey,   # Runde 1
    NumeracyTest,           # Runden 2–11
]
