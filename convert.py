#!/usr/bin/env python

import json
import sys
import argparse

from ansible.inventory.ini import InventoryParser
from pymongo import MongoClient
from bson.objectid import ObjectId

MONGO_HOST = "localhost"
MONGO_PORT = "27017"

def build_host_list(group):
  hosts = group.get_hosts()
  return_list = list()
  for host in hosts:
    return_list.append({"hostname": host.name, "vars": host.get_variables()})
  return return_list

def host_in_group(host_id, group_name):
  group = db.groups.find_one({"name": group_name})
  if group is None:
    print "Group %s does not exist , creating" % group_name
    group = {'name': group_name}
    group_id = db.groups.save(group)
    group = db.groups.find_one({"_id": group_id})
  host_id = ObjectId(host_id)
  if 'ref_hosts' in group:
    if host_id not in group['ref_hosts']:
      group['ref_hosts'].append(host_id)
  else:
    group['ref_hosts'] = []
    group['ref_hosts'].append(host_id)

  db.groups.save(group)


parser = argparse.ArgumentParser()
parser.add_argument('-f', metavar='Filename', nargs=1, help='The ansible host file path', required=True)
parser.add_argument('-u', action="store_true", help="Human readable format")
parser.add_argument('-d', action="store_true", help="Dry run ( Does not update Mongo )")
args = parser.parse_args()

if args.f:
  file_name = args.f[0]
  print "Opening ", file_name
  hostfile = InventoryParser(filename=file_name)
else:
  print "You have to specify a filename"
  sys.exit(1)

groups = hostfile.groups.values()
hosts = hostfile.hosts.values()

host_list = {}
json_obj = {}
groups_json = {}

for group in groups:
  groups_json[group.name] = {}
  groups_json[group.name]['vars'] = group.get_variables()
  if group.name is "all":
    host_list = build_host_list(group)


if not args.d:
  mongoclient = MongoClient(MONGO_HOST, MONGO_PORT)
  db = mongoclient.spot

  # Inserting hosts in Mongo
  for host in host_list:
    db_host = db.ansible_hosts.find_one({"hostname": host['hostname']})
    if db_host is not None:
      host['_id'] = db_host['_id']

    host_id = db.ansible_hosts.save(host)
    print "Host: %s, Mongo_ID: %s" % (host['hostname'], host_id)
    host_in_group(host_id, host['vars']['group_names'][0])

  # Inserting Groups in Mongo
  for group in groups:
    g_obj = {"name": group.name, "vars": group.get_variables()}
    db_group = db.groups.find_one({"name": group.name})
    if db_group is not None:
      g_obj['_id'] = db_group['_id']
    print "Group: %s, Mongo_ID: %s" % (group.name, db.groups.save(g_obj))

  mongoclient.close()
else:
  if args.u:
    print "Groups"
    print json.dumps(groups_json, sort_keys=True, indent=4, separators=(',', ': '))
    print "Hosts"
    # print json.dumps(host_list,sort_keys=True,indent=4,separators=(',',': '))
    for host in host_list:
      print host
  else:
    print json.dumps(groups_json)
    print json.dumps(host_list)
