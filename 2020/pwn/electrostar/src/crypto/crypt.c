#include <openssl/conf.h>
#include <openssl/evp.h>
#include <openssl/err.h>

#include <openssl/obj_mac.h>
#include <openssl/pem.h>
#include <openssl/ec.h>
#include <sys/mman.h>

#include "private.h"
#include "public.h"
#include "colors.h"

EC_GROUP *curve;

unsigned char* private_pem_p = private_pem;

char* sha256_hash(char* data, size_t data_len) {
    unsigned char* hash  = malloc(SHA256_DIGEST_LENGTH);

    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, data, data_len);
    SHA256_Final(hash, &sha256);
    return hash;
}

unsigned char* sign(char* data, size_t data_len, size_t* sig_len) { 

    /* ... Do some crypto stuff here ... */

    EC_KEY *key = NULL;

    BIO* private_bio = BIO_new_mem_buf(private_pem_p, private_pem_len);
    if (private_bio == NULL) {
        ERR_print_errors_fp(stdout);
        exit(1);
    }

    EVP_PKEY* evpkey = NULL;
    evpkey = PEM_read_bio_PrivateKey(private_bio, &evpkey, NULL, NULL);

    BIO_free(private_bio);

    if (evpkey==NULL){
        puts(RED "ERROR: Could not find PEM for private key:" CL);
        ERR_print_errors_fp(stdout);
        exit(1);
    }
    
    key = EVP_PKEY_get1_EC_KEY(evpkey);
    if (key==NULL){
        puts(RED "ERROR: Could not load private key:" CL);
        ERR_print_errors_fp(stdout);
        exit(1);
    }

    EVP_PKEY_free(evpkey);

    if(!EC_KEY_set_group(key,curve)) {
        puts(RED "ERROR: Could not set group for private key:" CL);
        ERR_print_errors_fp(stdout);
        exit(1);
    }

    *sig_len = ECDSA_size(key);
    
    unsigned char* sig_DER = calloc(*sig_len, 1);

    if (!ECDSA_sign(0, data, data_len, sig_DER, (unsigned int*)sig_len, key)) {
        puts(RED "ERROR: Could not make signature:" CL);
        ERR_print_errors_fp(stdout);
        exit(1);
    }

    /*
    for(int i = 0; i < *sig_len; i++)
        printf("%02x", sig_DER[i]);
    printf("\n");
    */

    EC_KEY_free(key);

    return sig_DER;
}


int validate(unsigned char* data, size_t data_len, const unsigned char* sig, size_t sig_len) {

    EC_KEY *key = NULL;

    if (!has_gui) {
        puts("Checking Module Signature:" WHITE);
        for(int i = 0; i < 64; i++) {
            if (i != 0 && i % 32 == 0)
                puts("");
            if (i < sig_len)
                printf("%02x", sig[i]);
            else
                printf("00");
        }
        puts(CL);
    }

    BIO* public_bio = BIO_new_mem_buf(public_pem, public_pem_len);
    if (public_bio == NULL) {
        ERR_print_errors_fp(stdout);
        exit(1);
    }

    EVP_PKEY* evpkey = NULL;
    evpkey = PEM_read_bio_PUBKEY(public_bio, &evpkey, NULL, NULL);

    BIO_free(public_bio);

    if (evpkey==NULL){
        puts(RED "ERROR: Could not find PEM for public key:" CL);
        ERR_print_errors_fp(stdout);
        exit(1);
    }

    key = EVP_PKEY_get1_EC_KEY(evpkey);
    if (key==NULL){
        puts("ERROR: Could load public key:");
        ERR_print_errors_fp(stdout);
        exit(1);
    }

    EVP_PKEY_free(evpkey);

    if(!EC_KEY_set_group(key,curve)) {
        puts(RED "ERROR: Could not set group for public key:" CL);
        ERR_print_errors_fp(stdout);
        exit(1);
    }

    int ret = ECDSA_verify(0, data, data_len, sig, sig_len, key);

    if (ret == -1) {
        puts(RED "ERROR: Signature invalid" CL);
        ERR_print_errors_fp(stdout);
    }

    EC_KEY_free(key);

    return ret;
}

int validate_blob(unsigned char* blob, size_t* blob_len, char**hash_out) {
    if (*blob_len < 1)
        return -1;

    unsigned char sig_len = blob[0];
    if (sig_len > 64)
        return -1;

    if (*blob_len < sig_len + 1) {
        return -1;
    }

    unsigned char* sig = blob + 1;

    // Move past len and sig
    *blob_len -= sig_len + 1;

    unsigned char* hash = sha256_hash(blob + sig_len + 1, *blob_len);

    if (!has_gui) {
        puts("Module hash:" WHITE);
        for(int i = 0; i < SHA256_DIGEST_LENGTH; i++)
            printf("%02x", hash[i]);
        puts(CL);
    }

    int res = validate(hash, SHA256_DIGEST_LENGTH, sig, sig_len);

    if (hash_out != NULL)
        *hash_out = hash;
    else
        free(hash);

    if (res != 1)
        return res;

    memmove(blob, blob + sig_len + 1, *blob_len);
    return res;
}

char* load_data_from_file(FILE* f, size_t* data_len) {
    fseek(f, 0, SEEK_END);
    size_t file_size = ftell(f);
    // Max size check
    if (file_size > 0x1000000) {
        puts(RED "ERROR: Image too large" CL);
        return NULL;
    }
    fseek(f, 0, SEEK_SET);
    unsigned char* data = calloc(file_size,1);
    *data_len = fread(data, 1, file_size, f);
    return data;
}

char* load_and_validate_blob(FILE* f, size_t* blob_len, char**hash_out) {
    unsigned char* blob = load_data_from_file(f, blob_len);

    int res = validate_blob(blob, blob_len, hash_out);
    if (res != 1) {
        // Error validating blob
        free(blob);
        return NULL;
    }

    if (!has_gui)
        puts(GREEN "Image Signature Validated" CL);
    return blob;
}

void sign_and_dump_blob(unsigned char* blob, size_t blob_len, FILE* f) {
    unsigned char* hash = sha256_hash(blob, blob_len);
    size_t sig_len = 0;
    unsigned char* sig = sign(hash, SHA256_DIGEST_LENGTH, &sig_len);

    // Wite a single byte for the length
    fwrite(&sig_len, 1, 1, f);
    fwrite(sig, sig_len, 1, f);
    fwrite(blob, blob_len, 1, f);

    free(hash);
    free(sig);
}

void init_ec() {
    private_pem_p = mmap(0,0x1000, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, 0, 0);
    if (private_pem_p == NULL){
        puts(RED "Could not map for key" CL);
        exit(1);
    }
    if (madvise(private_pem_p, 0x1000, MADV_WIPEONFORK) != 0) {
        puts(RED "Could not map for key" CL);
        exit(1);
    }
    printf("%p\n",private_pem_p);
    memcpy(private_pem_p, private_pem, private_pem_len);
    memset(private_pem, 0, private_pem_len);

    if(NULL == (curve = EC_GROUP_new_by_curve_name(NID_secp224r1))) {
        puts(RED "ERROR: Failied to load curve:" CL);
        ERR_print_errors_fp(stdout);
        exit(1);
    }
}
