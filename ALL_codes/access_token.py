import requests
from flask import Flask, redirect, request, session

app = Flask(__name__)
app.secret_key = 'IiO0DeTk'  # Change this to a secure random value

ANGLEONE_AUTHORIZATION_URL = 'https://angleone.com/oauth/authorize'
ANGLEONE_TOKEN_URL = 'https://angleone.com/oauth/token'
CLIENT_ID = 'REUG1397'
CLIENT_SECRET = '9601574b-c305-4824-b2ef-016e138e6aef'
REDIRECT_URI = 'http://127.0.0.1:5000/'

@app.route('/')
def index():
    # Redirect the user to the AngleOne authorization URL
    auth_url = f'{ANGLEONE_AUTHORIZATION_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=read'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Handle the callback from AngleOne
    code = request.args.get('code')

    # Exchange the authorization code for an access token
    token_url = ANGLEONE_TOKEN_URL
    params = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_url, data=params)

    if response.status_code == 200:
        # Store the access token in the session
        session['access_token'] = response.json()['access_token']
        return 'Access Token Obtained Successfully!'
    else:
        return 'Failed to obtain Access Token'

if __name__ == '__main__':
    app.run(debug=True)
