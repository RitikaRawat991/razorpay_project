from dataclasses import asdict, is_dataclass

from sqlalchemy.orm import Session

from backend.database.models import Payment
from backend.revenue_monitor.events import PaymentEvent
from backend.risk_detection.action import create_recovery_action
from backend.risk_detection.detector import RiskDetector
from backend.risk_detection.diagnosis import RootCauseDiagnoser
from backend.risk_detection.executor import RecoveryActionExecutor
from backend.risk_detection.guard import RecoveryGuard
from backend.risk_detection.history import get_previous_failure_count
from backend.risk_detection.learning import RecoveryLearningService
from backend.risk_detection.memory import RecoveryMemoryService
from backend.risk_detection.merchant_learning import MerchantLearningService
from backend.risk_detection.opportunity import create_recovery_opportunity
from backend.risk_detection.outcome import create_recovery_outcome
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
        # ---------------------------------------------------------
        # Payment event data
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Initial state
        # ---------------------------------------------------------

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
        recovery_action = None
        recovery_outcome = None

        previous_failures = 0

        # ---------------------------------------------------------
        # Run recovery pipeline only for risky payments
        # ---------------------------------------------------------

        if risk.is_risky:

            # =====================================================
            # 1. Historical failure analysis
            # =====================================================

            previous_failures = get_previous_failure_count(
                db=db,
                merchant_id=event.merchant_id,
                payment_id=database_payment_id,
            )

            # =====================================================
            # 2. Recovery Opportunity Score
            # =====================================================

            opportunity_score = self.scorer.calculate(
                risk_score=risk.risk_score,
                amount=event.amount,
                previous_failures=previous_failures,
            )

            # =====================================================
            # 3. Root Cause Diagnosis
            # =====================================================

            diagnosis = self.diagnoser.diagnose(
                status=event.status,
                failure_reason=event.failure_reason,
                method=event.method,
                previous_failures=previous_failures,
            )

            # =====================================================
            # 4. Customer Recovery Memory
            # =====================================================

            memory = self.memory.record(
                db=db,
                customer_id=event.customer_id,
                payment_id=database_payment_id,
                root_cause=diagnosis.root_cause,
            )

            # =====================================================
            # 5. Merchant-Level Learning
            #
            # IMPORTANT:
            # Run merchant learning BEFORE prediction so that
            # historical merchant recovery performance can
            # influence the next recovery decision.
            # =====================================================

            merchant_learning = self.merchant_learning.learn(
                db=db,
                merchant_id=event.merchant_id,
            )

            merchant_recovery_rate = (
                merchant_learning.recovery_rate
                if merchant_learning is not None
                else 0.0
            )

            # =====================================================
            # 6. Predict Best Recovery Action
            #
            # Predictor now uses:
            # - root cause
            # - previous failures
            # - payment amount
            # - merchant historical recovery rate
            # =====================================================

            prediction = self.predictor.predict(
                amount=event.amount,
                root_cause=diagnosis.root_cause,
                previous_failures=previous_failures,
                merchant_recovery_rate=merchant_recovery_rate,
            )

            # =====================================================
            # 7. Recovery Safety Guard
            # =====================================================

            guard_decision = self.guard.check(
                action=prediction.recommended_action,
                confidence=diagnosis.confidence,
                recoverable=diagnosis.recoverable,
                amount=event.amount,
            )

            # =====================================================
            # 8. Execute Recovery Action
            # =====================================================

            execution = self.executor.execute(
                action=prediction.recommended_action,
                guard_allowed=guard_decision.allowed,
                payment_id=event.payment_id,
                amount=event.amount,
            )

            # =====================================================
            # 9. Verify Recovery
            # =====================================================

            payment_status = getattr(
                execution,
                "payment_status",
                event.status,
            )

            verification = self.verifier.verify(
                executed=execution.executed,
                payment_status=payment_status,
                amount=event.amount,
            )

            # =====================================================
            # 10. Update Payment State
            # =====================================================

            payment_record = (
                db.query(Payment)
                .filter(
                    Payment.id == database_payment_id
                )
                .first()
            )

            if payment_record is not None:

                if verification.recovered:
                    payment_record.status = "captured"
                    payment_record.failure_reason = None

                elif execution.executed:
                    payment_record.status = "failed"

                db.commit()
                db.refresh(payment_record)

            # =====================================================
            # 11. Create Recovery Opportunity
            # =====================================================

            opportunity = create_recovery_opportunity(
                db=db,
                payment_id=database_payment_id,
                customer_id=event.customer_id,
                risk_score=(
                    opportunity_score.score
                    if opportunity_score is not None
                    else risk.risk_score
                ),
                reason=diagnosis.root_cause,
            )

            # =====================================================
            # 12. Create Recovery Action
            # =====================================================

            if opportunity is not None:

                recovery_action = create_recovery_action(
                    db=db,
                    opportunity_id=opportunity.id,
                    action_type=prediction.recommended_action,
                    reason=diagnosis.root_cause,
                )

                # =================================================
                # 13. Create Recovery Outcome
                # =================================================

                recovery_outcome = create_recovery_outcome(
                    db=db,
                    action_id=recovery_action.id,
                    recovered=verification.recovered,
                    recovered_amount=verification.recovered_amount,
                    failure_reason=(
                        None
                        if verification.recovered
                        else verification.message
                    ),
                )

                # =================================================
                # 14. Update Opportunity Lifecycle
                # =================================================

                if verification.recovered:
                    opportunity.status = "recovered"

                elif execution.executed:
                    opportunity.status = "failed"

                else:
                    opportunity.status = "blocked"

                db.commit()
                db.refresh(opportunity)

                # =================================================
                # 15. Customer-Level Learning
                # =================================================

                learning = self.learning.learn_from_outcome(
                    db=db,
                    outcome=recovery_outcome,
                )

                # =================================================
                # 16. Refresh Merchant Learning
                #
                # The current attempt has now completed, so
                # merchant statistics should include this outcome.
                # =================================================

                merchant_learning = self.merchant_learning.learn(
                    db=db,
                    merchant_id=event.merchant_id,
                )

        # ---------------------------------------------------------
        # JSON-safe opportunity response
        # ---------------------------------------------------------

        opportunity_data = None

        if opportunity is not None:

            opportunity_data = {
                "id": opportunity.id,

                "payment_id": (
                    opportunity.payment_id
                ),

                "customer_id": (
                    opportunity.customer_id
                ),

                "risk_score": (
                    opportunity_score.score
                    if opportunity_score is not None
                    else opportunity.score
                ),

                "reason": (
                    diagnosis.root_cause
                    if diagnosis is not None
                    else opportunity.root_cause
                ),

                "status": (
                    opportunity.status
                ),
            }

        # ---------------------------------------------------------
        # JSON-safe recovery action response
        # ---------------------------------------------------------

        recovery_action_data = None

        if recovery_action is not None:

            recovery_action_data = {
                "id": recovery_action.id,

                "opportunity_id": (
                    recovery_action.opportunity_id
                ),

                "action_type": (
                    recovery_action.action_type
                ),

                "reason": (
                    diagnosis.root_cause
                    if diagnosis is not None
                    else None
                ),
            }

        # ---------------------------------------------------------
        # JSON-safe recovery outcome response
        # ---------------------------------------------------------

        recovery_outcome_data = None

        if recovery_outcome is not None:

            recovery_outcome_data = {
                "id": recovery_outcome.id,

                "action_id": (
                    recovery_outcome.action_id
                ),

                "recovered": (
                    recovery_outcome.outcome
                    == "recovered"
                ),

                "outcome": (
                    recovery_outcome.outcome
                ),

                "recovered_amount": (
                    recovery_outcome.recovered_amount
                ),

                "failure_reason": (
                    recovery_outcome.failure_reason
                ),
            }

        # ---------------------------------------------------------
        # Dataclass serializer
        # ---------------------------------------------------------

        def serialize(value):

            if value is None:
                return None

            if is_dataclass(value):
                return asdict(value)

            return value

        # ---------------------------------------------------------
        # Final response
        # ---------------------------------------------------------

        return {
            "payment": payment,

            "risk": serialize(
                risk
            ),

            "previous_failures": (
                previous_failures
            ),

            "opportunity_score": serialize(
                opportunity_score
            ),

            "diagnosis": serialize(
                diagnosis
            ),

            "memory": serialize(
                memory
            ),

            "prediction": serialize(
                prediction
            ),

            "guard": serialize(
                guard_decision
            ),

            "execution": serialize(
                execution
            ),

            "verification": serialize(
                verification
            ),

            "learning": serialize(
                learning
            ),

            "merchant_learning": serialize(
                merchant_learning
            ),

            "opportunity": opportunity_data,

            "recovery_action": (
                recovery_action_data
            ),

            "recovery_outcome": (
                recovery_outcome_data
            ),
        }