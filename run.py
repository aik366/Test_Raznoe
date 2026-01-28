import json


def main():
    d = {}
    with open('DATA/DAT.DB', 'r') as f:
        for i in f.read().replace("' ПЛЕНКА", "!").split('!')[1].strip().split('\n'):
            temp = i.split('|')
            d[temp[0]] = [temp[1].capitalize(), temp[2]]

    with open('DATA/plenka.json', 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
