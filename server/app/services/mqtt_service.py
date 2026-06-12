import asyncio
from collections.abc import Awaitable, Callable

import paho.mqtt.client as mqtt

from app.core.config import Settings

MessageHandler = Callable[[str], Awaitable[None]]


class MQTTService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: mqtt.Client | None = None
        self._handler: MessageHandler | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self.is_connected = False

    async def connect(self, handler: MessageHandler) -> None:
        self._handler = handler
        self._loop = asyncio.get_running_loop()

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if self._settings.mqtt_username:
            client.username_pw_set(
                self._settings.mqtt_username,
                self._settings.mqtt_password,
            )

        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message
        self._client = client

        await asyncio.to_thread(
            client.connect,
            self._settings.mqtt_host,
            self._settings.mqtt_port,
            self._settings.mqtt_keepalive,
        )
        client.loop_start()

    async def disconnect(self) -> None:
        if self._client is None:
            return

        self._client.loop_stop()
        await asyncio.to_thread(self._client.disconnect)
        self.is_connected = False

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: object,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        self.is_connected = reason_code == 0
        if self.is_connected:
            client.subscribe(self._settings.mqtt_data_topic)

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: object,
        disconnect_flags: mqtt.DisconnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        self.is_connected = False

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: object,
        message: mqtt.MQTTMessage,
    ) -> None:
        if self._handler is None or self._loop is None:
            return

        try:
            payload = message.payload.decode("utf-8")
        except UnicodeDecodeError:
            return

        asyncio.run_coroutine_threadsafe(self._handler(payload), self._loop)
