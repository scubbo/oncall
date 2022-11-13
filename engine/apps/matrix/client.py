import asyncio
import logging

from sys import exit

from nio import AsyncClient, LoginResponse, MatrixRoom, RoomMessageText

ROOM_MESSAGE_TYPE = "m.room.message"
TEXT_CONTENT_TYPE = "m.text"

logger = logging.getLogger(__name__)


class MatrixClient(object):
    def __init__(
            self,
            user_id: str,
            access_token: str,
            device_id: str,
            homeserver: str
    ):
        self.client = AsyncClient(homeserver)
        self.client.user_id = user_id
        self.client.access_token = access_token
        self.client.device_id = device_id

    @classmethod
    def _from_login_response(cls, resp: LoginResponse, homeserver: str):
        return MatrixClient(resp.user_id, resp.access_token, resp.device_id, homeserver)

    @classmethod
    def login_with_username_and_password(
            cls,
            user_id: str,  # @user:example.org
            password: str,
            device_name: str,
            homeserver: str

    ):
        """
        TODO: find a way to use OAuth (or some other more-secure-than-passwords-in-env-variables)
        means of logging in
        """
        if not (homeserver.startswith("https://") or homeserver.startswith("http://")):
            homeserver = "https://" + homeserver

        client = AsyncClient(homeserver, user_id)
        # We force this async function to run synchronously, since this method will be called
        # from (e.g.) `__init__` methods, which do not play nicely with async:
        # https://stackoverflow.com/questions/33128325/how-to-set-class-attribute-with-await-in-init
        resp: LoginResponse = asyncio.get_event_loop().run_until_complete(
            client.login(password, device_name=device_name))

        # check that we logged in succesfully
        if isinstance(resp, LoginResponse):
            print(resp)
            return MatrixClient._from_login_response(resp, homeserver)
        else:
            print(f'homeserver = "{homeserver}"; user = "{user_id}"')
            print(f"Failed to log in: {resp}")
            exit(1)

    # TODO - need to handle joining the room if not already joined

    async def send_message(
            self,
            room_alias: str,
            # message_text: RoomMessageText):
            # TODO - find out how to create a RoomMessageText properly (looks like formatting is a big deal)
            message_text: str):
        # TODO - explore the other attributes of RoomMessageText and see what use they might have
        # TODO - look into how far we should allow nio's classes to "leak" out into the app.
        room_resolution_response = await self.client.room_resolve_alias(room_alias)
        room_id = room_resolution_response.room_id
        logging.debug(f'{room_id=}')
        await self.client.room_send(
            room_id=room_id,
            message_type=ROOM_MESSAGE_TYPE,
            content={
                "msgtype": TEXT_CONTENT_TYPE,
                "body": message_text,
                "format": "org.matrix.custom.html",
                "formatted_body": message_text
            }
        )
        await self.client.sync_forever(timeout=30000)

    async def send_message_to_room_id(
            self,
            room_id: str,
            # message_text: RoomMessageText):
            # TODO - find out how to create a RoomMessageText properly (looks like formatting is a big deal)
            message_text: str):
        await self.client.room_send(
            room_id=room_id,
            message_type=ROOM_MESSAGE_TYPE,
            content={
                "msgtype": TEXT_CONTENT_TYPE,
                "body": message_text,
                "format": "org.matrix.custom.html",
                "formatted_body": message_text
            }
        )
        await self.client.sync_forever(timeout=30000)

