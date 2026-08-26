from dataclasses import dataclass


@dataclass
class RootCauseDiagnosis:
    root_cause: str
    confidence: int
    evidence: list[str]
    recoverable: bool


class RootCauseDiagnoser:
    def diagnose(
        self,
        status: str,
        failure_reason: str | None,
        method: str,
        previous_failures: int = 0,
    ) -> RootCauseDiagnosis:

        status = status.lower()
        reason = (failure_reason or "").lower()

        evidence = []

        if "insufficient" in reason or "fund" in reason:
            return RootCauseDiagnosis(
                root_cause="insufficient_funds",
                confidence=95,
                evidence=["failure_reason indicates insufficient funds"],
                recoverable=True,
            )

        if "expired" in reason:
            return RootCauseDiagnosis(
                root_cause="payment_method_expired",
                confidence=95,
                evidence=["failure_reason indicates expired payment method"],
                recoverable=True,
            )

        if "declin" in reason:
            return RootCauseDiagnosis(
                root_cause="issuer_decline",
                confidence=90,
                evidence=["failure_reason indicates issuer/card decline"],
                recoverable=True,
            )

        if status == "pending":
            return RootCauseDiagnosis(
                root_cause="payment_pending",
                confidence=90,
                evidence=["payment status is pending"],
                recoverable=True,
            )

        if status in {"failed", "declined"}:
            evidence.append("payment failed or was declined")

            if previous_failures >= 3:
                evidence.append(
                    f"customer/merchant history contains {previous_failures} previous failures"
                )

            evidence.append(f"payment method: {method}")

            return RootCauseDiagnosis(
                root_cause="payment_failure",
                confidence=70,
                evidence=evidence,
                recoverable=True,
            )

        return RootCauseDiagnosis(
            root_cause="unknown",
            confidence=20,
            evidence=["no strong failure signal detected"],
            recoverable=False,
        )