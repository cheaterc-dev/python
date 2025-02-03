from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests

# Параметры Google Sheets
SPREADSHEET_ID = '1cdhZJvPLOJ1j9WxAE1c3oSUAHZpjE84zFV0l52xiR_k'  # ID таблицы
RANGE_NAME = 'UA GSM Numbers!A2:M9000'  # Диапазон, включая столбец оператора
SERVICE_ACCOUNT_FILE = 'apiprometheus-b2585815780f.json'  # Файл ключа API

# Параметры Telegram
TELEGRAM_BOT_TOKEN = '7715113550:AAGmXQXalU0YRit1DVKZMnfm_04r6nWuUeE'  # Токен бота
CHAT_ID = '770491204'  # ID чата для отправки уведомлений


def get_data():
    """Загружает данные из Google Sheets."""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])


def count_free_numbers_by_operator(data):
    """Подсчитывает количество свободных номеров по каждому оператору."""
    operator_counts = {}  # Словарь для хранения количества номеров по операторам

    for row in data:
        try:
            status = row[2].strip().lower()  # "Статус" (3-й столбец)
            operator = row[9].strip().lower()  # "Оператор" (10-й столбец)

            if status == 'свободный':  # Проверяем, что статус "свободный"
                if operator:  # Проверяем, что оператор указан
                    operator_counts[operator] = operator_counts.get(operator, 0) + 1
        except IndexError:
            continue  # Пропускаем строки с недостаточными данными

    return operator_counts


def send_telegram_alert(message):
    """Отправляет сообщение в Telegram."""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=payload)


def main():
    """Основная функция."""
    data = get_data()  # Загружаем данные из Google Sheets
    operator_counts = count_free_numbers_by_operator(data)  # Подсчитываем номера по операторам

    # Формируем сообщение для Telegram
    if operator_counts:
        message = "📊UA:\n"
        for operator, count in operator_counts.items():
            message += f"• {operator.capitalize()}: {count}\n"
    else:
        message = "❌ Нет свободных номеров в таблице."

    send_telegram_alert(message)  # Отправляем уведомление


if __name__ == "__main__":
    main()
