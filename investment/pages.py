from otree.api import Page

class InvestmentDecision(Page):
    form_model = 'player'
    form_fields = ['choice']

    def vars_for_template(self):
        frame = self.participant.vars['frame_data'][self.round_number - 1]
        # Jede Option vorbereiten
        for idx, col in enumerate(frame['columns']):
            # 1) Outcome-Labels (z.B. "80 % – €2.50")
            col['outcome_labels'] = [
                f"{int(prob*100)} % – €{payoff:.2f}"
                for prob, payoff in zip(col['probs'], col['payoffs'])
            ]
            # 2) Display-Label abhängig vom Frame-Typ
            if frame['frame'] == 'blind':
                # Asset A, B, C
                col['display_label'] = f"Asset {chr(65 + idx)}"
            else:
                # Namens-Label + (Asset-Klasse)
                col['display_label'] = f"{col['display_name']} ({col['asset_class'].title()})"
        return {
            'frame': frame,
        }

page_sequence = [InvestmentDecision]