# -*- coding: utf-8 -*
import telebot
from telebot import apihelper
import time
import logging
from telebot import types
from string import Template
from config import API_TOKEN, group_chat_id
from work_csv import read_user_bio_csv, export_to_csv, form_dict, add_status_application
from work_csv import check_status_application, check_application_number

bot = telebot.TeleBot(API_TOKEN)
logging.basicConfig(filename='log.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')
user_dict = {}
status_application = 0


class User:
    def __init__(self, chat_id):
        self.chat_id = chat_id

        keys = ['fullname','telegram_nickname', 'email', 'resume', 'city', 'date_of_birth', 'working_hours', 'experience',
                'salary', 'teamwork', 'work', 'important', 'objection_1', 'objection_2', 'emphasis',
                'situation_1', 'situation_2', 'attracted_vacancy']
        for key in keys:
            self.key = None


def check_ban_users(func):
    def wrapper(message):
        try:
            read_txt = open('blacklist.txt', 'r')
            banned_users = [line.strip() for line in read_txt]
            for user in banned_users:
                if user == str(message.chat.id):
                    return bot.send_message(message.chat.id, 'Вы попали в бан лист')
            read_txt.close()
            return func(message)
        except Exception as e:
            bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
            logging.exception("Ошибка в функции start", exc_info=True)
            bot.send_message(group_chat_id, 'Произошла ошибка при проверке забаненных пользователей')

    return wrapper


@bot.message_handler(commands=['start'])
@check_ban_users
def start(message):
    try:
        send_mess = f"<b>Привет, {message.from_user.first_name}!</b> Текст текст текст"
        bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=Keyboard())
        msg = bot.send_message(message.chat.id, 'Вы готовы заполнить анкету?')
        bot.register_next_step_handler(msg, chat_id)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Ошибка в функции start", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка при старте')


