#!/usr/bin/python

import os
import sys
from slackclient import SlackClient

BOT_NAME = 'cluster_status'

token = os.environ.get('SLACK_BOT_TOKEN')

if __name__ == "__main__":
    if not token:
        print()
        print("ERROR: set SLACK_BOT_TOKEN as an environment variable")
        sys.exit(-1)

    slack_client = SlackClient(token)
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)

