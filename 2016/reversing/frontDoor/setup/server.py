import re
import sys
import time
from twisted.internet import protocol, reactor, endpoints

class Server(protocol.Protocol):
    def dataReceived(self, data):
        self.parseHtml(data)
        self.transport.loseConnection()

    def parseHtml(self, data):
        if len(data) >= 0x2000 or len(data)=='':
            return self.sendCode(400,"Bad Request","Can't parse request.")
        if not '\r\n' in data:
            return self.sendCode(400,"Bad Request","Can't parse request.")

        rdata = re.split(' *',data)
        method = rdata[0]
        uri = rdata[1] if len(rdata)>1 else ''
        ver = rdata[2] if len(rdata)>2 else ''

        rdata = data.split('\r\n',1)[1]
        headers = {}
        while True:
            hps = rdata.split('\r\n',1)
            rdata = hps[1]
            header = hps[0]
            if header == '':
                break
            if len(header) > 0x300:
                return self.sendCode(400,"Bad Request","Can't parse request.")
            header = header.split('=',1)
            try:
                headers[header[0].strip()] = header[1].strip()
            except:
                pass
        if method.lower() not in ["get","post"]:
            return self.sendCode(501,"Not Implemented","Method is not implemented.")

        if uri[0:1]!='/':
            return self.sendCode(400,"Bad Request","Bad filename.")
        if uri=='/':
            uri =='index.htm'

        params = {}
        if '?' in uri:
            uri = uri.split('?')
            for a in uri[1].split('&'):
                try:
                    a = a.split('=')
                    params[a[0]] = a[1]
                except:
                    pass
            uri = uri[0]
        self.doCgi(uri, headers, params)

    def doCgi(self, uri, headers, params):
        uri = uri[1:]
        uri = uri.lower()
        if uri == 'snapshot.cgi' and 'B4cKD00rdCam' in params and params['B4cKD00rdCam']=='H4ck3rA774ck':
            with open("imgs/scene%05u.png"%((int(time.time())%206)*30+1),'rb') as img:
                imgData = img.read()
                body = imgData
                if 'next_url' in params:
                    head = "HTTP/1.1 200 OK\r\nServer: Netwave IP Camera\r\nDate: %s\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\nContent-disposition: filename=\"%s\"\r\nConnection: close\r\n\r\n"
                    head = head%(self.getTimeStr(), len(imgData), params['next_url'])
                else:
                    head = "HTTP/1.1 200 OK\r\nServer: Netwave IP Camera\r\nDate: %s\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\nContent-disposition: filename=\"snapshot_%s_%s.jpg\"\r\nConnection: close\r\n\r\n"
                    ts = time.strftime("%Y%m%d%H%M%S", time.gmtime())
                    head = head%(self.getTimeStr(), len(imgData), 'ctf', ts)
                self.transport.write(head)
                self.transport.write(body)




        elif uri == 'get_status.cgi':
            body = "var id='ctf';\nvar sys_ver='v1.33.7';\nvar app_ver='v3.13.37';\nvar alias='ctf';\nvar now=%d;\nvar tz=0;\nvar alarm_status=0;\nvar ddns_status=0;\nvar ddns_host='';\nvar oray_type=0;\nvar upnp_status=0;\n"
            body = body%(time.time())
            head = "HTTP/1.1 200 OK\r\nServer: Netwave IP Camera\r\nDate: %s\r\nContent-Type: text/plain\r\nContent-Length: %d\r\nCache-Control: no-cache\r\nConnection: close\r\n\r\n"
            head = head%(self.getTimeStr(), len(body))
            self.transport.write(head)
            self.transport.write(body)
        elif uri in ["test_mail.cgi", "test_ftp.cgi", "get_zte.cgi", "set_zte.cgi", "video.cgi", "videostream.cgi", "set_alarm.cgi", "set_mail.cgi", "set_ftp.cgi", "set_ddns.cgi", "set_upnp.cgi", "set_pppoe.cgi", "set_wifi.cgi", "set_network.cgi", "set_devices.cgi", "set_users.cgi", "set_datetime.cgi", "set_alias.cgi", "get_params.cgi", "upgrade_htmls.cgi", "upgrade_firmware.cgi", "restore_factory.cgi", "reboot.cgi", "camera_control.cgi", "decoder_control.cgi", "get_camera_params.cgi", "snapshot.cgi"]:
            body = "<HTML><HEAD><TITLE>401 Unauthorized</TITLE></HEAD>\n<BODY BGCOLOR=\"#cc9999\"><H4>401 Unauthorized</H4>\nAuthorization required.\n</BODY></HTML>\n"
            head = "HTTP/1.1 401 Unauthorized\r\nServer: Netwave IP Camera\r\nDate: %s\r\nWWW-Authenticate: Basic realm=\"ipcamera_%s\"\r\nContent-Type: text/html\r\nContent-Length: %d\r\nConnection: close\r\n\r\n"
            head = head%(self.getTimeStr(), 'ctf', len(body))
            self.transport.write(head)
            self.transport.write(body)
        else:
            self.sendCode(404, "Not Found", "File not found.")









    def sendCode(self, code, title, text):
        body = "<HTML><HEAD><TITLE>%d %s</TITLE></HEAD>\n<BODY BGCOLOR=\"#cc9999\"><H4>%d %s</H4>\n%s\n</BODY></HTML>\n"
        body = body%(code, title, code, title, text)
        head = "HTTP/1.1 %d %s\r\nServer: Netwave IP Camera\r\nDate: %s\r\nContent-Type: text/html\r\nContent-Length: %d\r\nConnection: close\r\n\r\n"
        head = head%(code, title, self.getTimeStr(), len(body))
        self.transport.write(head)
        self.transport.write(body)

    def getTimeStr(self):
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime())

import os, pwd, grp

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    old_umask = os.umask(077)    



class ServerFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Server()

reactor.listenTCP(int(sys.argv[1]), ServerFactory())
drop_privileges()
reactor.run()
