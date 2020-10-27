#include "module_lib.h"

#define KEY_DOWN 258
#define KEY_UP 259
#define KEY_ENTER 343

#define REQ_DOWN_ITEM 515
#define REQ_UP_ITEM 514
#define REQ_TOGGLE_ITEM 524

#define O_ONEVALUE 1

void do_menu(void* my_menu_win) {
    void* items[3];
    items[0] = new_item("President:","Washington");
    items[1] = new_item("President:","Lincoln");
    items[2] = new_item("Submit","");
    items[3] = NULL;

    void* menu = new_menu(items);
    menu_opts_off(menu, O_ONEVALUE);

    set_menu_win(menu, my_menu_win);
    set_menu_sub(menu, derwin(my_menu_win, 6, 38, 3, 1));

    set_menu_mark(menu, " * ");

    box(my_menu_win, 0, 0);

    post_menu(menu);
    refresh();

    int non_selected = 1;

    while(1) {
        wrefresh(my_menu_win);
        int c = getch();
        if (c == -1)
            break;

        if (c == KEY_DOWN) {
            menu_driver(menu, REQ_DOWN_ITEM);
            continue;
        }
        if (c == KEY_UP) {
            menu_driver(menu, REQ_UP_ITEM);
            continue;
        }
        if (c != '\n' && c != '\r') {
            continue;
        }

        void* citem = current_item(menu);
        int index = item_index(citem);
        if (index != 2) {
            non_selected = 0;
            menu_driver(menu, REQ_TOGGLE_ITEM);
            continue;
        }

        if (non_selected) {
            // TODO flash error
            continue;
        }

        // Fall out of loop bc we are done
        break;
    }

    unsigned char buf[32] = {0};


    // Submit
    int total = 0;
    int index = 2;
    for (int i=0; i<2; i++) {
        int selected = item_value(items[i]);
        total += selected;
        buf[index++] = i;
    }

    buf[0] = total;

    int total_points = 0xf;
    int share = share/total;

    buf[1] = share;

    send_ipc(10, buf, 32);

    unpost_menu(menu);
}

void _start(void* handle, dlsymfunc dlsym, ipc_client* client) {
    g_client = client;
    load_got(handle, dlsym);



    void* my_menu_win = newwin(10, 40, 4, 4);
    keypad(my_menu_win, 1);

    while(1){
        do_menu(my_menu_win);
    }





    endwin();
}
