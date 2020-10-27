use super::*;

extern "C" {
    fn EVP_CIPHER_CTX_copy(out: *mut EVP_CIPHER_CTX, in_: *const EVP_CIPHER_CTX) -> i32;
}

#[no_mangle]
#[inline(never)]
pub unsafe fn encrypt(key: &[u8], iv: &[u8], data: &[u8]) -> Option<Vec<u8>> {
    let ctx = EVP_CIPHER_CTX_new();
    EVP_CipherInit(ctx, EVP_aes_128_gcm(), &key[0], &iv[0], 1);
    let mut ret = vec![0; data.len() + (data.len()/512)*16];
    let mut i = 0;
    let mut j = 0;
    while i < data.len() {
        if EVP_CipherUpdate(ctx, &mut ret[i + (i / 512)*16], &mut j, &data[i], 512) == 0 {
            EVP_CIPHER_CTX_free(ctx);
            return None;
        }
        i += 512;
        let ctx0 = EVP_CIPHER_CTX_new();
        EVP_CIPHER_CTX_copy(ctx0, ctx);
        if EVP_CipherFinal(ctx0, ptr::null_mut(), &mut j) == 0 {
            EVP_CIPHER_CTX_free(ctx0);
            EVP_CIPHER_CTX_free(ctx);
            return None;
        }
        EVP_CIPHER_CTX_ctrl(ctx0, EVP_CTRL_GCM_GET_TAG, 16, &mut ret[i + (i / 512)*16 - 16] as *mut _ as _);
        EVP_CIPHER_CTX_free(ctx0);
    }
    EVP_CIPHER_CTX_free(ctx);
    Some(ret)
}

#[no_mangle]
#[inline(never)]
pub unsafe fn decrypt(key: &[u8], iv: &[u8], data: &mut [u8]) -> Option<Vec<u8>> {
    let ctx = EVP_CIPHER_CTX_new();
    EVP_CipherInit(ctx, EVP_aes_128_gcm(), &key[0], &iv[0], 0);
    let mut ret = vec![0; data.len() - (data.len() / 512)*16];
    let mut i = 0;
    let mut j = 0;
    while i < data.len() {
        if EVP_CipherUpdate(ctx, &mut ret[i - (i / 512)*16], &mut j, &data[i], 512) == 0 {
            EVP_CIPHER_CTX_free(ctx);
            return None;
        }
        let ctx0 = EVP_CIPHER_CTX_new();
        EVP_CIPHER_CTX_copy(ctx0, ctx);
        EVP_CIPHER_CTX_ctrl(ctx0, EVP_CTRL_GCM_SET_TAG, 16, &mut data[i + 512] as *mut _ as _);
        if EVP_CipherFinal(ctx0, ptr::null_mut(), &mut j) == 0 {
            EVP_CIPHER_CTX_free(ctx0);
            EVP_CIPHER_CTX_free(ctx);
            return None;
        } else {
            EVP_CIPHER_CTX_free(ctx0);
        }
        i += 512+16;
    }
    EVP_CIPHER_CTX_free(ctx);
    Some(ret)
}
