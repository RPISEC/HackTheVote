//gcc -o server server.c -z execstack -s

#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <ctype.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <errno.h>
#include <signal.h>
#include <netinet/in.h>
#include <fcntl.h>

struct HttpData {
    int method;
    char* uri;
    char* body;
    char* user;
    char* pass;
    unsigned int bodyLen;
} httpData;

char userData[1024];

struct ExceptionChain {
    char type;
    struct ExceptionChain* next;
    const char* key;
    const char* message;
    void (*callback)(struct ExceptionChain*);
};
struct ExceptionChainEnd {
    char type;
    void (*callback)(const char*);
};

struct ExceptionHead {
    struct ExceptionChain chainSpace[10];
    char ipData[16];
    char passData[1024];
    struct ExceptionChain* next;
} exceptHead;

unsigned int chainCount = 0;

int socketFd;
struct sockaddr_in client;

char bodyData[2048];

char* ipToStr(struct in_addr* in) {
    return strcpy(exceptHead.ipData, inet_ntoa(*in));
}

int strToIp(struct in_addr* in) {
    return inet_aton(exceptHead.ipData,in);
}

void strToLower(char* p) {
    for ( ; *p; ++p) *p = tolower(*p);
}

void addException(const char* key, const char* message, void (*callback)(struct ExceptionChain*)) {
    struct ExceptionChain* chain = &exceptHead.chainSpace[chainCount++];
    chain->type = 1;
    chain->key = key;
    chain->message = message;
    chain->callback = callback;
    chain->next = exceptHead.next;
    exceptHead.next = chain;
}
void addExceptionEnd(const char* key, const char* message, void (*callback)(struct ExceptionChain*)) {
}

char date[128];
char headerData[4096];

char* getHeader(unsigned int code, const char* name, unsigned int len, const char* extra) {
    const time_t c_time = time(NULL);
    strftime(date, sizeof(date)-1, "%a, %d %b %Y %T GMT", gmtime(&c_time));
    const char* headerf = "HTTP/1.1 %u %s\r\n"
        "Date: %s\r\n"
        "Server: Vote-o-matic Admin Panel v1.3\r\n"
        "Content-Length: %u\r\n"
        "Content-Type: text/html\r\n%s"
        "Connection: close\r\n\r\n";
    snprintf(headerData, sizeof(headerData)-1, headerf, code, name, date, len, extra);
    return headerData;
}

char templateData[4096];

char* getTemplate(const char* title, const char* body) {
    const char* templatef = "<html><head>\n"
        "<title>%s</title>\n"
        "<style>.nav { height: 30px; width: 100%; position: fixed; top: 0; left: 0; background-color: #ddd }\n"
        ".innav { margin-left: 5px; margin-top: 5px }\n"
        ".innav > a {margin-right: 5px; margin-left: 5px }\n"
        "body { margin-top: 35px; background-color: #fff }\n"
        "</style></head>\n"
        "<body><div class=\"nav\"><div class=\"innav\">"
        "<span style=\"margin-right: 5px; margin-left:5px }\">Vote-o-matic</span>\n"
        "<a href=\"/\">Admin</a>&nbsp;"
        "<a href=\"/status\">Status</a>&nbsp;"
        "<a href=\"/count\">Count votes</a></div></div>\n"
        "%s\n"
        "</body></html>";
    snprintf(templateData, sizeof(templateData)-1, templatef, title, body);
    return templateData;
}


void internalError(const char* message) {
    const char* bodyf = "<h1 style=\"color: red;\">500 Error!</h1><p>%s</p>";
    snprintf(bodyData, sizeof(bodyData)-1, bodyf, message);

    char* template = getTemplate("500 Error!", bodyData);
    
    char* header = getHeader(500, "Internal Server Error", strlen(template), "");
    send(socketFd, header, strlen(header), 0);
    send(socketFd, template, strlen(template), 0);
}

char messageData[4096];

void notFoundError(const char* messagef) {
    snprintf(messageData, strlen(messagef)+strlen(httpData.uri)+1, messagef, httpData.uri);
    const char* bodyf = "<h1 style=\"color: red;\">404 Not Found!</h1><p>%s</p>";

    snprintf(bodyData, sizeof(bodyData)-1, bodyf, messageData);

    char* template = getTemplate("404 Error!", bodyData);
    
    char* header = getHeader(404, "Not Found Error", strlen(template), "");
    send(socketFd, header, strlen(header), 0);
    send(socketFd, template, strlen(template), 0);
}

