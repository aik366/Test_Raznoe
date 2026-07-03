import json

PATH_IN = r'\\office\\фасады мдф\\Dati_c\\dati'
PATH_OUT = r'\\Office\\555\bimgorbot\\price'
PATH_DATA = 'DATA\data.json'


def main():
    d = {}
    with open(f"{PATH_IN}\DAT.DB", 'r') as f:
        f_read = f.read().replace("' ПЛЕНКА", "!").split('!')
        # for i in f_read[1].strip().split('\n'):
        #     temp = i.split('|')
        #     d[temp[0]] = [temp[1].capitalize(), temp[2]]
        
        with open(PATH_DATA, encoding='utf-8') as file:
            dct = json.load(file)
            
        for n, i in enumerate(f_read[0].strip().split('\n')[6:18], 1):
            dct["plenka"][n] = int(i)
            
        with open(PATH_DATA, 'w', encoding='utf-8') as f:
            json.dump(dct, f, ensure_ascii=False, indent=4)
            
        # with open(PATH_DATA, encoding='utf-8') as file:
        #     dct = json.load(file)
        #     for i in dct["plenka"]:
        #         print(i)

    # with open(f"{PATH_OUT}\plenka.json", 'w', encoding='utf-8') as f:
    #     json.dump(d, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
