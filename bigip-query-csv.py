#!/usr/bin/env python3 
# Copyright Audun Ytterdal <audun.ytterdal@schibsted.com>
# License GPLv


from warnings import catch_warnings
from f5.bigip import ManagementRoot
import configparser
from pprint import pprint
import argparse
import dns.resolver
import re
import os
import signal

config = configparser.ConfigParser()
configfileread = config.read(['/etc/bigip-query.conf',os.path.expanduser('~/.bigip-query.conf'),'./bigip-query.conf'])

mgmt = ManagementRoot(config['DEFAULT']['hostname'], config['DEFAULT']['username'], config['DEFAULT']['password'])
ltm = mgmt.tm.ltm

pools = ltm.pools.get_collection()
vips = ltm.virtuals.get_collection()
pool = mgmt.tm.ltm.pools.pool

parser = argparse.ArgumentParser()
parser.add_argument("search", nargs='?',default='.*',help="Only output (regex) search matches, check name and ip, default is '.*'")
parser.add_argument("-n", "--negate", help="negate the regex", action="store_true")
args = parser.parse_args()


def handler(signum, frame):
    exit(1)


def printVirtualServer(vip):
    serverip = vip.destination.replace('/Common/','')
    tupples = serverip.split(":")
    if len(tupples) == 5: 
        tupples[4],port = tupples[4].split(".")
        host = ":".join(tupples)

    else: 
        host,port = tupples[0],tupples[1]

    if  port=="0":
        ptr = "N/A"
    else:
        try:
            query = dns.resolver.resolve_address(host)[0]
            ptr = str(query)
        except:
            ptr = "<missing>"
    print(vip.name + ";"+ serverip + ";" + vip.sourceAddressTranslation['type'] + ";" + ptr,end=';')
    
    if hasattr(vip,"description"):
        print(vip.description,end=';')
    else: 
        print("<no description>",end=';')
    if hasattr(vip,"pool"):
        pool = vip.pool.replace('/Common/','')
        pools = mgmt.tm.ltm.pools.pool.load(partition='Common',name=pool)
        #pprint(pools.raw)
        print(pool,end=';')
        for member in pools.members_s.get_collection():
            print(member.name,end =", ")
        print(";",end='')
    else: 
        print ("<no pool>;<no members>",end=';')
    if hasattr(vip, "rules"):
        print(str(vip.rules).replace('/Common/',''),end=';')
    else:
        print("<no rules>",end=';')
    for profile in vip.profiles_s.get_collection():
        print(profile.name,end=',')
    print(";")


signal.signal(signal.SIGINT, handler)

print("NAME;IP;SOURCENAT;REVERSE;DESCRIPTION;POOL;MEMBERS;RULES;PROFILES")

for vip in vips: 
    #print(vip.raw) 
    serverip = vip.destination.replace('/Common/','')
    rules = [ "<no rules>" ]
    pool = "<no pool>"
    if hasattr(vip,"rules"): 
        rules = vip.rules
    if hasattr(vip,"pool"):
        pool = vip.pool.replace('/Common/','')
    if args.negate:
        if not re.search(args.search,vip.name) and not re.search(args.search,vip.destination) and not re.search(args.search,str(rules)) and not re.search(args.search,pool) :
            printVirtualServer(vip)
    else:
        if re.search(args.search,vip.name) or re.search(args.search,vip.destination) or re.search(args.search,str(rules)) or re.search(args.search,pool):
            printVirtualServer(vip)


