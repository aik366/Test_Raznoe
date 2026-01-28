def main(freza=150, glubina=2.0):
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


def blenda(freza=150, glubina=2.0):
    with open('DATA/bl_input.txt', 'r', encoding='utf-8') as f:
        st = ''
        temp = [i.split('\n\n')[:-1] for i in f.read().split(']')[1:]]
        for i in temp:
            t_x, t_y = 0.0, 0.0
            st += (
                f'@ ROUT, 0 : "{freza}", 0, "1", 0, {glubina}, "", 1, 18, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, '
                f'0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, -1, 0, 5000, 18000, 0, 8000, "{freza}", 103, 1, 0, 0, 90, 0, 0, 0, 0, 0, 0, '
                f'90, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "", 0, 0, 0, 0, 0, 0, 0, 0, 0, "", 5, 0, 20, 80, 60, 0, "", "", "ROUT", '
                f'0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2000, 0, 0.1, 0, 0, 0, 1, 110\n')
            for n,  j in enumerate(i):
                if n == 0:
                    sp_start = j.split('\n')[3:5]
                    start_x, start_y = sp_start[0].replace('l', 'LPX')[2:], sp_start[1].replace('w', 'LPY')[2:]
                    st += f'  @ START_POINT, 0 : {start_x}, {start_y}, 0\n'
                else:
                    sp = j.split('\n')[2:4]
                    line_x, line_y = sp[0].replace('l', 'LPX')[2:], sp[1].replace('w', 'LPY')[2:]
                    if line_x[0] == '@':
                        l_x = float(line_x[1:]) + t_x
                        t_x = l_x
                        line_x = f'{start_x}+({l_x:.3f})'
                    if line_y[0] == '@':
                        l_y = float(line_y[1:]) + t_y
                        t_y = l_y
                        line_y = f'{start_y}+({l_y:.3f})'
                    st += f'  @ LINE_EP, 0 : {line_x}, {line_y}, 0, 0, 0, 0, 0, 0, 0\n'
            st += '  @ ENDPATH, 0 :\n\n'
    print(st)
    with open('DATA/bl_output.txt', 'w') as f:
        f.write(st)


if __name__ == '__main__':
    # main(144, 4)
    blenda(136, 1.5)
