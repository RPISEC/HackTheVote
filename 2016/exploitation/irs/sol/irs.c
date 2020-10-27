
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


struct Return{
    char name[50];
    char pass[50];
    int income;
    int deduct;
};

void menu(struct Return** taxes)
{
    int i;

    printf("Welcome to the IRS!\r\n");
    printf("How may we serve you today?\r\n");
    printf("1. File a tax return\r\n");
    printf("2. Delete a tax return\r\n");
    printf("3. Edit a tax return\r\n");
    printf("4. View a tax return\r\n");
    printf("5. Exit\r\n");
    printf("\r\n");
    printf("Tax returns on file:\r\n");
    
    for (i=0; i<5; i++)
    {
        if (taxes[i] != NULL)
            printf("%d - %s\r\n", i, taxes[i]->name);
    }
}

void add_return(char* name, char* pass, int income, int deduct, struct Return** taxes, int i)
{
    struct Return* new_return;

    new_return = (struct Return*)malloc(sizeof(struct Return));
    
    //add the name
    strncpy(new_return->name, name, strlen(name));
    
    //add the password 
    strncpy(new_return->pass, pass, strlen(pass));

    new_return->income = income;
    new_return->deduct = deduct; 

    taxes[i] = new_return;

    printf("Thank you for doing your civic duty %s!\r\n", name);
}

void delete_return(struct Return** taxes, int i)
{
    char* n = taxes[i]->name;

    printf("%s's tax return deleted\r\n", n);
    free(taxes[i]);
    taxes[i] = NULL;

}

void edit_return(struct Return** taxes, int i)
{
    char num[5];
    int in;
    int ded;

    printf("Enter the new income: ");
    fgets(num, sizeof(num), stdin);
    in = atoi(num);
    printf("Enter the new deductible: ");
    
    fgets(num, sizeof(num), stdin);
    ded = atoi(num);

    taxes[i]->income = in;
    taxes[i]->deduct = ded;

    printf("Is this correct?\r\n");
    printf("Income: %d\r\n", in);
    printf("Deductible: %d\r\n", ded);
    printf("y/n\r\n");

    gets(num);
    
    printf("Your changes have been recorded!\r\n");
}

void view_return(struct Return** taxes, int i)
{
    printf("--------------------------------------------------------------------------------\r\n");
    printf("| Name: %-70s |\r\n", taxes[i]->name);
    printf("| Income: %-68d |\r\n", taxes[i]->income);
    printf("| Deductable: %-64d |\r\n", taxes[i]->deduct);
    printf("| Password: %-66s |\r\n", taxes[i]->pass);
    printf("--------------------------------------------------------------------------------\r\n");
}

char check_pass(char* pass, struct Return** taxes, int i)
{
    return strncmp(pass, taxes[i]->pass, strlen(taxes[i]->pass)) == 0;
}

int main(int argc, char* argv[], char* envp[])
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    char buff[3];
    struct Return *taxes[5];

    char name[50];
    char pass[50];
    char num[5];
    int in;
    int ded;
    int i;

    for (i=0; i<5; i++)
        taxes[i] = NULL;

    //create Trump's return

    struct Return* Trump;
    Trump = (struct Return*)malloc(sizeof(struct Return));
    strncpy(Trump->name, "Donald Trump", strlen("Donald Trump"));
    strncpy(Trump->pass, "not_the_flag", strlen("not_the_flag"));
    Trump->income = 9999999999999;
    Trump->deduct = 9999999999999;

    taxes[0] = Trump;

    while(1)
    {
        menu(taxes); //print menu

        fgets(buff, sizeof(buff), stdin); //pick menu option

        memset(name, '\0', sizeof(name));
        memset(pass, '\0', sizeof(pass));

        if (!strncmp(buff, "1", 1)) //add form
        {
            for (i=0; i<5; i++)
            {
                if (taxes[i] == NULL)
                    break;
            }

            if (i == 5)
            {
                printf("The IRS is full. Please delete a record and try again\r\n");
                printf("If this problem persists, contact us at this address: %p\r\n", &taxes);
                continue;
            }

            printf("Enter the name: ");
            fgets(name, sizeof(name), stdin);
            name[strlen(name)-1] = '\0';

            printf("Enter the password: ");
            fgets(pass, sizeof(pass), stdin);
            pass[strlen(pass)-1] = '\0';

            printf("Enter the income: ");
            fgets(num, sizeof(num), stdin);

            in = atoi(num);

            printf("Enter the deductions: "); 
            fgets(num, sizeof(num), stdin);
            ded = atoi(num);

            add_return(name, pass, in, ded, taxes, i);
        }

        else if (!strncmp(buff, "2", 1)) //delete form
        {
            printf("Enter the name of the file to delete: ");
            fgets(name, sizeof(name), stdin);
            name[strlen(name)-1]='\0';

            printf("Enter the password: ");
            fgets(pass, sizeof(pass), stdin);
            pass[strlen(pass)-1]='\0';

            for (i=0; i<5; i++)
            {
                if (taxes[i] != NULL && !strncmp(name, taxes[i]->name, strlen(taxes[i]->name)))
                    break;
            }

            printf("%d\r\n", i == 5);

            if (i == 5)
            {
                printf("%s does not seem to be in our records\r\n", name);
                continue;
            }

            if (check_pass(pass, taxes, i))
                delete_return(taxes, i);
        }

        else if (!strncmp(buff, "3", 1)) //edit form
        {
            printf("Enter the name of the file to edit: ");
            fgets(name, sizeof(name), stdin);
            name[strlen(name)-1]='\0';

            for (i=0; i<5; i++)
            {
                if (taxes[i] != NULL && !strncmp(name, taxes[i]->name, strlen(taxes[i]->name)))
                    break;
            }

            if (i == 5)
            {
                printf("%s does not seem to be in our records\r\n", name);
                continue;
            }

            printf("Enter the password: ");
            fgets(pass, sizeof(pass), stdin);
            pass[strlen(pass)-1]='\0';

            if (check_pass(pass, taxes, i))
                edit_return(taxes, i);
        }

        else if (!strncmp(buff, "4", 1)) //view form
        {
            printf("Enter the name of the file to view: ");
            fgets(name, sizeof(name), stdin);
            name[strlen(name)-1]='\0';

            for (i=0; i<5; i++)
            {
                if (taxes[i] != NULL && !strncmp(name, taxes[i]->name, strlen(taxes[i]->name)))
                    break;
            }

            if (i == 5)
            {
                    printf("Sorry, %s is not in our records\r\n", name);
                    continue;
            }

            printf("Enter the password: ");
            fgets(pass, sizeof(pass), stdin);

            if (check_pass(pass, taxes, i))
                view_return(taxes, i);
        }

        else if(!strncmp(buff, "5", 1)) //quit
        {
            printf("Have a good day :)\r\n");
            break;
        }

        else
        {
            printf("Sorry, invalid option\r\n");
        }
    }
    return 0;
}
