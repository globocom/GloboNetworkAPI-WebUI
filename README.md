GloboNetworkAPI Web UI 
======================

This web tool helps network administrator manage and automate networking
resources (routers, switches and load balancers) and document logical and
physical networking.

It lays on top of
[GloboNetworkAPI](https://github.com/globocom/GloboNetworkAPI/), so you need
it installed and acessible in order to use the WebUI.
They were created to be vendor agnostic and to support different orquestrators
and environments without loosing the centralized view of all network resources
allocated.

It was not created to be and inventory database, so it does not
have CMDB functionalities.

## Features

* LDAP authentication
* Supports cabling documentation (including patch-panels/DIO’s)
* Separated Layer 2 and Layer 3 documentation (vlan/network)
* IPv4 and IPv6 support
* Automatic allocation of Vlans, Networks and IP’s
* ACL (access control list) automation (documentation/versioning/applying)
* Load-Balancer support
* Automated deploy of allocated resources on switches, routers and
  load balancers
* Load balancers management
* Expandable plugins for automating configuration

## Documentation
[Documentation](http://globonetworkapi-webui.readthedocs.org/en/latest/)

## Authors
[Authors](./AUTHORS.md)
