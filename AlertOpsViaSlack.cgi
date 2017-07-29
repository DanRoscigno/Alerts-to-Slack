#!/opt/IBM/netcool/python27/bin/python
print "Content-type: text/html"
print
print "<pre>"

import json
import requests
# put your webhook url that looks like:
#   https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX'
# in a file named webhooktoken.py and then it will be read in using the next two lines:
import webhooktoken
webhook_url = webhooktoken.token

import os, sys
from cgi import escape
print "<strong>Python %s</strong>" % sys.version
keys = os.environ.keys()
keys.sort()
for k in keys:
    print "%s\t%s" % (escape(k), escape(os.environ[k]))
user = os.environ['WEBTOP_USER']

slack_data = {
    "channel": "foo",
    # This next line subs the var user in for the SRE's name, and we got that name from os.environ['WEBTOP_USER']
    "text": "Sent by SRE %s" % user,
    "attachments": [
        {
            "fallback": "Summary: The router is on fire, Node: sifr40eoisfoo.very.long.domainname, AlertKey: CSI_ISMBadWebSiteFatal, NodeAlias: 127.0.0.2, Severity: Critical.",
            "title_link": "https://blue-hybrid.slack.com/messages/C60S7QPDW",
            "title": "Alert from SRE team",
            "color": "danger",
            "fields": [
                {
                    "short": "false",
                    "value": "The router is on fire",
                    "title": "Summary"
                },
                {
                    "short": "false",
                    "value": "sifr40eoisfoo.very.long.domainname",
                    "title": "Node"
                },
                {
                    "short": "false",
                    "value": "CSI_ISMBadWebSiteFatal",
                    "title": "AlertKey"
                },
                {
                    "short": "true",
                    "value": "127.0.0.2",
                    "title": "NodeAlias"
                },
                {
                    "short": "true",
                    "value": "Critical",
                    "title": "Severity"
                }
            ]
        }
    ]
}

slackResponse = requests.post(
    webhook_url, data=json.dumps(slack_data),
    headers={'Content-Type': 'application/json'}
)

if slackResponse.status_code != 200:
    raise ValueError(
        'There was an error (%s) during posting the message to slack, the response is:\n%s'
        % (slackResponse.status_code, slackResponse.text)
    )

for k in keys:
    print "%s\t%s" % (escape(k), escape(os.environ[k]))

print json.dumps(slack_data, sort_keys=False, indent=4, separators=(',', ': '))

print "</pre>"
