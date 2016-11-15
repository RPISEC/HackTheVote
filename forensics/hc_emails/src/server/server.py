#!/usr/bin/env python2
# -*- encoding: utf8 -*-

import sys
from SocketServer import ThreadingTCPServer, ForkingTCPServer, StreamRequestHandler

HOST, PORT = '0.0.0.0', 9999


class Handler(StreamRequestHandler):
    simulate_lockdown = True

    def __init__(self, request, client_address, server):
        self.user = None  # After logging in

        # Admin user
        self.users = {'clinton': 'IAmGoingToBeTheNextPresidentAndIWillDestroyTrump'}

        # Just for fun to fill up the pcap
        if self.simulate_lockdown:
            self.users['bernie'] = 'tH3_h4nDfUl_0n_top'
            self.users['Jeb'] = '!'
            self.users['trump'] = 'China'

        StreamRequestHandler.__init__(self, request, client_address, server)

    def println(self, s=''):
        self.wfile.write('{}\n'.format(s))

    def input(self, prompt=''):
        self.wfile.write(prompt)
        return self.rfile.readline().rstrip('\r\n')

    def handle(self):
        if self.simulate_lockdown:
            self.lockdown_sim()
        else:
            self.locked_mode()

    def lockdown_sim(self):
        self.greet()
        if not self.login():
            self.println('ACCESS DENIED!')
            return

        self.println('Welcome, {}'.format(self.user))

        if self.user == 'clinton':
            # There isn't really another pass here, just goes into lockdown
            self.input('Now, to access your emails, enter the SUPER SECRET PASSWORD: ')
            self.println('+-------------------------+\n'
                         '|!!! INTRUDER DETECTED !!!|\n'
                         '|     THE EMAILS HAVE     |\n'
                         '|    BEEN  COMPROMISED    |\n'
                         '|  !!! WIPING DRIVES !!!  |\n'
                         '|  !!! WIPING DRIVES !!!  |\n'
                         '|  !!! WIPING DRIVES !!!  |\n'
                         '|!!! ENTERING LOCKDOWN !!!|\n'
                         '+-------------------------+')

    def locked_mode(self):
        self.greet()
        self.println('+-----------------------------+\n'
                     '|       !!! WARNING !!!       |\n'
                     '| SYSTEM HAS BEEN LOCKED DOWN |\n'
                     '|     NON-ADMIN USERS ARE     |\n'
                     '|        NOW  DISABLED        |\n'
                     '+-----------------------------+\n')

        if not self.login():
            if self.user != 'clinton':
                self.println('{} is not an admin!'.format(self.user))
            else:
                self.println('ACCESS DENIED!')
            return

        self.println('Welcome, {}'.format(self.user))
        self.println('+-----------------------------+\n'
                     '|       !!! WARNING !!!       |\n'
                     '|   EMAILS HAVE  BEEN WIPED   |\n'
                     '| A SYSTEM SNAPSHOT WAS TAKEN |\n'
                     '|     BEFORE THE INCIDENT     |\n'
                     '+-----------------------------+\n\n\n')

        self.println("Download the snapshot from http://email.clinton.io/[admin username]/[admin pass]/snapshot")

    def greet(self):
        self.println("""██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗    ████████╗ ██████╗     ██╗  ██╗██╗██╗     ██╗      █████╗ ██████╗ ██╗   ██╗███████╗\n"""
                     """██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝    ╚══██╔══╝██╔═══██╗    ██║  ██║██║██║     ██║     ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝\n"""
                     """██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗         ██║   ██║   ██║    ███████║██║██║     ██║     ███████║██████╔╝ ╚████╔╝ ███████╗\n"""
                     """██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝         ██║   ██║   ██║    ██╔══██║██║██║     ██║     ██╔══██║██╔══██╗  ╚██╔╝  ╚════██║\n"""
                     """╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗       ██║   ╚██████╔╝    ██║  ██║██║███████╗███████╗██║  ██║██║  ██║   ██║   ███████║\n"""
                     """ ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝       ╚═╝    ╚═════╝     ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝\n"""
                     """   _                                                       _                                                       _                                \n"""
                     """  (_)                                                     (_)                                                     (_)                               \n"""
                     """ <___>                                                   <___>                                                   <___>                              \n"""
                     """  | |______                                               | |______                                               | |______                         \n"""
                     """  | |* * * )                                              | |* * * )                                              | |* * * )                        \n"""
                     """  | | * * (_________                                      | | * * (_________                                      | | * * (_________                \n"""
                     """  | |* * * |* *|####)                                     | |* * * |* *|####)                                     | |* * * |* *|####)               \n"""
                     """  | | * * *| * |   (________________                      | | * * *| * |   (________________                      | | * * *| * |   (________________\n"""
                     """  | |* * * |* *|####|##############|                      | |* * * |* *|####|##############|                      | |* * * |* *|####|##############|\n"""
                     """  | | * * *| * |    |              |                      | | * * *| * |    |              |                      | | * * *| * |    |              |\n"""
                     """  | |* * * |* *|####|##############|                      | |* * * |* *|####|##############|                      | |* * * |* *|####|##############|\n"""
                     """  | |~~~~~~| * |    |              |                      | |~~~~~~| * |    |              |                      | |~~~~~~| * |    |              |\n"""
                     """  | |######|* *|####|##############|                      | |######|* *|####|##############|                      | |######|* *|####|##############|\n"""
                     """  | |      |~~~'    |              |                      | |      |~~~'    |              |                      | |      |~~~'    |              |\n"""
                     """  | |######|########|##############|                      | |######|########|##############|                      | |######|########|##############|\n"""
                     """  | |      |        |              |                      | |      |        |              |                      | |      |        |              |\n"""
                     """  | |######|########|##############|                      | |######|########|##############|                      | |######|########|##############|\n"""
                     """  | |~~~~~~|        |              |                      | |~~~~~~|        |              |                      | |~~~~~~|        |              |\n"""
                     """  | |      |########|##############|                      | |      |########|##############|                      | |      |########|##############|\n"""
                     """  | |      '~~~~~~~~|              |                      | |      '~~~~~~~~|              |                      | |      '~~~~~~~~|              |\n"""
                     """  | |               |##############|                      | |               |##############|                      | |               |##############|\n"""
                     """  | |               '~~~~~~~~~~~~~~~                      | |               '~~~~~~~~~~~~~~~                      | |               '~~~~~~~~~~~~~~~\n"""
                     """  | |                                                     | |                                                     | |                               \n"""
                     """  | |                                                     | |                                                     | |                               \n"""
                     """  | |                                                     | |                                                     | |                               \n"""
                     """                                                                                                                                                    \n"""
                     """██████╗ ██████╗ ██╗██╗   ██╗ █████╗ ████████╗███████╗    ███████╗███╗   ███╗ █████╗ ██╗██╗         ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ \n"""
                     """██╔══██╗██╔══██╗██║██║   ██║██╔══██╗╚══██╔══╝██╔════╝    ██╔════╝████╗ ████║██╔══██╗██║██║         ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗\n"""
                     """██████╔╝██████╔╝██║██║   ██║███████║   ██║   █████╗      █████╗  ██╔████╔██║███████║██║██║         ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝\n"""
                     """██╔═══╝ ██╔══██╗██║╚██╗ ██╔╝██╔══██║   ██║   ██╔══╝      ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║         ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗\n"""
                     """██║     ██║  ██║██║ ╚████╔╝ ██║  ██║   ██║   ███████╗    ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║\n"""
                     """╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚═╝  ╚═╝   ╚═╝   ╚══════╝    ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝    ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝\n""")

    def login(self):
        self.user = self.input('login: ')
        pwd = self.input('password: ')
        return self.user in self.users and pwd == self.users[self.user]


def main():
    # Why, Windows? Why?
    srvclass = ThreadingTCPServer if 'win32' in sys.platform else ForkingTCPServer

    srvclass.allow_reuse_address = True
    srv = srvclass((HOST, PORT), Handler)

    try:
        print 'Starting server at {}:{}\n'.format(HOST, PORT)
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == '__main__':
    Handler.simulate_lockdown = False
    main()
