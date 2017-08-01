#!/opt/IBM/netcool/python27/bin/python
print "Content-type: text/html"
print
print "<pre>"

import json
import requests

"""
Put your webhook url that looks like:
   https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX'
and the slack channel name for each ops team in a file named webhooktoken.ini in this format:

[APPNAME1]
token: https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX
channel: app1-ops-events

[APPNAME2]
token: https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX
channel: app2-ops-events
"""

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("/opt/IBM/netcool/gui/omnibus_webgui/etc/cgi-bin/webhooktoken.ini")

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1



import os, sys
from cgi import escape

keys = os.environ.keys()

"""
Extract the information we need from the os.environ() key value pairs.
The fields passed in from Netcool (Node, Summary, etc., are in
the QUERY_STRING, which looks like this:
QUERY_STRING	datasource=OMNIBUS&$selected_rows.NodeAlias=foo-demo&\
$selected_rows.AlertKey=CSI_ISMBadWebSiteFatal&\
$selected_rows.application=NC&$selected_rows.Severity=5&\
$selected_rows.ITMDisplayItem=nc:foo-demo/Unity&\
CONVERSION.$selected_rows.Severity=Critical&\
$selected_rows.Summary=nc:foo-demo/Unity&$selected_rows.Node=foo-demo
"""
user = os.environ['WEBTOP_USER']

alert_string = os.environ['QUERY_STRING'];

# Given 'A - 13, B - 14, C - 29, M - 99'
# split the string into "<key> = <value>" parts: s.split('&')
# split each part into "<key> ", " <value>" pairs: item.split('-')
# remove the whitespace from each pair: (k.strip(), v.strip())

alert_kvpairs = dict((k.strip(), v.strip()) for k,v in
              (item.split('=') for item in alert_string.split('&')))

"""
This gives me these keys:
    Key				Description
 $selected_rows.AlertKey             AlertKey
 $selected_rows.NodeAlias		         IP Address
 $selected_rows.Summary	             Summary
 $selected_rows.ITMDisplayItem	     Alternate Summary
 $selected_rows.application		       Ops group (lookup for slack channel
 CONVERSION.$selected_rows.Severity  Severity String
 $selected_rows.Node	               Hostname
"""

summary        = alert_kvpairs['$selected_rows.Summary']
summary        = summary + " " + alert_kvpairs['$selected_rows.ITMDisplayItem']
itmdisplayitem = alert_kvpairs['$selected_rows.ITMDisplayItem']
node           = alert_kvpairs['$selected_rows.Node']
alertkey       = alert_kvpairs['$selected_rows.AlertKey']
nodealias      = alert_kvpairs['$selected_rows.NodeAlias']
severity       = alert_kvpairs['CONVERSION.$selected_rows.Severity']
application    = alert_kvpairs['$selected_rows.application']

if alert_kvpairs['CONVERSION.$selected_rows.Severity'] == 'Critical':
	color = 'danger'
else:
	color = 'warning'
# Up top we defined ConfigSectionMap, now we will lookup the channel and token
channel = ConfigSectionMap(application)['channel']
token = ConfigSectionMap(application)['token']

slack_data = {
    "channel": "%s" % channel,
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
    token, data=json.dumps(slack_data),
    headers={'Content-Type': 'application/json'}
)

if slackResponse.status_code != 200:
    raise ValueError(
        'There was an error (%s) during posting the message to slack, the response is:\n%s'
        % (slackResponse.status_code, slackResponse.text)
    )


#print json.dumps(slack_data, sort_keys=False, indent=4, separators=(',', ': '))

print "</pre>"
