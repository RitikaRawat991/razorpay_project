from dataclasses import dataclass


@dataclass
class OpportunityScore:
    score: int
    priority: str


class OpportunityScorer:
    def calculate(
        self,
        risk_score: int,
        amount: int,
        previous_failures: int = 0,
    ) -> OpportunityScore:

        score = risk_score

        # Payment value signal
        if amount >= 100000:
            score += 10
        elif amount >= 50000:
            score += 5

        # Failure history signal
        if previous_failures >= 5:
            score += 15
        elif previous_failures >= 3:
            score += 10
        elif previous_failures >= 1:
            score += 5

        score = min(score, 100)

        if score >= 80:
            priority = "high"
        elif score >= 50:
            priority = "medium"
        else:
            priority = "low"

        return OpportunityScore(
            score=score,
            priority=priority,
        )