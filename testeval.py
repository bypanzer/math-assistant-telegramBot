from  numericstringparser import NumericStringParser

nsp = NumericStringParser()
result = nsp.eval('2+3')
print(result)
# 16.0

result = nsp.eval('23/3')
print(result)
