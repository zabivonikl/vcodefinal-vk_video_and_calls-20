import traceback
from threading import Thread
from time import sleep

from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from vk import Vk


clients = []
vk = Vk()


class Operators:
    _operators = []

    def __init__(self):
        pass

    def add_operator(self, vk_id, link):
        self._operators.append({"id": vk_id, "link": link, "busy": True})
        return link

    def remove_operator(self, vk_id):
        self._operators = list(filter(lambda x: x["id"] != vk_id, self._operators))

    def free_operator(self, operator_id):
        while len(clients) == 0:
            sleep(1)
        client = clients[0]
        clients.remove(clients[0])
        link = list(filter(lambda x: x["id"] == operator_id, self._operators))[0]['link']
        vk.send_message([client], f"Свободный оператор: {link}")


kb = VkKeyboard()
kb.add_button("Звонок", VkKeyboardColor.POSITIVE)
kb.add_button("Оператор", VkKeyboardColor.POSITIVE)

operator_kb = VkKeyboard()
operator_kb.add_button("Свободен", VkKeyboardColor.POSITIVE)
operator_kb.add_line()
operator_kb.add_button("Не оператор", VkKeyboardColor.NEGATIVE)


def handler(incoming_event, operators):
    try:
        vk_id = str(incoming_event['from_id'])
        text: str = incoming_event["text"]
        if text == "Звонок":
            clients.append(vk_id)
            vk.send_message([vk_id], "Вы добавлены в очередь", keyboard=kb)
        elif text == "Оператор":
            link = operators.add_operator(vk_id, vk.create_call())
            vk.send_message([vk_id], f"Теперь вы оператор. Ссылка на звонок: {link}", keyboard=operator_kb)
        elif text == "Не оператор":
            operators.remove_operator(vk_id)
            vk.send_message([vk_id], "Теперь вы не оператор", keyboard=kb)
        elif text == "Свободен":
            vk.send_message([vk_id], "Ожидайте клиента", keyboard=operator_kb)
            operators.free_operator(vk_id)
        elif text == "Начать":
            vk.send_message([vk_id], "Чтобы начать вызов нажмите \"Звонок\"", keyboard=kb)
        else:
            vk.send_message([vk_id], "Недопустимая команда", keyboard=kb)
    except Exception as e:
        print(f"{e.__class__.__name__}: {e}")
        traceback.print_tb(e.__traceback__)


if __name__ == "__main__":
    operators = Operators()
    while True:
        event = vk.listen_server()
        Thread(target=handler, args=(event['message'], operators)).start()

