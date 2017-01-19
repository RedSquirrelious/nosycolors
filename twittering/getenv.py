import os
import ast

with open('../.env') as secrets:

	lies = dict(ast.literal_eval(secrets.read()))
	HOST = lies['HOST']

print(lies)