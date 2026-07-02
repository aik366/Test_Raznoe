import json
from config import PATH_DAT_DB, PATH_FASAD_DB, PATH_DATA_JSON, PATH_PLENKA_JSON, PATH_FAZAD_JSON


# Запись словаря в JSON
def write_json(filename, collection):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(collection, file, ensure_ascii=False, indent=4)


# Чтение словаря из JSON
def read_json(filename):
    with open(filename, encoding='utf-8') as file:
        return json.load(file)
   
   
def main():
    with open(PATH_FASAD_DB, 'r') as file:
        dict_fasad = {}
        for i in file.read().split('\n'):
            fasad_split = i.split('|')
            if i[0] == 'К':
                break
            dict_fasad[fasad_split[0]] = int(fasad_split[19])
    
        write_json(PATH_FAZAD_JSON, dict_fasad)


    with open(PATH_DAT_DB, 'r') as f:
        dict_write = {}
        f_read = f.read().replace("' ПЛЕНКА", "!").split('!')
        for i in f_read[1].strip().split('\n'):
            temp = i.split('|')
            dict_write[temp[0]] = [temp[1].capitalize(), temp[4]]

        write_json(PATH_PLENKA_JSON, dict_write)
        
        dict_read = read_json(PATH_DATA_JSON)
        for n, i in enumerate(f_read[0].strip().split('\n')[0:42]):
            if 6 <= n < 18:
                dict_read["plenka"][n-5] = int(i)
            if 28 <= n < 34:
                dict_read["zak_fz_kz"][n-28] = int(i)
            if n == 39:
                dict_read["tolshina"]["19"] = int(i)
            if n == 3:
                dict_read["tolshina"]["22"] = int(i)
            if n == 4:
                dict_read["tolshina"]["32"] = int(i)
  
        write_json(PATH_DATA_JSON, dict_read)
        
        


if __name__ == '__main__':
    main()
    print("Файл успешно записан")
