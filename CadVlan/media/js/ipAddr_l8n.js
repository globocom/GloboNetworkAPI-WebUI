/*
ipAddr - An IP utility knife for javascript
Copyright (C) 2010 Clif Bratcher

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

/* Default */
this.locale = 'en_US';

ipAddr.prototype.l8nTable={
    'enterAddress':{
        'en_US':'Please enter an address'
    },
    'IP6ErrorInvalidChar':{
        'en_US':'Ipv6 Error: Address contains an invalid character'
    },
    'IP6ErrorTooManyColons':{
        'en_US':'IPv6 Error: too many colons'
    },
    'IP6ErrorInvalidSyntax':{
        'en_US':'IPv6 Error: address does not follow common syntax'
    },
    'IP6ErrorColonGrouping':{
        'en_US':'IPv6 Error: colons grouped too tight'
    },
    'IP6ErrorStartingColon':{
        'en_US':'IPv6 Error: beginning colon'
    },
    'IP6ErrorTrailingColon':{
        'en_US':'IPv6 Error: trailing colon'
    },
    'IP6ErrorTooManyZeroes':{
        'en_US':'IPv6 Error: too many zeroes'
    },
    'InvalidCidrBlock':{
        'en_US':'Error: CIDR block is invalid'
    },
    'IP4ErrorDottedQuad':{
        'en_US':'IPv4 Error: Must be a dotted quad'
    },
    'IP4ErrorFourOctets':{
        'en_US':'IPv4 Error: must have exactly four octets'
    },
    'IP4ErrorFourOctets':{
        'en_US':'IPv4 Error: must have exactly four octets'
    },
    'IP4ErrorNegativeQuad':{
        'en_US':'IPv4 Error: octet value must be greater than zero'
    },
    'IP4ErrorMassiveQuad':{
        'en_US':'IPv4 Error: octet value must be less than 256'
    },
    'IP4ErrorReservedMulticast':{
        'en_US':'IPv4: block 224/4 reserved for multicast (RFC 3171)'
    },
    'IP4ErrorReservedSelfId':{
        'en_US':'IPv4: block reserved for self-identification (RFC 3330)'
    },
    'IP4ErrorReservedLoopback':{
        'en_US':'IPv4: block reserved for loopback (RFC 3330)'
    },
    'IP4ErrorReservedLocalBroadcast':{
        'en_US':'IPv4: block reserved for local broadcast (RFC 3330)'
    },
    /* Insert new l8n here */
    'UnknownError':{
        'en_US':'Unknown error'
    }
};

ipAddr.prototype.l8n=function(key) {
    var val=key;

    if (this.l8nTable[key]) {
        if (this.l8nTable[key][this.locale])
            val=this.l8nTable[key][this.locale];
        else
            val=this.l8nTable[key]['en_US'];
    }

    return val;
}
