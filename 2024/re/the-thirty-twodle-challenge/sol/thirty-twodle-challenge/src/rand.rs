
// Poorly translated from:
// https://gist.github.com/integeruser/4cca768836c68751904fe215c94e914c
// http://www.mscs.dal.ca/~selinger/random/

#[derive(Copy, Clone)]
pub struct RandState {
    r: [u32; 34],
    k: usize,
}

impl RandState {
    pub fn srand(seed: u32) -> Self {
        let mut r = [0; 34];
        r[0] = seed;
        for i in 1..31 {
            r[i] = (16807u64 * (r[i - 1] as u64) % 2147483647u64) as u32;
        }
        for i in 31..34 {
            r[i] = r[i - 31];
        }

        let mut result = Self {
            r,
            k: 0
        };

        for _ in 34..344 {
            result.rand_mut();
        }

        result
    }

    pub fn rand_mut(&mut self) -> u32 {
        let k1 = (self.k + 34 - 31) % 34;
        let k2 = (self.k + 34 - 3) % 34;
        self.r[self.k] = self.r[k1].wrapping_add(self.r[k2]);
        let r = self.r[self.k] >> 1;
        self.k = (self.k + 1) % 34;
        r
    }

    pub fn rand(&self) -> (u32, Self) {
        let mut copy = *self;
        let result = copy.rand_mut();
        (result, copy)
    }
}


mod test {
    use crate::rand::RandState;

    #[test]
    fn test() {
        let mut rand = RandState::srand(1337);
        assert_eq!(rand.rand_mut(), 292616681);
        assert_eq!(rand.rand_mut(), 1638893262);
        assert_eq!(rand.rand_mut(), 255706927);
        assert_eq!(rand.rand_mut(), 995816787);
        assert_eq!(rand.rand_mut(), 588263094);
        assert_eq!(rand.rand_mut(), 1540293802);
        assert_eq!(rand.rand_mut(), 343418821);
        assert_eq!(rand.rand_mut(), 903681492);
        assert_eq!(rand.rand_mut(), 898530248);
        assert_eq!(rand.rand_mut(), 1459533395);

        let rand = RandState::srand(1337);
        let (r, rand) = rand.rand();
        assert_eq!(r, 292616681);
        let (r, rand) = rand.rand();
        assert_eq!(r, 1638893262);
        let (r, rand) = rand.rand();
        assert_eq!(r, 255706927);
        let (r, rand) = rand.rand();
        assert_eq!(r, 995816787);
        let (r, rand) = rand.rand();
        assert_eq!(r, 588263094);
        let (r, rand) = rand.rand();
        assert_eq!(r, 1540293802);
        let (r, rand) = rand.rand();
        assert_eq!(r, 343418821);
        let (r, rand) = rand.rand();
        assert_eq!(r, 903681492);
        let (r, rand) = rand.rand();
        assert_eq!(r, 898530248);
        let (r, rand) = rand.rand();
        assert_eq!(r, 1459533395);
    }
}
