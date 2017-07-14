import sys
import re
import ast
from evaluator import evaluate

background = ' '
grid = [[background]]
mod = [[False]]
stack = []
x = 0
y = 0
ox = 0
oy = 0

hist = [(0, 0)]

##########
DEBUG = False
##########

mirrorhrz  = '''¡¢£¤¥¦©¬®µ½¿€ÆÇÐÑ×ØŒÞßæçðıȷñ÷øœþ !"#$%&'()*+,-.\\0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~¶'''
mirrorhrz += '''°¹²³⁴⁵⁶⁷⁸⁹⁺¯⁼⁽⁾▔▁▏▕▀▄▌▐┳┻┫┣━┃═║┬┴┤├┯┷┨┠↶↷↑↓←→↖↗↘↙⇧⇩⇦⇨↥↧↤↦⇑⇓⇐⇒ẒȦḂĊḊĖḞĠḢİĿṀṄȮṖṘṠṪẆẊẎŻạḅḍẹḥịḳḷṃṇọṛṣṭụṿẉỵẓȧḃċḋėḟġḣŀṁṅȯṗṙṡṫẇẋẏż«»‘’“”'''
mirrorver  = '''¡¢£¤¥¦©¬®µ½¿€ÆÇÐÑ×ØŒÞßæçðıȷñ÷øœþ !"#$%&'()*+,-.\\0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ]/[^_`abcdefghijklmnopqrstuvwxyz}|{~¶'''
mirrorver += '''°¹²³⁴⁵⁶⁷⁸⁹⁺¯⁼⁾⁽▁▔▕▏▄▀▌▐┻┳┣┫━┃═║┴┬├┤┷┯┠┨↷↶↓↑→←↘↙↖↗⇩⇧⇨⇦↧↥↦↤⇓⇑⇒⇐ẒȦḂĊḊĖḞĠḢİĿṀṄȮṖṘṠṪẆẊẎŻạḅḍẹḥịḳḷṃṇọṛṣṭụṿẉỵẓȧḃċḋėḟġḣŀṁṅȯṗṙṡṫẇẋẏż»«‘’“”'''
code_page  = '''¡¢£¤¥¦©¬®µ½¿€ÆÇÐÑ×ØŒÞßæçðıȷñ÷øœþ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~¶'''
code_page += '''°¹²³⁴⁵⁶⁷⁸⁹⁺¯⁼⁽⁾▁▔▏▕▄▀▌▐┻┳┫┣━┃═║┴┬┤├┷┯┨┠↶↷↓↑←→↙↘↗↖⇩⇧⇦⇨↧↥↤↦⇓⇑⇐⇒ẒȦḂĊḊĖḞĠḢİĿṀṄȮṖṘṠṪẆẊẎŻạḅḍẹḥịḳḷṃṇọṛṣṭụṿẉỵẓȧḃċḋėḟġḣŀṁṅȯṗṙṡṫẇẋẏż«»‘’“”'''
#               !-!!!!-----!!!--!!!!--!----!!-!--!------!!!!-!------------!!-!-!!---------------------------------!---------!------!-!-----!-!--
#               ---------------!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!-----------------------------------------------------------------!!----

syms = {}

def hreflect(grid):
	return [[mirrorhrz[code_page.find(col)] for col in row] for row in grid]

def vreflect(row):
	return [mirrorver[code_page.find(col)] for col in row]

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

def cut(grid, mod):
	grid = [[cell for cell in row] for row in grid]
	mod = [[cell for cell in row] for row in mod]
	for i in range(4):
		while mod and not any(mod[-1]):
			grid = grid[:-1]
			mod = mod[:-1]
		grid = list(map(list, zip(*grid)))[::-1]
		mod = list(map(list, zip(*mod)))[::-1]
	return grid

def output(grid, end = ''):
	global mod
	print('\n'.join(map(''.join, cut(grid, mod))), end = end)

def display(i, j, grid):
	global x, y, ox, oy, mod
	index = (j == y + oy and i == x + ox)
	index += (2 * mod[j][i])
	L = ' [({'[index]
	R = ' ])}'[index]
	return '%s%s%s' % (L, grid[j][i], R)

def debug(grid, end = None):
	if DEBUG:
		global x, y, ox, oy, mod
		print('\n'.join(map(''.join, [[display(i, j, grid) for i in range(len(grid[j]))] for j in range(len(grid))])))
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

def back():
	global hist, x, y
	hist = hist[-1:] + hist[:-1]
	x, y = hist[-1]

