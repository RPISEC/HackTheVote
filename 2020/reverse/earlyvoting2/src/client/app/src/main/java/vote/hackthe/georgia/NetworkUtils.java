package vote.hackthe.georgia;

import android.net.Uri;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Date;

import javax.net.ssl.HttpsURLConnection;

public class NetworkUtils {
    private static final String LOG_TAG = "httpstuff";
    private static final String SERVER_BASE = "http://earlyvoting.hackthe.vote/georgia";

    public static String loginRequest(String username, String password, String token){
        HttpURLConnection urlConnection = null;
        BufferedReader reader = null;
        BufferedWriter writer = null;
        String bookJSONString = null;
        boolean res = false;
        try {
            Uri builtURI = Uri.parse(SERVER_BASE).buildUpon().appendPath("login").build();
            URL requestURL = new URL(builtURI.toString());

            urlConnection = (HttpURLConnection) requestURL.openConnection();
            urlConnection.setRequestMethod("POST");
            urlConnection.setDoOutput(true);
            urlConnection.setChunkedStreamingMode(0);
            urlConnection.connect();


            BufferedOutputStream outputStream = new BufferedOutputStream(urlConnection.getOutputStream());
            writer = new BufferedWriter(new OutputStreamWriter(outputStream, "UTF-8"));
            //String token = new TokenGenerator(username, password).get_token();
            writer.write(String.format("username=%s&password=%s&token=%s", username, password, token));
            writer.flush();

            InputStream inputStream = urlConnection.getInputStream();
            reader = new BufferedReader(new InputStreamReader(inputStream));
            StringBuilder builder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
                builder.append("\n");
            }
            if (builder.length() == 0) {
                return "";
            }

            bookJSONString = builder.toString();
            //Log.d(LOG_TAG, bookJSONString);
            JSONObject jo = new JSONObject(bookJSONString);
            if (!jo.getBoolean("success"))
                return "";
            return jo.getString("message");
        } catch (IOException e) {
            e.printStackTrace();
        }  catch (JSONException e) {
            e.printStackTrace();
        } finally {
            if (urlConnection != null) {
                urlConnection.disconnect();
            }
            if (writer != null) {
                try {
                    writer.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return "";
    }
    public static boolean voteRequest(String vote, String token){
        HttpURLConnection urlConnection = null;
        BufferedReader reader = null;
        BufferedWriter writer = null;
        String bookJSONString = null;
        boolean res = false;
        try {
            Uri builtURI = Uri.parse(SERVER_BASE).buildUpon().appendPath("vote").build();
            URL requestURL = new URL(builtURI.toString());

            urlConnection = (HttpURLConnection) requestURL.openConnection();
            urlConnection.setRequestMethod("POST");
            urlConnection.setDoOutput(true);
            urlConnection.setChunkedStreamingMode(0);
            urlConnection.connect();

            BufferedOutputStream outputStream = new BufferedOutputStream(urlConnection.getOutputStream());
            writer = new BufferedWriter(new OutputStreamWriter(outputStream, "UTF-8"));
            //String token = new TokenGenerator(username, password).get_token();
            writer.write(String.format("authtoken=%s&vote=%s", token, vote));
            writer.flush();

            InputStream inputStream = urlConnection.getInputStream();
            reader = new BufferedReader(new InputStreamReader(inputStream));
            StringBuilder builder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
                builder.append("\n");
            }
            if (builder.length() == 0) {
                return false;
            }

            bookJSONString = builder.toString();
            Log.d(LOG_TAG, bookJSONString);
            JSONObject jo = new JSONObject(bookJSONString);
            return jo.getBoolean("success");
        } catch (IOException e) {
            e.printStackTrace();
        }  catch (JSONException e) {
            e.printStackTrace();
        } finally {
            if (urlConnection != null) {
                urlConnection.disconnect();
            }
            if (writer != null) {
                try {
                    writer.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return false;
    }
}
