from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import (
    Payment,
    RecoveryMemory,
    RecoveryOpportunity,
    RecoveryAction,
    RecoveryOutcome,
)


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


# ============================================================
# DASHBOARD
# ============================================================

@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    total_payments = (
        db.query(Payment)
        .count()
    )

    failed_payments = (
        db.query(Payment)
        .filter(
            Payment.status == "failed"
        )
        .count()
    )

    total_opportunities = (
        db.query(RecoveryOpportunity)
        .count()
    )

    total_actions = (
        db.query(RecoveryAction)
        .count()
    )

    pending_recoveries = (
        db.query(RecoveryOpportunity)
        .filter(RecoveryOpportunity.status == "pending_recovery")
        .count()
    )

    executed_actions = (
        db.query(RecoveryAction)
        .filter(RecoveryAction.status == "executed")
        .count()
    )

    blocked_actions = (
        db.query(RecoveryAction)
        .filter(RecoveryAction.status == "blocked")
        .count()
    )

    successful_recoveries = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.outcome == "recovered"
        )
        .count()
    )

    failed_recoveries = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.outcome == "failed"
        )
        .count()
    )

    recovered_rows = (
        db.query(
            RecoveryOutcome.recovered_amount
        )
        .filter(
            RecoveryOutcome.outcome == "recovered"
        )
        .all()
    )

    recovered_amount = sum(
        row[0] or 0
        for row in recovered_rows
    )

    recovery_rate = (
        round(
            (
                successful_recoveries
                / total_actions
            ) * 100,
            2,
        )
        if total_actions > 0
        else 0.0
    )

    failed_payment_recovery_rate = (
        round(
            (
                successful_recoveries
                / failed_payments
            ) * 100,
            2,
        )
        if failed_payments > 0
        else 0.0
    )

    # --------------------------------------------------------
    # Recent recoveries
    # --------------------------------------------------------

    outcomes = (
        db.query(RecoveryOutcome)
        .order_by(
            RecoveryOutcome.id.desc()
        )
        .limit(10)
        .all()
    )

    recent_recoveries = []

    for outcome in outcomes:

        action = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.id
                == outcome.action_id
            )
            .first()
        )

        if action is None:
            continue

        opportunity = (
            db.query(RecoveryOpportunity)
            .filter(
                RecoveryOpportunity.id
                == action.opportunity_id
            )
            .first()
        )

        if opportunity is None:
            continue

        payment = (
            db.query(Payment)
            .filter(
                Payment.id
                == opportunity.payment_id
            )
            .first()
        )

        recent_recoveries.append(
            {
                "outcome_id": outcome.id,
                "payment_id": (
                    payment.id
                    if payment
                    else None
                ),
                "razorpay_payment_id": (
                    payment.payment_id
                    if payment
                    else None
                ),
                "customer_id": (
                    opportunity.customer_id
                ),
                "root_cause": (
                    opportunity.root_cause
                ),
                "action": (
                    action.action_type
                ),
                "outcome": (
                    outcome.outcome
                ),
                "recovered_amount": (
                    outcome.recovered_amount
                    or 0
                ),
            }
        )

    # --------------------------------------------------------
    # Customer learning
    # --------------------------------------------------------

    memories = (
        db.query(RecoveryMemory)
        .order_by(
            RecoveryMemory.id.desc()
        )
        .limit(10)
        .all()
    )

    customer_learning = []

    for memory in memories:
        customer_learning.append(
            {
                "customer_id": (
                    memory.customer_id
                ),
                "root_cause": (
                    memory.root_cause
                ),
                "status": (
                    memory.recovery_status
                ),
                "attempts": (
                    memory.attempts
                ),
                "payment_id": (
                    memory.payment_id
                ),
            }
        )

    # --------------------------------------------------------
    # Recovery funnel
    # --------------------------------------------------------

    funnel = {
        "failed_payments": failed_payments,
        "recovery_opportunities": (
            total_opportunities
        ),
        "recovery_actions": total_actions,
        "successful_recoveries": (
            successful_recoveries
        ),
    }

    # --------------------------------------------------------
    # Final dashboard response
    # --------------------------------------------------------

    return {
        "summary": {
            "total_payments": total_payments,
            "failed_payments": failed_payments,
            "recovery_opportunities": (
                total_opportunities
            ),
            "recovery_actions": total_actions,
            "pending_recoveries": pending_recoveries,
            "executed_actions": executed_actions,
            "blocked_actions": blocked_actions,
            "successful_recoveries": (
                successful_recoveries
            ),
            "failed_recoveries": (
                failed_recoveries
            ),
            "recovered_amount": recovered_amount,
            "recovery_rate": recovery_rate,
            "failed_payment_recovery_rate": (
                failed_payment_recovery_rate
            ),
        },

        "funnel": funnel,

        "recent_recoveries": (
            recent_recoveries
        ),

        "customer_learning": (
            customer_learning
        ),
    }


