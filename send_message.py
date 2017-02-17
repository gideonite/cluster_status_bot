import sys

import os
import time
import datetime
import requests
from slackclient import SlackClient

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

def send_msg(msg, ch, slack_client):
    # TODO duplicated =(
    #log("sending msg: " + msg)

    slack_client.api_call("chat.postMessage", \
                          channel=ch, \
                          text=msg, as_user=True)

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
if __name__ == "__main__":
    user_or_channel, msg = sys.argv[1:]

    send_msg(msg, user_or_channel, slack_client)