void notAuthedException(struct ExceptionChain* chain) {
    const char* bodyf = "<h1 style=\"color: red;\">401 Unauthorized</h1><p>%s</p>";

    snprintf(bodyData, sizeof(bodyData)-1, bodyf, chain->message);

    char* template = getTemplate("401 Unauthorized", bodyData);
    
    char* header = getHeader(401, "Unauthorized", strlen(template), "WWW-Authenticate: Basic realm=\"Vote-o-matic Admin\"\r\n");
    send(socketFd, header, strlen(header), 0);
    send(socketFd, template, strlen(template), 0);
}


void internalException(struct ExceptionChain* chain) {
    internalError(chain->message);
}

void notFoundException(struct ExceptionChain* chain) {
    notFoundError(chain->message);
}

char errorData[4096];

void uncaughtException(const char* name) {
    const char* errorf = "Exception not handled: %s";

    snprintf(errorData, sizeof(errorData)-1, errorf, name);
    internalError(errorData);
}

void setExceptions() {
    struct ExceptionChainEnd* chain = (struct ExceptionChainEnd*)&exceptHead.chainSpace[chainCount++];
    chain->type = 2;
    chain->callback = &uncaughtException;
    exceptHead.next = (struct ExceptionChain*)chain;

    addException("parse_error", "HTTP parse error!", internalException);
    addException("not_implemented", "That method is not implemented...", internalException);
    addException("not_found", "The requested page '%s' was not found...", notFoundException);
    addException("no_auth", "You are not authorized to access this page!", notAuthedException);
    addException("too_early", "It is too early to count votes. Come back after the 8th.", internalException);
}


void throwException(const char* key) {
    struct ExceptionChain* chain = exceptHead.next;
    //printf("Exception %s %p\n",key, chain);
    while (1) {
        //printf("Checking chain: chain.type=%x chain.callback=%p\n",chain->type, chain->callback);
        if ((chain->type&2) || !strcmp(key, chain->key)) {
            printf("Matching chain!\n");
            if (chain->type&1) {
                //printf("Code %08x\n",*(unsigned int*)chain->callback);
                chain->callback(chain);
            } else {
                ((struct ExceptionChainEnd*)chain)->callback(key);
            }
            return;
        }
        chain = chain->next;
    }
}


char base64Data[1024];

char* base64Decode(const char* auth) {
    unsigned int i = 0;
    unsigned int bits = 0;
    unsigned int val = 0;
    unsigned int offset;
    char* iter = base64Data;
    while (i<sizeof(base64Data)) {
        if (*auth == '\0') {
            *iter = '\0';
            break;
        }
        if (*auth >= '0' && *auth <= '9') {
            offset = *auth - '0'+26+26;
        } else if (*auth >= 'A' && *auth <='Z') {
            offset = *auth - 'A';
        } else if (*auth >= 'a' && *auth <='z') {
            offset = *auth - 'a'+26;
        } else if (*auth == '+') {
            offset = 62;
        } else if (*auth == '/') {
            offset = 63;
        } else {
            *iter = '\0';
            break;
        }
        auth++;

        unsigned int used = 0;
        while (used < 6) {
            unsigned int num = 8 - bits;
            if (num > 6 - used)
                num = 6 - used;
            val <<= num;
            val += (offset >> (6-num-used)) & ~(-1<<num);

            bits += num;
            used += num;
            if (bits == 8) {
                *(iter++) = val;
                bits = 0;
                val = 0;
            }
        }
    }
    return base64Data;
}

void statusPage() {
    const char* bodyf = "<h1 style=\"color: blue;\">Status</h1>\n"
        "<p>Your ip: %s<br/>\n"
        "Socket id: %u<br/>\n"
        "Firmware: <a href=\"%s\">v1.3</a><br/>\n"
        "Username: %s<br/>\n"
        "Password: %s</p>\n";

    char url[100];
    int fd = open("last_firmware_update_url",O_RDONLY);
    url[read(fd, url, 99)]='\0';
    close(fd);

    snprintf(bodyData, sizeof(bodyData), bodyf, ipToStr(&client.sin_addr),socketFd, url, httpData.user, httpData.pass);
    bodyData[strlen(bodyData)] = '\0';
    
    char* template = getTemplate("Status", bodyData);

    char* header = getHeader(200, "Ok", strlen(template), "");
    send(socketFd, header, strlen(header), 0);
    send(socketFd, template, strlen(template), 0);
}

