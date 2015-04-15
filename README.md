Ansible MongoDB dynamic inventory
=====================================
This dynamic inventory will read from a MongoDB database and parse it as ansible-readable json. 

---
####The json object structure on Mongo is:

Host:
```json
{
    "hostname" : "lhr-www01",
    "vars" : {
        "inventory_hostname" : "lhr-www01",
        "group_names" : [ 
            "lhr-www"
        ]
    },
    "hostname" : "lhr-www02",
    "vars" : {
        "inventory_hostname" : "lhr-www02",
        "group_names" : [ 
            "lhr-www"
        ]
    }
}
```
#### Group:
```json
{
    "name" : "lhr4-www",
    "vars" : {
        "ngx_base" : "ngx-www",
        "ngx_ver" : "1.4.0"
    }
}
```

---

To use the dynamic inventory, just specify it with "-i", ansible will take care of the rest.
```shell
$ ansible -i /opt/mongo-dynamic-inventory/inventory.py <hostgroup> -m <module> [-a <attrs>]
```

If you already have an ansible hosts file, you can use the **convert.py** script, it will parse the hosts file and write it into Mongo. 
```shell
$ /opt/mongo-dynamic-inventory/convert.py -h
usage: convert.py [-h] [-f Filename] [-u] [-d]

usage: convert.py [-h] -f Filename [-u] [-d]

optional arguments:
  -h, --help   show this help message and exit
  -f Filename  The ansible host file path
  -u           Human readable format
  -d           Dry run ( Does not update Mongo )
```