def test_get_channels(test_client, mock_services, consumer):
    response = test_client.get("/v1/channels/")
    json_data = response.json()

    mock_services.channel_service.get_channels.assert_called_once_with(consumer.id)
    assert response.status_code == 200
    assert json_data["success"] is True
    assert json_data["message"] == "Channels fetched correctly"
    assert len(json_data["channels"]) == 0


def test_disable_channels(test_client, mock_services, consumer):
    payload = [
        {
            "uuid": "channel-uuid",
            "title": "Channel",
            "link": "https://example.com/feed",
            "disabled_by_user": True,
            "logo_url": "https://example.com/logo.png"
        }
    ]

    response = test_client.post("/v1/channels/disabled", json=payload)
    json_data = response.json()

    mock_services.channel_service.set_disabled_channels.assert_called_once()
    args = mock_services.channel_service.set_disabled_channels.call_args.args
    assert args[0] == consumer.id
    assert args[1][0].uuid == "channel-uuid"
    assert response.status_code == 200
    assert json_data == {
        "success": True,
        "message": "Channels have been disabled for logged user.",
    }
