#!/usr/bin/env python2
"""
Fills the pcap with a shit ton of login attempts
and a legitimate one that sends the server into "lockdown"
"""

from random import random, randint, choice
from string import digits, ascii_letters, punctuation

from pwn import remote

HOST, PORT = 'email.clinton.io', 9999
num_sessions = 1000  # Number of fake guesses before locking down
ascii = digits + ascii_letters + punctuation

users = {
    'clinton': 'IAmGoingToBeTheNextPresidentAndIWillDestroyTrump',
    'bernie': 'tH3_h4nDfUl_0n_top',
    'Jeb': '!',
    'trump': 'China'
}


def rand_login():
    s = remote(HOST, PORT)

    # login
    s.recvuntil(': ')
    user = choice(users.keys())
    s.sendline(user)

    # pass
    # Sometimes log in correctly, otherwise use a random pass
    # Never login as clinton
    s.recvuntil(': ')
    pwd = users[user] if user != 'clinton' and random() < 0.25 else ''.join([choice(ascii) for j in xrange(randint(5, 50))])
    s.sendline(pwd)

    s.recvall()
    s.close()


def legit_login():
    # Send it into lockdown
    s = remote(HOST, PORT)
    user = 'clinton'

    # login
    s.recvuntil(': ')
    s.sendline(user)

    # pass
    s.recvuntil(': ')
    s.sendline(users[user])

    # rekt
    s.recvuntil(': ')
    s.sendline('uhhh....China?')

    s.recvall()
    s.close()


if __name__ == '__main__':
    [rand_login() for i in xrange(num_sessions)]
    legit_login()
