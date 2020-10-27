#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/*
gcc -s -fstack-protector-all -Wall -Wextra -Werror -Wl,-z,relro,-z,now -fPIE -pie main.c
*/


/* Heap layout
0xffffffff'ffffffff

ballotBoxLocationAlt2

candidatesList2

ballotBoxLocation2

**overflow here**
ballotBoxLocationAlt

ballotBoxLocation

candidatesList

voterName2

voterName

0x00000000'00000000
*/

#define NAME_LEN 100
#define DEBUG 0
#define BALLOT_LEN 1056

struct ballotStruct {
    unsigned long candidatesListLength;
    unsigned long voteOffset;
    char* voterName;
    char* candidatesList;
    char* ballotBoxLocation;
};

struct ballotStruct ballot;
struct ballotStruct ballotOld;
unsigned int ballotsSubmitted;

void PrintMenu() {
    printf("\n========== Voting Booth ==========\n");
    printf("1. Enter ballot\n");
    printf("2. View ballot\n");
    printf("3. Undo newest ballot\n");
    printf("4. Submit ballot\n");
    printf("5. Exit\n");
    printf("Choice: ");
    fflush(stdout);
}

char* ReadChars(unsigned int length, char * data, char stopOnNewLine) {
    if (!data) {
        data = malloc(length + 1);
    }
    char ch;

    if (!data) {
        printf("Too many candidates...\n");
        exit(1);
    }

    for (unsigned int i = 0; i < length; i++) {
        ch = getchar();

        if (stopOnNewLine && ch == '\n') {
            data[i] = '\x00';
            return data;
        }

        data[i] = ch;
    }
    data[length] = '\x00';
    return data;
}

unsigned long ReadULong() {
    char buf[32] = {0};
    fgets(buf, sizeof(buf), stdin);
    return (unsigned long) strtoul(buf, 0, 10);
}

unsigned int ReadUInt() {
    char buf[32] = {0};
    fgets(buf, sizeof(buf), stdin);
    return (unsigned int) strtoul(buf, 0, 10);
}

//
// The user has requested to revert to the most recently saved ballot. Store
// the current ballot and restore the saved ballot. No frees, only swaps.
//

void RevertBallot() {
    char * temp1;
    unsigned long temp2;

#if DEBUG
    printf("Name addr: %p\n", ballot.voterName);
#endif

    printf("Reverting ballot.\n");

    temp1 = ballot.voterName;
    ballot.voterName = ballotOld.voterName;
    ballotOld.voterName = temp1;

    temp1 = ballot.candidatesList;
    ballot.candidatesList = ballotOld.candidatesList;
    ballotOld.candidatesList = temp1;

    temp1 = ballot.ballotBoxLocation;
    ballot.ballotBoxLocation = ballotOld.ballotBoxLocation;
    ballotOld.ballotBoxLocation = temp1;

    temp2 = ballot.candidatesListLength;
    ballot.candidatesListLength = ballotOld.candidatesListLength;
    ballotOld.candidatesListLength = temp2;

    temp2 = ballot.voteOffset;
    ballot.voteOffset = ballotOld.voteOffset;
    ballotOld.voteOffset = temp2;
    
#if DEBUG
    printf("Name addr: %p\n", ballot.voterName);
#endif

    printf("Ballot reverted.\n");
}

//
// A new ballot is about to be submitted. Free the previously saved ballot if
// it exists and save the current ballot.
//

void SaveOldBallot(char * tempName) {
    char* tempNamePointer;

    //
    // Swap name buffer pointers. Also ensure newly entered name ends up in
    // ballot.voterName. This is pretty ugly but it works and luckily no one
    // will see this unless they decompile the program...
    //
    // (I saw we had more pwn than RE so I created code so bad it's basically
    // RE)
    //

    tempNamePointer = ballotOld.voterName;
    ballotOld.voterName = ballot.voterName;
    ballot.voterName = tempNamePointer;
    memcpy(ballot.voterName, ballotOld.voterName, NAME_LEN + 1);
    memcpy(ballotOld.voterName, tempName, NAME_LEN + 1);

    //
    // Free old candidatesList if it exists.
    //

    if(ballotOld.candidatesList) {
#if DEBUG
        printf("Freeing ballotOld.candidatesList: %p\n", ballotOld.candidatesList);
#endif
        free(ballotOld.candidatesList);
        ballotOld.candidatesList = NULL;
    }

    //
    // If current ballot has a candidatesList, save it to ballotOld. Otherwise,
    // set ballotOld.candidatesList to NULL;
    //

    if (ballot.candidatesList) {
        printf("Saving ballot.\n");
        ballotOld.candidatesList = ballot.candidatesList;
        ballot.candidatesList = NULL;
        ballotOld.candidatesListLength = ballot.candidatesListLength;
        ballotOld.voteOffset = ballot.voteOffset;
    } else {
        ballotOld.candidatesList = NULL;
    }

    //
    // Free both ballotOld.ballotBoxLocation if they exist.
    //

    if (ballotOld.ballotBoxLocation) {
#if DEBUG
        printf("Freeing (char**)ballotOld.ballotBoxLocation: %p\n", ((char**)ballotOld.ballotBoxLocation)[0]);
        printf("Freeing ballotOld.ballotBoxLocation: %p\n", ballotOld.ballotBoxLocation);
#endif
        free(((char**)ballotOld.ballotBoxLocation)[0]);
        free(ballotOld.ballotBoxLocation);

        ballotOld.ballotBoxLocation = NULL;
    }

    //
    // Save both current ballotOld.ballotBoxLocation if they exist.
    //

    if (ballot.ballotBoxLocation) {
        ballotOld.ballotBoxLocation = ballot.ballotBoxLocation;
        ballot.ballotBoxLocation = NULL;
    } else {
        ballotOld.ballotBoxLocation = NULL;
    }
}

