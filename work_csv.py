# -*- coding: utf-8 -*
import csv
import pandas as pd

default_encoding = 'utf-8'

def read_user_bio_csv():
    len_user_bio = []
    with open('operators.csv') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            len_user_bio.append(row['city'])
        file.close()
    return len(len_user_bio) + 1


def export_to_csv(user):
    user_bio = form_dict(user)
    user_bio['status_application'] = 'Заявка еще не проверена специалистом'
    with open('operators.csv', 'a', encoding=default_encoding, newline='') as file:
        writer = csv.DictWriter(file, delimiter=';', fieldnames=list(user_bio.keys()))
        #Запись заголовков
        # writer.writeheader()
        writer.writerow(user_bio)
        file.close()


def add_status_application(number_application, status_application):
    df = pd.read_csv('operators.csv', sep=';', encoding=default_encoding)
    index = df.query(f'application_number == "{number_application}"').index[0]
    df.loc[index, 'status_application'] = status_application
    df.to_csv('operators.csv', sep = ';', encoding = default_encoding, index = False)
    return df.loc[index, 'chat_id']

def check_status_application(message_chat_id):
    df = pd.read_csv('operators.csv', sep=';', encoding=default_encoding)
    index = df.query(f'chat_id == "{message_chat_id}"').index[0]
    status_application = df.loc[index, 'status_application']
    return status_application

def check_application_number(message_chat_id):
    df = pd.read_csv('operators.csv', sep=';', encoding=default_encoding)
    index = df.query(f'chat_id == "{message_chat_id}"').index[0]
    application_number = df.loc[index, 'application_number']
    return application_number




# Создание словаря с данными о пользователе для повторного использования в других функциях
def form_dict(user):
    user_bio = {
        'application_number': read_user_bio_csv(),
        'chat_id': user.chat_id,
        'fullname': user.fullname,
        'telegram_nickname': user.telegram_nickname,
        'email': user.email,
        'resume': user.resume,
        'city': user.city,
        'date_of_birth': user.date_of_birth,
        'working_hours': user.working_hours,
        'experience': user.experience,
        'salary': user.salary,
        'teamwork': user.teamwork,
        'work': user.work,
        'important': user.important,
        'objection_1': user.objection_1,
        'objection_2': user.objection_2,
        'emphasis': user.emphasis,
        'situation_1': user.situation_1,
        'situation_2': user.situation_2,
        'attracted_vacancy': user.attracted_vacancy

    }
    return user_bio
