#!/usr/bin/env run-cargo-script
/*!
```cargo
[dependencies]
libc = "0.2.74"
openssl-sys = "0.9"
```
*/
extern crate openssl_sys;

use std::collections::HashSet;
use std::fmt;
use std::fs::File;
use std::io::{BufRead, BufReader, Read, Write, stdin, stdout};
pub use std::ptr;
pub use openssl_sys::*;

pub struct SBFI {
    pub cells: Vec<u64>,
    pub program: Vec<u8>,
    pub idx: usize,
    pub pc: usize,
    pub jumpstack: Vec<usize>,
}

impl fmt::Debug for SBFI {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.debug_struct("SBFI")
            .field("cells", &self.cells)
            .field("program", &String::from_utf8_lossy(&self.program[std::cmp::max(self.pc as isize, 0) as usize..std::cmp::min(self.pc+5, self.program.len())]))
            .field("idx", &self.idx)
            .field("pc", &self.pc)
            .field("jumpstack", &self.jumpstack)
            .finish()
    }
}

const NUM_CELLS: usize = 24;
const PROGRAM_SIZE: usize = 4096;

pub mod interpreter;

impl SBFI {
    pub fn new() -> SBFI {
        SBFI {
            cells: vec![0; NUM_CELLS],
            program: vec![],
            idx: 0,
            pc: 0,
            jumpstack: vec![],
        }
    }
    pub fn interpret(&mut self, instruction: u8) {
        interpreter::interpret_instruction(self, instruction);
    }
    pub fn step(&mut self, debug: bool) {
        if debug {
            println!("before step ({}): {:?}", self.program[self.pc] as char, self);
        }
        self.interpret(self.program[self.pc]);
    }
    pub fn eval(&mut self, debug: bool) {
        let mut seen = HashSet::new();
        while self.pc < self.program.len() {
            let oldpc = self.pc;
            self.step(debug && !seen.contains(&self.pc));
            seen.insert(oldpc);
        }
        if debug {
            println!("end of eval: {:?}", self);
        }
    }
}

pub mod cryptography;
use cryptography::{encrypt, decrypt};

fn main() -> std::io::Result<()> { repl() }

#[no_mangle]
pub static HELLO_WORLD_SBF: &'static [u8; 2612] = include_bytes!("../hello_world.sbf");

#[no_mangle]
fn repl() -> std::io::Result<()> {
    let mut program = vec![0; PROGRAM_SIZE];
    program[0..2612].copy_from_slice(HELLO_WORLD_SBF);
    let mut urandom = File::open("/dev/urandom").unwrap();
    let mut key = [0u8; 16];
    let mut iv = [0u8; 16];
    urandom.read_exact(&mut key[..]).unwrap();
    urandom.read_exact(&mut iv[..]).unwrap();
    println!("Welcome to SBFOS, type \"boot\" to boot the default program, or \"help\" for more options.");
    loop {
        print!("secure-boot$ ");
        stdout().flush()?;
        let stdin = stdin();
        let mut buffered_stdin = BufReader::new(stdin.lock());
        let mut input = String::new();
        buffered_stdin.read_line(&mut input)?;
        if input.len() == 0 {
            break;
        }
        match input.trim() {
            "help" => show_help_menu(),
            "boot" => run_program(&program[..])?,
            "dump" => unsafe { dump_program(&key, &iv, &program[..])? },
            "load" => unsafe { load_program(&mut buffered_stdin, &key, &iv, &mut program[..])? },
            other => { println!("Unknown command {:?}", other); },
        }
    }
    println!("");
    Ok(())
}

#[no_mangle]
#[inline(never)]
fn show_help_menu() {
    println!("Supported commands:");
    println!("\thelp - display this menu");
    println!("\tboot - run the currently loaded program");
    println!("\tdump - display a ciphertext of the currently loaded program suitable for reloading");
    println!("\tload - load a program from its ciphertext");
}

#[no_mangle]
#[inline(never)]
fn run_program(program: &[u8]) -> std::io::Result<()> {
    let mut sbfi = SBFI::new();
    sbfi.program.extend(program);
    sbfi.eval(false);
    Ok(())
}

#[no_mangle]
#[inline(never)]
unsafe fn dump_program(key: &[u8], iv: &[u8], program: &[u8]) -> std::io::Result<()> {
    let ctxt = encrypt(key, iv, program).expect("encryption shouldn't fail - if you see this at runtime, contact the organizers");
    println!("{}", hexdump(&ctxt[..], 64));
    Ok(())
}

#[inline(never)]
unsafe fn load_program<R: Read>(mut r: R, key: &[u8], iv: &[u8], program: &mut [u8]) -> std::io::Result<()> {
    let mut buf = vec![0u8; PROGRAM_SIZE + (16*PROGRAM_SIZE/512)];
    let mut i = 0;
    println!("Enter ciphertext as hexpairs ({} raw bytes):", buf.len());
    while i < 2*buf.len() {
        let mut x = [0u8; 1];
        r.read_exact(&mut x)?;
        let shift_amount = if i % 2 == 0 { 4 } else { 0 };
        let nybble_value = match x[0] {
            y @ b'0'..= b'9' => y - b'0',
            y @ b'a'..= b'f' => y - b'a' + 10,
            y @ b'A'..= b'F' => y - b'A' + 10,
            _ => continue,
        };
        buf[i/2] |= nybble_value << shift_amount;
        i += 1;
    }
    if let Some(ptxt) = decrypt(key, iv, &mut buf) {
        assert_eq!(ptxt.len(), program.len());
        program[..].copy_from_slice(&ptxt[..]);
        println!("Successfully loaded new program");
    } else {
        println!("Decryption failed");
    }
    Ok(())
}

#[no_mangle]
pub static NYBBLE_LUT: &[u8; 16] = b"0123456789abcdef";

#[no_mangle]
fn hexdump(data: &[u8], bytes_per_line: usize) -> String {
    let mut buf = String::new();
    for (i, x) in data.iter().enumerate() {
        buf.push(NYBBLE_LUT[((x >> 4) & 0xf) as usize] as char);
        buf.push(NYBBLE_LUT[(x & 0xf) as usize] as char);
        if i % bytes_per_line == bytes_per_line - 1 {
            buf.push('\n')
        }
    }
    buf
}
