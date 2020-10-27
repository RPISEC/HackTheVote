#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

#define ARR_SIZE(arr) sizeof((arr))/sizeof((arr)[0])

char* frags[] = {"Agave", "Leather", "Vanilla", "Wintergreen", "Balsam", "Teakwood", "Rain"};
char* dyes[] = {"Grey", "Green", "Orange", "White", "Purple"};

struct wax {
    unsigned char refcnt;
    char* frag;
    char* dye;
};

struct candle {
    char name[16];
    struct wax* wax;
};

#define NWAX 8
struct wax* waxes[NWAX];
#define NCANDLES 32
struct candle* candles[NCANDLES];

void unref(struct wax* wax) {
    if (wax && --wax->refcnt == 0)
        free(wax);
}

void menu() {
    puts("1: Make some wax");
    puts("2: Throw out some wax");
    puts("3: Pour a candle");
    puts("4: View candles");
    puts("5: Sell candle");
    puts("6: Go home");
    printf("Choice: ");
}

unsigned long read_ulong() {
    char buf[32];
    buf[read(0, buf, sizeof(buf)-1)] = 0;
    return strtoul(buf, 0, 10);
}

void make_wax() {
    int idx;
    for (idx = 0; idx < NWAX && waxes[idx]; idx++);
    if (idx >= NWAX) {
        puts("No wax buckets available...");
        return;
    }

    puts("Pick a fragrance oil:");
    for (int i = 0; i < ARR_SIZE(frags); i++)
        printf("%d: %s\n", i, frags[i]);
    printf("Choice: ");
    int frag = read_ulong();
    if (frag < 0 || frag >= ARR_SIZE(frags)) {
        puts("Not a valid fragrance oil...");
        return;
    }

    puts("Pick a dye:");
    for (int i = 0; i < ARR_SIZE(dyes); i++)
        printf("%d: %s\n", i, dyes[i]);
    printf("Choice: ");
    int dye = read_ulong();
    if (dye < 0 || dye >= ARR_SIZE(dyes)) {
        puts("Not a valid dye...");
        return;
    }

    struct wax* wax = malloc(sizeof(struct wax));
    wax->refcnt = 1;
    wax->frag = frags[frag];
    wax->dye = dyes[dye];
    waxes[idx] = wax;

    puts("Created wax");
}

void list_waxes() {
    for (int i = 0; i < NWAX; i++)
        if (waxes[i]) {
            printf("%d:\n", i);
            puts(waxes[i]->frag);
            puts(waxes[i]->dye);
        }
}

void dump_wax() {
    puts("Which wax would you like to dump:");
    list_waxes();
    printf("Choice: ");
    int iwax = read_ulong();
    if (iwax < 0 || iwax >= NWAX || !waxes[iwax]) {
        puts("Not a valid wax bucket...");
        return;
    }
    unref(waxes[iwax]);
    waxes[iwax] = 0;

    puts("Wax dumped");
}

void pour_candle() {
    int idx;
    for (idx = 0; idx < NCANDLES && candles[idx]; idx++);
    if (idx >= NCANDLES) {
        printf("The shop is already full of candles...\n");
        return;
    }

    puts("Pick a wax to pour:");
    list_waxes();
    printf("Choice: ");
    int iwax = read_ulong();
    if (iwax < 0 || iwax >= NWAX || !waxes[iwax]) {
        puts("Not a valid wax bucket...");
        return;
    }

    struct candle* candle = malloc(sizeof(struct candle));
    puts("Name this candle:");
    read(0, candle->name, sizeof(candle->name));

    candle->wax = waxes[iwax];
    waxes[iwax]->refcnt++;
    candles[idx] = candle;

    puts("Candle poured");
}

void list_candles() {
    for (int i = 0; i < NCANDLES; i++)
        if (candles[i]) {
            printf("%d: ", i);
            puts(candles[i]->name);
        }
}

void sell_candle() {
    puts("Sell which candle:");
    list_candles();
    printf("Choice: ");
    int idx = read_ulong();
    if (idx < 0 || idx >= NCANDLES || !candles[idx]) {
        printf("Can't sell this candle...\n");
        return;
    }

    unref(candles[idx]->wax);
    free(candles[idx]);
    candles[idx] = 0;

    puts("Candle sold");
}