def forward():
	global hist, x, y
	hist = hist[1:] + hist[:1]
	x, y = hist[-1]

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
	readers = 'sb='
	readahead = False
	while index < len(code):
		if readahead:
			readahead = False
			if code[index] not in '0123456789({$\'':
				blocks += [code[index]]
				index += 1
		elif code[index] == '{':
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
				('\'(.)', lambda match: '!' + match.group(1)),
				('`(.)', lambda match: ast.literal_eval('"\\' + match.group(1) + '"')),
				('\"(\\.|[^\"])+\"', lambda match: ast.literal_eval(match.group(0))),
				('(\\d+)', lambda match: int(match.group(1))),
				('(\\d+(\\.\\d*)?|\\d*\\.\\d+)', lambda match: float(match.group(1))),
				('\\$\\D', lambda match: match.group(0)),
				('  ([^ ]| [^ ])+(  |$)', lambda match: None)
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
						result = pattern[1](match)
						if type(result) != type(None):
							blocks += [pattern[1](match)]
						matched = True
						break
				if not matched:
					blocks += [code[index]]
					readahead = blocks[-1] in readers
					index += 1
	index = 0
	while index < len(blocks):
		if blocks[index] == '$':
			blocks[index] += str(blocks[index + 1])
			blocks = blocks[:index + 1] + blocks[index + 2:]
		index += 1
	index = 0
	while index < len(blocks):
		if type(blocks[index]) == type('') and re.match('!.', blocks[index]):
			blocks[index] = blocks[index][1]
		index += 1
	if DEBUG:
		print(blocks)
	return blocks

def expand():
	while y + oy >= len(grid):
		extendDown()
	while y + oy < 0:
		extendUp()
	while x + ox >= len(grid[y + oy]):
		extendRight()
	while x + ox < 0:
		extendLeft()

def place(char):
	global grid, x, y, ox, oy
	if char == '\n':
		y += 1
		expand()
	elif char == '\b':
		x -= 2
	elif char == '\r':
		y += 1
		x = 0
	else:
		expand()
		grid[y + oy][x + ox] = char
		mod[y + oy][x + ox] = True
		debug(grid)
	return x, y

def __(content):
	if type(content) == type(0):
		return chr(content)
	else:
		return content

def _(sym):
	if type(sym) == type('') and sym.startswith('$') and sym != '$':
		try:
			return __(syms[sym[1]])
		except KeyError:
			raise SystemExit("[!] [FAIL] Identifier %s not defined" % sym[1])
	else:
		return __(sym)

