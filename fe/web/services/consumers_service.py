from web.api_client.client import AuthenticatedClient, Client
from web.api_client.api.consumers import login, register, verification, me, credentials, invitation_code
from web.api_client.models import BodyLogin, RegistrationDTO, TokenResponse, ConsumerDTO, UpdateCredentialsDTO
from typing import Optional
from .base_service import BaseService

class ConsumersService(BaseService):
    def __init__(self, client: AuthenticatedClient | Client):
        self.client = client

    def login_user(self, credential: str, password: str) -> Optional[TokenResponse]:
        form_data = BodyLogin(
            username=credential,
            password=password
        )

        response = login.sync_detailed(
            client=self.client,
            body=form_data
        )

        self._handle_response(response)

        try:
            return response.parsed
        except KeyError:
            return None

    def request_new_registration(self, registration: RegistrationDTO):
        response = register.sync_detailed(
            client=self.client,
            body=registration
        )

        self._handle_response(response)

        if response.parsed is not None:
            return True
        else:
            return False

    def verify_email(self, email: str, code: int) -> Optional[TokenResponse]:
        response = verification.sync_detailed(
            client=self.client,
            email=email,
            code=code
        )

        self._handle_response(response)

        try:
            return response.parsed
        except KeyError:
            return None

    def get_current_user(self) -> ConsumerDTO:
        if not isinstance(self.client, AuthenticatedClient):
            raise Exception('This method can be called only with authenticated client.')

        response = me.sync_detailed(
            client=self.client
        )

        self._handle_response(response)

        return response.parsed.consumer

    def update_credentials(self, new_credentials: UpdateCredentialsDTO):
        if not isinstance(self.client, AuthenticatedClient):
            raise Exception('This method can be called only with authenticated client.')

        response = credentials.sync_detailed(
            client=self.client,
            body=new_credentials
        )

        self._handle_response(response)

        try:
            return response.parsed
        except KeyError:
            return None

    def generate_code(self) -> int:
        if not isinstance(self.client, AuthenticatedClient):
            raise Exception('This method can be called only with authenticated client.')

        response = invitation_code.sync_detailed(
            client=self.client
        )

        self._handle_response(response)

        return response.parsed.code
