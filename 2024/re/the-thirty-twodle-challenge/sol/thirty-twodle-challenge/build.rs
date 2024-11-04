fn main() {
    // Tell Cargo that if the given file changes, to rerun this build script.
    println!("cargo::rerun-if-changed=obj/challenge.c");
    println!("cargo::rerun-if-changed=obj/wordlist.h");
    // Use the `cc` crate to build a C file and statically link it.
    cc::Build::new()
        .file("obj/challenge.c")
        .file("obj/wordlist.h")
        .compile("hello");
}
