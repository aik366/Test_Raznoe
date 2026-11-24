import json


    
# with open("test.json", "w", encoding="utf-8") as file:
#     json.dump(d, file, ensure_ascii=False, indent=4)
text = f'{"Тикер":<6}{"Кол-во":<6} {"Средняя":<8}{"Текущая":<8}{"Доход":<8}{"За день":<8}'
with open("test.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    
    for key in data:
        print(f'{key:<6}') 
        print(text)      
        for key, vol in data[key].items():
            print(f'{key:<6}{vol["Кол-во"]:<6} {vol["Средняя"]:<8}{vol["Текущая"]:<8}{vol["Доход"]:<8}{vol["За день"]:<8}')
        print()

                                 