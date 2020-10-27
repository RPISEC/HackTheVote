package vote.hackthe.alabama;

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

import static java.lang.Math.abs;

public class NetworkUtils {
    private static final String LOG_TAG = "httpstuff";
    private static final String SERVER_BASE = "http://earlyvoting.hackthe.vote/alabama";

    public static String loginRequest(String username, String password, String token) {
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
            // Log.d(LOG_TAG, bookJSONString);
            JSONObject jo = new JSONObject(bookJSONString);
            if (!jo.getBoolean("success"))
                return "";
            return jo.getString("message");
        } catch (IOException e) {
            e.printStackTrace();
        } catch (JSONException e) {
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

    public static boolean voteRequest(String vote, String token) {
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
        } catch (JSONException e) {
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

    public static String timeRequest(Date curDate) {
        HttpURLConnection urlConnection = null;
        BufferedReader reader = null;
        BufferedWriter writer = null;
        String bookJSONString = null;
        String res = "";
        try {
            Uri builtURI = Uri.parse("https://worldtimeapi.org/api/timezone/America/Chicago.json");
            URL requestURL = new URL(builtURI.toString());
            urlConnection = (HttpsURLConnection) requestURL.openConnection();
            urlConnection.setRequestMethod("GET");
            urlConnection.connect();

            InputStream inputStream = urlConnection.getInputStream();
            reader = new BufferedReader(new InputStreamReader(inputStream));
            StringBuilder builder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
                builder.append("\n");
            }

            bookJSONString = builder.toString();
            //bookJSONString = "{\"abbreviation\":\"CDT\",\"client_ip\":\"XXX\",\"datetime\":\"2020-11-03T12:00:00.000000-05:00\",\"day_of_week\":2,\"day_of_year\":308,\"dst\":true,\"dst_from\":\"2020-03-08T08:00:00+00:00\",\"dst_offset\":3600,\"dst_until\":\"2020-11-01T07:00:00+00:00\",\"raw_offset\":-21600,\"timezone\":\"America/Chicago\",\"unixtime\":1604401201,\"utc_datetime\":\"XXXX\",\"utc_offset\":\"-05:00\",\"week_number\":45}\n";
            //Log.d(LOG_TAG, bookJSONString);

            JSONObject jo = new JSONObject(bookJSONString);
            if (jo.getString("datetime").substring(5, 7).equals("11"))
                res += "17";
            // 33
            res += String.valueOf((abs(jo.getInt("unixtime") - curDate.getTime()/ 1000) >> 3) + 33);
            if (jo.getInt("day_of_year") == 308)
                res += "ce";
            if (jo.getInt("week_number") == 45)
                res += "e3";
            if (jo.getInt("dst_offset") == -5)
                res += "4d"; // x
            if (jo.getInt("unixtime") - 1604401200 < 46800)
                res += "9f";
            if (jo.getString("datetime").substring(10, 11).equals("T"))
                res += "19";
            // ca
            res += jo.getString("timezone").substring(5, 7);
            // d
            res += jo.getString("abbreviation").substring(1, 2).toLowerCase();
            res += "f";
        } catch (IOException e) {
            e.printStackTrace();
        } catch (JSONException e) {
        } finally {
            if (urlConnection != null) {
                urlConnection.disconnect();
            }
            if (writer != null) {
                try {
                    writer.close();
                } catch (IOException e) {
                }
            }
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                }
            }
        }
        return res;
    }
}
