from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/alabama/login", methods=["POST"])
def login1():
    for field in ("username", "password", "token"):
        if field not in request.form:
            return jsonify({"success": False, "message": f"Needs {field}"})
    if (
        request.form["username"] == "PaulineAAvery"
        and request.form["password"] == "oghaCh5ei"
    ):
        if request.form["token"] == "1733cee39f19cadf":
            return jsonify({"success": True, "message": "27efa4c9b8e2cc50"})
        return jsonify({"success": False, "message": f"Invalid token"})
    return jsonify({"success": False, "message": f"Invalid credentials"})


@app.route("/alabama/vote", methods=["POST"])
def vote1():
    for field in ("authtoken", "vote"):
        if field not in request.form:
            return jsonify({"success": False, "message": f"Needs {field}"})
    if request.form["authtoken"] != "27efa4c9b8e2cc50":
        return jsonify({"success": False, "message": f"Invalid authtoken"})
    return jsonify(
        {
            "success": True,
            "message": "flag{Thanks for voting with Alabama's secure Android app!}",
        }
    )


@app.route("/georgia/login", methods=["POST"])
def login2():
    for field in ("username", "password", "token"):
        if field not in request.form:
            return jsonify({"success": False, "message": f"Needs {field}"})
    if (
        request.form["username"] == "BrandonJPatterson"
        and request.form["password"] == "loob1Quiep"
    ):
        if request.form["token"] == 'd4e5f69bacfdf8b6':
            return jsonify({"success": True, "message": "997a21b6e4574818"})
        return jsonify({"success": False, "message": f"Invalid token"})
    return jsonify({"success": False, "message": f"Invalid credentials"})


@app.route("/georgia/vote", methods=["POST"])
def vote2():
    for field in ("authtoken", "vote"):
        if field not in request.form:
            return jsonify({"success": False, "message": f"Needs {field}"})
    if request.form["authtoken"] != "997a21b6e4574818":
        return jsonify({"success": False, "message": f"Invalid authtoken"})
    return jsonify(
        {
            "success": True,
            "message": "flag{patching didn't help very much, did it}"
        }
    )
