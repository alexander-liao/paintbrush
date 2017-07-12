import sys
import re
import ast

background = ' '
grid = [[background]]
mod = [[False]]
stack = []
x = 0
y = 0
ox = 0
oy = 0

##########
DEBUG = False
##########

code_page  = '''¡¢£¤¥¦©¬®µ½¿€ÆÇÐÑ×ØŒÞßæçðıȷñ÷øœþ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~¶'''
code_page += '''°¹²³⁴⁵⁶⁷⁸⁹⁺¯⁼⁽⁾ƁƇƊƑƓƘⱮƝƤƬƲȤɓƈɗƒɠɦƙɱɲƥʠɼʂƭʋȥẠḄḌẸḤỊḲḶṂṆỌṚṢṬỤṾẈỴẒȦḂĊḊĖḞĠḢİĿṀṄȮṖṘṠṪẆẊẎŻạḅḍẹḥịḳḷṃṇọṛṣṭụṿẉỵẓȧḃċḋėḟġḣŀṁṅȯṗṙṡṫẇẋẏż«»‘’“”'''

def extendLeft():
    global grid, background, ox, mod
    grid = [[background] + row for row in grid]
    mod = [[False] + row for row in mod]
    ox += 1

def extendRight():
    global grid, background, mod
    grid = [row + [background] for row in grid]
    mod = [row + [False] for row in mod]

def extendDown():
    global grid, background, mod
    grid = grid + [[background] * len(grid[0])]
    mod = mod + [[False] * len(mod[0])]

def extendUp():
    global grid, background, oy, mod
    grid = [[background] * len(grid[0])] + grid
    mod = [[False] * len(mod[0])] + mod
    oy += 1

def output(grid, end = ''):
    print('\n'.join(map(''.join, grid)), end = end)

def debug(grid, end = None):
    if DEBUG:
        global x, y, ox, oy
        print('\n'.join(map(''.join, [[' ['[j == y + oy and x + ox == i] + grid[j][i] + ' ]'[j == y + oy and x + ox == i] for i in range(len(grid[j]))] for j in range(len(grid))])))
        print('-' * max(map(len, grid)) * 3)

def push(value):
    stack.append(value)

def peek(default = None):
    return stack[-1] if stack else default

def pop(default = None):
    return stack.pop() if stack else default

def updateBackground(bkg):
    global grid, mod, background
    background = bkg
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if not mod[i][j]:
                grid[i][j] = background

class func():
    def __init__(self, code):
        self.code = code
    def __str__(self):
        return 'func:{%s}' % self.code
    def __repl__(self):
        return str(self)

def block(code):
    blocks = []
    index = 0
    while index < len(code):
        if code[index] == '{':
            brackets = 1
            inner = ''
            while brackets:
                index += 1
                if code[index] == '{':
                    brackets += 1
                elif code[index] == '}':
                    brackets -= 1
                    if not brackets:
                        index += 1
                        break
                inner += code[index]
            blocks += [func(inner)]
        else:
            patterns = [
                ('\'(.)', lambda match: match.group(1)),
                ('`(.)', lambda match: ast.literal_eval('\\' + match.group(1))),
                ('\"(\\.|[^\"])+\"', lambda match: ast.literal_eval(match.group(0))),
                ('(\\d+(\\.\\d*)?|\\d*\\.\\d+)', lambda match: int(match.group(1)))
            ]
            matched = False
            if code[index] == ';':
                index += 1
            elif code[index] == '(':
                bracketed = '('
                brackets = 1
                while brackets:
                    index += 1
                    if code[index] == '(':
                        brackets += 1
                    elif code[index] == ')':
                        brackets -= 1
                    bracketed += code[index]
                blocks += [ast.literal_eval(bracketed)]
            else:
                for pattern in patterns:
                    match = re.match(pattern[0], code[index:])
                    if match:
                        index += match.end()
                        blocks += [pattern[1](match)]
                        matched = True
                        break
                if not matched:
                    blocks += [code[index]]
                    index += 1
    index = 0
    while index < len(blocks):
        if blocks[index] == '$':
            blocks[index] += str(blocks[index + 1])
            blocks = blocks[:index + 1] + blocks[index + 2:]
        index += 1
    if DEBUG:
        print(blocks)
    return blocks

