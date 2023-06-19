from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials

SPREADSHEET_ID = '1EuqtYAOY3mhgjbOSljBEKcuj46NJU1jBRYymaWD_So4'


def update_registration(range_name: str, row_index: int, list_of_values: list):
    """Пример использования Sheets API.
    Обновляет данные в таблице для указанной строки.
    """
    try:
        service = build('sheets', 'v4', credentials=get_credentials())

        # Вызываем Sheets API
        sheet = service.spreadsheets()
        values = [list_of_values]
        body = {'values': values}
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{range_name}!H{row_index}:H{row_index}',
            valueInputOption='RAW',
            body=body
        ).execute()
        return 'Данные успешно обновлены в таблице.'
    except HttpError as err:
        return str(err)