def execute(code):
	if DEBUG:
		print('exec', code)
	if type(code) == type(''):
		code = block(code)
	global grid, background, x, y, mod, ox, oy, syms, hist
	index = 0
	modifier = False
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
				for k in range(len(blocks)):
					if blocks[k].startswith('$'):
						blocks[index] = args[int(blocks[index][1:]) - 1]
						used = True
			else:
				used = True
			for q in range(reps):
				for k in range(len(blocks)):
					if blocks[k] == '$0':
						blocks[k] = q
				execute(blocks)
			if not used:
				push(original)
		elif type(code[index]) != type(''):
			push(code[index])
		elif code[index] == 's':
			sides = pop() if type(peek()) == type(0) else 1
			if type(peek()) == type('') and len(peek()) == 1:
				char = pop()
			else:
				index += 1
				char = _(code[index])
			kx, ky = x, y
			for i in range(kx - sides + 1, kx + sides):
				for j in range(ky - sides + 1, ky + sides):
					x, y = i, j
					place(char)
			x, y = kx, ky
		elif code[index] == 'b':
			if type(peek()) == type('') and len(peek()) == 1:
				char = pop()
			else:
				index += 1
				char = _(code[index])
			updateBackground(char)
		elif code[index] == 'l':
			if type(peek()) == type(''):
				push(pop().lower())
			else:
				place(grid[y + oy][x + ox].lower())
		elif code[index] == 'u':
			if type(peek()) == type(''):
				push(pop().upper())
			else:
				place(grid[y + oy][x + ox].upper())
		elif code[index] == 'æ':
			push("abcdefghijklmnopqrstuvwxyz")
		elif code[index] == 'Æ':
			push('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
		elif code[index] == '=':
			if type(peek()) == type('') and len(peek()) == 1:
				char = pop()
			else:
				index += 1
				char = _(code[index])
			syms[char] = pop()
		elif code[index] in '+-*×:÷':
			oper = ['+', '-', '**', '*', '//', '/']['+-*×:÷'.find(code[index])]
			push(eval('pop() %s pop()' % oper))
		elif code[index] == '¥':
			push(str(pop()))
		elif code[index] == '£':
			push(input())
		elif code[index] == '€':
			push(ast.literal_eval(input()))
		elif code[index] == 'Ø':
			push(evaluate(input()))
		elif code[index] == 'Ñ':
			push(sys.stdin.readline())
		elif code[index] == 'ñ':
			push(sys.stdin.read(1))
		elif code[index] == 'Œ':
			push(syms[sys.stdin.read(1)])
		elif code[index] in '↓↑←→↙↘↗↖⇩⇧⇦⇨':
			i = '↓↑←→↙↘↗↖⇩⇧⇦⇨'.find(code[index])
			dx = [0, 0, -1, 1, -1, 1, 1, -1][i % 8]
			dy = [1, -1, 0, 0, 1, 1, -1, -1][i % 8]
			wrap = i >= 8
			arg = pop()
			if type(arg) == type(0):
				x += dx * arg
				y += dy * arg
				if wrap:
					y = y % len(grid)
					x = x % len(grid[y + oy])
				else:
					expand()
			elif type(arg) == type(''):
				for i in range(len(arg)):
					kx, ky = x, y
					place(arg[i])
					if (x, y) == (kx, ky):
						x += dx
						y += dy
					if wrap:
						y = y % len(grid)
						x = x % len(grid[y + oy])
					else:
						expand()
			else:
				x += dx
				y += dy
				if wrap:
					y = y % len(grid)
					x = x % len(grid[y + oy])
				else:
					expand()
		elif code[index] == '▁':
			shift = pop() if type(peek()) == type(0) else 1
			grid = grid[:-shift] or [[background]]
			mod = mod[:-shift] or [[False]]
			while y + oy >= len(grid):
				y -= 1
		elif code[index] == '▔':
			shift = pop() if type(peek()) == type(0) else 1
			grid = grid[shift:] or [[background]]
			mod = mod[shift:] or [[False]]
			y -= shift
		elif code[index] == '▏':
			shift = pop() if type(peek()) == type(0) else 1
			grid = [row[shift:] for row in grid]
			if not any(grid):
				grid = [[background]]
				y = 0
			mod = [row[shift:] for row in mod]
			if not any(mod):
				mod = [[False]]
				y = 0
			x -= shift
		elif code[index] == '▕':
			shift = pop() if type(peek()) == type(0) else 1
			grid = [row[:-shift] for row in grid]
			if not any(grid):
				grid = [[background]]
			mod = [row[:-shift] for row in mod]
			if not any(mod):
				mod = [[False]]
			while y + oy >= len(grid):
				y -= 1
			while x + ox >= len(grid[y + oy]):
				x -= 1
		elif code[index] in '▄┻':
			K = hreflect if not modifier else (lambda x: x)
			grid += K(grid[::-1][code[index] == '┻':])
			mod += mod[::-1][code[index] == '┻':]
		elif code[index] in '▀┳':
			K = hreflect if not modifier else (lambda x: x)
			grid = K(grid[::-1][code[index] == '┳':]) + grid
			mod = mod[::-1][code[index] == '┳':] + mod
			oy += len(grid) // 2
		elif code[index] in '▌┫':
			K = vreflect if not modifier else (lambda x: x)
			grid = [K(row[::-1][code[index] == '┫':]) + row for row in grid]
			mod = [row[::-1][code[index] == '┫':] + row for row in mod]
			ox += len(grid[y + oy]) // 2
		elif code[index] in '▐┣':
			K = vreflect if not modifier else (lambda x: x)
			grid = [row + K(row[::-1][code[index] == '┣':]) for row in grid]
			mod = [row + row[::-1][code[index] == '┣':] for row in mod]
		elif code[index] == '━':
			span = pop() if type(peek()) == type(0) else 1
			grid = [grid[row] for row in range(len(grid)) if abs(row - (y + oy)) >= span] or [[background]]
			mod = [mod[row] for row in range(len(mod)) if abs(row - (y + oy)) >= span] or [[False]]
			while y + oy >= len(grid):
				y -= 1
		elif code[index] == '┃':
			span = pop() if type(peek()) == type(0) else 1
			grid = [[row[col] for col in range(len(row)) if abs(col - (x + ox)) >= span] for row in grid]
			if not any(grid):
				grid = [[background]]
			mod = [[row[col] for col in range(len(row)) if abs(col - (x + ox)) >= span] for row in mod] or [[False]]
			if not any(mod):
				mod = [[False]]
			while y + oy >= len(grid):
				y -= 1
			while x + ox >= len(grid[y + oy]):
				x -= 1
		elif code[index] in '┴┬':
			rows = pop() if type(peek()) == type(0) else 1
			grid.insert(y + oy + (code[index] == '┬'), *[[background] * len(grid[y + oy]) for i in range(rows)])
			mod.insert(y + oy + (code[index] == '┬'), *[[False] * len(mod[y + oy]) for i in range(rows)])
			y += code[index] == '┴'
		elif code[index] in '┤├':
			cols = pop() if type(peek()) == type(0) else 1
			for row in range(len(grid)):
				grid[row].insert(x + ox + (code[index] == '├'), *([background] * cols))
				mod[row].insert(x + ox + (code[index] == '├'), *([False] * cols))
			x += code[index] == '┤'
		elif code[index] in '┷┯':
			reps = pop() if type(peek()) == type(0) else 1
			grid.insert(y + oy + (code[index] == '┯'), *[[col for col in grid[y + oy]] for i in range(reps)])
			mod.insert(y + oy + (code[index] == '┯'), *[[col for col in mod[y + oy]] for i in range(reps)])
			y += code[index] == '┷'
		elif code[index] in '┨┠':
			reps = pop() if type(peek()) == type(0) else 1
			for row in range(len(grid)):
				grid[row].insert(x + ox + (code[index] == '┠'), *([grid[row][x + ox]] * reps))
				mod[row].insert(x + ox + (code[index] == '┠'), *([mod[row][x + oy]] * reps))
			x += code[index] == '┨'
		elif code[index] == '═':
			span = pop() if type(peek()) == type(0) else 1
			for i in range(-span + 1, span):
				try:
					grid[y + oy + i] = [background] * len(grid[y + oy])
					mod[y + oy + i] = [False] * len(mod[y + oy])
				except IndexError:
					pass
		elif code[index] in '↧↥':
			reps = pop() if type(peek()) == type(0) else 1
			k = len(grid)
			grid = [[col for col in row] for row in grid * (reps + 1)]
			mod = [[col for col in row] for row in mod * (reps + 1)]
			if code[index] == '↥':
				oy += k * reps
		elif code[index] in '↤↦':
			reps = pop() if type(peek()) == type(0) else 1
			k = len(grid[0])
			grid = [[col for col in row * (reps + 1)] for row in grid]
			mod = [[col for col in row * (reps + 1)] for row in mod]
			if code[index] == '↤':
				ox += k * reps
		elif code[index] in '⇓⇑':
			reps = pop() if type(peek()) == type(0) else 1
			y = (y + oy) * (reps + 1) + (code[index] == '⇑') * reps
			oy = 0
			g = []
			for row in grid:
				for i in range(reps + 1):
					g.append([col for col in row])
			grid = g
			m = []
			for row in mod:
				for i in range(reps + 1):
					m.append([col for col in row])
			mod = m
		elif code[index] in '⇐⇒':
			reps = pop() if type(peek()) == type(0) else 1
			x = (x + ox) * (reps + 1) + (code[index] == '⇐') * reps
			ox = 0
			grid = [sum([[col] * (reps + 1) for col in row], []) for row in grid]
			mod = [sum([[col] * (reps + 1) for col in row], []) for row in mod]
		elif code[index] == '║':
			span = pop() if type(peek()) == type(0) else 1
			for row in range(len(grid)):
				for i in range(-span + 1, span):
					try:
						grid[row][x + ox + i] = background
						mod[row][x + ox + i] = False
					except IndexError:
						pass
		elif code[index] == '»':
			index += 1
			push(code[index])
		elif code[index] == '«':
			pop()
		elif code[index] == '↶':
			back()
			index += 1
			modifier = False
			continue # Hack to bypass adding this move to the history
		elif code[index] == '↷':
			forward()
			index += 1
			modifier = False
			continue # Hack to bypass adding this move to the history
		elif code[index] == '!':
			mod = [[True for col in row] for row in mod]
		elif code[index] == '¡':
			mod = [[False for col in row] for row in mod]
		elif code[index] == '?':
			for row in range(len(mod)):
				for col in range(len(mod[row])):
					if grid[row][col] == background:
						mod[row][col] = False
		elif code[index] == '@':
			top = pop()
			sec = pop()
			push(top)
			push(sec)
		elif code[index] == '¦':
			array = list(str(pop()))
			for value in array[::-1]:
				push(value)
		elif code[index] == '¿':
			index += 1
			if peek():
				execute(code[index])
		elif code[index] == '¤':
			index += 1
			if not peek():
				execute(code[index])
		elif code[index] == 'œ':
			modifier = True
			index += 1
			continue
		else:
			push(code[index])
		index += 1
		hist += [(x, y)]
		modifier = False
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
			code = code.rstrip()
		if 'u' in sys.argv[1]:
			code = ''.join(char for char in code.replace('\n', '¶') if char in code_page)
		else:
			code = ''.join(code_page[ord(i)] for i in code)
		DEBUG = 'y' in sys.argv[1]
		(debug if DEBUG else output)(execute(code), '\n' if 'n' in sys.argv[1] else '')
