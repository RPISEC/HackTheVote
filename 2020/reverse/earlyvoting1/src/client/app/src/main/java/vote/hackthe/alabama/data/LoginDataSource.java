package vote.hackthe.alabama.data;

import android.util.Log;

import vote.hackthe.alabama.NetworkUtils;
import vote.hackthe.alabama.data.model.LoggedInUser;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.DateTimeException;
import java.util.Date;

/**
 * Class that handles authentication w/ login credentials and retrieves user information.
 */
public class LoginDataSource {

    public Result<LoggedInUser> login(String username, String password) {
        String token;
        //SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssX");
        //Date startDate = sdf.parse("2020-11-03T06:00:00-05");
        token = NetworkUtils.timeRequest(new Date());
        //token = "1733cee39f19cadf";
        //username = "PaulineAAvery";
        //password = "oghaCh5ei";
        //Log.d("login", "checking timeb: " + token + " " + token.length());
        if (token.length() != 16) {

            return new Result.Error(new DateTimeException("The polls haven't opened yet"));
        }

        try {
            String authtoken = NetworkUtils.loginRequest(username, password, token);
            if (authtoken.length() != 0) {
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