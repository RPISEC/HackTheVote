#[test]
fn test_ballot() {
    let mut rng = rand_core::OsRng;
    let ballot = Ballot::new(Scalar::from(0u8), Scalar::ZERO, Scalar::ZERO, &mut rng);
    println!("{:?}", ballot);
    println!("{:?}", ballot.p.check());
}

#[test]
fn test_winning_ballot() {
    let ballot = Ballot::new(-Scalar::from(99u8), Scalar::ZERO, Scalar::from(100u8), &mut OsRng);
    println!("{}", serde_json::to_string(&ballot).unwrap());
}
