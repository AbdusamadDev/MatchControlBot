from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Iterable

from auth import get_credentials

SPREADSHEET_ID = '1EuqtYAOY3mhgjbOSljBEKcuj46NJU1jBRYymaWD_So4'


def read_sheet_values(table_name, keys):
    service = build('sheets', 'v4', credentials=get_credentials())
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=table_name).execute()
    values = result.get('values')

    data = [dict(zip(keys, row)) for row in values[1:]]

    return data


def get_data_from_id(id: str, table_name: str, keys: list, key: str):
    list_of_values = read_sheet_values(table_name=table_name, keys=keys)
    # print(list_of_values)
    final_result = [value for value in list_of_values if value.get(key) == id]
    return final_result


def normalize_data(data_value):
    list_of_buttons = []
    if not data_value or not isinstance(data_value, Iterable):
        return list_of_buttons
    for data in data_value:
        if len(data) >= 5:
            per_button_text = "%s (%s) %s Где: %s\n" % (
                data.get("date"), data.get("weekday"), data.get("time"), data.get("address"))
            list_of_buttons.append(per_button_text)

    return list_of_buttons


if __name__ == '__main__':
    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    regular_user = get_data_from_id(
        table_name="Матчи!A:I",
        id="5122119678",
        keys=match_keys,
        key="user_id"
    )
    print(regular_user)