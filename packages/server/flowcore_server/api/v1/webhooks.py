from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Any, Dict
import hmac
import hashlib
import time
import json
import logging
from uuid import UUID

from flowcore_server.db.models import WebhookTrigger
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.dependencies.core import get_uow
from flowcore_server.services.environment_service import EnvironmentService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)

async def get_db_session(uow: AbstractUnitOfWork = Depends(get_uow)) -> AsyncSession:
    # Small hack to grab the raw session for our raw query since we don't have a WebhookTriggerRepository
    async with uow:
        # In SqlAlchemyUnitOfWork, self.session is set during __aenter__
        yield getattr(uow, 'session')

@router.post("/{webhook_id}")
async def receive_webhook(
    webhook_id: UUID,
    request: Request,
    x_flowcore_signature: str = Header(...),
    x_flowcore_timestamp: str = Header(...),
    uow: AbstractUnitOfWork = Depends(get_uow),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Receives a webhook trigger for a pipeline execution.
    Requires HMAC signature validation with replay protection.
    """
    # 1. Fetch WebhookTrigger from DB
    result = await session.execute(select(WebhookTrigger).where(WebhookTrigger.id == webhook_id))
    webhook = result.scalars().first()
    
    if not webhook or not webhook.is_active:
        raise HTTPException(status_code=404, detail="Webhook not found or inactive")

    # 2. Replay protection (5 minute window)
    try:
        timestamp = int(x_flowcore_timestamp)
        current_time = int(time.time())
        if abs(current_time - timestamp) > 300:
            raise HTTPException(status_code=400, detail="Timestamp outside acceptable window (replay protection)")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")

    # 3. Decrypt the secret key (Stored encrypted with Fernet)
    env_service = EnvironmentService(uow)
    try:
        secret_key = env_service.decrypt(webhook.secret_key_hash)
    except Exception:
        logger.error(f"Failed to decrypt secret key for webhook {webhook_id}")
        raise HTTPException(status_code=500, detail="Internal server error configuration")

    # 4. Verify HMAC signature
    body_bytes = await request.body()
    payload_to_sign = f"{timestamp}:{body_bytes.decode('utf-8')}".encode('utf-8')
    
    expected_signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=payload_to_sign,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, x_flowcore_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 5. Extract JSON payload for context
    try:
        payload = json.loads(body_bytes.decode('utf-8'))
    except json.JSONDecodeError:
        payload = {"raw_body": body_bytes.decode('utf-8')}

    # 6. Trigger Pipeline Execution
    from flowcore_server.dependencies.core import get_scheduler_service
    scheduler = get_scheduler_service()
    
    trigger_context = {
        "trigger_type": "webhook",
        "webhook_id": str(webhook_id),
        "payload": payload
    }
    
    # We use ExecutionService to start it
    exec_service = scheduler.execution_service
    run = await exec_service.start_execution(
        pipeline_id=str(webhook.pipeline_id),
        version="latest",
        trigger_type="webhook",
        parameters=payload
    )
    
    return {"status": "accepted", "run_id": run.id}
