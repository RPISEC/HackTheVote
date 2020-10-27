package vote.hackthe.alabama.ui.login;

/**
 * Class exposing authenticated user details to the UI.
 */
class LoggedInUserView {
    private String displayName;
    private String token;
    //... other data fields that may be accessible to the UI

    LoggedInUserView(String displayName, String token) {
        this.displayName = displayName;
        this.token = token;
    }

    String getToken() {
        return token;
    }
}