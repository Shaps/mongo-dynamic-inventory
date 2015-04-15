#!/usr/bin/python

import argparse
from pymongo import MongoClient
try:
    import json
except ImportError:
    import simplejson as json

MONGO_HOST = "localhost"
MONGO_PORT = "27017"


def get_group_hosts(**kwargs):
  group = kwargs['group']
  if "ref_hosts" in group:
    hosts = db.ansible_hosts.find({"_id": {"$in": group['ref_hosts']}})
  else:
    hosts = db.ansible_hosts.find({"vars.group_names": group['name']})
  ret_list = []
  for host in hosts:
    ret_list.append(host['hostname'])
  return sorted(ret_list)


def get_group_vars(group):
  ret_vars = {}
  group_vars = db.groups.find_one({"name": group}, fields={"vars": True, "_id": False})
  if group_vars is not None:
    ret_vars = group_vars['vars']

  return ret_vars


def get_host_vars(host):
  host = db.ansible_hosts.find_one({"hostname": host})
  return host['vars']

parser = argparse.ArgumentParser()
parser.add_argument('--list', action="store_true")
parser.add_argument('--host', metavar='Hostname', nargs=1, help='The hostname to search variables for')
parser.add_argument('-H', action="store_true", help="Human readable format")
args = parser.parse_args()

mongoclient = MongoClient(MONGO_HOST, MONGO_PORT)
db = mongoclient.spot
json_docs = dict()
json_docs['_meta'] = dict()
json_docs['_meta']['hostvars'] = dict()
scanned_groups = []

if args.list:
    all_group = db.groups.find_one({"name": "all"})
    all_group_vars = get_group_vars(all_group).items()
    groups = db.groups.find()
    for group in groups:
      if group['name'] not in scanned_groups:
        group_hosts = get_group_hosts(group=group)
        json_docs.update({
            group['name']: {
                "hosts": group_hosts,
                "vars": group['vars']
            }
        })
        for host in group_hosts:
          host_vars = get_host_vars(host)
          json_docs['_meta']['hostvars'][host] = dict(list(host_vars.items() + group['vars'].items() + all_group_vars))
        scanned_groups.append(group['name'])
    if args.H:
        print json.dumps(json_docs, sort_keys=False, indent=4, separators=(',', ': '))
    else:
        print json.dumps(json_docs)


elif args.host:
    host = args.host[0]
    host = db.ansible_hosts.find_one({'hostname': host}, fields={"vars": True, "_id": False})
    if host:
      for group in host["vars"]["group_names"]:
        host["vars"] = dict(list(host['vars'].items() + get_group_vars(group).items()))
    else:
      host = {}
      host['vars'] = {}

    if args.H:
        print json.dumps(host["vars"], sort_keys=True, indent=4, separators=(',', ': '))
    else:
        print json.dumps(host["vars"])
mongoclient.close()
