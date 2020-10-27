use super::*;

#[test]
fn test_sbfi() {
    let mut sbfi = SBFI::new();

    sbfi.program.extend(&HELLO_WORLD_SBF[..]);
    
    sbfi.eval(false);
    //println!("{:p}", &sbfi.cells[0] as *const u64);
    //println!("{:x} {:x}", sbfi.cells[2], sbfi.cells[4]);
    println!("{:?}", sbfi);
}

#[test]
fn test_encryption() {
    //let mut urandom = File::open("/dev/urandom").unwrap();
    let mut key = [0u8; 16];
    let mut iv = [0u8; 16];
    //urandom.read_exact(&mut key[..]).unwrap();
    //urandom.read_exact(&mut iv[..]).unwrap();
    let mut input = vec![0; 2048];
    for i in 0..input.len() {
        input[i] = (i % 256) as _;
    }
    let output = unsafe { encrypt(&key[..], &iv[..], &input) };
    println!("ciphertext: {:?}", output);
    let mut output = output.expect("encryption shouldn't fail");
    let result = unsafe { decrypt(&key[..], &iv[..], &mut output) };
    println!("decryption result: {:?}", result);
    assert_eq!(result, Some(input));
    for i in 0..output.len() {
        let mut modified_ctxt = output.clone();
        modified_ctxt[i] ^= 1;
        assert_eq!(unsafe { decrypt(&key[..], &iv[..], &mut modified_ctxt) }, None);
    }
}

#[test]
fn test_sbfi_execve() {
    let mut sbfi = SBFI::new();
    sbfi.program.extend(&b">>,>++++++++<<<.>>>+++++++++++++++++++++++++++++++++++++++++++++++++++>,----------------<."[..]);
    sbfi.eval(false);
    println!("{:?}", sbfi);
}
