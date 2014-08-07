About Globo NetworkAPI WebUI 
############################


Description
***********

Globo NetworkAPI WebUI is a Front End tool to manage and automate networking resources (routers, switches and load balancers) and document logical and physical networking.

They were created to be vendor agnostic and to support different orquestrators and environments without loosing the centralized view of all network resources allocated.

It was not created to be and inventory database, so it does not have CMDB functionalities.

Features
********

* LDAP authentication
* Supports cabling documentation (including patch-panels/DIO's)
* Separated Layer 2 and Layer 3 documentation (vlan/network)
* IPv4 and IPv6 support
* Automatic allocation of Vlans, Networks and IP's
* ACL (access control list) automation (documentation/versioning/applying)
* Load-Balancer support
* Automated deploy of allocated resources on switches, routers and load balancers
* Load balancers management
* Expandable plugins for automating configuration


Architecture
************

.. _architecture-img_ref:

.. image:: diagrams/architecture.png