# ============================================================
# SUMMARY
# ============================================================

@router.get("/summary")
def analytics_summary(
    db: Session = Depends(get_db),
):
    total_payments = (
        db.query(Payment)
        .count()
    )

    failed_payments = (
        db.query(Payment)
        .filter(
            Payment.status == "failed"
        )
        .count()
    )

    total_opportunities = (
        db.query(RecoveryOpportunity)
        .count()
    )

    total_actions = (
        db.query(RecoveryAction)
        .count()
    )

    pending_recoveries = (
        db.query(RecoveryOpportunity)
        .filter(RecoveryOpportunity.status == "pending_recovery")
        .count()
    )

    executed_actions = (
        db.query(RecoveryAction)
        .filter(RecoveryAction.status == "executed")
        .count()
    )

    blocked_actions = (
        db.query(RecoveryAction)
        .filter(RecoveryAction.status == "blocked")
        .count()
    )

    successful_recoveries = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.outcome == "recovered"
        )
        .count()
    )

    failed_recoveries = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.outcome == "failed"
        )
        .count()
    )

    recovered_rows = (
        db.query(
            RecoveryOutcome.recovered_amount
        )
        .filter(
            RecoveryOutcome.outcome == "recovered"
        )
        .all()
    )

    recovered_amount = sum(
        row[0] or 0
        for row in recovered_rows
    )

    recovery_rate = (
        round(
            successful_recoveries
            / total_actions
            * 100,
            2,
        )
        if total_actions > 0
        else 0.0
    )

    failed_payment_recovery_rate = (
        round(
            successful_recoveries
            / failed_payments
            * 100,
            2,
        )
        if failed_payments > 0
        else 0.0
    )

    return {
        "total_payments": total_payments,
        "failed_payments": failed_payments,
        "recovery_opportunities": total_opportunities,
        "recovery_actions": total_actions,
        "pending_recoveries": pending_recoveries,
        "executed_actions": executed_actions,
        "blocked_actions": blocked_actions,
        "successful_recoveries": successful_recoveries,
        "failed_recoveries": failed_recoveries,
        "recovered_amount": recovered_amount,
        "recovery_rate": recovery_rate,
        "failed_payment_recovery_rate": (
            failed_payment_recovery_rate
        ),
    }


# ============================================================
# RECOVERIES
# ============================================================

