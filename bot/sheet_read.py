from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Iterable

from auth import get_credentials

SPREADSHEET_ID = '1EuqtYAOY3mhgjbOSljBEKcuj46NJU1jBRYymaWD_So4'
RANGE_TABLE = 'Расписание!A1:G'
RANGE_MATCHS = 'Матчи!A1:G'


def read_sheet_values(table_name, keys):
    """Читает значения из таблицы."""
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=table_name).execute()
        values = result.get('values')

        # Преобразование в словарь
        data = [dict(zip(keys, row)) for row in values[1:]]

        return data
    except HttpError as err:
        print(f"Ошибка при чтении таблицы: {err}")
        return []


def get_data_from_id(id: str, table_name: str, keys: list, key:str):
    final_result = []
    # keys = ["match_id", "team", "user_id", "fullname", "username", "phone", "pay"]
    list_of_values = read_sheet_values(table_name=table_name, keys=keys)
    for value in list_of_values:
        # print(value)
        if value.get(key) == id:
            final_result.append(value)
    return final_result


def normalize_data(data_value):
    list_of_buttons = []
    if not data_value or not isinstance(data_value, Iterable):
        return list_of_buttons
    for data in data_value:
        if len(data) >= 5:
            per_button_text = "%s (%s) %s\nгде: %s" % (
                data.get("date"), data.get("weekday"), data.get("time"), data.get("address"))
            list_of_buttons.append(per_button_text)

    return list_of_buttons


def read_sheet_values1(table_name):
    """Читает значения из таблицы."""
    try:
        service = build('sheets', 'v4', credentials=get_credentials())
        sheet = service.spreadsheets()

        # Чтение данных из диапазона RANGE_TABLE
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_TABLE).execute()
        values = result.get('values')

        # Преобразование в словарь
        keys = ["id", "date", "weekday", "address", "time"]
        data = [dict(zip(keys, row)) for row in values[1:]]

        # Чтение данных из диапазона RANGE_MATCHS
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_MATCHS).execute()
        match_values = result.get('values')

        # Преобразование данных из диапазона RANGE_MATCHS
        match_keys = ["match_id", "team", "user_id", "fullname", "username", "phone_number", "pay"]
        match_data = [dict(zip(match_keys, row)) for row in match_values[1:]]

        return data, match_data
    except HttpError as err:
        print(f"Ошибка при чтении таблицы: {err}")
        return [], []


def normalize_data2(data_value, match_data_value):
    list_of_buttons = []
    if not data_value or not isinstance(data_value, Iterable):
        return list_of_buttons
    for data in data_value:
        if len(data) >= 5:
            per_button_text = "%s (%s) %s\nгде: %s" % (
                data.get("date"), data.get("weekday"), data.get("time"), data.get("address"))
            list_of_buttons.append(per_button_text)

    return list_of_buttons


credentials = get_credentials()  # Получение учетных данных (предполагается, что у вас есть функция get_credentials())

# Чтение данных из таблицы
# data, match_data = read_sheet_values1(credentials)

# grouped_data = {}
# for match_row in match_data:
#     match_id = match_row["match_id"]
#     if match_id not in grouped_data:
#         grouped_data[match_id] = []
#     grouped_data[match_id].append(match_row)

# Вывод данных группированно по match_id
# print("Данные из диапазона RANGE_MATCHS:")
# for match_id, rows in grouped_data.items():
#     print(f"match_id {match_id}:")
#     for row in rows:
#         del row['match_id']  # Удаление ключа 'match_id'
#         print(row)

# if __name__ == '__main__':
    # print(get_data_from_id(id='3', table_name="Матчи!A1:G"))
