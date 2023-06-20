from auth import get_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from sheet_read import read_sheet_values
import pytz

SPREADSHEET_ID = '1EuqtYAOY3mhgjbOSljBEKcuj46NJU1jBRYymaWD_So4'


def delete(sheet_name: str, row_number: int):
    """Удаляет указанную строку из таблицы."""
    try:
        service = build('sheets', 'v4', credentials=get_credentials())

        # Вызываем Sheets API
        sheet = service.spreadsheets()
        sheet_metadata = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheet_id = None
        for s in sheets:
            if s['properties']['title'] == sheet_name:
                sheet_id = s['properties']['sheetId']
                break
        if sheet_id is None:
            return 'Неверное имя листа.'

        body = {
            'requests': [
                {
                    'deleteDimension': {
                        'range': {
                            'sheetId': sheet_id,
                            'dimension': 'ROWS',
                            'startIndex': row_number - 1,
                            'endIndex': row_number
                        }
                    }
                }
            ]
        }
        response = sheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body
        ).execute()
        return 'Строка успешно удалена из таблицы.'
    except HttpError as err:
        return str(err)


def unix(date, time):
    datetime_string = f'{date} {time}'
    datetime_format = '%d.%m.%y %H:%M'
    datetime_obj = datetime.strptime(datetime_string, datetime_format)
    unix_timestamp = int(datetime_obj.timestamp())
    current_unix_time = int(datetime.now(pytz.timezone("Asia/Almaty")).timestamp())

    return current_unix_time - unix_timestamp


def subtract_from_current_date(date_str):
    deadline = datetime.strptime(date_str, "%d.%m.%y")
    current_date = datetime.now().date()

    difference = current_date - deadline.date()
    return int(difference.days)


def delete_expired(table, keys):
    data = read_sheet_values(table, keys)
    # try:
    row_index = 2  # Начальное значение номера строки
    for i in data:
        print(unix(i.get("date"), i.get("time")) > 0)
        if unix(i.get("date"), i.get("time")) > 0:
            print(i, row_index)
            print(delete(table.split("!")[0], row_number=row_index))
        else:
            row_index += 1


if __name__ == '__main__':
    # mkeys = ["match_id", "date", "weekday", "address", "time"]
    # delete_expired("Расписание!A1:G", keys=mkeys)
    # Example usage
    print(subtract_from_current_date("10.06.23"))  # Subtract "29.06.23" from the current date
