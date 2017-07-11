import sys

background = ' '
grid = [[background]]
x = 0
y = 0

code_page  = '''¡¢£¤¥¦©¬®µ½¿€ÆÇÐÑ×ØŒÞßæçðıȷñ÷øœþ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~¶'''
code_page += '''°¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ƁƇƊƑƓƘⱮƝƤƬƲȤɓƈɗƒɠɦƙɱɲƥʠɼʂƭʋȥẠḄḌẸḤỊḲḶṂṆỌṚṢṬỤṾẈỴẒȦḂĊḊĖḞĠḢİĿṀṄȮṖṘṠṪẆẊẎŻạḅḍẹḥịḳḷṃṇọṛṣṭụṿẉỵẓȧḃċḋėḟġḣŀṁṅȯṗṙṡṫẇẋẏż«»‘’“”'''

def extendLeft():
    global grid, background, x
    grid = [[background] + row for row in grid]
    x += 1

def extendRight():
    global grid, background
    grid = [row + [background] for row in grid]

def extendDown():
    global grid, background, y
    grid = grid + [[background] * len(grid[0])]
    y += 1

def extendUp():
    global grid, background
    grid = [[background] * len(grid[0])] + grid

def output(grid, end = ''):
    print('\n'.join(map(''.join, grid)), end = end)

def execute(code):
    global grid, background, x, y
    index = 0
    while index < len(code):
        if code[index] == 's':
            index += 1
            if index < len(code):
                grid[y][x] = code[index].replace('¶', '\n')
            else:
                raise RuntimeError('set character token placed at EOF')
        elif code[index] == '>':
            x += 1
            if x >= len(grid[y]):
                extendRight()
        elif code[index] == '<':
            x -= 1
            if x < 0:
                extendLeft()
        elif code[index] == 'v':
            y += 1
            if y >= len(grid):
                extendDown()
        elif code[index] == '^':
            y -= 1
            if y < 0:
                extendUp()
        index += 1
    return grid # TODO

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit('Paintbrush: python paintbrush <initial flags> <filename/program> <arg1> ...: f for file, u for unicode encoding for input, n for trailing newline')
    else:
        if 'f' in sys.argv[1]:
            code = open(sys.argv[2], 'r').read()
        else:
            code = sys.argv[2]
        if 'u' in sys.argv[1]:
            code = ''.join(char for char in code.replace('\n', '¶') if char in code_page)
        else:
            code = ''.join(code_page[ord(i)] for i in code)
        output(execute(code), '\n' if 'n' in sys.argv[1] else '')
