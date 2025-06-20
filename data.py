from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests

SPREADSHEET_ID = ''  # Spreadsheet ID
RANGE_NAME = 'GEO VOIP Numbers!A2:K8900'  # Extended range to include the G column
SERVICE_ACCOUNT_FILE = ''  # Path to the service account JSON file

TELEGRAM_BOT_TOKEN = ''  # Токен Telegram-бота
CHAT_ID = ''  # chat_id для отправки уведомлений


# Пороговые значения для каждой страны
COUNTRIES_THRESHOLDS = {
    'австралия': 5,
    'польша': 15,
    'чили': 25,
    'казахстан': 10,
    'британия': 50,
    'бразилия': 15,
    'нидерланды': 5,
    'швеция': 5,
    'чили' : 15

}

def get_data():
    """Функция для получения данных из Google Sheets."""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])



def count_free_numbers(data):
    """Подсчитывает свободные номера для указанных стран, фильтрация по 'MMD' только для Польши."""
    country_counts = {country: 0 for country in COUNTRIES_THRESHOLDS}
    for row in data:
        try:
            status = row[2].strip().lower()       # Статус (колонка C)
            country = row[5].strip().lower()      # Страна (колонка F)
            type_column_general = row[7].strip().lower() if len(row) > 7 else ''  # H
            type_column_poland = row[8].strip().lower() if len(row) > 8 else ''   # I

            if status == 'свободный':
                if country == 'польша':
                    if 'mmd' in type_column_poland:
                        country_counts[country] += 1
                elif country in COUNTRIES_THRESHOLDS:
                    country_counts[country] += 1

        except IndexError:
            continue  # Пропускаем строки с недостаточными данными
    return country_counts

def send_telegram_alert(message):
    """Функция для отправки уведомлений в Telegram."""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response

def check_alerts(country_counts):
    """Проверяет количество свободных номеров и отправляет уведомления, если они ниже порога."""
    for country, count in country_counts.items():
        threshold = COUNTRIES_THRESHOLDS[country]
        if count < threshold:
            message = f"⚠️ В {country.capitalize()} количество свободных номеров ниже порога: {count} (порог: {threshold})."
            send_telegram_alert(message)

def main():
    """Основная функция."""
    data = get_data()
    country_counts = count_free_numbers(data)
    check_alerts(country_counts)

if __name__ == "__main__":
    main()
