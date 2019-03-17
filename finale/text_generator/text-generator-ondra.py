from random import shuffle


def get_message(znaky):
    out = []
    for key in znaky:
        for i in range(znaky[key]):
            out.append(key)
    shuffle(out)
    lengths = []
    for i in range(4):
        lengths.append(3)
        lengths.append(5)
    shuffle(lengths)
    out_str = ''

    num = 0
    for c in out:
        out_str += c
        num += len(c)
        if num > lengths[-1]:
            return get_message(znaky)
        if num == lengths[-1]:
            out_str += ' '
            num = 0
            lengths.pop()

    out_str = out_str[:-1]
    return out_str


def fixed_get_char(c):
    global word_len
    word_len += 1
    if c == ' ':
        if word_len == 4:
            word_len = 0
            return '000'
        word_len = 0
        return ''

    encoding = {
        'G': '001',
        'U': '010',
        'E': '011',
        'Q': '100',
        'T': '101',
        'F': '110',
        'I': '111',
        'Á': '',
    }
    return encoding[c]


def encode_fixed_length(plain):
    global word_len
    word_len = 0
    encoded = []
    for c in plain:
        encoded.append(fixed_get_char(c))
    return ''.join(encoded)


def prefix_get_char(c):
    global word_len
    word_len += 1
    if c == ' ':
        if word_len == 4:
            word_len = 0
            return '100'
        word_len = 0
        return ''

    encoding = {
        'G': '00',
        'U': '01',
        'E': '1100',
        'Q': '1101',
        'T': '1110',
        'F': '1111',
        'I': '101',
        'Á': '',
    }
    return encoding[c]


def encode_prefix(plain):
    global word_len
    word_len = 0
    encoded = []
    for c in plain:
        encoded.append(prefix_get_char(c))
    return ''.join(encoded)


znaky = {
    'G': 8,
    'U': 8,
    'E': 2,
    'Q': 2,
    'T': 2,
    'F': 2,
    'IÁ': 4,
}

for i in range(10):
    plain = get_message(znaky)
    print('"' + plain + '"')
    print(encode_fixed_length(plain), len(encode_fixed_length(plain)))
    print(encode_prefix(plain), len(encode_prefix(plain)))
