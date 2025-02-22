#!/usr/bin/python3

import bson
import re
import smtplib
from email.mime.text import MIMEText

def format_query(query_usr):
	query_list = []
	for key, value in query_usr.items():
		if key == "hostname":
			qtag = ""
		else:
			qtag = "%s:" % key
		query_list.append("%s%s" % (qtag, value))
	return " ".join(query_list)

allowed_filters = (
	'status',
	'hood',
	'nickname',
	'hardware',
	'firmware',
	'mac',
	'hostname',
	'contact',
	'community',
	'neighbor',
	'neighbour',
	'gw',
	'selected',
	'bat',
	'batselected',
	'network',
	'os',
	'babel',
	'batman',
	'kernel',
	'nodewatcher',
)

def parse_router_list_search_query(args):
	query_usr = bson.SON()
	if "q" in args:
		for word in args["q"].strip().split(" "):
			if not word:
				# Case of "q=" without arguments
				break
			if not ':' in word:
				key = "hostname"
				value = word
			else:
				key, value = word.split(':', 1)
			if key in allowed_filters:
				query_usr[key] = query_usr.get(key, "") + value
	s = ""
	j = ""
	t = []
	i = 0
	for key, value in query_usr.items():
		if i==0:
			prefix = " WHERE "
		else:
			prefix = " AND "
		if value.startswith('!'):
			no = "NOT "
			value = value[1:]
		else:
			no = ""
		
		if value == "EXISTS":
			k = key + ' <> "" AND ' + key + " IS NOT NULL"
		elif value == "EXISTS_NOT":
			k = key + ' = "" OR ' + key + " IS NULL"
		elif key == 'mac':
			j += " INNER JOIN ( SELECT router, mac FROM router_netif GROUP BY router, mac) AS j ON router.id = j.router "
			k = "HEX(mac) {} REGEXP %s".format(no)
			t.append(value.replace(':',''))
		elif (key == 'gw'):
			j += " INNER JOIN router_gw ON router.id = router_gw.router "
			k = "HEX(router_gw.mac) {} REGEXP %s".format(no)
			t.append(value.replace(':',''))
		elif (key == 'selected'):
			j += " INNER JOIN router_gw ON router.id = router_gw.router "
			k = "HEX(router_gw.mac) {} REGEXP %s AND router_gw.selected = TRUE".format(no)
			t.append(value.replace(':',''))
		elif (key == 'bat'):
			j += """ INNER JOIN router_gw ON router.id = router_gw.router
				INNER JOIN (
					gw_netif AS n1
					INNER JOIN gw_netif AS n2 ON n1.mac = n2.vpnmac AND n1.gw = n2.gw
				) ON router_gw.mac = n1.mac
			"""
			k = "HEX(n2.mac) {} REGEXP %s".format(no)
			t.append(value.replace(':',''))
		elif (key == 'batselected'):
			j += """ INNER JOIN router_gw ON router.id = router_gw.router
				INNER JOIN (
					gw_netif AS n1
					INNER JOIN gw_netif AS n2 ON n1.mac = n2.vpnmac AND n1.gw = n2.gw
				) ON router_gw.mac = n1.mac
			"""
			k = "HEX(n2.mac) {} REGEXP %s AND router_gw.selected = TRUE".format(no)
			t.append(value.replace(':',''))
		elif (key == 'neighbor') or (key == 'neighbour'):
			j += " INNER JOIN ( SELECT router, mac FROM router_neighbor GROUP BY router, mac) AS j ON router.id = j.router "
			k = "HEX(mac) {} REGEXP %s".format(no)
			t.append(value.replace(':',''))
		elif (key == 'hood'):
			k = "hoods.name {} REGEXP %s".format(no)
			t.append(value.replace("_","."))
		elif (key == 'hardware') or (key == 'nickname'):
			k = key + " {} REGEXP %s".format(no)
			t.append(value.replace("_","."))
		elif (key == 'hostname') or (key == 'firmware'):
			k = key + " {} REGEXP %s".format(no)
			t.append(value)
		elif key == 'contact':
			k = "contact {} REGEXP %s".format(no)
			t.append(value)
		elif key == 'network':
			# local hood included for v2
			if value.lower() == 'local':
				k = no + " (router.v2 = TRUE AND local = TRUE)"
			elif value.lower() == 'v2':
				k = no + " (router.v2 = TRUE AND local = FALSE)"
			elif value.lower() == 'v1':
				k = no + " router.v2 = FALSE"
			else:
				continue
		elif key == 'babel':
			k = "babel_version {} REGEXP %s".format(no)
			t.append(value.replace("_","."))
		elif key in ('os','batman','kernel','nodewatcher',):
			k = key + " {} REGEXP %s".format(no)
			t.append(value.replace("_","."))
		else:
			k = no + key + " = %s"
			t.append(value)
		i += 1
		s += prefix + k
	where = j + " " + s
	return (where, tuple(t), format_query(query_usr))

def send_email(recipient, subject, content, sender="FFF Monitoring <noreply@monitoring.freifunk-franken.de>"):
	msg = MIMEText(content)
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = recipient
	s = smtplib.SMTP('localhost')
	s.send_message(msg)
	s.quit()

def is_authorized(owner, session):
	if ("user" in session) and (owner == session.get("user")):
		return True
	elif session.get("admin"):
		return True
	else:
		return False
