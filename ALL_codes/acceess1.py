from flask import Flask, redirect, request
import requests
import base64

app = Flask(__name__)

# Your AngleOne API key and API secret
api_key = "IiO0DeTk"
api_secret = "9601574b-c305-4824-b2ef-016e138e6aef"

# AngleOne OAuth 2.0 endpoints
authorization_base_url = "https://angleone-auth-server.com/oauth/authorize"
token_url = "https://angleone-auth-server.com/oauth/token"

# Redirect URI for your Flask app
redirect_uri = "http://127.0.0.1:5000/callback"

# Encode API key and secret for Basic Authentication
api_credentials = base64.b64encode(f"{api_key}:{api_secret}".encode("utf-8")).decode("utf-8")

@app.route("/")
def home():
    # Redirect to AngleOne authorization URL
    return redirect(authorization_base_url + f"?client_id={api_key}&redirect_uri={redirect_uri}&response_type=code")

@app.route("/callback")
def callback():
    # Get authorization code from the callback URL
    code = request.args.get("code")

    # Exchange authorization code for an access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    headers = {
        "Authorization": f"Basic {api_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(token_url, data=token_data, headers=headers)

    if response.status_code == 200:
        # Access token successfully obtained
        access_token = response.json()["access_token"]
        return f"Access Token: {access_token}"

    return "Failed to obtain access token"

if __name__ == "__main__":
    app.run(debug=True)
