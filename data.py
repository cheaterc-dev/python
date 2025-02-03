from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests

# Конфигурация Google Sheets
SPREADSHEET_ID = ''  # ID таблицы
RANGE_NAME = 'GEO VOIP Numbers!A2:G8900'  # Расширен диапазон до G-столбца
SERVICE_ACCOUNT_FILE = 'apiprometheus-b2585815780f.json'  # JSON-файл с ключами Google API

# Конфигурация Telegram
TELEGRAM_BOT_TOKEN = 'E'  # Токен Telegram-бота
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
    """Подсчитывает свободные номера для указанных стран, учитывая фильтр 'mobile' только для Британии и Польши."""
    country_counts = {country: 0 for country in COUNTRIES_THRESHOLDS}  # Инициализация словаря
    for row in data:
        try:
            status = row[2].strip().lower()  # Статус (второй столбец)
            country = row[4].strip().lower()  # Страна (пятый столбец)
            type_column = row[6].strip().lower() if len(row) > 6 else ''  # Проверяем столбец G (седьмой индекс)

            if status == 'свободный':
                if country in ['британия', 'польша']:
                    if 'mobile' in type_column:
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
