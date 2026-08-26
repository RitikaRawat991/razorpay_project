from sqlalchemy.orm import Session

from backend.revenue_monitor.monitor import PaymentEvent
from backend.risk_detection.detector import RiskDetector
from backend.risk_detection.diagnosis import RootCauseDiagnoser
from backend.risk_detection.executor import RecoveryActionExecutor
from backend.risk_detection.guard import RecoveryGuard
from backend.risk_detection.history import get_previous_failure_count
from backend.risk_detection.learning import RecoveryLearningService
from backend.risk_detection.memory import RecoveryMemoryService
from backend.risk_detection.merchant_learning import MerchantLearningService
from backend.risk_detection.opportunity import create_recovery_opportunity
from backend.risk_detection.predictor import RecoveryPredictor
from backend.risk_detection.scorer import OpportunityScorer
from backend.risk_detection.verification import RecoveryVerifier


class RiskDetectionService:
    def __init__(self):
        self.detector = RiskDetector()
        self.scorer = OpportunityScorer()
        self.diagnoser = RootCauseDiagnoser()
        self.memory = RecoveryMemoryService()
        self.predictor = RecoveryPredictor()
        self.guard = RecoveryGuard()
        self.executor = RecoveryActionExecutor()
        self.verifier = RecoveryVerifier()
        self.learning = RecoveryLearningService()
        self.merchant_learning = MerchantLearningService()

    def evaluate(
        self,
        db: Session,
        event: PaymentEvent,
        database_payment_id: int,
    ):
        payment = {
            "payment_id": event.payment_id,
            "merchant_id": event.merchant_id,
            "customer_id": event.customer_id,
            "amount": event.amount,
            "status": event.status,
            "method": event.method,
            "created_at": event.created_at,
            "failure_reason": event.failure_reason,
        }

        risk = self.detector.assess(payment)

        opportunity = None
        opportunity_score = None
        diagnosis = None
        memory = None
        prediction = None
        guard_decision = None
        execution = None
        verification = None
        learning = None
        merchant_learning = None
        previous_failures = 0

        if risk.is_risky:

            # 1. Get historical failure information
            previous_failures = get_previous_failure_count(
                db=db,
                merchant_id=event.merchant_id,
                payment_id=database_payment_id,
            )

            # 2. Calculate recovery opportunity score
            opportunity_score = self.scorer.calculate(
                risk_score=risk.risk_score,
                amount=event.amount,
                previous_failures=previous_failures,
            )

            # 3. Diagnose the root cause
            diagnosis = self.diagnoser.diagnose(
                status=event.status,
                failure_reason=event.failure_reason,
                method=event.method,
                previous_failures=previous_failures,
            )

            # 4. Store customer recovery memory
            memory = self.memory.record(
                db=db,
                customer_id=event.customer_id,
                payment_id=database_payment_id,
                root_cause=diagnosis.root_cause,
            )

            # 5. Predict recovery outcome
            prediction = self.predictor.predict(
                amount=event.amount,
                root_cause=diagnosis.root_cause,
                previous_failures=previous_failures,
            )

            # 6. Check whether the predicted action is safe
            guard_decision = self.guard.check(
                action=prediction.recommended_action,
                confidence=diagnosis.confidence,
                recoverable=diagnosis.recoverable,
                amount=event.amount,
            )

            # 7. Execute only if Guard allows it
            execution = self.executor.execute(
                action=prediction.recommended_action,
                guard_allowed=guard_decision.allowed,
            )

            # 8. Verify recovery outcome
            verification = self.verifier.verify(
                executed=execution.executed,
                payment_status=event.status,
                amount=event.amount,
            )

            # 9. Learn from customer recovery outcome
            learning = self.learning.learn(
                db=db,
                memory_id=memory.id,
                recovered=verification.recovered,
            )

            # 10. Learn merchant-level recovery pattern
            merchant_learning = self.merchant_learning.learn(
                db=db,
                merchant_id=event.merchant_id,
            )

            # 11. Create recovery opportunity
            opportunity = create_recovery_opportunity(
                db=db,
                payment_id=database_payment_id,
                customer_id=event.customer_id,
                risk_score=opportunity_score.score,
                reason=diagnosis.root_cause,
            )

        return {
            "payment": payment,
            "risk": risk,
            "previous_failures": previous_failures,
            "opportunity_score": opportunity_score,
            "diagnosis": diagnosis,
            "memory": memory,
            "prediction": prediction,
            "guard": guard_decision,
            "execution": execution,
            "verification": verification,
            "learning": learning,
            "merchant_learning": merchant_learning,
            "opportunity": opportunity,
        }