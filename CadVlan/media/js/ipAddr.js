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

function ipAddr(addr, cidr) {
  this.addr = addr;
  this.cidr = cidr;
  this.args = {};
  this.args.ipv4 = true;
  this.args.ipv6 = true;
  this.args.block_reserved = false;

  this.msg = '';

  /* Simple validation */
  if (!addr)
    return this.setFailMsg('enterAddress');

  /* CIDR notation has precidence over an argument */
  if (this.addr.match(/\//)) {
    var addrsp  = this.addr.split('/');
    this.addr = addrsp[0];
    this.cidr = addrsp[1];
  }

  if (this.addr.match(/:/)) {
    this.version = 6;
    this.maxcidr = 128;
    if (isNaN(this.cidr)) this.cidr = 128;
  }
  else if (this.addr.length >= 7) {
    this.version = 4;
    this.maxcidr = 32;
    if (isNaN(this.cidr)) this.cidr = 32;
  }

  this.Msg        = function () {return this.msg;}
  this.setMsg     = function (msg) {this.msg = this.l8n(msg);}
  this.setFailMsg = function (msg) {this.setMsg(msg); return false;}
  this.Cidr       = function () {return this.cidr; }
  this.Version    = function () {return this.version || 0;}

  String.prototype.repeat = function(num) {
    if (!num || num < 1) return '';
    return new Array(num + 1).join(this);
  }

  this.isIPv4 = function () {
    return (this.Version() == 4);
  }

  this.isIPv6 = function () {
    return (this.Version() == 6);
  }

  this.FullAddress = function () {
    if (!this.Valid()) return '';
    return this.Address() + '/' + this.cidr;
  }

  this.Wildcard = function () {
    if (!this.Valid()) return '';
    switch (this.Version()) {
      case 6:  return this.v6_bin_expand(this.binv());
      case 4:  return this.v4_bin_expand(this.binv());
      default: return '';
    }
  }
  this.Netmask = function () {
    if (!this.Valid()) return '';
    switch (this.Version()) {
      case 6:  return this.v6_bin_expand(this.Binmask());
      case 4:  return this.v4_bin_expand(this.Binmask());
      default: return '';
    }
  }

  this.Network = function () {
    if (!this.Valid()) return '';
    switch (this.Version()) {
      case 6:  return this.ip6_network();
      case 4:  return this.ip4_network();
      default: return '';
    }
  }

  this.MaxHost = function () {
    if (!this.Valid()) return '';
    switch (this.Version()) {
      case 6:  return this.ip6_max_host();
      case 4:  return this.ip4_max_host();
      default: return '';
    }
  }

  this.MinHost = function () {
    if (!this.Valid()) return '';
    switch (this.Version()) {
      case 6:  return this.ip6_min_host();
      case 4:  return this.ip4_min_host();
      default: return '';
    }
  }

  this.Broadcast = function () {
    if (this.Version() != 4) return '';
    if (!this.Valid()) return '';

    var ip_quads   = this.Address().split('.');
    var mask_quads = this.Wildcard().split('.');
    var outp = [];

    for (var i=0; i<=3; i++)
      outp.push(ip_quads[i] | mask_quads[i]);

    return outp.join('.');
  }

  this.Expanded = function () {
    if (!this.Valid()) return '';
    switch (this.Version()) {
      case 6:  return this.ip6_expand(this.addr.toUpperCase());
      case 4:  return this.ip4_expand(this.addr);
      default: return '';
    }
  }

  this.Address = function () {
    if (!this.ValidAddress()) return '';
    switch (this.Version()) {
      case 6:  return this.ip6_compressed();
      case 4:  return this.addr;
      default: return '';
    }
  }

  /* Due to the maximum value of 2^128, we're using strings */
  this.HostCount = function () {
    if (!this.Valid()) return '';
    switch (this.Version()) {
      case 6:  return this.v6cidrs[128-this.cidr];
      case 4:  return Math.pow(2, 32 - this.cidr).toString();
      default: return '';
    }
  }

  this.Binmask = function () {
    if (!this.ValidCidr()) return '';
    return this.cidr_expand(this.cidr, this.maxcidr);
  }


  this.IP4MappedIP6 = function () {
    if (this.Version() != 4) return '';
    var v4mappedv6 = ip6_ip4_expand('::FFFF:' + this.addr);
    if (!v4mappedv6) return '';
    return this.ip6_compress(v4mappedv6);
  }

  this.v4_bin_expand = function (bitmask) {
    if (!bitmask) return '';
    var chunks = [];
    while (bitmask) {
      chunks.push(this.b2d(bitmask.slice(0, 8), 3));
      bitmask = bitmask.slice(8);
    }
    for (var i=0; i<=3; i++)
      chunks[i] = parseInt(chunks[i]);

    return chunks.join('.');
  }

  this.v6_bin_expand = function (bitmask) {
    if (!bitmask) return '';
    var chunks = [];
    while (bitmask) {
      chunks.push(this.b2h(bitmask.slice(0, 16)));
      bitmask = bitmask.slice(16);
    }
    return chunks.join(':');
  }


  this.ip6_ip4_expand = function (ip) {
    var chunks = ip.match(/^([0:]+:FFFF:)([\d.]+)$/i);
    var ipv6   = chunks[1];
    var ipv4   = chunks[2];
    var quads  = [];

    if (!this.ipv4_validate(ipv4)) return '';

    octets = ipv4.split('.');

    for (var i=0; i < octets.length; i++) {
      var quad = parseInt(octets[i]).toString(16);
      if (quad.length == 1)
        quad = '0' + quad;
      quads.push(quad);
    }

    return ipv6+quads[0]+quads[1]+':'+quads[2]+quads[3];
  }

  this.ip6_compressed = function() {
    var out    = '';
    var chunks = this.addr.split(/:/);
    for (var i=0; i < chunks.length; i++) {
      var chunk = chunks[i].replace(/^0+/,'');
      if (!chunk) chunk = 0;
      out += chunk + ':';
    }

    out = out.replace(/(:0)+/,':');
    out = out.replace(/^0/,'');
    out = out.replace(/:0$/,':');
    out = out.substr(0, out.length-1).toUpperCase();

    /* Wonky edge-case */
    if (!out.match(/::/))
      if (out.replace(/[^:]:$/)) out += ':';

    return out;
  }

  this.ip4_min_host = function () {
    var quads = this.Network().split('.');
    if (this.cidr != 32) quads[3]++;
    return quads.join('.');
  }

  this.ip6_min_host = function () {
    var chunks = this.Network().split(':');
    chunks[7] = 1 + parseInt(chunks[7], 16);
    chunks[7] = chunks[7].toString(16);
    return this.ip6_expand(chunks.join(':'));
  }

  this.ip4_max_host = function () {
    var quads = this.Broadcast().split('.');
    if (this.cidr != 32) quads[3]--;
    return quads.join('.');
  }

  this.ip6_max_host = function () {
    var chunks      = this.Expanded().split(':');
    var mask_chunks = this.Wildcard().split(':');
    var outp = [];

    for (var i=0; i<=7; i++) {
      var chunk = parseInt(chunks[i], 16) | parseInt(mask_chunks[i], 16);
      outp.push(chunk.toString(16));
    }

    return this.ip6_expand(outp.join(':')).toUpperCase();
  }

  this.ip4_expand = function (ip) {
    var quads = ip.split('.');
    var outp  = [];
    for (var i=0; i < quads.length; i++)
      outp.push('0'.repeat(3-quads[i].length) + quads[i]);
    return outp.join('.');
  }


  this.ip6_expand = function (ip) {
    var colons = (ip.split(':').length - 1);
    if (colons > 8) {
      this.setMsg('IP6ErrorTooManyColons');
      return '';
    }

    var missing = 8 - colons;

    if (/:::/.test(ip)) {
      this.setMsg('IP6ErrorColonGrouping');
      return '';
    }

    /* Expand beginning and trailing colons */
    ip = ip.replace(/^::/, '0000::');
    ip = ip.replace(/::$/, '::0000');

    if (ip.match(/^:/)) {
      this.setMsg('IP6ErrorStartingColon');
      return '';
    }
    else if (ip.match(/:$/)) {
      this.setMsg('IP6ErrorTrailingColon');
      return '';
    }

    /* Expand the grouping */
    ip = ip.replace(/::/g, ':'+'0000:'.repeat(missing));

    var oldchunks = ip.split(/:/);
    var newchunks = [];
    for (var i=0; i < oldchunks.length; i++) {
      var chunk = oldchunks[i];
      if (chunk.match(/0{5}/)) {
        this.setMsg('IP6ErrorTooManyZeroes');
        return '';
      }
      if (chunk == 0) chunk = '';
      newchunks.push('0'.repeat(4 - chunk.length) + chunk);
    }

    return newchunks.join(':');
  }


  this.b2h = function (bin) {
    var outp = parseInt(this.b2d(bin));
    outp = outp.toString(16).toUpperCase();
    return '0'.repeat(4 - outp.length) + outp;
  }

  this.b2d = function (bin, len) {
    var outp = 0;
    for (var i = 0; i<=bin.length; i++)
      if(bin.charAt(i) == 1)
        outp += Math.pow(2, bin.length - 1 - i);
    outp = outp.toString();
    if (!len) return outp;
    return '0'.repeat(len - outp.length) + outp;
  }

  this.binv = function () {
    var outp = '';
    var bin = this.Binmask();
    for (var i = 0; i < bin.length; i++) {
      if (bin.charAt(i) == 1)
        outp += '0';
      else
        outp += '1';
    }
    return outp;
  }

  this.ip4_network = function () {
    var ip   = this.addr.split('.');
    var mask = this.v4_bin_expand(this.cidr_expand(this.cidr, 32)).split('.');
    var outp = [];

    for (var i=0; i<=3; i++)
      outp.push(ip[i] & mask[i]);

    return outp.join('.');
  }

  this.ip6_network = function () {
    var v6   = this.ip6_expand(this.addr).split(':');
    var mask = this.v6_bin_expand(this.cidr_expand(this.cidr, 128)).split(':');
    var outp = [];

    for (var i=0; i <= 7; i++)
      outp.push(parseInt(v6[i], 16) & parseInt(mask[i], 16)).toString(16);

    return this.ip6_expand(outp.join(':').toUpperCase());
  }

  this.cidr_expand = function (val, max) {
    return '1'.repeat(parseInt(val)) + '0'.repeat(max - val);
  }

  this.cidr_invert = function (val, max) {
    var outp = '0'.repeat(parseInt(val));
    outp += '1'.repeat(max - val);
    return outp;
  }

  this.ValidCidr = function () {
    if (!isNaN(this.validcidr)) return this.validcidr;

    if (this.cidr < 0 || this.maxcidr < this.cidr) {
      this.setMsg('InvalidCidrBlock');
      return this.validcidr = false;
    }

    return this.validcidr = true;
  }

  this.ValidIP6Address = function () {
    if (this.Version() != 6)   return false;
    if (!this.addr.match(/:/)) return false;

    if (!this.addr.match(/^[0-9A-F:.]+$/i))
        return this.setFailMsg('IP6ErrorInvalidChar');

    if (this.addr.match(/^.+:FFFF:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/i)) {
      this.addr = this.ip6_ip4_expand(this.addr);
      if (this.addr == '') return false;
    }

    /* Force consistant case */
    var ip = this.ip6_expand(this.addr.toUpperCase());
    if (!ip) return false;

    if (!ip.match(/^(?:[A-F0-9]{4}:){7}[A-F0-9]{4}$/))
      return this.setFailMsg('IP6ErrorInvalidSyntax');

    return true;
  }

  this.ValidIP4Address = function () {
    if (this.Version() != 4) return false;
    return this.ipv4_validate(this.addr);
  }

  this.ipv4_validate = function (host) {
    if (host.length < 7) return false;

    if (!host.match(/^[\d.]+$/))
      return this.setFailMsg('IP4ErrorDottedQuad');

    var octet = host.split(/\./);

    if (octet.length != 4)
      return this.setFailMsg('IP4ErrorFourOctets');

    for (var i=0; i < 4; i++) {
      var quad = octet[i]
      if (!quad)
        return this.setFailMsg('IP4ErrorFourOctets');
      else if (quad < 0)
        return this.setFailMsg('IP4ErrorNegativeQuad');
      else if (255 < quad)
        return this.setFailMsg('IP4ErrorMassiveQuad');
    }

    if (!this.args.block_reserved)
      return true;

    if (224 <= octet[0] && octet[0] <= 239)
      this.setFailMsg('IP4ErrorReservedMulticast');

    else if (octet[0] == 0)
      return this.setFailMsg('IP4ErrorReservedSelfId');

    else if (octet[0] == 127)
      return this.setFailMsg('IP4ErrorReservedLoopback');

    else if (octet[0] == 255 &&
        octet[1] == 255 &&
        octet[2] == 255 &&
        octet[3] == 255)
      return this.setFailMsg('IP4ErrorReservedLocalBroadcast');

    return true;
  }

  this.ValidAddress = function () {
    if (!isNaN(this.validaddr)) return this.validaddr;

    if (this.args.ipv6 && this.ValidIP6Address())
      return this.validaddr = true;

    if (this.args.ipv4 && this.ValidIP4Address())
      return this.validaddr = true;

    return false;
  }

  this.Valid = function () {
    if (!isNaN(this.validhost)) return this.validhost;

    if (this.ValidCidr() && this.ValidAddress())
      return this.validhost = true;

    return this.validhost = false;
  }

  this.v6cidrs=[
      '1','2','4','8',
      '16','32','64','128','256','512','1024','2048','4096',
      '8192','16384','32768','65536','131072','262144','524288','1048576',
      '2097152','4194304','8388608','16777216','33554432','67108864',
      '134217728','268435456','536870912','1073741824','2147483648',
      '4294967296','8589934592','17179869184','34359738368','68719476736',
      '137438953472','274877906944','549755813888','1099511627776',
      '2199023255552','4398046511104','8796093022208','17592186044416',
      '35184372088832','70368744177664','140737488355328','281474976710656',
      '562949953421312','1125899906842624','2251799813685248',
      '4503599627370496','9007199254740992','18014398509481984',
      '36028797018963968','72057594037927936','144115188075855872',
      '288230376151711744','576460752303423488','1152921504606846976',
      '2305843009213693952','4611686018427387904','9223372036854775808',
      '18446744073709551616','36893488147419103232','73786976294838206464',
      '147573952589676412928','295147905179352825856','590295810358705651712',
      '1180591620717411303424','2361183241434822606848',
      '4722366482869645213696','9444732965739290427392',
      '18889465931478580854784','37778931862957161709568',
      '75557863725914323419136','151115727451828646838272',
      '302231454903657293676544','604462909807314587353088',
      '1208925819614629174706176','2417851639229258349412352',
      '4835703278458516698824704','9671406556917033397649408',
      '19342813113834066795298816','38685626227668133590597632',
      '77371252455336267181195264','154742504910672534362390528',
      '309485009821345068724781056','618970019642690137449562112',
      '1237940039285380274899124224','2475880078570760549798248448',
      '4951760157141521099596496896','9903520314283042199192993792',
      '19807040628566084398385987584','39614081257132168796771975168',
      '79228162514264337593543950336','158456325028528675187087900672',
      '316912650057057350374175801344','633825300114114700748351602688',
      '1267650600228229401496703205376','2535301200456458802993406410752',
      '5070602400912917605986812821504','10141204801825835211973625643008',
      '20282409603651670423947251286016','40564819207303340847894502572032',
      '81129638414606681695789005144064','162259276829213363391578010288128',
      '324518553658426726783156020576256','649037107316853453566312041152512',
      '1298074214633706907132624082305024','2596148429267413814265248164610048',
      '5192296858534827628530496329220096',
      '10384593717069655257060992658440192',
      '20769187434139310514121985316880384',
      '41538374868278621028243970633760768',
      '83076749736557242056487941267521536',
      '166153499473114484112975882535043072',
      '332306998946228968225951765070086144',
      '664613997892457936451903530140172288',
      '1329227995784915872903807060280344576',
      '2658455991569831745807614120560689152',
      '5316911983139663491615228241121378304',
      '10633823966279326983230456482242756608',
      '21267647932558653966460912964485513216',
      '42535295865117307932921825928971026432',
      '85070591730234615865843651857942052864',
      '170141183460469231731687303715884105728',
      '340282366920938463463374607431768211456'];

  return this;
}

/* This s overridden by ipAddr_l8n.js */
ipAddr.prototype.l8n = function (msg) {return msg};

