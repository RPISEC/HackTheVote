#include <openssl/md5.h>
#include <openssl/bn.h>

#include <stdio.h>
#include <stdlib.h>

#include <unistd.h>
#include <fcntl.h>

#define SIZE_N 512

int
main(int argc, char **argv)
{
    BN_CTX *ctx = BN_CTX_new();
    BIGNUM *n = NULL;
    BIGNUM *rem = BN_new();
    BIGNUM *q = BN_new();
    BIGNUM *p;
    char p_str[SIZE_N/2];
    char n_str[SIZE_N];
    int r = 0;
    unsigned int seed = 1477958400; /* 11/01/16 0:0:0 */
    //seed = 1477984206; // Seed answer

    /* Read modulus from file */
    r = open("modulus.bin", 0);
    read(r, n_str, SIZE_N);
    close(r);
    /* Convert to bignum */
    n = BN_bin2bn(n_str, SIZE_N, NULL);

    /* Find the rand seed */
    while (1) {
        srand(seed);
        for (int j = 0; j < 1500; j++) { // We don't know how many times is_prime failed
            for (int i = 0; i < MD5_DIGEST_LENGTH; i++) {
                r = rand();
                MD5((char*)&r, sizeof(int), p_str+(i*MD5_DIGEST_LENGTH));
            }
            // Convert to bignum and check if valid
            p = BN_bin2bn(p_str, sizeof(p_str), NULL);
            BN_mod(rem, n, p, ctx);
            if (BN_is_zero(rem)) {
                printf("Found seed! %u is_prime_loop: %u\n", seed, j);
                printf("p: ");
                BN_print_fp(stdout, p);
                BN_div(q, rem, n, p, ctx);
                printf("\nq: ");
                BN_print_fp(stdout, q);
                return 0;
            }
            BN_free(p);
        }
        seed++;
        /* Progress */
        if (seed % 1000 == 0)
            printf("%u\n", seed);
    }
  
    BN_free(p);
    return 0;
}
