l = "[0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8]"

countbits = "(literal[num & 0xFF] + literal[(num >> 8) & 0xFF] + literal[(num >> 16) & 0xFF] + literal[(num >> 24) & 0xFF] + literal[(num >> 32) & 0xFF] + literal[(num >> 40) & 0xFF] + literal[(num >> 48) & 0xFF] + literal[(num >> 56) & 0xFF])"
bitflip = "vote ^ (((countbits(random & 12297829382473034410) % 2) << 0) | ((countbits(random & 14757395258967641292) % 2) << 1) | ((countbits(random & 17361641481138401520) % 2) << 2) | ((countbits(random & 18374966859414961920) % 2) << 3) | ((countbits(random & 18446462603027742720) % 2) << 4) | ((countbits(random & 18446744069414584320) % 2) << 5))"
recover = "((countbits(encrypted_vote & 12297829382473034410) % 2) << 0) | ((countbits(encrypted_vote & 14757395258967641292) % 2) << 1) | ((countbits(encrypted_vote & 17361641481138401520) % 2) << 2) | ((countbits(encrypted_vote & 18374966859414961920) % 2) << 3) | ((countbits(encrypted_vote & 18446462603027742720) % 2) << 4) | ((countbits(encrypted_vote & 18446744069414584320) % 2) << 5)"


def interp(s):
    while "countbits" in s:
        start = s.index("countbits")
        end = s[start:].index(")") + start + 1
        exp = s[start + 9 : end + 1]
        s = s[:start] + countbits.replace("num", exp) + s[end:]
    return s


bitflip = interp(bitflip)
recover = interp(recover)

print(l)
print(bitflip)
print(recover)
