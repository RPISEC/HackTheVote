import socket
import subprocess
import time
from pathlib import Path
import struct
from hashlib import sha256

HOST = 'hashconsulting.hackthe.vote'
#HOST = 'localhost'
PORT = 50007

if not Path('recovered_dictionary.txt').is_file():
    print('recover dictionary first')
    exit(1)

with open('debug.txt', 'w') as f:
    pass

with open('word.txt', 'w') as f:
    f.write("IBOHjYMP4wIvjXw\n")

def test_pow(chall, solution, hardness):
    h = sha256(chall + struct.pack("<Q", solution)).hexdigest()
    return int(h, 16) < 2 ** 256 / hardness

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    start_time = time.time()
    data = ""
    pow_challenge = s.recv(1024).strip()
    i = 0
    while True:
        if i % 1000000 == 0: print('Progress: %d' % i)
        if test_pow(pow_challenge, i, 9999999):
            s.send(str(i).encode() + b'\n')
            break
        i += 1

    while "send guesses\n" not in data:
        data += s.recv(1024).decode()
    with open('hashes.txt', 'w') as f:
        f.write('\n'.join([h + ':ahNgah7d' for h in data[:-14].split('\n')]))

    subprocess.run("hashcat -m 10 hashes.txt recovered_dictionary.txt --debug-mode=4 --debug-file=debug.txt -O -r all_rules.txt", shell=True)
    subprocess.run("hashcat -m 10 hashes.txt recovered_dictionary.txt --debug-mode=4 --debug-file=debug.txt -O -r all_rules.txt -r most_rules.txt", shell=True)
    subprocess.run("hashcat -m 10 hashes.txt recovered_dictionary.txt --debug-mode=4 --debug-file=debug.txt -O -r most_rules.txt -r all_rules.txt", shell=True)
    subprocess.run("hashcat -m 10 hashes.txt recovered_dictionary.txt --debug-mode=4 --debug-file=debug.txt -O -r all_rules.txt -r some_rules.txt -r some_rules.txt", shell=True)
    subprocess.run("hashcat -m 10 hashes.txt recovered_dictionary.txt --debug-mode=4 --debug-file=debug.txt -O -r some_rules.txt -r all_rules.txt -r some_rules.txt", shell=True)
    subprocess.run("hashcat -m 10 hashes.txt recovered_dictionary.txt --debug-mode=4 --debug-file=debug.txt -O -r some_rules.txt -r some_rules.txt -r all_rules.txt", shell=True)
    with open('debug.txt') as f:
        debug = f.read().strip().split('\n')
    print('\n'.join(sorted(debug, key=lambda x: x.split(':')[1])))
    recovered_rules = list(set([line.split(':')[1] for line in debug]))
    for i, r in enumerate(recovered_rules):
        print(i, r)
    compute_time = time.time()
    print(f"Computation took {compute_time - start_time} seconds. There are {60*5 - (compute_time - start_time)} seconds left.")

    print('input 10 rules to use, 1 per line')
    good_rules = list()
    while len(good_rules) < 10:
        try:
            good_rules.append(recovered_rules[int(input())])
        except ValueError:
            print('try again')
    with open('recovered_rules.txt', 'w') as f:
        f.write('\n'.join(good_rules))
    p = (
        subprocess.run(
            ["hashcat", "-r", "recovered_rules.txt", "--stdout", "word.txt"],
            capture_output=True,
        )
        .stdout.strip()
        .split(b"\n")
    )
    print(p)
    for pp in p:
        s.sendall(pp + b'\n')
    print(s.recv(1024))
    print(s.recv(1024))
