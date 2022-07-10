import os
from random import randint

import dotenv
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard
from vk_api.vk_api import VkApiMethod

dotenv.load_dotenv()


class Vk:
    _group_session: VkApi
    _group_api: VkApiMethod

    _user_session: VkApi
    _user_api: VkApiMethod

    def __init__(self):
        self._group_session = VkApi(token=os.environ["GROUP_API_KEY"], client_secret=os.environ["GROUP_API_KEY"])
        self._group_api = self._group_session.get_api()

        self._user_session = VkApi(token=os.environ["USER_API_KEY"])
        self._user_api = self._user_session.get_api()

    def listen_server(self):
        for event in VkBotLongPoll(self._group_session, os.environ["GROUP_ID"]).listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                return event.object

    def send_message(
            self,
            peer_ids: list[str],
            text: str = None,
            attachments: list[str] = None,
            keyboard: VkKeyboard = None
    ):
        params = {
            "peer_ids": peer_ids,
            "random_id": randint(0, 8192)
        }
        if attachments:
            params.update({"attachment": attachments})
        if text:
            params.update({"message": text})
        if keyboard:
            params.update({"keyboard": keyboard.get_keyboard()})
        self._group_api.messages.send(**params)

    def create_call(self):
        return self._user_api.messages.startCall()["join_link"]
