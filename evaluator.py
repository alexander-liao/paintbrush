'''
This is just to prevent evaluated inputs from behaving weirdly by reading out variables in paintbrush.py. However, this in no way makes using `eval` any safer. The `ast.literal_eval` version is much preferred except when you need to evaluate statements, not just literals. Otherwise, eval remains unsafe.
'''

def evaluate(k):
	'''
	This function just does `eval` with its argument.
	'''
	return eval(k)