void indexPage() {
    const char* body = "<h1 style=\"color: blue;\">Vote-o-matic</h1>\n"
        "<p>This is the Vote-o-matic admin panel. This panel may only be accessed by trained and authorized personnel. If you do believe you do not fit this category, please exit this browser and report this incident to the proper authorities.</p>\n"
        "<p>To prevent abuse, votes cannot be released by the voting machines until the voting period is over.</p>";
    char* template = getTemplate("Vote-o-matic", body);
    
    char* header = getHeader(200, "Ok", strlen(template), "");
    send(socketFd, header, strlen(header), 0);
    send(socketFd, template, strlen(template), 0);
}

void countPage() {
    const char* form = "<h1 style=\"color: blue;\">Count Votes</h1>\n"
        "<form action=\"/count\" method=\"POST\">\n"
        "<label>Enter the voting machine IP to request votes from:</label><br/>\n"
        "<input type=\"number\" style=\"width: 45px\" name=\"ip0\" max=255 min=0>."
        "<input type=\"number\" style=\"width: 45px\" name=\"ip1\" max=255 min=0>."
        "<input type=\"number\" style=\"width: 45px\" name=\"ip2\" max=255 min=0>."
        "<input type=\"number\" style=\"width: 45px\" name=\"ip3\" max=255 min=0><br/>\n"
        "<input type=\"submit\" value=\"Query Votes\">\n"
        "</form>";
    char* template = getTemplate("Count Votes", form);
    
    char* header = getHeader(200, "Ok", strlen(template), "");
    send(socketFd, header, strlen(header), 0);
    send(socketFd, template, strlen(template), 0);
}

void doCountPost() {
    if (httpData.body == NULL || *httpData.body == '\0') {
        throwException("invalid_request");
        return;
    }
    
    int i = 0;
    *exceptHead.ipData = '\0';
    char* param = strtok(httpData.body, "&");
    while(param!=NULL) {
        if (i==0 && !strncmp(param, "ip0=", 4)) {
            strcat(exceptHead.ipData, param+4);
            strcat(exceptHead.ipData, ".");
            i++;
        }
        if (i==1 && !strncmp(param, "ip1=", 4)) {
            strcat(exceptHead.ipData, param+4);
            strcat(exceptHead.ipData, ".");
            i++;
        }
        if (i==2 && !strncmp(param, "ip2=", 4)) {
            strcat(exceptHead.ipData, param+4);
            strcat(exceptHead.ipData, ".");
            i++;
        }
        if (i==3 && !strncmp(param, "ip3=", 4)) {
            strcat(exceptHead.ipData, param+4);
            i++;
        }
        param = strtok(NULL, "&");
    }
    printf("ip: %s\n",exceptHead.ipData);


    struct sockaddr_in remote;
    memset((void*)&remote, 0, sizeof(remote));
    remote.sin_family = AF_INET;
    remote.sin_port = htons(3000);
    if (!strToIp((struct in_addr*)&remote.sin_addr.s_addr)) {
        throwException("invalid_ip");
        return;
    }

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (connect(sock, (struct sockaddr*)&remote, sizeof(remote))) {
        throwException("invalid_ip");
        return;
    }

    send(sock, "count\n", 6, 0);
    recv(sock, errorData, 32,0);
    errorData[32]='\0';

    char* num1 = strtok(errorData, ":");
    char* num2 = strtok(NULL, "\n");


    const char* bodyf = "<h1 style=\"color: green;\">Vote Counts</h1>\n"
        "<p><span style=\"color: blue;\">Clinton</span>: %s<br/>\n"
        "<span style=\"color: red;\">Trump</span>: %s<br/>\n"
        "<span style=\"color: brown;\">3rd Party</span>: 0<br/></p>\n";
    snprintf(bodyData, sizeof(bodyData), bodyf, num1, num2);
    bodyData[strlen(bodyData)] = '\0';
    
    char* template = getTemplate("Status", bodyData);

    char* header = getHeader(200, "Ok", strlen(template), "");
    send(socketFd, header, strlen(header), 0);
    send(socketFd, template, strlen(template), 0);

}

