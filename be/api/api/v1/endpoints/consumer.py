from fastapi import APIRouter, Depends
from api.api.dependencies import get_consumer_service, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from api.models import Consumer
from api.schemas import RegistrationDTO, ConsumerDTO, UpdateCredentialsDTO
from api.schemas.responses import ConsumerResponse, BaseResponse, TokenResponse, InvitationCodeResponse
from dataclasses import asdict
from api.core.errors import InvalidInvitationCode

consumer_router = APIRouter(
    prefix="/consumers",
    tags=["consumers"]
)

@consumer_router.post("/register", response_model=BaseResponse)
def register(registration: RegistrationDTO, consumer_service = Depends(get_consumer_service)):
    if consumer_service.validate_provided_invitation_code(registration.invite_code):
        consumer_service.request_registration(registration)
        return BaseResponse(
            success=True,
            message="New pending registration created."
        )
    else:
        raise InvalidInvitationCode()

@consumer_router.post("/verification", response_model=TokenResponse)
def verification(email: str, code: int, consumer_service = Depends(get_consumer_service)):
    token = consumer_service.verify_registration(email=email, code=code)
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )

@consumer_router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), consumer_service = Depends(get_consumer_service)):
    token = consumer_service.authenticate(form.username, form.password)
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )

@consumer_router.get("/me", response_model=ConsumerResponse)
def me(current_user: Consumer = Depends(get_current_user)):
    return ConsumerResponse(
        success=True,
        message="Current user fetched successfully.",
        consumer = ConsumerDTO(**asdict(current_user))
    )

@consumer_router.put("/credentials", response_model=TokenResponse)
def credentials(request: UpdateCredentialsDTO, user: Consumer = Depends(get_current_user), consumer_service = Depends(get_consumer_service)):
    token = consumer_service.update_credentials_and_issue_token(request, user)
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )

@consumer_router.get("/invitation_code", response_model=InvitationCodeResponse)
def invitation_code(user: Consumer = Depends(get_current_user), consumer_service = Depends(get_consumer_service)):
    code = consumer_service.generate_code(consumer_id=user.id)
    return InvitationCodeResponse(
        success=True,
        message="Invitation code generated.",
        code=code
    )