def chat_id(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = User(chat_id)
        get_message_bot = message.text
        # Удаление старой клавиатуры
        markup = types.ReplyKeyboardRemove(selective=False)
        if get_message_bot == 'да' or get_message_bot == 'Да':
            bot.send_message(message.chat.id,
                             '<b>Примечание: этот бот работает последовательно - это значит, что он принимает только одно сообщение. Помните об этом, оставляя заявку.</b>',
                             parse_mode='html')
            bot.send_message(message.chat.id, 'Хорошо, оставьте некоторые данные о себе', reply_markup=markup)
            msg = bot.send_message(message.chat.id, 'Ваше ФИО')
            bot.register_next_step_handler(msg, fullname)

        elif get_message_bot == 'нет' or get_message_bot == 'Нет':
            bot.send_message(message.chat.id,
                             'К сожалению, мы не сможем с вами работать, если что-то изменится - пишите',
                             reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Ошибка в функции chat_id", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def fullname(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.fullname = get_message_bot
        msg = bot.send_message(message.chat.id, 'Ваш никнейм в Telegram')
        bot.register_next_step_handler(msg, telegram_nickname)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции fullname", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def telegram_nickname(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.telegram_nickname = get_message_bot
        msg = bot.send_message(message.chat.id, 'Адрес электронной почты')
        bot.register_next_step_handler(msg, email)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции telegram_nickname", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def email(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.email = get_message_bot
        msg = bot.send_message(message.chat.id, 'Ссылка на ваше резюме')
        bot.register_next_step_handler(msg, resume)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции email", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def resume(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.resume = get_message_bot
        msg = bot.send_message(message.chat.id, 'В каком городе вы проживаете?')
        bot.register_next_step_handler(msg, city)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции resume", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def city(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.city = get_message_bot
        msg = bot.send_message(message.chat.id, 'Ваша дата рождения')
        bot.register_next_step_handler(msg, date_of_birth)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции city", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def date_of_birth(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.date_of_birth = get_message_bot
        msg = bot.send_message(message.chat.id,
                               'Какое количество часов в день вы готовы уделять работе? Днем или вечером?')
        bot.register_next_step_handler(msg, working_hours)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции date_of_birth", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def working_hours(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.working_hours = get_message_bot
        msg = bot.send_message(message.chat.id, 'Кратко опишите ваш опыт работы')
        bot.register_next_step_handler(msg, experience)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции working_hours", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def experience(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.experience = get_message_bot
        msg = bot.send_message(message.chat.id, 'На какой уровень дохода вы рассчитываете?')
        bot.register_next_step_handler(msg, salary)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции experience", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def salary(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.salary = get_message_bot
        msg = bot.send_message(message.chat.id, 'Какое у вас видение команды в которой предстоит работать?')
        bot.register_next_step_handler(msg, teamwork)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции salary", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def teamwork(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.teamwork = get_message_bot
        msg = bot.send_message(message.chat.id,
                               'Работаете ли вы на данный момент?')
        bot.register_next_step_handler(msg, work)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции teamwork", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def work(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.work = get_message_bot
        msg = bot.send_message(message.chat.id, 'Что для вас самое важное в работе?')
        bot.register_next_step_handler(msg, important)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции work", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def important(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.important = get_message_bot
        msg = bot.send_message(message.chat.id, 'Текст текст текст')
        bot.register_next_step_handler(msg, objection_1)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции important", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def objection_1(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.objection_1 = get_message_bot
        msg = bot.send_message(message.chat.id, 'Текст текст текст')
        bot.register_next_step_handler(msg, objection_2)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции objection_1", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def objection_2(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.objection_2 = get_message_bot
        msg = bot.send_message(message.chat.id,'Текст текст текст')
        bot.register_next_step_handler(msg, emphasis)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции objection_2", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def emphasis(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.emphasis = get_message_bot
        msg = bot.send_message(message.chat.id, 'Текст текст текст')
        bot.register_next_step_handler(msg, situation_1)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции emphasis", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def situation_1(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.situation_1 = get_message_bot
        msg = bot.send_message(message.chat.id, 'Текст текст текст')
        bot.register_next_step_handler(msg, situation_2)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции situation_1", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def situation_2(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.situation_2 = get_message_bot
        msg = bot.send_message(message.chat.id, 'Чем вас привлекла вакансия?')
        bot.register_next_step_handler(msg, attracted_vacancy)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции situation_2", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def attracted_vacancy(message):
    try:
        get_message_bot = message.text
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.attracted_vacancy = get_message_bot
        bot.send_message(chat_id, getRegData(user, 'Ваша заявка, ', message.from_user.first_name), parse_mode="Markdown")
        msg = bot.send_message(message.chat.id, 'Всё верно?', reply_markup=Keyboard())
        bot.register_next_step_handler(msg, send_request)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции attracted_vacancy", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в опросе')


def send_request(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        markup = types.ReplyKeyboardRemove(selective=False)
        get_message_bot = message.text
        if get_message_bot == 'да' or get_message_bot =='Да':
            len_csv = read_user_bio_csv()
            bot.send_message(group_chat_id, getRegDataAdmin(user, f'Заявка № {len_csv} от бота', bot.get_me().username),
                             parse_mode="Markdown")
            msg = bot.send_message(message.chat.id, f'Текст текст текст', reply_markup=markup)
            bot.send_message(message.chat.id, f'Когда будете готовы - напишите сюда команду /ready')
            export_to_csv(user)
        elif get_message_bot == 'нет' or get_message_bot == 'Нет':
            msg = bot.send_message(message.chat.id, 'Введите /start, чтобы заново начать регистрацию', reply_markup=markup)
        else:
            msg = bot.send_message(message.chat.id, 'Введите да или нет', reply_markup=Keyboard())
            bot.register_next_step_handler(msg, check_profile)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции send_request", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка при отправке заявки')


def check_profile(message):
    try:
        markup = types.ReplyKeyboardRemove(selective=False)
        chat_id = message.chat.id
        user = user_dict[chat_id]
        get_message_bot = message.text
        if get_message_bot == 'да' or get_message_bot =='Да':
            len_csv = read_user_bio_csv()
            bot.send_message(group_chat_id, getRegDataAdmin(user, f'Заявка № {len_csv} от бота', bot.get_me().username),
                             parse_mode="Markdown")
            msg = bot.send_message(message.chat.id, f'Текст текст текст', reply_markup=markup)
            bot.send_message(message.chat.id, f'Когда будете готовы - напишите сюда команду /ready')
            export_to_csv(user)
        elif get_message_bot == 'нет' or get_message_bot == 'Нет':
            msg = bot.send_message(message.chat.id, 'Введите /start, чтобы заново начать регистрацию', reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции check_profile", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка при отправке заявки')


@bot.message_handler(commands=['ready'])
@check_ban_users
def ready(message):
    try:
        msg = bot.send_message(message.chat.id, 'Текст текст текст')
        bot.register_next_step_handler(msg, get_voice)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции ready", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в команде /ready')


def get_voice(message):
    try:
        if message.content_type == 'voice':
            msg = bot.send_message(message.chat.id,
                                   f'{message.from_user.first_name},cпасибо за уделенное время. У вас остались вопросы?',
                                   reply_markup=Keyboard())
            application_number = check_application_number(message.chat.id)
            bot.register_next_step_handler(msg, ask_voice)
            bot.send_message(group_chat_id, f'Голосовое сообщение от заявки № {application_number}')
            bot.forward_message(group_chat_id, message.chat.id, message.message_id)
        else:
            msg = bot.send_message(message.chat.id, 'Вы отправили не голосовое сообщение, снова введите команду /ready')
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции get_voice", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в команде /ready')


def ask_voice(message):
    try:
        get_message_bot = message.text
        markup = types.ReplyKeyboardRemove(selective=False)
        if get_message_bot == 'да' or get_message_bot =='Да':
            msg = bot.send_message(message.chat.id, 'Перечислите их в одном сообщении', reply_markup=markup)
            bot.register_next_step_handler(msg, check_ask_voice)
        elif get_message_bot == 'нет' or get_message_bot == 'Нет':
            msg = bot.send_message(message.chat.id,'Результаты по вашей заявке придут в чат или можно уточнить командой /status',
            reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже')
        logging.exception("Произошла ошибка в функции ask_voice", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в команде /ready')


def check_ask_voice(message):
    try:
        get_message_bot = message.text
        bot.send_message(message.chat.id,' Текст текст текст')
        bot.send_message(group_chat_id, f'Вопрос от соискателя')
        bot.forward_message(group_chat_id, message.chat.id, message.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже и начать заново')
        logging.exception("Произошла ошибка в функции check_ask_voice", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в команде /ready')


@bot.message_handler(commands=['accept'])
@check_ban_users
def accept_voice(message):
    try:
        if int(message.chat.id) == int(group_chat_id):
            msg = bot.send_message(group_chat_id, 'Какой номер заявки?')
            bot.register_next_step_handler(msg, request_number)
    except Exception as e:
        bot.send_message(group_chat_id, 'Произошла ошибка в принятии заявки')
        logging.exception("Произошла ошибка в функции accept_voice", exc_info=True)


def request_number(message):
    try:
        number_application = int(message.text)
        msg = bot.send_message(group_chat_id,
                               'Выберите статус заявки:\n1 - заявка одобрена;\n2 - заявка не очень одобрена;\n3 - заявка не одобрена')
        bot.register_next_step_handler(msg, status_request, number_application)
    except Exception as e:
        bot.send_message(group_chat_id, 'Произошла ошибка в принятии заявки')
        logging.exception("Произошла ошибка в функции request_number", exc_info=True)


def status_request(message, number_application):
    try:
        status_request = int(message.text)
        accept_mess_text = f'Здравствуйте!\nВаша заявка одобрена'
        if status_request == 1:
            status_application = 'Заявка одобрена'
            bot.send_message(group_chat_id, 'Вы одобрили заявку')
            chat_id = add_status_application(number_application, status_application)
            bot.send_message(chat_id, accept_mess_text)
        elif status_request == 2:
            status_application = 'Заявка не очень одобрена'
            bot.send_message(group_chat_id, 'Вы не очень одобрили заявку')
            chat_id = add_status_application(number_application, status_application)
            bot.send_message(chat_id, accept_mess_text)
        elif status_request == 3:
            status_application = 'Заявка не одобрена'
            bot.send_message(group_chat_id, 'Вы не одобрили заявку')
            chat_id = add_status_application(number_application, status_application)
            bot.send_message(chat_id, f'Заявка не одобрена')
    except Exception as e:
        bot.send_message(group_chat_id, 'Произошла ошибка в принятии заявки')
        logging.exception("Произошла ошибка в функции status_request", exc_info=True)


@bot.message_handler(commands=['status'])
@check_ban_users
def status(message):
    try:
        status_application = check_status_application(message.chat.id)
        if status_application == 'Заявка одобрена' or status_application == 'Заявка не очень одобрена':
            msg = bot.send_message(message.chat.id,
                                   f'Здравствуйте!\nВаша заявка одобрена.')
        elif status_application == 'Заявка не одобрена':
            msg = bot.send_message(message.chat.id, f'Здравствуйте!Не одобрена')
        else:
            msg = bot.send_message(message.chat.id, f'{status_application}.')
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте зайти позже и начать заново')
        logging.exception("Произошла ошибка в функции status", exc_info=True)


@bot.message_handler(commands=['voteban'])
@check_ban_users
def ask_ban_user(message):
    try:
        if int(message.chat.id) == int(group_chat_id):
            msg = bot.send_message(group_chat_id, 'Вы хотите забанить пользователя. Введите его чат ид')
            bot.register_next_step_handler(msg, ban_user)
    except Exception as e:
        bot.send_message(group_chat_id, 'Произошла ошибка при попытке забанить пользователя')
        logging.exception("Произошла ошибка в функции status_request", exc_info=True)


def ban_user(message):
    try:
        ban_user_chat_id = message.text.strip()
        txt = open('blacklist.txt', 'a')
        txt.write(str(ban_user_chat_id) + '\n')
        txt.close()
        bot.send_message(group_chat_id, f'Вы забанили пользователя {ban_user_chat_id}')
    except Exception as e:
        bot.send_message(group_chat_id, 'Произошла ошибка при попытке забанить пользователя')
        logging.exception("Произошла ошибка в функции status_request", exc_info=True)


@bot.message_handler()
@check_ban_users
def other_posts(message):
    # if int(message.chat.id) != int(group_chat_id):
    msg = bot.send_message(message.chat.id,
                           'Я не знаю таких команд.\nДля начала работы необходимо написать команду /start.')


# Клавиатура
def Keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Да')
    btn2 = types.KeyboardButton('Нет')
    markup.add(btn1, btn2)
    return markup


# Формирование формы заявки для пользователя
def getRegData(user, title, name):
    try:
        t = Template(
            '*$title* *$name* \nФИО: *$fullname*\nНикнейм в телеграме: *$telegram_nickname*\nE-mail: *$email*\nРезюме:*$resume*\nГород: *$city*\nДата рождения: *$date_of_birth*\nРабочие часы: *$working_hours* \nОпыт работы: *$experience*\nОжидаемый доход: *$salary*\nВиденье команды: *$teamwork*\nРаботаете ли в данный момент: *$work*\nСамое важной в работе: *$important*\nВозражение1: *$objection_1*\nВозражение 2: *$objection_2*\nУдарение: *$emphasis*\nСитуация 1: *$situation_1*\nСитуация 2: *$situation_2*\nЧем привлекла вакансия: *$attracted_vacancy*')

        user_bio = form_dict(user)
        user_bio['title'] = title
        user_bio['name'] = name
        return t.substitute(user_bio)
    except Exception as e:
        logging.exception("Произошла ошибка в функции getRegData", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в формировании заявки для пользователя')


# Формирование формы заявки для администратора
def getRegDataAdmin(user, title, name):
    try:
        t = Template(
            '*$title* *$name* \nЧат ид: *$chat_id*\nФИО: *$fullname*\nНикнейм в телеграме: *$telegram_nickname*\nE-mail:*$email*\nРезюме:*$resume*\nГород: *$city*\nДата рождения: *$date_of_birth*\nРабочие часы: *$working_hours* \nОпыт работы: *$experience*\nОжидаемый доход: *$salary*\nВиденье команды: *$teamwork*\nРаботаете ли в данный момент: *$work*\nСамое важной в работе: *$important*\nВозражение 1: *$objection_1*\nВозражение2: *$objection_2*\nУдарение: *$emphasis*\nСитуация 1: *$situation_1*\nСитуация 2: *$situation_2*\nЧем привлекла вакансия: *$attracted_vacancy*')

        user_bio = form_dict(user)
        user_bio['title'] = title
        user_bio['name'] = name
        return t.substitute(user_bio)
    except Exception as e:
        logging.exception("Произошла ошибка в функции getRegDataAdmin", exc_info=True)
        bot.send_message(group_chat_id, 'Произошла ошибка в формировании заявки для группы')


bot.polling(none_stop=True)
