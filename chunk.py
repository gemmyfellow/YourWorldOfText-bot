

def chunk(iterable, size):
    if not iterable or size <= 0:
        return []
    i = 0
    while i < len(iterable):
        j = i + size
        yield iterable[i:j]
        i = j
   
   
print([chunk for chunk in chunk([1,2,3,4,5,6,7,8,9],4)]) 