#!/usr/bin/python3

CONFIG = {
	"vpn_netif": "fffVPN",				# Name of VPN interface
	"vpn_netif_l2tp": "l2tp",			# Beginning of names of L2TP interfaces
	"vpn_netif_aux": "fffauxVPN",		# Name of AUX interface
	"offline_threshold_minutes": 15,	# Router switches to offline after X minutes
	"orphan_threshold_days": 7,			# Router switches to orphaned state after X days
	"delete_threshold_days": 180,		# Router is deleted after X days
	"router_stat_days": 30,				# Router stats are collected for X days (if online)
	"router_stat_mindiff_secs": 10,		# Time difference (uptime) required for a new entry in router stats
	"event_num_entries": 20,			# Number of events stored per router
	"global_stat_days": 365,			# Global/hood stats are collected for X days
	"csv_dir": "/var/lib/ffmap/csv",	# Directory where the .csv files for TileStache/mapnik are stored
	"debug_dir": "/data/fff",			# Output directory for debug .txt files
}
