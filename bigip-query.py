#!/usr/bin/env python3 

from warnings import catch_warnings
from f5.bigip import ManagementRoot
import configparser
from pprint import pprint
import argparse
import dns.resolver
import re
import signal

config = configparser.ConfigParser()
config.read('bigip-query.conf')

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
            ptr = "MISSING"
    print(vip.name + " IP:"+ serverip + " Sourcenat:" + vip.sourceAddressTranslation['type'] + " Reverse:" + ptr)
    
    if hasattr(vip,"description"):
        print(' - Description: "'+ vip.description + '"')
    if hasattr(vip,"pool"):
        pool = vip.pool.replace('/Common/','')
        pools = mgmt.tm.ltm.pools.pool.load(partition='Common',name=pool)
        #pprint(pools.raw)
        print(" - Pool: " + pool)
        print(" - Members: ",end=" ")
        for member in pools.members_s.get_collection():
            print(member.name,end =", ")
        print()
    if hasattr(vip, "rules"):
        print(" - iRules: " +  str(vip.rules).replace('/Common/',''))
    print(" - Profiles: ")
    for profile in vip.profiles_s.get_collection():
        print("  - " + profile.context +": " + profile.name )

signal.signal(signal.SIGINT, handler)

for vip in vips: 
    #print(vip.raw) 
    serverip = vip.destination.replace('/Common/','')
    rules = [ "<no rules>" ]
    pool = ""
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