def expand():
    while y + oy >= len(grid):
        extendDown()
    while y + oy < 0:
        extendUp()
    while x + ox >= len(grid[y]):
        extendRight()
    while x + ox < 0:
        extendLeft()

def place(char):
    global grid, x, y, ox, oy
    if char == '\n':
        y += 1
        expand()
    elif char == '\b':
        x -= 1
    else:
        expand()
        grid[y + oy][x + ox] = char
        mod[y + oy][x + ox] = True
        debug(grid)
    return x, y

def execute(code):
    debug('exec', code)
    if type(code) == type(''):
        code = block(code)
    global grid, background, x, y, mod
    index = 0
    while index < len(code):
        if type(code[index]) == type(func('')):
            reps = 1
            inner = code[index].code
            blocks = block(inner)
            used = False
            if type(peek()) == type(1):
                reps = pop()
            original = pop()
            if type(original) != type(None):
                if type(original) != type(()):
                    args = (original,)
                for index in range(len(blocks)):
                    if blocks[index].startswith('$'):
                        blocks[index] = args[int(blocks[index][1:]) - 1]
                        used = True
            else:
                used = True
            for q in range(reps):
                for index in range(len(blocks)):
                    if blocks[index] == '$0':
                        blocks[index] = q
                        used = True
                execute(blocks)
            if not used:
                push(original)
        elif type(code[index]) != type(''):
            push(code[index])
        elif code[index] == 's':
            sides = pop() if type(peek()) == type(0) else 1
            index += 1
            char = code[index] if type(code[index]) == type('') else chr(int(code[index]))
            kx, ky = x, y
            for i in range(kx - sides + 1, kx + sides):
                for j in range(ky - sides + 1, ky + sides):
                    x, y = i, j
                    place(char)
        elif code[index] == 'b':
            index += 1
            updateBackground(code[index])
        elif code[index] in '>v<^]_[¯':
            i = '>v<^]_[¯'.find(code[index])
            dx = [1, 0, -1, 0, 1, 0, -1, 0][i]
            dy = [0, 1, 0, -1, 0, 1, 0, -1][i]
            wrap = i > 3
            arg = pop()
            if type(arg) == type(0):
                x += dx * arg
                y += dy * arg
                if wrap:
                    y = y % len(grid)
                    x = x % len(grid[y])
                else:
                    expand()
            elif type(arg) == type(''):
                for i in range(len(arg)):
                    place(arg[i])
                    x += dx
                    y += dy
                    if wrap:
                        y = y % len(grid)
                        x = x % len(grid[y])
                    else:
                        expand()
            else:
                x += dx
                y += dy
                if wrap:
                    y = y % len(grid)
                    x = x % len(grid[y])
                else:
                    expand()
        elif code[index] == '»':
            index += 1
            push(code[index])
        elif code[index] == '«':
            pop()
        else:
            push(code[index])
        index += 1
    return grid

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit('Paintbrush: python paintbrush <initial flags> <filename/program> <arg1> ...: f for file, u for unicode encoding for input, n for trailing newline, k to trim the program, y to debug')
    else:
        if 'f' in sys.argv[1]:
            code = open(sys.argv[2], 'r').read()
        else:
            code = sys.argv[2]
        if 'k' in sys.argv[1]:
            code = code.strip()
        if 'u' in sys.argv[1]:
            code = ''.join(char for char in code.replace('\n', '¶') if char in code_page)
        else:
            code = ''.join(code_page[ord(i)] for i in code)
        DEBUG = 'y' in sys.argv[1]
        (debug if DEBUG else output)(execute(code), '\n' if 'n' in sys.argv[1] else '')
