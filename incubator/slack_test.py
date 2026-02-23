
import requests
import json
import os




class slack_sender:
    def __init__(self):
        try:

            # Define email sender and receiver
         

            self.webhook_url_path = "/home/cjchandler/Desktop/slackwebhookurl.txt"
            self.webhook_url = ""
            with open(self.webhook_url_path, 'r', encoding='utf-8') as f:
                    self.webhook_url = f.read()
                    self.webhook_url = self.webhook_url.strip()
                    print(self.webhook_url)

        except:
            print("couldn't load webhook url")
            quit()
           
    def send_message( self, body):
       
        message_data = {
            "text": body
        }

        response = requests.post(
            self.webhook_url,
            data=json.dumps(message_data),
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
       
       

SS = slack_sender()

SS.send_message("testosI")