void setup() {
    setvbuf(stdout, 0, _IONBF, 0);
    puts("                              Midnight Candle Shop                              ");
    puts("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWWNNNNNNWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMMMMMMMMMMMMMWNX0kdolc::;;;;;;:clodxk0XWMMMMMMMMMMMMMMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMMMMMMMMMWXOdl;'......................,:lx0NWMMMMMMMMMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMMMMMMN0dc,................................;lxKWMMMMMMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMMMWKd:.......................................'ckXWMMMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMNOl'.......',;:clllllc:;,'......................;oKWMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMWOc.....,:lxOKXNNWWWWWWWNNK0Okdc;'..................,oKWMMMMMMMMMMMM");
    puts("WWWWWWWWWWWKo'...;okKNWMMMMMMMMMMMMMMMMMMMMWX0dc,.................,dXWWWWWWWWWWW");
    puts("ddddddddddo;..,lkXWMMMMMMMMMMMMMMMMMMMMMMMMMMMWNKd:.................:dxddddddddd");
    puts("NNNNNNNNKl..,o0NMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWXd,................,dKNNNNNNNX");
    puts("MMMMMMMXo.'lONMMMMMMMMMMMMMMNKXWMMMMMMMMMMMMMMMMMMMNk;................'xWMMMMMMM");
    puts("MMMMMMNo',xXWMMMMMMMMMMMMMMMNOdx0WMMMMMMMMMMMMMMMMMMXo.................,xWMMMMMM");
    puts("MMMMMWx';kNMMMMMMMMMMMMMMMMMMWKo:dXMMMMMMMMMMMMMMMMMNd'.................,OMMMMMM");
    puts("MMMMM0;;kNMMMMMMMMMMMMMMMMMMMMWO;'oKMMMMMMMMMMMMMMMW0c...................cXMMMMM");
    puts("MMMMNo,xNMMMMMMMMMMMMMMMMMMMMMNk,.'dXMMMMMMMMMMMMMWKl'...................'xWMMMM");
    puts("MMMM0:lKMMMMMMMMMMMMMMMMMMMMMNk:...:0WMMMMMMMMMMMW0l'.....................lXMMMM");
    puts("MMMMk:xNMMMMMMMMMMMMMMMMMMMWKo,....,kWMMMMMMMMMWXx;.......................;0MMMM");
    puts("MMMWd:0WMMMMMMMMMMMMMMMMMMW0c......;OWMMMMMMMWXkc'........................'OMMMM");
    puts("MMMNdcKMMMMMMMMMMMMMMMMMMMWO,.....;xNMMMMMMMXOl;''',,,,........';;'.......'kMMMM");
    puts("MMMWdcKMMMMMMMMMMMMMMMMMMMMXo'.'cxKWMMMMMMMMX0000KKKXXk:...,;cl:,.........'kMMMM");
    puts("MMMWxcOWMMMMMMMMMMMMMMMMMMXkl;';ld0NMMMMMMMMMMMMMMMMMMNkxkOOko;...........;0MMMM");
    puts("MMMM0cdNMMMMMMMMMMMMMMMMMW0;......oXMMMMMMMMMMMMMMMMMMMWX0xc,.............cXMMMM");
    puts("MMMMXoc0WMMMMMMMMMMMMMMMMW0;......lXMMMMMMMMMMMMMMMMMMWOc'................xWMMMM");
    puts("MMMMWO:oXMMMMMMMMMMMMMMMMW0;......lXMMMMMMMMMMMMMMMMMMNd'................:KMMMMM");
    puts("MMMMMNd;dXMMMMMMMMMMMMMMMW0;......lXMMMMMMMMMMMMMMMMMW0:................,kWMMMMM");
    puts("MMMMMMXl;dXWMMMMMMMMMMMMMW0;......lXMMMMMMMMMMMMMMMMMKo'...............'dNMMMMMM");
    puts("MMMMMMMKc,l0WMMMMMMMMMMMMW0;......lXMMMMMMMMMMMMMMMWKl'...............'dNMMMMMMM");
    puts("MMMMMMMMXl';xXWMMMMMMMMMMW0;......lXMMMMMMMMMMMMMMNk:................'dNMMMMMMMM");
    puts("kkkkkkkkkd:'':xXWMMMMMMMMW0;......lXMMMMMMMMMMMMNOl'................,lxkkkkkkkkk");
    puts("kkkkkkkkkkOkc..;oOXWMMMMMW0;......lXMMMMMMMMMWKkc'................'oOkxxxxxxxxxx");
    puts("MMMMMMMMMMMMNk:..';okKXWWW0;......lXMMMMMWNKkl;.................'cOWMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMXk:....';ldxd,......l0K0Oxdo:,..................'lONMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMMMNOl,..............',''......................;d0WMMMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMMMMMWXko;.................................':d0NMMMMMMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMMMMMMMMMN0xl:,........................,:okKWMMMMMMMMMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMMMMMMMMMMMMMNX0kdoc:;;,,'''',,;;:loxk0XWMMMMMMMMMMMMMMMMMMMMMMMMMM");
    puts("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWNNXXXXXXXXNNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM");
    puts("");
}

int main() {
    setup();

    while (1) {
        menu();
        switch (read_ulong()) {
            case 1:
                make_wax();
                break;
            case 2:
                dump_wax();
                break;
            case 3:
                pour_candle();
                break;
            case 4:
                list_candles();
                break;
            case 5:
                sell_candle();
                break;
            case 6:
                return 0;
        }
    }
}
