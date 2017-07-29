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

# Extract the information we need from the os.environ() key value pairs.
# The fields passed in from Netcool (Node, Summary, etc., are in 
# the QUERY_STRING, which looks like this:
# QUERY_STRING	datasource=OMNIBUS&$selected_rows.NodeAlias=foo-demo&$selected_rows.AlertKey=CSI_ISMBadWebSiteFatal&$selected_rows.application=NC&$selected_rows.Severity=5&$selected_rows.ITMDisplayItem=nc:foo-demo/Unity&CONVERSION.$selected_rows.Severity=Critical&$selected_rows.Summary=nc:foo-demo/Unity&$selected_rows.Node=foo-demo

user = os.environ['WEBTOP_USER']

alert_string = os.environ['QUERY_STRING'];

# Given 'A - 13, B - 14, C - 29, M - 99'
# split the string into "<key> = <value>" parts: s.split('&')
# split each part into "<key> ", " <value>" pairs: item.split('-')
# remove the whitespace from each pair: (k.strip(), v.strip())

alert_kvpairs = dict((k.strip(), v.strip()) for k,v in 
              (item.split('=') for item in alert_string.split('&')))

for k in alert_kvpairs:
    print "%s\t%s" % (escape(k), escape(alert_kvpairs[k]))

# This gives me these keys:
#    Key				Description
# $selected_rows.AlertKey		AlertKey
# $selected_rows.NodeAlias		IP Address
# $selected_rows.Summary		Summary
# $selected_rows.ITMDisplayItem		Alternate Summary
# $selected_rows.application		Ops group (lookup for slack channel
# CONVERSION.$selected_rows.Severity	Severity String
# $selected_rows.Node			Hostname

summary        = alert_kvpairs['$selected_rows.Summary']
summary        = summary + " " + alert_kvpairs['$selected_rows.ITMDisplayItem']
itmdisplayitem = alert_kvpairs['$selected_rows.ITMDisplayItem']
node           = alert_kvpairs['$selected_rows.Node']
alertkey       = alert_kvpairs['$selected_rows.AlertKey']
nodealias      = alert_kvpairs['$selected_rows.NodeAlias']
severity       = alert_kvpairs['CONVERSION.$selected_rows.Severity']

if alert_kvpairs['CONVERSION.$selected_rows.Severity'] == 'Critical':
	color = 'danger'
else:
	color = 'warning'

slack_data = {
    "channel": "foo",
    # This next line subs the var user in for the SRE's name, and we got that name from os.environ['WEBTOP_USER']
    "text": "Sent by SRE %s" % user,
    "attachments": [
        {
            "fallback": "Summary: %s %s, Node: %s, AlertKey: %s, NodeAlias: %s, Severity: Critical." % (summary, itmdisplayitem, node, alertkey, nodealias),
            "title_link": "https://blue-hybrid.slack.com/messages/C60S7QPDW",
            "title": "Alert from SRE team",
            "color": "%s" % color,
            "fields": [
                {
                    "short": "false",
                    "value": "%s" % summary,
                    "title": "Summary"
                },
                {
                    "short": "false",
                    "value": "%s" % node,
                    "title": "Node"
                },
                {
                    "short": "false",
                    "value": "%s" % alertkey,
                    "title": "AlertKey"
                },
                {
                    "short": "true",
                    "value": "%s" % nodealias,
                    "title": "NodeAlias"
                },
                {
                    "short": "true",
                    "value": "%s" % severity,
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
