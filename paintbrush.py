import sys

background = '.'
grid = [[background]]

codepage  = '''................................................................................................................................'''
codepage += '''................................................................................................................................'''

def extendLeft():
    global grid, background
    grid = [[background] + row for row in grid]

def extendRight():
    global grid, background
    grid = [row + [background] for row in grid]

def extendDown():
    global grid, background
    grid = grid + [[background] * len(grid[0])]

def extendUp():
    global grid, background
    grid = [[background] * len(grid[0])] + grid

def output(grid, end = ''):
    print('\n'.join(map(''.join, grid)), end = end)

def execute(code):
    extendDown()
    extendRight()
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
            code = ''.join(char for char in code.replace('\n', '¶') if char in jelly.code_page)
        else:
            code = ''.join(jelly.code_page[ord(i)] for i in code)
        output(execute(code), '\n' if 'n' in sys.argv[1] else '')
