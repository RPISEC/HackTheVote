#ifndef FOX_H
#define FOX_H

struct Candidate {
    void (*action)(struct Candidate*, long);
    char name[100];
    char* voteMessage;
    int isCandidate;
    char* slogan;
    long delegates;
    long votes;
};

struct Person {
    void (*action)(struct Candidate*, long);
    char name[100];
    long votesToGive;
    int isCandidate;
};

#endif
