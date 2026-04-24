from app.api_client.client import AuthenticatedClient
from app.api_client.models import ChannelDTO
from app.api_client.api.channels import channels, disabled
from .base_service import BaseService

class ChannelsService(BaseService):
    def __init__(self, client: AuthenticatedClient):
        self.client = client

    def get_all_channels(self) -> list[ChannelDTO]:
        response = channels.sync_detailed(
            client=self.client
        )

        self._handle_response(response)

        return response.parsed.channels if response.parsed.channels else []

    def set_disabled_channels(self, channels_to_disable: list[ChannelDTO]) -> None:
        response = disabled.sync_detailed(
            client=self.client,
            body=channels_to_disable
        )

        self._handle_response(response)

