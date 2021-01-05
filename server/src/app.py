from flask import Flask, render_template, make_response, redirect, request
from firebase import firebase
import polling2
import os
import requests
import datetime
import math

firebase = firebase.FirebaseApplication('', None)

app = Flask(__name__)

client_id = 'c5ce888ced12a359100959dea8c73c4699e1ec85da710681376cdf1b1fbc46fc'
client_secret = '9d9f32d7e153969e3c585f4f078683a9997bda85e8afd1cdabd6f7b0f4058647'
callback_uri = 'https://sleeping-aid-xolr33b7eq-uc.a.run.app/callback'

authorization_base_url='https://account.withings.com/oauth2_user/authorize2'
token_url='https://wbsapi.withings.net/v2/oauth2'

@app.route('/')
def index():
    authorization_url = authorization_base_url + "?response_type=code&client_id="+client_id+"&state=singledads&scope=user.activity,user.sleepevents&redirect_uri="+callback_uri
    return redirect(authorization_url)

@app.route('/callback', methods=['GET', 'POST'])
def callback():
    if request.method == 'POST':
        timestamp = str(math.floor(datetime.datetime.now().timestamp()))
        for key, val in request.form.items():
            firebase.put('/subscribe/' + timestamp, key, val)
        
        context = { 'page': request.form }
        return render_template('index.html', context=context)

    params={
        'code': request.args.get('code'),
        'client_id': client_id,
        'client_secret': client_secret,
        'action': 'requesttoken', 
        'redirect_uri': callback_uri,
        'grant_type': 'authorization_code'
    }

    response = requests.post(url=token_url, params=params)
   
    data = response.json()

    firebase.put('/auth','access_token', data['body']['access_token'])
    # access_token = data['body']['access_token']

    context = { 'page': data }
    return render_template('index.html', context=context)

def log_response(response):
    timestamp = str(math.floor(datetime.datetime.now().timestamp()))
    firebase.put('/polling', timestamp, str(response.json()))
    return False

@app.route("/heartrate", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    d = math.floor(datetime.datetime.now().timestamp())
    access_token = firebase.get('/auth/access_token', None)

    params = {
        'action': 'get',
        'startdate': str(d - 120),
        'enddate': str(d),
        'data_fields': 'hr'
    }
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    # response = requests.post(url='https://wbsapi.withings.net/v2/sleep', params=params, headers=headers)
    # data = response.json()

    # Poll for 2 hours
    polling2.poll(lambda: requests.post(url='https://wbsapi.withings.net/v2/sleep', params=params, headers=headers), step=60,timeout=7200, check_success=log_response)
    context = { 'page': "finished polling" }
    return render_template('index.html', context=context)

@app.route("/subscribe", methods=["GET"])
def subscribe():
    access_token = firebase.get('/auth/access_token', None)
    params = {
        'action': 'subscribe',
        'callbackurl': callback_uri,
        'appli': '50',  # 44
    }
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    response = requests.post(url='https://wbsapi.withings.net/notify', params=params, headers=headers)
    data = response.json()

    context = { 'page': data, 'info':'subscribe' }
    return render_template('index.html', context=context)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))