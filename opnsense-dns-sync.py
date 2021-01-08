#!/usr/bin/env python3

from lxml import etree
from paramiko import SSHClient
from scp import SCPClient
import socket
import sys
import os
import time

master_system = "firewall1.example.com"
slave_systems = ["firewall2.example.com", "firewall3.example.com"]
username = "root"
master_conf = f"/tmp/config.xml.{master_system}"

try:
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(master_system, 22, username)
    scp = SCPClient(ssh.get_transport())
    scp.get("/conf/config.xml", master_conf)
    scp.close()
except:
    print("Could not download master config.xml")
    sys.exit(1)

for slave_system in slave_systems:
    slave_conf = f"/tmp/config.xml.{slave_system}"
    try:
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(slave_system, 22, username)
        scp = SCPClient(ssh.get_transport())
        scp.get("/conf/config.xml", slave_conf)
    except:
        print(f"Could not download slave config.xml.{slave_system}")


    # remove slave configs
    slave_tree = etree.parse(slave_conf).getroot()
    hosts = slave_tree.xpath('/opnsense/unbound/hosts')
    for h in hosts:
        h.getparent().remove(h)
    # check if the stuff is gone:
    assert len(slave_tree.xpath('/opnsense/unbound/hosts')) == 0

    # fill template:
    master_hosts = etree.parse(master_conf).getroot().xpath('/opnsense/unbound/hosts')
    parent_node = slave_tree.xpath('/opnsense/unbound')[0]
    for host in master_hosts:
        parent_node.append(host)
    with open(slave_conf, 'w') as f:
        f.write(etree.tostring(slave_tree, pretty_print=True).decode())
        print(f"wrote merged config to '{slave_conf}'")

    # put file back
    scp.put(slave_conf, remote_path="/conf/config.xml")
    stdin, stdout, stderr = ssh.exec_command("pluginctl dns")
    err = stderr.read().decode()
    if err:
        print(err)
    time.sleep(1)
    scp.close()
    ssh.close()
os.remove(master_conf)

