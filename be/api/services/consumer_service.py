import secrets
from typing import Optional
from api.models import Consumer
from api.schemas import RegistrationDTO, UpdateCredentialsDTO
from api.interfaces import ConsumerInterface, ValkeyInterface
from api.core.errors import RegistrationExpiredError, EmailAlreadyUsedError, UsernameAlreadyUsedError, InvalidCredentialsError, InvalidCurrentPasswordError, PasswordReuseError
from .email_service import EmailService
from .security_service import SecurityService

class ConsumerService:
    def __init__(
        self,
        consumers: ConsumerInterface,
        valkey: ValkeyInterface,
        security: SecurityService,
        email: EmailService,
    ):
        self.consumers = consumers
        self.valkey = valkey
        self.security = security
        self.email = email

    def is_email_used(self, email: str) -> bool:
        consumer = self.consumers.get_consumer_by_email(email)
        if consumer:
            return True

        return False

    def is_username_used(self, username: str) -> bool:
        consumer = self.consumers.get_consumer_by_username(username)
        if consumer:
            return True

        return False

    def validate_new_registration(self, registration: RegistrationDTO) -> None:
        consumer = self.consumers.get_consumer_by_email(email=registration.email)
        if consumer:
            raise EmailAlreadyUsedError()

        consumer = self.consumers.get_consumer_by_username(username=registration.username)
        if consumer:
            raise UsernameAlreadyUsedError()

    def create_new_registration(self, registration: RegistrationDTO, code: int) -> None:
        is_pending = self.valkey.is_registration_pending(registration)
        if is_pending:
            self.valkey.delete_registration_from_pending(registration)

        self.valkey.create_pending_registration(registration, code)

    def request_registration(self, registration: RegistrationDTO) -> None:
        self.validate_new_registration(registration)
        registration.password = self.security.get_password_hash(registration.password)
        code = secrets.randbelow(900000) + 100000
        self.email.send_verification_code(registration.email, code)
        self.create_new_registration(registration, code)

    def register_consumer(self, email: str, code: int) -> Consumer:
        registration = self.valkey.provided_code_correct(email=email, code=code)
        if registration:
            return self.consumers.register_consumer(registration)
        else:
            raise RegistrationExpiredError()

    def verify_registration(self, email: str, code: int) -> str:
        consumer = self.register_consumer(email=email, code=code)
        return self.security.create_access_token(consumer)

    def get_consumer_by_credential(self, credential: str) -> Optional[Consumer]:
        consumer = self.consumers.get_consumer_by_username(credential)
        if not consumer:
            consumer = self.consumers.get_consumer_by_email(credential)

        return consumer

    def get_consumer_by_username(self, username: str) -> Optional[Consumer]:
        return self.consumers.get_consumer_by_username(username)

    def get_consumers_hash(self, id: int) -> Optional[str]:
        return self.consumers.get_consumers_hash(id)

    def authenticate(self, credential: str, password: str) -> str:
        consumer = self.get_consumer_by_credential(credential)
        if not consumer:
            raise InvalidCredentialsError()

        consumer_hash = self.get_consumers_hash(consumer.id)
        if not consumer_hash or not self.security.verify_password(consumer_hash, password):
            raise InvalidCredentialsError()

        return self.security.create_access_token(consumer)

    def update_credentials(self, request: UpdateCredentialsDTO, user: Consumer):
        if request.new_username:
            self.consumers.update_consumers_username(user_id=user.id, new_username=request.new_username)
            user.username = request.new_username

        if request.new_password:
            self.consumers.update_consumers_password(user_id=user.id, new_hash=request.new_password)

        return user

    def update_credentials_and_issue_token(self, request: UpdateCredentialsDTO, user: Consumer) -> str:
        current_hash = self.get_consumers_hash(user.id)
        if not current_hash or not self.security.verify_password(current_hash, request.old_password):
            raise InvalidCurrentPasswordError()

        if request.new_password:
            if self.security.is_password_identical_to_hash(current_hash, request.new_password):
                raise PasswordReuseError()
            request.new_password = self.security.get_password_hash(request.new_password)

        updated_consumer = self.update_credentials(request, user)
        return self.security.create_access_token(updated_consumer)

    def validate_provided_invitation_code(self, code: int) -> bool:
        return self.valkey.validate_invite_code(code=code)

    def generate_code(self, consumer_id: int) -> int:
        return self.valkey.generate_invite_code(consumer_id=consumer_id)
