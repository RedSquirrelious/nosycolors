args=['A', 'C', 'd']
sql='SELECT fooid FROM foo WHERE bar IN (%s)' 
in_p=', '.join(list(map(lambda x: '%s', args)))
print(in_p)
sql = sql % in_p
print(sql)