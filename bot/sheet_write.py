from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials

# Если требуется изменить эти области, удалите файл token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Идентификатор и диапазон таблицы.
SPREADSHEET_ID = '1EuqtYAOY3mhgjbOSljBEKcuj46NJU1jBRYymaWD_So4'
RANGE_NAME = 'Пользователи!A:E'


def write_registration(range_name: str, list_of_values: list):
    """Пример использования Sheets API.
    Записывает данные в таблицу.
    """
    try:
        service = build('sheets', 'v4', credentials=get_credentials())

        # Вызываем Sheets API
        sheet = service.spreadsheets()
        values = [list_of_values]
        body = {
            'values': values
        }
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body,
            insertDataOption='INSERT_ROWS',
        ).execute()
        return 'Данные успешно записаны в таблицу.'
    except HttpError as err:
        return str(err)



