import random
import telebot
import telegram.parsemode


def get_available_skills():
    result = [
        'Athletic',
        'Acrobatic',
        'Immunity',
        'Erudition',
        'Acument',
        'Charisma',
        'Diplomacy',
        'Linguistics',
        'Composure',
        'Observation',
        'Fight',
        'Melee Weapon',
        'Pistols',
        'Assault',
        'Sniper',
        'Shotguns',
        'Bruiser',
        'Machinefight',
        'Mechanics',
        'Electricity',
        'Cybersecurity',
        'Craft',
        'Manufacture',
        'Biology',
        'Technologies',
        'Computers',
        'Sociology',
        'Culture',
        'Design',
        'Performance',
        'Stealth',
        'Motorskill',
        'Survival',
        'Economy',
        'Mining',
        'Jurisdiction',
        'Pilotage',
        'Medicine']
    return result


class SLSkill:

    def __init__(self):
        self.name = "name"
        self.level = 0


class SLCharacter:

    def __init__(self):
        self.chat_id = ""
        self.user_id = ""
        self.name = "name"
        self.race = "race"
        self.skills = []
        self.tricks = []


def get_skills_panel(character: SLCharacter):
    keyboard = telebot.types.InlineKeyboardMarkup()

    for skill in get_available_skills():
        button_label = skill + ": "
        if character:
            learned_skill: SLSkill
            for learned_skill in character.skills:
                if learned_skill.name == skill:
                    button_label += str(learned_skill.level)
                    break

        if len(skill + ": ") == button_label:
            button_label += "0"

        skill_button = telebot.types.InlineKeyboardButton(button_label, skill + ":" + character.name)
        keyboard.add(skill_button)

    return keyboard


def get_character_control_panel():
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_race = telebot.types.InlineKeyboardButton(text='Изменить ксенотип',
                                                  callback_data='change-race:')
    key_skills = telebot.types.InlineKeyboardButton(text='Редактировать навыки',
                                                    callback_data='change-skills:')
    key_tricks = telebot.types.InlineKeyboardButton(text='Изменить трюки',
                                                    callback_data='change-tricks:')
    key_inventory = telebot.types.InlineKeyboardButton(text='Изменить инвентарь',
                                                       callback_data='change-inv:')
    keyboard.add(key_race)
    keyboard.add(key_skills)
    keyboard.add(key_tricks)
    keyboard.add(key_inventory)
    return keyboard


class StarLimitBot:

    def __init__(self):
        self.characters = []
        self.available_skills = get_available_skills()

        self.bot = telebot.TeleBot('6582585294:AAGcyYZisXTgt-8ObHJmUye3AAs4qG2aIzs')

        @self.bot.message_handler(content_types=['text'])
        def read_messages(message: telebot.types.Message):
            print("Received message: " + message.text)
            if message.text.startswith('/roll'):
                array_elements: list
                array_elements = message.text.split(' ')
                if len(array_elements) == 4:
                    charname = array_elements[1]
                    skillname = array_elements[2]
                    bonus = int(array_elements[3])
                    result = self.parse_roll(charname, skillname, bonus)
                    answer = "<b>" \
                             + charname \
                             + "</b> | Твой результат броска " \
                             + skillname + " равен <b>" \
                             + str(result) + "</b>"
                    self.bot.send_message(message.from_user.id, answer, telegram.parsemode.ParseMode.HTML)
            if message.text.startswith('/newcharacter'):
                chat_type = message.chat.type
                if chat_type != 'private':
                    self.bot.send_message(message.from_user.id, "Ты не можешь создать нового персонажа в группе или в канале! Для создания нового героя перейди в личные сообщения с ботом")
                else:
                    self.bot.send_message(message.from_user.id, "Введите имя персонажа: ")
                    self.bot.register_next_step_handler(message, self.handle_new_character_after_nickname)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call: telebot.types.CallbackQuery):
            data: str = call.data
            if data.startswith('change-race'):
                user_id = call.from_user.id
                chat_id = call.chat_instance
                self.handle_character_change_race(user_id, chat_id)
            if data.startswith('change-skills'):
                self.handle_character_change_skills(call)

        random.seed(None)
        print("Bot is ready!")
        self.bot.polling(none_stop=True, interval=1)

    def parse_roll(self, char_name: str, skill: str, bonus: int):
        element: SLCharacter
        skill_base: SLSkill
        for element in self.characters:
            if 'SLCharacter' in type(element):
                if element.name == char_name:
                    for skill_base in element.skills:
                        if skill_base.name == skill:
                            summary_bonus = skill_base.level + bonus
                            roll_result = random.randrange(-4, 4, 1)
                            roll_result += summary_bonus
                            return roll_result
                        break
                break
        roll_result = random.randrange(-4, 4, 1) + bonus
        return roll_result

    def handle_new_character_after_nickname(self, message: telebot.types.Message):
        new_character = SLCharacter()
        new_character.name = message.text
        new_character.chat_id = message.chat.id
        new_character.user_id = message.from_user.id
        text_to_send = "Твой персонаж создан, но еще не проинициализирован. Тебе стоит добавить его ксенотип, навыки, трюки и инвентарь.\n"
        text_to_send += "По любым вопросам заполнения проконсультируйся с твоим текущим ДМом.\n"
        text_to_send += "Вы можете в любой момент изменить параметры персонажа. Для этого вызовите команду /editchar"
        keyboard = get_character_control_panel()
        self.bot.send_message(chat_id=message.from_user.id, text=text_to_send, reply_markup=keyboard)

    def handle_character_change_race(self, user_id, chat_id):
        character: SLCharacter = None
        s_character: SLCharacter
        for s_character in self.characters:
            if s_character.user_id == user_id:
                character = s_character
        if character:
            text_to_send = "Введите название вашего ксенотипа: "
            self.bot.send_message(chat_id=user_id, text=text_to_send)
            self.bot.register_next_step_handler_by_chat_id(chat_id, self.handle_character_change_race_answer)
        else:
            self.bot.send_message(chat_id=user_id, text='У вас не создан персонаж. Для начала создайте героя командой /newcharacter')

    def handle_character_change_race_answer(self, message: telebot.types.Message):
        character: SLCharacter = None
        s_character: SLCharacter
        for s_character in self.characters:
            if s_character.user_id == message.from_user.id:
                character = s_character

        if character:
            character.race = message.text
            text_to_set = 'Ксенотип успешно изменен на ' + message.text + '!'
            keyboard = get_character_control_panel(message.from_user.id, message.chat.id)
            self.bot.send_message(message.from_user.id, text_to_set, reply_markup=keyboard)

    def handle_character_change_skills(self, call: telebot.types.CallbackQuery):
        character: SLCharacter = None
        s_character: SLCharacter
        for s_character in self.characters:
            if s_character.user_id == call.from_user.id:
                character = s_character

        if character:
            text_to_set = "Выберите навык, который хотите изменить"

        else:
            self.bot.send_message(chat_id=call.from_user.id, text='У вас не создан персонаж. Для начала создайте героя командой /newcharacter')