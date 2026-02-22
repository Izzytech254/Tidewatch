"""Twilio SMS notification service for flood alerts."""

from datetime import datetime
from typing import Optional

from app.config import settings
from app.models.schemas import AlertSubscription, AlertNotification, RiskScore

# In-memory store for subscriptions (would be a database in production)
_subscriptions: dict[str, AlertSubscription] = {}


def _get_twilio_client():
    """Lazy-load Twilio client only when needed."""
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        return None
    try:
        from twilio.rest import Client
        return Client(settings.twilio_account_sid, settings.twilio_auth_token)
    except Exception as e:
        print(f"[Twilio] Failed to create client: {e}")
        return None


def subscribe(subscription: AlertSubscription) -> bool:
    """Add or update an alert subscription."""
    key = subscription.phone_number
    _subscriptions[key] = subscription
    print(f"[Alerts] Subscribed: {subscription.phone_number} for {subscription.address}")
    return True


def unsubscribe(phone_number: str) -> bool:
    """Remove an alert subscription."""
    if phone_number in _subscriptions:
        del _subscriptions[phone_number]
        return True
    return False


def get_subscriptions() -> list[AlertSubscription]:
    """Get all active subscriptions."""
    return list(_subscriptions.values())


def _build_alert_message(sub: AlertSubscription, risk: RiskScore) -> str:
    """Build human-readable alert message."""
    return (
        f"🌊 TideWatch Alert\n"
        f"Location: {sub.address}\n"
        f"Risk Level: {risk.grade.value} ({risk.score}/100)\n"
        f"{risk.summary}\n"
        f"Recommendations: {'; '.join(risk.recommendations[:2])}"
    )


async def send_alert(
    subscription: AlertSubscription,
    risk: RiskScore,
) -> Optional[AlertNotification]:
    """Send an SMS alert for a risk threshold breach."""
    message_text = _build_alert_message(subscription, risk)

    client = _get_twilio_client()
    if client is None:
        # Log the alert even if we can't send it
        print(f"[Alerts] Would send to {subscription.phone_number}: {message_text}")
        return AlertNotification(
            subscription=subscription,
            risk=risk,
            message=message_text,
            sent_at=datetime.utcnow(),
        )

    try:
        message = client.messages.create(
            body=message_text,
            from_=settings.twilio_from_number,
            to=subscription.phone_number,
        )
        print(f"[Alerts] Sent SMS {message.sid} to {subscription.phone_number}")
        return AlertNotification(
            subscription=subscription,
            risk=risk,
            message=message_text,
            sent_at=datetime.utcnow(),
        )
    except Exception as e:
        print(f"[Alerts] Failed to send SMS: {e}")
        return None


# Grade severity ordering for threshold comparison
_GRADE_SEVERITY = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}


def should_alert(risk: RiskScore, threshold_grade: str) -> bool:
    """Check if risk grade meets or exceeds the alert threshold."""
    risk_severity = _GRADE_SEVERITY.get(risk.grade.value, 0)
    threshold_severity = _GRADE_SEVERITY.get(threshold_grade, 2)
    return risk_severity >= threshold_severity
