from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages and session storage

WEBEX_API_URL = "https://webexapis.com/v1"


# ✅ Helper function to make API requests
def webex_request(endpoint, method="GET", data=None):
    if "access_token" not in session:
        flash("❌ No access token found. Please login again.", "danger")
        return None
    
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    url = f"{WEBEX_API_URL}/{endpoint}"

    response = requests.request(method, url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        flash("❌ Webex API Error: " + response.text, "danger")
        return None


# ✅ Homepage - Enter Webex Token
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["access_token"] = request.form["access_token"]
        
        # Test token validity
        user_info = webex_request("people/me")
        if not user_info:
            session.pop("access_token", None)
            return redirect(url_for("index"))

        return redirect(url_for("menu"))

    return render_template("index.html")


# ✅ Main Menu
@app.route("/menu")
def menu():
    if "access_token" not in session:
        return redirect(url_for("index"))
    
    return render_template("menu.html")


# ✅ Test Webex Connection (Option 0)
@app.route("/test_connection")
def test_connection():
    success = bool(webex_request("people/me"))
    return render_template("test_connection.html", success=success)


# ✅ Display User Info (Option 1)
@app.route("/user_info")
def user_info():
    user_info = webex_request("people/me")
    if not user_info:
        return redirect(url_for("menu"))

    return render_template("user_info.html", user_info=user_info)


# ✅ Display List of Rooms (Option 2)
@app.route("/rooms")
def rooms():
    rooms_data = webex_request("rooms")
    
    if rooms_data:
        rooms_list = rooms_data.get("items", [])[:5]  # Get the first 5 rooms
        return render_template("rooms.html", rooms=rooms_list)

    return redirect(url_for("menu"))


# ✅ Create a Room (Option 3)
@app.route("/create_room", methods=["GET", "POST"])
def create_room():
    if request.method == "POST":
        room_title = request.form["room_title"]
        response = webex_request("rooms", "POST", {"title": room_title})

        if response:
            flash(f"✅ Room '{room_title}' created successfully!", "success")
        else:
            flash("❌ Failed to create room. Please try again.", "danger")

    return render_template("create_room.html")


# ✅ Send Message to a Room (Option 4)
@app.route("/send_message", methods=["GET", "POST"])
def send_message():
    rooms_data = webex_request("rooms")

    if not rooms_data:
        return redirect(url_for("menu"))

    rooms_list = rooms_data.get("items", [])[:5]

    if request.method == "POST":
        room_id = request.form["room_id"]
        message = request.form["message"]
        response = webex_request("messages", "POST", {"roomId": room_id, "text": message})

        if response:
            flash("✅ Message sent successfully!", "success")
        else:
            flash("❌ Failed to send message. Please try again.", "danger")

    return render_template("send_message.html", rooms=rooms_list)


# ✅ Logout (Clears Session)
@app.route("/logout")
def logout():
    session.clear()
    flash("✅ Logged out successfully.", "success")
    return redirect(url_for("index"))


# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
