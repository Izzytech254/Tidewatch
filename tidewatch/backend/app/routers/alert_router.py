"""Alert subscription API routes."""

from fastapi import APIRouter, HTTPException
from app.models.schemas import AlertSubscription
from app.services import notification_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("/subscribe")
async def subscribe(subscription: AlertSubscription):
    """Subscribe to flood risk alerts for an address."""
    success = notification_service.subscribe(subscription)
    if success:
        return {"status": "subscribed", "address": subscription.address}
    raise HTTPException(status_code=500, detail="Failed to create subscription")


@router.delete("/unsubscribe/{phone_number}")
async def unsubscribe(phone_number: str):
    """Unsubscribe from flood risk alerts."""
    success = notification_service.unsubscribe(phone_number)
    if success:
        return {"status": "unsubscribed"}
    raise HTTPException(status_code=404, detail="Subscription not found")


@router.get("/subscriptions")
async def list_subscriptions():
    """List all active alert subscriptions."""
    subs = notification_service.get_subscriptions()
    return {"count": len(subs), "subscriptions": subs}
