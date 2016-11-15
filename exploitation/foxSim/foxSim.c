#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "nwo.h"
#include "fox.h"

int main();

uint32_t hash(char * data, size_t length) {
    uint32_t val = 0;
    int i;
    for (i=0; i<length; i++) {
        val += data[i];
        val += (val << 10);
        val ^= (val >> 6);
    }

    val += (val<<3);
    val ^= (val>>11);
    val += (val<<15);
    return val;
}

struct MapNode {
    char * key;
    void * data;
};

struct MapNode hashMap[100] = { {0} };

void mapPut(char * key, void * data) {
    uint32_t hashVal = hash(key,strlen(key));
    struct MapNode node = { .key = key, .data = data };
    hashMap[hashVal % 100] = node;
}

void* mapGet(char * key) {
    uint32_t hashVal = hash(key,strlen(key));
    return hashMap[hashVal % 100].data;
}

void voteForCandidate(struct Candidate* can, long votes) {
    can->votes += votes;
    printf("%s\n",can->voteMessage);
    printf("%lu votes added to %s\n",votes,can->name);
}

void voteForWriteIn(struct Candidate* can, long message) {
    if (message==0 || message < (long)main) {
        printf("%s\n",can->voteMessage);
    } else {
        printf("%s\n",(char*)message);
    }
}

long assignVotes(struct Candidate* can, struct Person* person, long votes) {
    person->votesToGive = votes;
    if (person->isCandidate) {
        return NWO_memberVote(can, person, votes);
    }
    else if (person == (struct Person*)can) {
        can->voteMessage = "Nice try, but we won't let you vote for yourself unless you have payed your dues to the NWO.";
        return person->votesToGive;
    } else if (!can->isCandidate) {
        can->voteMessage = "Hey, that person is not approved by the NWO. They don't get that vote.";
        person->votesToGive = 0;
    } else if (!person->isCandidate && votes != 1) {
        printf("Sorry you can only give one vote\n");
        person->votesToGive = 1;
    }

    return person->votesToGive;
}

void doVote(struct Candidate* can, struct Person* person) {
    long votes = 0;
    printf("How many votes do you want to give %s? ",can->name);
    scanf("%lu",&votes);
    while (getchar()!='\n') {}
    long realVotes = assignVotes(can,person,votes);
    can->action(can, realVotes);
}


struct Candidate* createCandidate(char* name, char* slogan) {
    struct Candidate* can = (struct Candidate*)malloc(sizeof(struct Candidate));
    strncpy(can->name, name, 100);
    can->isCandidate = 1;
    can->voteMessage = "Thanks for voting for me!";
    can->slogan = slogan;
    can->votes = 0;
    can->action = voteForCandidate;

    return can;
}

struct Person* createPerson(char* name) {
    struct Person* person = (struct Person*)malloc(sizeof(struct Person));
    strncpy(person->name, name, 100);
    person->isCandidate = 0;
    person->votesToGive = 0;
    person->action = voteForWriteIn;

    return person;
}

void strip(char* str) {
    long len = strlen(str);
    if (str[len-1]=='\n')
        str[len-1]='\0';
}

char* candidateNames[] = {"Trump","Cruz","Rubio","Jeb!"};

void voteLoop() {
    struct Candidate* c;
    struct Person* p;
    char buff[101];
    int i = 0;
    while (1) {
        printf("Hello, welcome to the FOX NEWS voting simulator\nPlease enter your name: ");
        if (fgets(buff, 100, stdin)==NULL) {
            perror("fgets");
            exit(1);
        }
        strip(buff);
        for (i = 0; i< 4; i++) {
            if (!strcmp(buff,candidateNames[i])) {
                printf("We know you are not %s. Get out of here...\n",candidateNames[i]);
                goto getThemOutOfHere;
            }
        }
        p = mapGet(buff);
        if (p==NULL) {
            p = createPerson(buff);
            mapPut(buff,p);
            printf("Added you to the record.\n");
        } else {
            printf("Found you in the records.\n");
        }

        printf("Please enter who you want to vote for: ");
        if (fgets(buff, 100, stdin)==NULL) {
            perror("fgets");
            exit(1);
        }
        strip(buff);
        c = mapGet(buff);
        if (c==NULL) {
            printf("Person not found... Sorry...\n");
        } else {
            doVote(c, p);
        }
getThemOutOfHere:
        printf("[Press enter to finish voting]\n");
        while (getchar()!='\n') {}
    }
}

int main() {
    setbuf(stdout, NULL);
    mapPut("Trump",createCandidate("Trump","Make america great again!"));
    mapPut("Cruz",createCandidate("Cruz","Reigniting the Promise of America"));
    mapPut("Rubio",createCandidate("Rubio","A New American Century"));
    mapPut("Jeb!",createCandidate("Jeb!","Please clap..."));
    voteLoop();
}






