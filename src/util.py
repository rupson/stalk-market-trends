def newLineOrPipe(i):
    if i % 4 == 0:
        return '\n'
    else:
        return ' | '


def nullIfUndefined(data, index):
    try:
        return data[index]
    except:
        return 'null'

def dataOrDefault(data, index, default):
    try:
        return data[index]
    except:
        return default

def isHeaderLine(line):
    return line[0].lower() == 'date'