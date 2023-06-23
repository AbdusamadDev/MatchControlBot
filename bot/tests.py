# state = {}
# state['data1'] = ("Значение 1", "Значение 2", "Значение 3")
#
# # Запись новых значений в поле 'data1'
# state['data1'] = ("Новое значение 1", "Новое значение 2")
#
# print(state['data1'])  # Выведет: ("Новое значение 1", "Новое значение 2")
print(list(range(1, 10)))
a = [chr(i) for i in range(1, 1000) if i not in list(range(1, 10)) + [46]]
for i in a:
    print(i)

for i in list(range(1, 10)) + [46]:
    print(i)
