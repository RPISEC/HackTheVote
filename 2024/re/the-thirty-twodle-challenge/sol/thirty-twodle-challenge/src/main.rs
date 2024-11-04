use std::hint::black_box;
use std::time::Instant;
use lazy_static::lazy_static;
use crate::rand::RandState;

mod rand;

const LETTERS: usize = 5;
const SOLUTION_COUNT: usize = 32;
const GUESS_COUNT: usize = 37;
const PRINT_ROWS: usize = 8;
const PRINT_COLS: usize = 4;

lazy_static! {
    static ref WORD_LIST: Vec<word_t> = load_word_list(include_str!("wordlist.txt"));
    static ref VALID_WORD_LIST: Vec<word_t> = load_word_list(include_str!("valid_wordlist.txt"));
}

fn load_word_list(text: &str) -> Vec<word_t> {
    text.split("\n").map(|chars| {
        assert_eq!(chars.len(), LETTERS);

        let mut word: word_t = word_t { letters: [b' '; LETTERS] };
        for i in 0..LETTERS {
            word.letters[i] = chars.as_bytes()[i];
        }
        word
    }).collect::<Vec<_>>()
}

#[repr(C)]
#[allow(non_camel_case_types)]
#[derive(Copy, Clone)]
struct word_t {
    pub letters: [u8; 5]
}

#[repr(C)]
#[allow(non_camel_case_types)]
#[derive(Copy, Clone)]
struct game_t {
    pub seed: u32,
    pub guesses: [word_t; 37],
    pub solutions: [word_t; 32],
    pub auto_solves: [u8; 32],
    pub guess_count: u8
}

extern "C" {
    fn chal_main(argc: u32, argv: *mut *mut u8) -> u32;
    fn check_word(guess: *const u8, solution: *const u8) -> u8;
    fn score_word(guess: *const word_t, solution: *const word_t, score: *mut [u8; 5]);
    fn print_guess(guess: *const word_t, solution: *const word_t, is_auto_solve: i32);
    fn print_game(game: *const game_t);
    fn mark_auto_solve(game: *mut game_t, word: *const word_t, solution: u8);
    fn run_auto_solver(game: *mut game_t) -> u8;
}

fn to_word(s: impl ToString) -> word_t {
    let string = s.to_string();
    word_t {
        letters: [
            string.as_bytes()[0],
            string.as_bytes()[1],
            string.as_bytes()[2],
            string.as_bytes()[3],
            string.as_bytes()[4],
        ]
    }
}

fn from_word(w: word_t) -> String {
    String::from_utf8_lossy(&w.letters).to_string()
}


fn main() {
    let make_game = |seed: u32| -> game_t {
        let mut solutions = [word_t { letters: [b' '; 5] }; 32];
        let mut rand = RandState::srand(seed);
        for i in 0..32 {
            solutions[i] = WORD_LIST[rand.rand_mut() as usize % WORD_LIST.len()];
        }

        game_t {
            seed,
            guesses: [word_t { letters: [0u8; 5] }; 37],
            solutions,
            auto_solves: [0; 32],
            guess_count: 0,
        }
    };

    let make_guess = |game: &mut game_t, guess: &word_t| {
        game.guesses[game.guess_count as usize].letters[0] = guess.letters[0];
        game.guesses[game.guess_count as usize].letters[1] = guess.letters[1];
        game.guesses[game.guess_count as usize].letters[2] = guess.letters[2];
        game.guesses[game.guess_count as usize].letters[3] = guess.letters[3];
        game.guesses[game.guess_count as usize].letters[4] = guess.letters[4];
        game.guess_count += 1;
    };

    let reset = |game: &mut game_t| {
        for i in 0..GUESS_COUNT {
            game.guesses[i].letters[0] = 0;
            game.guesses[i].letters[1] = 0;
            game.guesses[i].letters[2] = 0;
            game.guesses[i].letters[3] = 0;
            game.guesses[i].letters[4] = 0;
        }
        game.guess_count = 0;
    };

    let count_auto = |game: &mut game_t, words: &Vec<word_t>| {
        reset(game);
        for word in words {
            make_guess(game, word);
        }
        let mut solves = 0;
        while unsafe { run_auto_solver(game) } != 0 {
            solves += 1;
        }
        return solves;
    };

    let mut words = vec![
        to_word("waqfs"),
        to_word("brick"),
        to_word("glent"),
        to_word("jumpy"),
        to_word("vozhd"),
    ];

    let mut best = 0;
    let mut best_board = None;
    let mut best_seed = None;

    for seed in 0..10000 {
        let mut board = make_game(seed);
        let solves = count_auto(&mut board, &words);

        if solves > best {
            best = solves;
            best_board = Some(board);
            best_seed = Some(seed);
        }
    }

    count_auto(&mut best_board.unwrap(), &words);
    unsafe { print_game(&best_board.unwrap()); }

    println!("got {best} with {best_seed:x?}");
}