#!/opt/IBM/netcool/python27/bin/python
import cgi
import cgitb; cgitb.enable()  # for troubleshooting

print "Content-type: text/html"
print

print """
<html>

<head><title>POSTed Data</title></head>

<body>

  <h3> Posted Data</h3>
"""

print """


  <pre>
"""
import os, sys
keys = os.environ.keys()

import urlparse
alert_info = {}
alert_info = dict(urlparse.parse_qsl(os.environ['QUERY_STRING']))

keys = alert_info.keys()
keys.sort()
for k in keys:
    print "%s\t\t%s" % (cgi.escape(k), cgi.escape(alert_info[k]))

print "%s\t\t%s" % ('WEBTOP_USER', os.environ['WEBTOP_USER'])

print """
  </pre>
</body>

</html>
"""
