use super::{SBFI, NUM_CELLS};

pub fn interpret_instruction(sbfi: &mut SBFI, instruction: u8) {
    match instruction {
        b'-' => { sbfi.cells[sbfi.idx] = sbfi.cells[sbfi.idx].wrapping_sub(1); },
        b'+' => { sbfi.cells[sbfi.idx] = sbfi.cells[sbfi.idx].wrapping_add(1); },
        b'<' => { sbfi.idx = sbfi.idx.wrapping_sub(1) % NUM_CELLS; },
        b'>' => { sbfi.idx = sbfi.idx.wrapping_add(1) % NUM_CELLS; },
        b'[' => { sbfi.jumpstack.push(sbfi.pc); },
        b']' => {
            if let Some(loopstart) = sbfi.jumpstack.pop() {
                if sbfi.cells[sbfi.idx] != 0 {
                    sbfi.pc = loopstart;
                    return;
                }
            }
        },
        b',' => { sbfi.cells[sbfi.idx] = &sbfi.cells[sbfi.idx] as *const _ as usize as u64 },
        b'.' => {
            let mut args = [0; 7];
            for (i, x) in args.iter_mut().enumerate() {
                *x = sbfi.cells[(sbfi.idx + i) % NUM_CELLS] as i64;
            }
            let ret = unsafe { libc::syscall(args[0], args[1], args[2], args[3], args[4], args[5], args[6]) };
            sbfi.cells[sbfi.idx] = ret as u64;
        }
        _ => {},
    }
    sbfi.pc += 1;
}
