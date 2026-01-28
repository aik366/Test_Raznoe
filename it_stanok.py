def main(freza=150, glubina=2):
    st = (
        f'@ ROUT, 0 : "{freza}", 0, "1", 0, {glubina}, "", 1, 18, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, '
        f'0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, -1, 0, 5000, 18000, 0, 8000, "{freza}", 103, 1, 0, 0, 90, 0, 0, 0, 0, 0, 0, '
        f'90, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "", 0, 0, 0, 0, 0, 0, 0, 0, 0, "", 5, 0, 20, 80, 60, 0, "", "", "ROUT", '
        f'0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2000, 0, 0.1, 0, 0, 0, 1, 110\n')
    with open('DATA/1.ply', 'r', encoding='utf-8') as f:
        ply = [i for i in f.read().split('U')[-1].strip().split('\n')]
        start_point = ply[0].split(' ')[:2]
        st += f'  @ START_POINT, 0 : {start_point[0][1:]}, {start_point[1][1:]}, 0\n'
        for i in ply[2:]:
            point = i.split(' ')[:2]
            st += f'  @ LINE_EP, 0 : {point[0][1:]}, {point[1][1:]}, 0, 0, 0, 0, 0, 0, 0\n'
        st += '  @ ENDPATH, 0 :\n'

    with open('DATA/it_stanok.txt', 'w') as f:
        f.write(st)


if __name__ == '__main__':
    main(144, 4)
