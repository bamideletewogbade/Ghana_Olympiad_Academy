from flask import Flask, render_template, request, jsonify

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = '1Ff7o2adQyI8rg0E9b0mI434tj3SFAziLQfAj2RD3inc' 
RANGE_NAME = 'Form Responses 1!E:E'

app = Flask(__name__)

def is_email_registered(email):
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return False

        for row in values:
            if len(row) >= 1 and row[0] == email:
                return True

        return False

    except HttpError as err:
        print(err)
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None

    if request.method == 'POST':
        user_email = request.form.get('email')
        is_registered = is_email_registered(user_email)

        if is_registered:
            message = f'{user_email} is registered for AMO 2023.'
        else:
            message = f'{user_email} is not registered.'

    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)