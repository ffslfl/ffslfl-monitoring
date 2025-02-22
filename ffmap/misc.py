#!/usr/bin/python3

import time
import datetime

from ffmap.config import CONFIG
#from socket import inet_pton, inet_ntop, AF_INET6
from ipaddress import IPv4Address, IPv6Address

ipv6local = IPv6Address('fc00::')

def utcnow():
	return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

def int2mac(data,keys=None):
	if keys:
		for k in keys:
			data[k] = int2mac(data[k])
		return data
	if data:
		return ':'.join(format(s, '02x') for s in data.to_bytes(6,byteorder='big'))
		#return ':'.join(format(s, '02x') for s in bytes.fromhex('{0:x}'.format(data)))
	else:
		return ''

def int2shortmac(data,keys=None):
	if keys:
		for k in keys:
			data[k] = int2shortmac(data[k])
		return data
	if data:
		return '{:012x}'.format(data)
	else:
		return ''

def shortmac2mac(data):
	if data:
		return ':'.join(format(s, '02x') for s in bytes.fromhex(data.replace(':','')))
	else:
		return ''

def mac2int(data):
	if data:
		return int(data.replace(":",""),16)
	else:
		return None

def int2mactuple(data,index=None):
	if index:
		for r in data:
			r[index] = int2mac(r[index])
	else:
		for r in data:
			r = int2mac(r)
	return data

def ipv6tobin(data):
	if data:
		return IPv6Address(data).packed
		#return inet_pton(AF_INET6,data)
	else:
		return None

def ipv6tobinmasked(data):
	if data:
		ip = IPv6Address(data)
		if ip >= ipv6local:
			return ip.packed
		else:
			li = list(ip.packed)
			# mask 1234:1234:ffff:ffff:ffff:ffff:ffff:ff34
			li[4:15] = [255,255,255,255,255,255,255,255,255,255,255]
		return IPv6Address(bytes(li)).packed
	else:
		return None

def bintoipv6(data):
	if data:
		return IPv6Address(data).compressed
		#return inet_ntop(AF_INET6,data)
	else:
		return ''

def ipv4toint(data):
	if data:
		return int(IPv4Address(data))
		#return inet_pton(AF_INET,data)
	else:
		return None
def inttoipv4(data):
	if data:
		return str(IPv4Address(data))
		#return inet_ntop(AF_INET,data)
	else:
		return ''

def writelog(path, content):
	with open(path, "a") as csv:
		csv.write(time.strftime('{%Y-%m-%d %H:%M:%S}') + " - " + content + "\n")

def writefulllog(content):
	with open(CONFIG["debug_dir"] + "/fulllog.log", "a") as csv:
		csv.write(time.strftime('{%Y-%m-%d %H:%M:%S}') + " - " + content + "\n")

def neighbor_color(quality,netif,rt_protocol):
	color = "#04ff0a"
	if rt_protocol=="BATMAN_V":
		if quality < 10:
			color = "#ff1e1e"
		elif quality < 20:
			color = "#ff4949"
		elif quality < 40:
			color = "#ff6a6a"
		elif quality < 80:
			color = "#ffac53"
		elif quality < 1000:
			color = "#ffeb79"
	else:
		if quality < 105:
			color = "#ff1e1e"
		elif quality < 130:
			color = "#ff4949"
		elif quality < 155:
			color = "#ff6a6a"
		elif quality < 180:
			color = "#ffac53"
		elif quality < 205:
			color = "#ffeb79"
		elif quality < 230:
			color = "#79ff7c"
	if netif.startswith("eth") or netif == "br-ethmesh":
		#color = "#999999"
		color = "#008c00"
	if quality < 0:
		color = "#06a4f4"
	return color

def defrag_table(mysql,table,sleep):
	minustime=0
	allrows=0
	start_time = time.time()

	qry = "ALTER TABLE `%s` ENGINE = InnoDB" % (table)
	mysql.execute(qry)
	mysql.commit()

	end_time = time.time()
	if sleep > 0:
		time.sleep(sleep)

	writelog(CONFIG["debug_dir"] + "/deletetime.txt", "Defragmented table %s: %.3f seconds" % (table,end_time - start_time))
	print("--- Defragmented table %s: %.3f seconds ---" % (table,end_time - start_time))

def defrag_all(mysql):
	alltables = ('gw','gw_admin','gw_netif','hoods','hoodsv2','router','router_events','router_gw','router_ipv6','router_neighbor','router_netif','users')

	for t in alltables:
		defrag_table(mysql,t,1)

	writelog(CONFIG["debug_dir"] + "/deletetime.txt", "-------")
