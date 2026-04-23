from app.core.errors import RateLimitExceededError
from fastapi import Request
import logging
from app.handlers.exception_handlers import create_error_response

logger = logging.getLogger(__name__)

async def manage_request(request: Request, call_next):
    services = request.app.state.services
    security_service = services.security_service
    cache_service = services.cache_service

    ip_address = request.client.host if request.client else "Unknown"
    log_identity = ip_address
    rate_limit_key = ip_address

    auth_header = request.headers.get("Authorization", None)
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.removeprefix("Bearer ").strip()
            payload = security_service.decode_access_token(token)

            if payload and "email" in payload:
                log_identity = payload["email"]
                rate_limit_key = payload["email"]
        except Exception:
            pass

    if not cache_service.can_request_go_through(rate_limit_key):
        return create_error_response(RateLimitExceededError())

    response = await call_next(request)

    try:
        body = await request.body()
        logger.info(f"DEBUG: Request: {request.method} {request.url.path} | Headers: {request.headers} | Body: {body.decode('utf-8')}")
        logger.info(f"USER: {log_identity} | {request.method} {request.url.path} | Status: {response}")
    except Exception as e:
        print(f"[ CRITICAL] Logging failed because: {e}")

    return response