void doRequest() {
    struct _vtime {
        char urlBuff[12];
        time_t c_time;
        char a;
    } vtime;
    vtime.c_time = time(NULL);

    vtime.urlBuff[0] = '\0';
    
    if (!strcmp(httpData.uri, "/")) {
        indexPage();
    } else {
        strncat(vtime.urlBuff, httpData.uri, 16);
        char* q = strchr(vtime.urlBuff,'?');
        if (q)
            *q = '\0';
        
        if (!strcmp(vtime.urlBuff, "/status")) {
            statusPage();
        } else if (!strcmp(vtime.urlBuff, "/count")) {
            if (vtime.c_time < 1478667600) {
                throwException("too_early");
            } else {
                if (httpData.method == 0)
                    countPage();
                else
                    doCountPost();
            }
        } else {
            throwException("not_found");
        }
    }

}

int parseHtml(char* req) {
    char* method = strtok(req, " ");

    int methodType = 0;
    strToLower(method);
    if (!strcmp(method, "get")) {
        methodType = 0;
    } else if (!strcmp(method, "post")) {
        methodType = 1;
    } else {
        throwException("not_implemented");
        return 0;
    }
    httpData.method = methodType;

    char* uri = req;
    uri = strtok(NULL, " ");
    httpData.uri = uri;
    if (uri[0] != '/') {
        throwException("not_found");
    }


    char* head = strtok(NULL, "");
    char* body = strstr(head, "\r\n\r\n");
    *body='\0';
    body += 4;

    httpData.body = body;
    httpData.bodyLen = strlen(body);

    printf("Head: %s\n",head);
    printf("Body: %s\n",body);

    char* auth = NULL;

    char* headE = strtok(head, "\r\n");
    while (headE != NULL && *headE != '\0') {
        if (!strncmp(headE, "Authorization: ", 15)) {
            if (strncmp(headE+15, "Basic ", 6)) {
                throwException("not_basic");
                return 0;
            } else {
                auth = headE+15+6;
            }
        }
        headE = strtok(NULL, "\r\n");
        printf("'%s'\n",headE);
    }

    if (auth == NULL || strncmp(auth, "YWRtaW46RUI0UEZjVWhtOVJVTnc=", 28)) {
        throwException("no_auth");
        return 0;
    }
    auth = base64Decode(auth);
    *strchr(auth, ':') = '\0';
    httpData.user = strncpy(userData, auth, sizeof(userData));
    httpData.pass = strncpy(exceptHead.passData, auth+strlen(httpData.user)+1, sizeof(exceptHead.passData));

    doRequest();

    return 1;
}

char reqData[0x3000];

void process() {
    while (1) {
        unsigned int len = 0;
        int nlen;
        while (1) {
            nlen = recv(socketFd, reqData+len, 4096, 0);
            if (nlen <= 0) {
                return;
            }
            len += nlen;
            if (len >= 0x3000) {
                throwException("too_large");
                return;
            }
            if (nlen < 4096)
                break;
        }
        printf("Got buff %s\n",reqData);
        parseHtml(reqData);
        printf("Done parse\n");
    }
}

void alarmHnd() {
    signal(SIGALRM, SIG_IGN); 
    exit(1);
}

int main() {
    signal(SIGALRM, alarmHnd);
    struct sigaction sigchld_action = {
        .sa_handler = SIG_DFL,
        .sa_flags = SA_NOCLDWAIT
    };
    sigaction(SIGCHLD, &sigchld_action, NULL);

    setExceptions();

    int serverfd = socket(PF_INET, SOCK_STREAM, 0);
    if (serverfd < 0) {
        perror("socket()");
        exit(1);
    }

    int enable = 1;
    if (setsockopt(serverfd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0)
            perror("setsockopt(SO_REUSEADDR)");

    struct sockaddr_in server;
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(8080);

    if (bind(serverfd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("bind()");
        exit(1);
    }

    listen(serverfd, 5);

    int fromlen = sizeof( client );
    int pid;

    while (1) {
        int newsock = accept(serverfd, (struct sockaddr *)&client, (socklen_t*)&fromlen);
        pid = fork();
        if (pid < 0) {
            perror("fork()");
            close(newsock);
        } else if(pid==0) {
            alarm(60);
            socketFd = newsock;
            printf("Connected! %d %u\n",newsock, errno);
            process();
            close(socketFd);
            exit(0);
        } else {
            close(newsock);
        }

    }



}
