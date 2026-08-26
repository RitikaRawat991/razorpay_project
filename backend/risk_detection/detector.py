from dataclasses import dataclass


@dataclass
class RiskAssessment:
    is_risky: bool
    risk_score: int
    reason: str


class RiskDetector:
    def assess(self, payment: dict) -> RiskAssessment:
        status = payment["status"].lower()
        amount = payment["amount"]

        score = 0
        reasons = []

        if status in {"failed", "declined"}:
            score += 60
            reasons.append("payment_failed")

        if status == "pending":
            score += 30
            reasons.append("payment_pending")

        if amount >= 100000:
            score += 20
            reasons.append("high_value_payment")

        score = min(score, 100)

        return RiskAssessment(
            is_risky=score >= 50,
            risk_score=score,
            reason=", ".join(reasons) if reasons else "no_risk_signal",
        )