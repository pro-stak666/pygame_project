def from_10_to_16(integer):
    if integer < 16777216:
        a = hex(integer)[2:]
        return a
    else:
        return 'xxxxxx'


def into_the_correct_type(s):
    a = ''.join(s[:-1])
    return a + (62 - len(a)) * ' ' + s[-1]


def psevdo_hex_browser(name):
    file = open(name, 'rb')
    filelines = file.read()
    chunks = [filelines[i:i + 16] for i in range(0, len(filelines), 16)]
    print('          00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f\n')
    for i in range(len(chunks)):
        s = []
        r = from_10_to_16(i)
        s.append((5 - len(r)) * '0' + r + '0    ')
        for j in range(len(chunks[i])):
            r = from_10_to_16(chunks[i][j])
            s.append((2 - len(r)) * '0' + r + ' ')
        s1 = ''
        for j in range(len(chunks[i])):
            if chr(chunks[i][j]).isprintable():
                s1 += chr(chunks[i][j])
            else:
                s1 += '.'
        s.append(s1)
        print(into_the_correct_type(s))


psevdo_hex_browser('data.txt')