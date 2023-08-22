from pprint import pprint
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

# Налаштування для доступу до Google Sheets
CREDENTIALS_FILE = 'creds.json'
SPREADSHEET_ID = '1YYJO5DPNIeNyBNh0WMmBBwzy-i6b47zyk6L7_JT024Y'

class GoogleSheetsHelper:
    def __init__(self):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE,
            ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        self.http_auth = self.credentials.authorize(httplib2.Http())
        self.service = build('sheets', 'v4', http=self.http_auth)

    def get_data_from_sheet(self, range):
        try:
            values = self.service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range).execute()
            return [item for sublist in values.get('values', []) for item in sublist]
        except Exception as e:
            print("Помилка отримання даних з Google Sheets:", e)
            return []

    def add_user_data_to_sheet(self, user_data):
        range = 'user baseline!A:A'  # Стовпець A у таблиці "user baseline"
        try:
            # Отримати дані з Google Sheets
            values = self.service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range).execute()

            # Розпакувати дані з об'єкта values
            usernames = [item for sublist in values.get('values', []) for item in sublist]

            # Перевірити, чи юзернейм ще не зареєстровано, і додати його до таблиці
            if user_data not in usernames:
                values = [[user_data]]
                body = {'values': values}
                self.service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range=range,
                                                           valueInputOption='RAW', body=body).execute()
        except Exception as e:
            print("Помилка додавання даних до Google Sheets:", e)

def get_info_from_sheets(link):
    gsh = GoogleSheetsHelper()

    # Отримуємо дані з усіх аркушів та рядків
    ranges = [
        'Arina Supreme VIP!E3:E19',
        'Arina Supreme VIP!A3:A19',
        'Arina Supreme VIP!B3:B19',
        'Arina Supreme VIP!C3:C19',
        'Arina Supreme VIP!F3:F19',
        'Arina Supreme VIP!D3:D19',
        'Baby Haze VIP!E3:E16',
        'Baby Haze VIP!A3:A16',
        'Baby Haze VIP!B3:B16',
        'Baby Haze VIP!C3:C16',
        'Baby Haze VIP!F3:F16',
        'Baby Haze VIP!D3:D16',
        'Baby Haze Free!E3:E3',
        'Baby Haze Free!A3:A3',
        'Baby Haze Free!B3:B3',
        'Baby Haze Free!C3:C3',
        'Baby Haze Free!F3:F3',
        'Baby Haze Free!D3:D3'
    ]

    values = [gsh.get_data_from_sheet(r) for r in ranges]

    # Розділяємо значення на окремі списки для кожного аркуша
    (links_1, names_1, ages_1, countries_1, info_f1, info_d1,
     links_2, names_2, ages_2, countries_2, info_f2, info_d2,
     link_from_q3, name_from_q3, age_from_q3, country_from_q3, info_f3, info_d3) = values

    idx = -1  # Ініціалізуємо idx перед використанням

    if link in links_1:
        idx = links_1.index(link)
        if idx < len(names_1) and idx < len(ages_1) and idx < len(countries_1):
            name = names_1[idx]
            age = ages_1[idx]
            country = countries_1[idx]
            return f"Arina Supreme VIP:\nІм'я: {name}\nВік: {age}\nКраїна: {country}\nСтатус: {info_f1[idx]}\n{info_d1[idx]}"

    if link in links_2:
        idx = links_2.index(link)
        if idx < len(names_2) and idx < len(ages_2) and idx < len(countries_2):
            name = names_2[idx]
            age = ages_2[idx]
            country = countries_2[idx]
            return f"Baby Haze VIP:\nІм'я: {name}\nВік: {age}\nКраїна: {country}\nСтатус: {info_f2[idx]}\n{info_d2[idx]}"

    if link in link_from_q3:
        idx = link_from_q3.index(link)
        name = name_from_q3[idx]
        age = age_from_q3[idx]
        country = country_from_q3[idx]
        return f"Baby Haze Free:\nІм'я: {name}\nВік: {age}\nКраїна: {country}\nСтатус: {info_f3[idx]}\n{info_d3[idx]}"

    return "Інформацію для цього посилання не знайдено."

def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_data = user.username or user.first_name
    gsh = GoogleSheetsHelper()
    gsh.add_user_data_to_sheet(user_data)
    update.message.reply_text(f"Привіт, {user.first_name}! "
                              f"Відправте мені посилання на Кита або VIP-а, і я надам вам інформацію про нього.")

def handle_message(update: Update, context: CallbackContext) -> None:
    link = update.message.text.strip()
    if link:
        info = get_info_from_sheets(link)
        update.message.reply_text(info)
    else:
        update.message.reply_text("Будь ласка, вставте посилання на Кита або VIP-а.")

def stop_bot(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Дякую за використання бота! Поверніться, натиснувши кнопку /start, якщо буде потреба.")
    context.bot.stop()

def main():
    bot_token = '6469823130:AAGbQYcFWABnzhjCZmimBatzNFgmX2EKxBg'  # Замініть на свій токен бота

    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CommandHandler("stop", stop_bot))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