//
// Read in name, ballot, and candidate offset in that order. Allocate name
// buffer, ballot buffer, and vote buffer also in that order. Save old ballot
// and free old old ballot if one exists.
//

void ReadData() {
    unsigned long len;
    unsigned long offset;

    printf("Enter your name: ");
    fflush(stdout);

    char tempName[NAME_LEN + 1];

    memcpy(tempName, ballot.voterName, NAME_LEN + 1);

    ballot.voterName = ReadChars(NAME_LEN, ballot.voterName, 1);

#if DEBUG
    printf("Name addr: %p\n", ballot.voterName);
#endif

    printf("Enter length of list of candidates: ");
    fflush(stdout);
    len = ReadULong();
    if (len > BALLOT_LEN) {
        printf("I don't remember there being that many candidates...\n");
        return;
    }

    //
    // Don't save old ballot unless we know length of new ballot is valid
    //

    SaveOldBallot((char*) &tempName);

    ballot.candidatesListLength = len;

    printf("Enter list of candidates separated by NULLs: ");
    fflush(stdout);
    ballot.candidatesList = ReadChars(ballot.candidatesListLength, NULL, 0);

    printf("Enter offset of your vote: ");
    fflush(stdout);
    offset = ReadULong();

#if DEBUG
        printf("ballot.candidatesList addr: %p\n", (void *)ballot.candidatesList);
        printf("ballot.candidatesList + offset addr: %p\n", (void *) (ballot.candidatesList + offset));
#endif

    // Verify offset, integer overflow bug
    if (ballot.candidatesList + offset > ballot.candidatesList + ballot.candidatesListLength) {
        printf("Offset too large!\n");

#if DEBUG
        printf("(not) Freeing ballot.candidatesList: %p\n", ballot.candidatesList);
#endif
        // Don't free here so tcache can be filled
        //free(ballot.candidatesList);
        ballot.candidatesList = NULL;
        return;
    }
    ballot.voteOffset = offset;

    ballot.ballotBoxLocation = malloc(strlen(ballot.candidatesList + ballot.voteOffset) + 1 + sizeof(char*));

#if DEBUG
    printf("ballot.ballotBoxLocation addr: %p\n", (void *)ballot.ballotBoxLocation);
#endif

    if (!ballot.ballotBoxLocation) {
        printf("Something went wrong...\n");
        exit(1);
    }

    char* altLoc = malloc(strlen(ballot.candidatesList + ballot.voteOffset) + 1);
    if (!altLoc) {
        printf("Something went wrong...\n");
        exit(1);
    }

#if DEBUG
    printf("ballot.ballotBoxLocation alt addr: %p\n", (void *)altLoc);
#endif

    memcpy(ballot.ballotBoxLocation, &altLoc, sizeof(char*));

    return;
}

void PrintBallot() {
    if (!ballot.candidatesList) {
        printf("I don't have a ballot...\n");
        return;
    }

    printf("Ballot:\n");
    fwrite(ballot.candidatesList, ballot.candidatesListLength, 1, stdout);
    fflush(stdout);

#if DEBUG
        printf("\nAddress of your vote: %p\n", (void*) (ballot.candidatesList + ballot.voteOffset));
#endif

    printf("\nYour vote: %s\n", ballot.candidatesList + ballot.voteOffset);
}

void SubmitBallot() {
#if DEBUG
    printf("Name addr: %p\n", ballot.voterName);
#endif

    if (!ballot.candidatesList) {
        printf("I don't have a ballot...\n");
        return;
    }
    ballotsSubmitted += 1;
    if (ballotsSubmitted%10 == 0) {
        printf("Ballot HDD full, submitting to alternate storage location.\n");
    }
    if ((ballotsSubmitted / 10)%2) {
#if DEBUG
    printf("Copying %p to %p.\n", ballot.candidatesList + ballot.voteOffset, *(char**)ballot.ballotBoxLocation);
#endif
        strcpy(*(char**)ballot.ballotBoxLocation, ballot.candidatesList + ballot.voteOffset);
    } else {
#if DEBUG
    printf("Copying %p to %p.\n", ballot.candidatesList + ballot.voteOffset, ballot.ballotBoxLocation + sizeof(char*));
#endif
        strcpy(ballot.ballotBoxLocation + sizeof(char*), ballot.candidatesList + ballot.voteOffset);
    }
    printf("Thank you, your ballot has been submitted!\n");
}

int main() {
    printf("Welcome to the voting booth. Please submit your ballot with your vote marked.\n");
    ballot.voterName = NULL;
    ballot.candidatesList = NULL;
    ballot.ballotBoxLocation = NULL;
    ballotOld.voterName = NULL;
    ballotOld.candidatesList = NULL;
    ballotOld.ballotBoxLocation = NULL;
    ballotsSubmitted = 0;
    ballot.voterName = malloc(NAME_LEN + 1);
    ballotOld.voterName = malloc(NAME_LEN + 1);
    if (!ballot.voterName || !ballotOld.voterName) {
        printf("Rough day...\n");
        exit(1);
    }
    while (1) {
        PrintMenu();
        switch(ReadUInt()) {
            case 1:
                ReadData();
                break;
            case 2:
                PrintBallot();
                break;
            case 3:
                RevertBallot();
                break;
            case 4:
                SubmitBallot();
                break;
            case 5:
                printf("Shutting down...\n");
                exit(0);
                break;
            default:
                printf("Unknown option\n");
        }
    }

    return 0;
}