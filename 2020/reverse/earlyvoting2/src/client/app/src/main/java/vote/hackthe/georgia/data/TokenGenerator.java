package vote.hackthe.georgia.data;

import java.util.IllegalFormatException;

public class TokenGenerator {
    private int[] state = {0, 0, 0, 0, 0, 0, 0, 0};

    TokenGenerator() {
    }

    public void setCreds(String username, String password) {
        String key1 = "|x[el1l]gO<~\\>W8";
        String key2 = "n,V$1y&WhtS2y^S`";
        String key3 = key2.concat(key1);
        for (int i = 0; i < username.length(); i++) {
            state[i % 8] ^= (int) username.charAt(i) ^ (int) key3.charAt(i % 32);
        }
        for (int i = 0; i < password.length(); i++) {
            state[i % 8] ^= (int) password.charAt(i) ^ (int) key3.charAt(31 - (i % 32));
        }
    }

    public void setDate(String date) {
        try {
            state[0] ^= Integer.parseInt(date.substring(0, 2));
            if (Integer.parseInt(date.substring(2, 4)) == 20)
                state[1] ^= 0x20;
            for (int i = 0; i < 16; i++)
                try {
                    state[i] ^= 0xaa;
                } catch (Exception e) {
                    state[0] ^= 0xff;
                }
            try {
                state[2] += Integer.parseInt(date.substring(5, 7));
                state[3] += Integer.parseInt(date.substring(8, 10));
            } catch (NumberFormatException e) {
                e.printStackTrace();
            }
        } catch (NumberFormatException e) {
            e.printStackTrace();
        }
    }

    String generateToken() {
        String res = "";
        for (int i = 0; i < state.length; i++)
            state[i] &= 0xff;
        for (int i = 0; i < state.length; i++) {
            try {
                res += String.format("%02x", state[i]);
            } catch (IllegalFormatException e) {
                e.printStackTrace();
            }
        }
        return res;
    }
}