@router.get("/recoveries")
def get_recoveries(
    db: Session = Depends(get_db),
):
    outcomes = (
        db.query(RecoveryOutcome)
        .order_by(
            RecoveryOutcome.id.desc()
        )
        .all()
    )

    results = []

    for outcome in outcomes:

        action = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.id
                == outcome.action_id
            )
            .first()
        )

        if action is None:
            continue

        opportunity = (
            db.query(RecoveryOpportunity)
            .filter(
                RecoveryOpportunity.id
                == action.opportunity_id
            )
            .first()
        )

        if opportunity is None:
            continue

        payment = (
            db.query(Payment)
            .filter(
                Payment.id
                == opportunity.payment_id
            )
            .first()
        )

        results.append(
            {
                "outcome_id": outcome.id,
                "action_id": action.id,
                "opportunity_id": opportunity.id,
                "payment_id": (
                    payment.id
                    if payment
                    else None
                ),
                "razorpay_payment_id": (
                    payment.payment_id
                    if payment
                    else None
                ),
                "customer_id": (
                    opportunity.customer_id
                ),
                "action": (
                    action.action_type
                ),
                "root_cause": (
                    opportunity.root_cause
                    or action.reason
                ),
                "outcome": (
                    outcome.outcome
                ),
                "recovered": (
                    outcome.outcome
                    == "recovered"
                ),
                "recovered_amount": (
                    outcome.recovered_amount
                ),
                "failure_reason": (
                    outcome.failure_reason
                ),
                "verified_at": (
                    outcome.verified_at
                ),
            }
        )

    return {
        "count": len(results),
        "recoveries": results,
    }


# ============================================================
# OPPORTUNITIES
# ============================================================

@router.get("/opportunities")
def get_opportunities(
    db: Session = Depends(get_db),
):
    opportunities = (
        db.query(RecoveryOpportunity)
        .order_by(
            RecoveryOpportunity.id.desc()
        )
        .all()
    )

    results = []

    for opportunity in opportunities:

        actions = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.opportunity_id
                == opportunity.id
            )
            .all()
        )

        payment = (
            db.query(Payment)
            .filter(
                Payment.id
                == opportunity.payment_id
            )
            .first()
        )

        results.append(
            {
                "opportunity_id": (
                    opportunity.id
                ),
                "payment_id": (
                    opportunity.payment_id
                ),
                "razorpay_payment_id": (
                    payment.payment_id
                    if payment
                    else None
                ),
                "customer_id": (
                    opportunity.customer_id
                ),
                "risk_score": (
                    opportunity.score
                ),
                "reason": (
                    opportunity.root_cause
                ),
                "status": (
                    opportunity.status
                ),
                "actions": [
                    {
                        "id": action.id,
                        "action_type": (
                            action.action_type
                        ),
                        "reason": (
                            action.reason
                        ),
                        "status": action.status,
                        "razorpay_order_id": action.razorpay_order_id,
                    }
                    for action in actions
                ],
            }
        )

    return {
        "count": len(results),
        "opportunities": results,
    }


# ============================================================
# MEMORY
# ============================================================

@router.get("/memory")
def get_memory(
    customer_id: int,
    db: Session = Depends(get_db),
):
    memories = (
        db.query(RecoveryMemory)
        .filter(
            RecoveryMemory.customer_id
            == customer_id
        )
        .order_by(
            RecoveryMemory.id.desc()
        )
        .all()
    )

    return {
        "count": len(memories),
        "memory": [
            {
                "id": memory.id,
                "customer_id": memory.customer_id,
                "payment_id": memory.payment_id,
                "root_cause": memory.root_cause,
                "recovery_status": (
                    memory.recovery_status
                ),
                "attempts": memory.attempts,
                "created_at": memory.created_at,
            }
            for memory in memories
        ],
    }


# ============================================================
# FUNNEL
# ============================================================

@router.get("/funnel")
def get_funnel(
    db: Session = Depends(get_db),
):
    failed_payments = (
        db.query(Payment)
        .filter(
            Payment.status == "failed"
        )
        .count()
    )

    recovery_opportunities = (
        db.query(RecoveryOpportunity)
        .count()
    )

    recovery_actions = (
        db.query(RecoveryAction)
        .count()
    )

    successful_recoveries = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.outcome == "recovered"
        )
        .count()
    )

    return {
        "failed_payments": failed_payments,
        "recovery_opportunities": (
            recovery_opportunities
        ),
        "recovery_actions": recovery_actions,
        "successful_recoveries": (
            successful_recoveries
        ),
    }
