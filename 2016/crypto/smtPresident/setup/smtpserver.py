from datetime import datetime
import asyncore
from smtpd import SMTPServer

class EmlServer(SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data):
        filename = '../handout/emails/%s.eml' % (str(rcpttos[0]))
        f = open(filename, 'w')
        f.write("From: " + str(mailfrom) + '\n')
        f.write("To: " + str(rcpttos[0]) + '\n')
        f.write(data + '\n')
        f.close
        print '%s saved.' % filename


def run():
    foo = EmlServer(('localhost', 1337), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
	run()
