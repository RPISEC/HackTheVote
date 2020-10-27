package vote.hackthe.georgia.data;

import android.util.Log;

import vote.hackthe.georgia.NetworkUtils;
import vote.hackthe.georgia.data.model.LoggedInUser;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.time.DateTimeException;
import java.util.Date;

/**
 * Class that handles authentication w/ login credentials and retrieves user information.
 */
public class LoginDataSource {

    public Result<LoggedInUser> login(String username, String password) {
        //username = "BrandonJPatterson";
        //password = "loob1Quiep";
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssX");
        TokenGenerator tg = new TokenGenerator();
        tg.setCreds(username, password);
        tg.setDate(sdf.format(new Date()));
        String token = tg.generateToken();
        if (token.length() != 16) {
            return new Result.Error(new DateTimeException("Failed to generate token"));
        }
        //Log.d("login", "logging in " + username + ":" + password + " with token " + token);
        try {
            String authtoken = NetworkUtils.loginRequest(username, password, token);
            if (authtoken.length() != 0) {
                Log.d("login", "http success");
                LoggedInUser fakeUser = new LoggedInUser(authtoken, username);
                return new Result.Success<>(fakeUser);
            }
            else {
                return new Result.Error(new IOException("Error logging in"));
            }
        } catch (Exception e) {
            return new Result.Error(new IOException("Error logging in", e));
        }
    }

    public void logout() {
        // TODO: revoke authentication
    }
}