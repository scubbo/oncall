import asyncio
import logging

from sys import exit
from time import sleep

from nio import AsyncClient, LoginResponse, MatrixRoom, RoomMessageText

from .rooms import room_name_normalizer

ROOM_MESSAGE_TYPE = "m.room.message"
TEXT_CONTENT_TYPE = "m.text"

logger = logging.getLogger(__name__)


class MatrixClient(object):
    def __init__(
            self,
            client: AsyncClient
    ):
        self.client = client

    @classmethod
    async def login_with_username_and_password(
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
        resp: LoginResponse = await client.login(password, device_name=device_name)

        # check that we logged in succesfully
        if isinstance(resp, LoginResponse):
            return MatrixClient(client)
        else:
            print(f'homeserver = "{homeserver}"; user = "{user_id}"')
            print(f"Failed to log in: {resp}")
            exit(1)

    @room_name_normalizer()
    async def send_message_to_room(
            self,
            room_name: str,
            # message_text: RoomMessageText):
            # TODO - find out how to create a RoomMessageText properly (looks like formatting is a big deal)
            message_text: str):
        # TODO - explore the other attributes of RoomMessageText and see what use they might have
        # TODO - look into how far we should allow nio's classes to "leak" out into the app.
        await self.client.room_send(
            room_id=room_name,
            message_type=ROOM_MESSAGE_TYPE,
            content={
                "msgtype": TEXT_CONTENT_TYPE,
                "body": message_text,
                "format": "org.matrix.custom.html",
                "formatted_body": message_text
            }
        )

    @room_name_normalizer()
    async def join_room(self, room_name: str):
        # This returns a `Union[JoinResponse, JoinError]`, which I think is more Go-style
        # than Pythonic. If we wanted to check return type and take differing action
        # based on that, this would probably be the place to check and throw an Exception.
        # I'll leave it up to the Oncall team what code style they want.
        print(f'DEBUG - trying to join room (should be normalized): {room_name=}')
        return await self.client.join(room_name)

    @room_name_normalizer()
    async def is_in_room(self, room_name: str):
        # If we really wanted, we could maintain a set of "joined_rooms" in the client,
        # update it every time `join_room` (or a hypothetical `leave_room`) is called,
        # and avoid a network call for this method. But that complexity doesn't seem
        # worth the latency gain - in particular, note that you'd have to account for
        # room-aliases, which could change without warning, so you'd need to be
        # listening for room update events in order to stay up-to-date. Better, I think,
        # to just go to the source of truth. Until latency becomes a limiting factor - YAGNI
        #
        # See also the comment on `join_room` about Union-type responses encoding success/failure
        return room_name in (await self.client.joined_rooms()).rooms

    async def is_in_room_unmodified(self, room_name: str):
        logger.critical(f'In unmodified function')
        normalized_room_name = await self._normalize_room_name(room_name)
        logger.critical(f'{normalized_room_name=}')
        rooms = (await self.client.joined_rooms()).rooms
        logger.critical(f'{rooms=}')
        return normalized_room_name in rooms

    async def _normalize_room_name(self, room_name: str) -> str:
        """
        Rooms can be referred to by:
        * a room_id - a single canonical identifier for a room, of the form
            `!<SomeLettersOfVaryingCase>:<homeserver_domain>`
        * a room_alias - of which one room can have many, of the form
            `#<FriendlyName>:<homeserver_domain>`

        This method accepts a name of either(/unknown) type, and normalizes
        to the canonical room_id.

        (Note the intentional use of the noun "name" to encompass both
        `id` and `alias`. If you can think of a better noun, please adopt it!)
        """
        # TODO - repeated points about exceptions vs. Union-type response
        # TODO - (maybe) expand this to accept identifiers without the homeserver domain?
        # Or handle that upstream in the UI and only use, uhh, FQRNs internally?
        logger.critical(f'_normalize... called with {room_name=}')
        logger.critical(f'is event loop running? {asyncio.get_event_loop().is_running()}')
        if room_name.startswith("!"):
            return room_name
        normalization_response = await self.client.room_resolve_alias(room_name)
        logger.critical(f'{normalization_response=}')
        logger.critical(f'{normalization_response.room_id=}')
        return normalization_response.room_id
