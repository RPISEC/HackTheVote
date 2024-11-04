use curve25519_dalek::{RistrettoPoint, Scalar, digest::Update};
use group::{Group, GroupEncoding};
use lazy_static::lazy_static;
use rand_core::{OsRng, CryptoRngCore};
use serde::{Serialize, Deserialize};
use sha2::{Digest, Sha512};
use std::{fs, io::{self, Write}, ops};

lazy_static! {
    static ref BLINDING_FACTOR: RistrettoPoint = {
        RistrettoPoint::hash_from_bytes::<Sha512>(b"ZEROVOTE_BLINDING_FACTOR")
    };
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PedersenCommitment {
    pub point: RistrettoPoint,
}

impl PedersenCommitment {
    fn commit(x: Scalar, r: Scalar) -> PedersenCommitment {
        PedersenCommitment {
            point: RistrettoPoint::mul_base(&x) + *BLINDING_FACTOR * &r,
        }
    }
}

impl ops::Add<&PedersenCommitment> for PedersenCommitment {
    type Output = PedersenCommitment;

    fn add(self, other: &PedersenCommitment) -> PedersenCommitment {
        PedersenCommitment {
            point: self.point + &other.point,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct VoteCiphertext {
    pub count: PedersenCommitment,
    pub x: Scalar,
}

impl VoteCiphertext {
    fn new(vote: Scalar, rng: &mut impl CryptoRngCore) -> VoteCiphertext {
        let x = Scalar::random(rng);
        VoteCiphertext {
            count: PedersenCommitment::commit(vote, x),
            x,
        }
    }
}

impl ops::Add<&VoteCiphertext> for VoteCiphertext {
    type Output = VoteCiphertext;

    fn add(self, other: &VoteCiphertext) -> VoteCiphertext {
        VoteCiphertext {
            count: self.count + &other.count,
            x: self.x + &other.x,
        }
    }
}

impl ops::AddAssign<&VoteCiphertext> for VoteCiphertext {
    fn add_assign(&mut self, other: &VoteCiphertext) {
        self.count.point += &other.count.point;
        self.x += &other.x;
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Proof {
    xh: RistrettoPoint,
    rh: RistrettoPoint,
    xcr: Scalar,
}

impl Proof {
    fn generate(ctxt: VoteCiphertext, rng: &mut impl CryptoRngCore) -> Proof {
        let r = Scalar::random(rng);
        let xh = -RistrettoPoint::mul_base(&Scalar::ONE) + ctxt.count.point;
        let rh = *BLINDING_FACTOR * &r;
        let c = Scalar::from_hash::<Sha512>(Sha512::new().chain(xh.to_bytes()).chain(rh.to_bytes()));
        let xcr = ctxt.x * c + r;
        Proof { xh, rh, xcr }
    }

    fn check(&self) -> Result<(), ()> {
        let c = Scalar::from_hash::<Sha512>(Sha512::new().chain(self.xh.to_bytes()).chain(self.rh.to_bytes()));
        let lhs = *BLINDING_FACTOR * &self.xcr;
        let rhs = self.rh + self.xh * &c;
        if lhs == rhs {
            Ok(())
        } else {
            Err(())
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Ballot {
    a: VoteCiphertext,
    b: VoteCiphertext,
    c: VoteCiphertext,
    p: Proof,
}

impl Ballot {
    fn new(a: Scalar, b: Scalar, c: Scalar, rng: &mut impl CryptoRngCore) -> Ballot {
        let a = VoteCiphertext::new(a, rng);
        let b = VoteCiphertext::new(b, rng);
        let c = VoteCiphertext::new(c, rng);
        let p = Proof::generate(a.clone() + &b + &c, rng);
        Ballot { a, b, c, p }
    }
}

pub struct VoteAggregate {
    pub total_a: VoteCiphertext,
    pub total_b: VoteCiphertext,
    pub total_c: VoteCiphertext,
    pub count: u64,
}

impl VoteAggregate {
    fn new() -> VoteAggregate {
        let mut rng = OsRng;
        VoteAggregate {
            total_a: VoteCiphertext::new(Scalar::ZERO, &mut rng),
            total_b: VoteCiphertext::new(Scalar::ZERO, &mut rng),
            total_c: VoteCiphertext::new(Scalar::ZERO, &mut rng),
            count: 0,
        }
    }
    fn decrypt(&self) -> (u64, u64, u64) {
        let ag = self.total_a.count.point - *BLINDING_FACTOR * self.total_a.x;
        let bg = self.total_b.count.point - *BLINDING_FACTOR * self.total_b.x;
        let cg = self.total_c.count.point - *BLINDING_FACTOR * self.total_c.x;
        let (mut a, mut b, mut c) = (0, 0, 0);
        let mut tmp = RistrettoPoint::identity();
        for i in 0..self.count {
            if ag == tmp {
                a = i;
            }
            if bg == tmp {
                b = i;
            }
            if cg == tmp {
                c = i;
            }
            tmp += RistrettoPoint::mul_base(&Scalar::ONE);
        }
        (a, b, c)
    }
}

impl ops::AddAssign<&Ballot> for VoteAggregate {
    fn add_assign(&mut self, ballot: &Ballot) {
        if ballot.p.check().is_ok() {
            self.total_a += &ballot.a;
            self.total_b += &ballot.b;
            self.total_c += &ballot.c;
            self.count += 1;
        }
    }
}


fn init_ballots() -> Vec<Ballot> {
    let mut rng = OsRng;
    let mut ballots = Vec::new();
    for _ in 0..50 {
        ballots.push(Ballot::new(Scalar::ONE, Scalar::ZERO, Scalar::ZERO, &mut rng));
    }
    for _ in 0..50 {
        ballots.push(Ballot::new(Scalar::ZERO, Scalar::ONE, Scalar::ZERO, &mut rng));
    }
    ballots
}

fn main() -> io::Result<()> {
    println!("Welcome to ZeroVote, your friendly Zero Knowledge voting system!");
    'menu: loop {
        println!("1) Create ballot");
        println!("2) Cast vote");
        println!("3) Exit");
        print!("> ");
        io::stdout().flush()?;
        let mut choice = String::new();
        io::stdin().read_line(&mut choice)?;
        match choice.trim() {
            "1" => {
                'vote: loop {
                    println!("Who do you want to vote for?");
                    println!("a) Alice");
                    println!("b) Bob");
                    println!("c) Carol");
                    print!("> ");
                    io::stdout().flush()?;
                    let mut candidate = String::new();
                    io::stdin().read_line(&mut candidate)?;
                    let (mut a, mut b, mut c) = (Scalar::ZERO, Scalar::ZERO, Scalar::ZERO);
                    match candidate.trim() {
                        "a" => { a = Scalar::ONE; },
                        "b" => { b = Scalar::ONE; },
                        "c" => { c = Scalar::ONE; },
                        _ => {
                            println!("Invalid candidate.");
                            continue 'vote;
                        }
                    };
                    let ballot = Ballot::new(a, b, c, &mut OsRng);
                    println!("Here's your ballot: {}", serde_json::to_string(&ballot).unwrap());
                    continue 'menu;
                }
            },
            "2" => {
                let mut ballots = init_ballots();
                let mut aggregate = VoteAggregate::new();
                let mut ballot = String::new();
                println!("Enter ballot:");
                io::stdin().read_line(&mut ballot)?;
                if let Ok(ballot) = serde_json::from_str::<Ballot>(&ballot) {
                    ballots.push(ballot);
                } else {
                    println!("Invalid ballot.");
                    continue 'menu;
                }
                for ballot in ballots.iter() {
                    aggregate += ballot;
                }
                let (a, b, c) = aggregate.decrypt();
                if a > b && a > c {
                    println!("Alice wins!");
                } else if b > a && b > c {
                    println!("Bob wins!");
                } else if c > a && c > b {
                    println!("Carol wins!");
                    let flag = fs::read_to_string("/flag").unwrap();
                    println!("Flag: {}", flag);
                } else {
                    println!("Vote counts: Alice {}, Bob {}, Carol {}", a, b, c);
                }
                break 'menu;
            }
            "3" => {
                println!("Goodbye.");
                break 'menu;
            }
            _ => {
                println!("Invalid choice.");
                continue 'menu;
            }
        }
    }
    Ok(())
}
