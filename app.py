import os
import logging

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.upload import VkUpload
from vk_api.bot_longpoll import VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from expiring_dict import ExpiringDict
import COVID19Py

keyboard = VkKeyboard(one_time=False)
keyboard.add_button('Коронавирус в мире', color=VkKeyboardColor.PRIMARY)
keyboard.add_button('Коронавирус в россии', color=VkKeyboardColor.PRIMARY)

corona_dict = ExpiringDict(max_len=2, max_age_seconds=3600)
covid19 = COVID19Py.COVID19()

vk_session = vk_api.VkApi(token=os.getenv('TOKEN'), api_version='5.95')
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, os.getenv('GROUP_ID'))
upload = VkUpload(vk_session)

logging.basicConfig(format='%(levelname)s %(name)s [%(asctime)s]: %(message)s',
                    datefmt='%d:%m:%Y:%H:%M:%S')

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.info('start')


def get_info():
    global corona_dict
    corona_dict['world'] = covid19.getLatest()
    corona_dict['ru'] = covid19.getLocationByCountryCode("RU")[0]['latest']


for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        text = event.object.text
        log.info(f'message {text} id {event.obj.peer_id}')
        if text == 'Начать':
            message = 'Начали'
        elif text == 'Коронавирус в мире':
            if not corona_dict.get('world'):
                get_info()
            message = f'🤧 Заражено: {corona_dict["world"]["confirmed"]} человек\n\
                        😲 Умерло: {corona_dict["world"]["deaths"]} человек\n\
                        😎 Излечено: {corona_dict["world"]["recovered"]} человек'
        elif text == 'Коронавирус в россии':
            if not corona_dict.get('ru'):
                get_info()
            message = f'🤧 Заражено: {corona_dict["ru"]["confirmed"]} человек\n\
                        😲 Умерло: {corona_dict["ru"]["deaths"]} человек\n\
                        😎 Излечено: {corona_dict["ru"]["recovered"]} человек'
        else:
            message = 'я не знаю такой команды'
        vk.messages.send(peer_id=event.obj.peer_id, message=message, random_id=0, keyboard=keyboard.get_keyboard())
