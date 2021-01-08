# opnsense_dns_sync

This script syncs the Unbound DNS overrides from an OPNsense master node to a set of slave nodes.
It cat run on any machine that has root access to the firewalls. Just put the hostname of the master into the variable `master_system` and the slaves into the list `slave_systems`.
The sync is directly done in the config.xml of the systems and therefore persistent. The services will be restarted if the configuration was changed.
