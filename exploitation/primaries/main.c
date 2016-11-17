// Compile with:
// gcc main.c -Wall -s -static -m32 -o primaries

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define deathrays \
      __asm__ volatile("push     %eax      \n"\
                       "xor      %eax, %eax\n"\
                       "jz       .+5       \n"\
                       ".word    0xC483    \n"\
                       ".byte    0x04      \n"\
                       "pop      %eax      \n");

struct candidate {
  char name[0x100];
  void(* victory_speech)();
  unsigned int votes;
  unsigned int delegates;
};

struct voter {
  char* name;
  unsigned long ssn;
  struct candidate* cand;
  char* date_of_birth;
};

void winner(){
  printf(" declare myself the winner!\n");
  fflush(stdout);
  return;
}

struct candidate* initcandidate(){
  struct candidate* cptr = malloc(sizeof(struct candidate));
  memset(cptr->name, 0, 0x100);
  cptr->votes = 0;
  cptr->delegates = 0;
  cptr->victory_speech = &winner;

  return cptr;
}

struct voter* initvoter(){
  struct voter* vptr = malloc(sizeof(struct voter));
  vptr->name = malloc(0x100);
  memset(vptr->name, 0, 0x100);
  vptr->date_of_birth = malloc(0x100);
  memset(vptr->date_of_birth, 0, 0x100);

  return vptr;
}

void freecandidate(struct candidate* cptr){
  free(cptr);

  return;
}

void freevoter(struct voter* vptr){
  free(vptr->name);
  free(vptr->date_of_birth);
  free(vptr);

  return;
}

struct candidate* getvoterinfo(struct voter* v,
                  struct candidate* c1,
                  struct candidate* c2,
                  struct candidate* c3,
                  struct candidate** writeins,
                  int numwriteins
                 ){

  printf("Please enter your full name:\n");
  fflush(stdout);
  fgets(v->name, 0x100, stdin);

  printf("Please enter your SSN:\n");
  fflush(stdout);
  scanf("%lu", &(v->ssn));
  getchar();

  printf("Please enter your date of birth:\n");
  fflush(stdout);
  fgets(v->date_of_birth, 0x100, stdin);

  struct candidate* c4 = NULL;

  printf("Please enter the candidate you are voting for:\n");
  printf("\t(1) %s\n", c1->name);
  printf("\t(2) %s\n", c2->name);
  printf("\t(3) %s\n", c3->name);
  printf("\t(4) write-in\n");
  fflush(stdout);
  unsigned int choice = 0;
  int i = 0;
  scanf("%u", &choice);
  getchar();
  switch(choice){
    case 1:
      v->cand = c1;
      c1->votes++;
    case 2:
      v->cand = c2;
      c2->votes++;
    case 3:
      v->cand = c3;
      c3->votes++;
    case 4:
      c4 = initcandidate();
      printf("Who do you want to vote for?\n");
      fflush(stdout);
      fgets(c4->name, 0x120, stdin);
      for(i = 0; i < numwriteins; i++){
        if(strcmp(writeins[i]->name, c4->name) == 0){
          v->cand = writeins[i];
          writeins[i]->votes++;
          freecandidate(c4);
          return NULL;
        }
      }
      v->cand = c4;
      c4->votes++;
      return c4;
    default:
      v->cand = NULL;
  }

  deathrays;
  return NULL;
}

void finishcaucus(struct candidate* c1,
                  struct candidate* c2,
                  struct candidate* c3,
                  struct candidate** writeins,
                  int numwriteins
                 ){

  c1->delegates = c1->votes/10;
  c2->delegates = c2->votes/10;
  c3->delegates = c3->votes/10;

  int i = 0;
  for(i = 0; i < numwriteins; i++){
    writeins[i]->delegates = writeins[i]->votes/10;
  }

  int mindelegates = 0;
  struct candidate* cwinner = NULL;
  if(c1->delegates > mindelegates){
    mindelegates = c1->delegates;
    cwinner = c1;
  }
  if(c2->delegates > mindelegates){
    mindelegates = c2->delegates;
    cwinner = c2;
  }
  if(c3->delegates > mindelegates){
    mindelegates = c3->delegates;
    cwinner = c3;
  }

  for(i = 0; i < numwriteins; i++){
    if(writeins[i]->delegates > mindelegates){
      mindelegates = writeins[i]->delegates;
      cwinner = writeins[i];
    }
  }

  if(mindelegates > 0){
    printf("I, %s, ", cwinner->name);
    fflush(stdout);
    cwinner->victory_speech();
  }
  else{
    printf("There was no winner, no delegates were received!\n");
    fflush(stdout);
  }

  deathrays;
  return;
};

int main(int argc, char* argv[]){
  struct candidate* c1 = initcandidate();
  struct candidate* c2 = initcandidate();
  struct candidate* c3 = initcandidate();
  strcpy(c1->name, "David Hasselhoff");
  strcpy(c2->name, "Arnold Schwarzenegger");
  strcpy(c3->name, "Stephen Colbert");

  struct candidate* newc = NULL;
  struct candidate* writeins[100];
  struct voter* voters[100];
  int numvoters = 0;
  int numwriteins = 0;

  int i = 0;
  for(i = 0; i < 100; i++){
    struct voter* v = initvoter();
    newc = getvoterinfo(v, c1, c2, c3, writeins, numwriteins);
    if(newc != NULL){
      writeins[numwriteins++] = newc;
      newc = NULL;
    }
    voters[numvoters++] = v;
  }

  finishcaucus(c1,c2,c3,writeins, numwriteins);

  freecandidate(c1);
  freecandidate(c2);
  freecandidate(c3);

  for(i = 0; i < numwriteins; i++){
    if(writeins[i] != NULL){
      freecandidate(writeins[i]);
    }
  }

  for(i = 0; i < numvoters; i++){
    if(voters[i] != NULL){
      freevoter(voters[i]);
    }
  }

  deathrays;
  return 0;
}
