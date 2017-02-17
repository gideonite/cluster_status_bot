#!/usr/bin/python 

import os
import time
import datetime
import requests
from slackclient import SlackClient
from bs4 import BeautifulSoup as bs

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
CLUSTER_STATUS_URL = "https://scicomp.ethz.ch/wiki/System_status"

def log(msg):
    # TODO use a framework
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(timestamp + " LOG: " + msg)

def parse_status_from_href(href):
    if 'red' in href:
        return 'down'
    elif 'orange' in href:
        return 'partially operational'
    elif 'green' in href:
        return 'up and running'
    else:
        raise Exception("unhandled system status")

def fetch_cluster_status():
    log("fetching cluster status")

    page = requests.get(CLUSTER_STATUS_URL)
    soup = bs(page.content, "lxml")
    tables = soup.findAll('table')
    assert len(tables) == 2, \
        "Invariant that there are only two tables is no longer true"

    main, key = tables

    rows = main.findAll('tr')

    assert len(rows) == 2, \
        "Main table no longer has 2 rows. Fail."

    header, row = rows

    service_names = [h.contents[0] for h in header.findAll('a')]

    imgs = [a['href'] for a in row.findAll('a')]

    msgs = [parse_status_from_href(img) for img in imgs]

    ret = list(zip(service_names, msgs))

    ret = [(service_name, msg) for (service_name, msg) in ret if 'Brutus' not in service_name]

    return ret, ('down' in msgs)

def send_msg(msg, slack_client):
    log("sending msg: " + msg)

    slack_client.api_call("chat.postMessage", \
                          channel="@gideon", \
                          text=msg, as_user=True)
    
def report(msgs, slack_client):
    log("reporting")

    for service,status in msgs:
        print(service, status)

    text = '```'\
           + "\n".join([service + ": " + status for service, status in msgs]) \
           + '```'

    send_msg(text, slack_client)

REPORTED = False
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
READ_WEBSOCKET_DELAY = 60 # seconds
if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")

        while True:
            msgs, is_broken = fetch_cluster_status()

            if is_broken and not REPORTED:
                report(msgs, slack_client)
                REPORTED = True
            elif not is_broken and REPORTED:
                send_msg("all systems are go!", slack_client)
                REPORTED = False

            time.sleep(READ_WEBSOCKET_DELAY)
