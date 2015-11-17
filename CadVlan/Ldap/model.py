# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ldap
import logging
import commands
from datetime import datetime
from datetime import timedelta
from ldap import modlist, SERVER_DOWN, NO_SUCH_OBJECT
from CadVlan.settings import LDAP_INITIALIZE, LDAP_DC, LDAP_CREDENTIALS_USER, LDAP_CREDENTIALS_PASSWORD, LDAP_MANAGER_PASSWORD, LDAP_SSL, LDAP_PASSWORD_DEFAULT_HASH,\
    LDAP_INITIALIZE_SSL, CACERTDIR, LDAP_MANAGER_USER


class LDAPError(Exception):

    def __init__(self, error):
        self.error = error

    def __str__(self):
        msg = u"%s" % (self.error)
        return msg.encode("utf-8", "replace")


class LDAPConnectionError(LDAPError):

    def __init__(self,):
        LDAPError.__init__(self, u"Erro de comunicação com LDAP server.")


class LDAPMethodError(LDAPError):

    def __init__(self, error):
        LDAPError.__init__(self, error)


class LDAPNotFoundError(LDAPError):

    def __init__(self, error):
        LDAPError.__init__(self, error)


class LDAPInvalidParameterError(LDAPError):

    def __init__(self, error, param=None, value=None):
        LDAPError.__init__(
            self, u"Invalid parameter: %s. Value: %s." % (param, value))
        self.param = param
        self.value = value


class CN_TYPES():
    USER = "Usuarios"
    GROUP = "Grupos"
    SUDOERS = "Sudoers"
    POLICY = "Politicas"


class COMMAND_TYPES():
    LOCK = "sudo chmod -R 755 /mnt%s/.ssh/"
    UNLOCK = "sudo chmod -R 000 /mnt%s/.ssh/"


class Ldap():

    logger = logging.getLogger(__name__)

    def __init__(self, user):
        self.groupStandard = "44000"
        self.groupStandardCn = "globo.com"
        self.groupStandardExternal = "44001"
        self.groupStandardExternalCn = "externo"
        self.producao = "44007"
        self.desenvolvimento = "44008"
        self.rangeUsers = range(40000, 44000)
        self.rangeGroups = range(44002, 45001)
        self.rangeUsersExternal = range(50000, 52001)
        self.grupoPadraoGlobo_id = 44000
        self.grupoPadraoExterno_id = 44001
        self.user = user

    def _get_conn(self):
        """
        Returns LDAP connection
        """
        try:
            if LDAP_SSL:
                ldap.set_option(
                    ldap.OPT_X_TLS_CACERTFILE, CACERTDIR + 'glb_cacert.pem')
                ldap.set_option(
                    ldap.OPT_X_TLS_CERTFILE, CACERTDIR + 'glb_clientcrt.pem')
                ldap.set_option(
                    ldap.OPT_X_TLS_KEYFILE, CACERTDIR + 'glb_clientkey.pem')
                ldap.set_option(ldap.OPT_DEBUG_LEVEL, 1)

            conn = ldap.initialize(
                "%s://%s" % (('ldaps' if LDAP_SSL else 'ldap'), (LDAP_INITIALIZE_SSL if LDAP_SSL else LDAP_INITIALIZE)))

            conn.protocol_version = ldap.VERSION3
            conn.simple_bind_s(
                self._get_str(LDAP_CREDENTIALS_USER, CN_TYPES.USER), LDAP_CREDENTIALS_PASSWORD)

            return conn

        except SERVER_DOWN, e:
            self.logger.error("server down %s" % e)
            raise LDAPConnectionError()
        except Exception, e:
            self.logger.error("exception %s" % e)
            raise LDAPError(e)

    def _get_conn_manager(self):
        """
        Returns LDAP manager connection
        """
        try:

            conn = self._get_conn()
            conn.simple_bind_s(self._get_manager(), LDAP_MANAGER_PASSWORD)

            return conn

        except SERVER_DOWN, e:
            raise LDAPConnectionError()
        except Exception, e:
            raise LDAPError(e)

    def _get_manager(self):
        strng = "cn=%s,ou=%s,%s" % (LDAP_MANAGER_USER, CN_TYPES.USER, LDAP_DC)
        return strng

    def _get_str(self, cn, ou):
        strng = "cn=%s,%s" % (cn, self._get_str_ou(ou))
        return strng

    def _get_str_ou(self, ou):
        strng = "ou=%s,%s" % (ou, LDAP_DC)
        return strng

    def get_group(self, cn):
        return self._get_cn(cn, CN_TYPES.GROUP)

    def get_sudoer(self, cn):
        return self._get_cn(cn, CN_TYPES.SUDOERS)

    def get_user(self, cn):
        return self._get_cn(cn, CN_TYPES.USER)

    def _get_cn(self, cn, cn_type):
        """
        Returns CN of a cn_type existing in LDAP
        If cn_type is USER, aditional data will be searched

        :param cn: String with CN to be searched
        :param cn_type: Type of CN to be searched (CN_TYPES) 
        """
        try:
            conn = self._get_conn()

            dn = self._get_str(cn, cn_type)

            ob = conn.search_ext_s(dn, ldap.SCOPE_BASE)[0]

            dic = {}
            for k in ob[1]:
                if cn_type == CN_TYPES.SUDOERS:
                    if len(ob[1][k]) == 1 and k != "sudoCommand" and k != "sudoUser":
                        dic[k] = ob[1][k][0]
                    else:
                        dic[k] = ob[1][k]
                else:
                    if len(ob[1][k]) == 1:
                        dic[k] = ob[1][k][0]
                    else:
                        dic[k] = ob[1][k]

            if cn_type == CN_TYPES.USER:

                pol = self._cmd_line(cn, "pwdPolicySubentry")

                polName = pol["pwdPolicySubentry"].split("=")[1]
                polName = polName.split(",")[0]
                dic["pwdPolicySubentry"] = pol["pwdPolicySubentry"]
                dic["policy"] = polName

            return dic

        except NO_SUCH_OBJECT, e:
            self.logger.error("NO SUCH OBJECT %s" % e)
            raise LDAPNotFoundError(e)
        except Exception, e:
            self.logger.error("Exception %s" % e)
            raise LDAPError(e)

    def _parse_groups(self, member_uid):
        """
        Assemble the list with information from User.

        :param member_uid: List of identifiers of the Users of Group.
        """
        memberUid = []
        if member_uid:

            if type(member_uid) == type([]):

                for i in range(len(member_uid)):
                    mem = str(member_uid[i])
                    memberUid.append(mem)

            else:
                mem = str(member_uid)
                memberUid.append(mem)

        return memberUid

    def _parse_sudoers(self, sudoUser, sudoCommand):
        """
        Assemble the two lists with information from Sudoer.

        :param sudoUser: List of identifiers of the Group of Sudoer.
        :param sudoCommand: List of commands.
        """
        groups = []
        if sudoUser:

            if type(sudoUser) == type([]):

                for i in range(len(sudoUser)):
                    grp = str(sudoUser[i])
                    groups.append("%%%s" % grp)

            else:
                grp = str(sudoUser)
                groups.append("%%%s" % grp)

        cmds = []
        if sudoCommand:

            if type(sudoCommand) == type([]):

                for i in range(len(sudoCommand)):
                    cmd = str(sudoCommand[i])
                    cmds.append("%s" % cmd)

            else:
                cmd = str(sudoCommand)
                cmds.append("%s" % cmd)

        return groups, cmds

    def _alter_cn(self, cn, cn_type, dicNew):
        """
        Modifies a cn from a dictionary containing the fields to be changed.

        :param cn: String with CN to be searched
        :param cn_type: Type of CN to be searched (CN_TYPES)
        :param dicNew: Dictionary containing the fields to be changed
        """
        try:

            conn = self._get_conn_manager()

            dn = self._get_str(cn, cn_type)

            cn = self._get_cn(cn, cn_type)

            dicOld = {}
            for k in dicNew:
                if cn.has_key(k):
                    dicOld[k] = cn[k]

            "Policy"
            if cn_type == CN_TYPES.USER and dicOld.has_key("pwdPolicySubentry"):

                if dicOld["pwdPolicySubentry"] != dicNew["pwdPolicySubentry"]:

                    mod_attrs = [
                        (ldap.MOD_REPLACE, "pwdPolicySubentry", dicNew["pwdPolicySubentry"])]

                    try:
                        conn.modify_ext_s(dn, mod_attrs)
                    except Exception, e:
                        self.logger.error(
                            "LDAP - Erro quando %s modificava politica do usuarios na base ldap:" % self.user)
                        self.logger.error("LDAP - %s" % str(e))
                        raise LDAPMethodError(e)

                del dicOld["pwdPolicySubentry"]
                del dicNew["pwdPolicySubentry"]

            ldif = modlist.modifyModlist(dicOld, dicNew)

            conn.modify_s(dn, ldif)

        except Exception, e:
            raise LDAPError(e)

        finally:
            try:
                conn.unbind_s()
            except:
                pass

    def _cmd_line(self, cn, field):
        """
        Execute commands

        cn: String with cn to be passed in command
        field: String with field to be passed in command
        """
        try:
            cmd = """ldapsearch -x -h %s -D "%s" -b "%s" -w %s "cn=%s" %s""" % (
                LDAP_INITIALIZE,
                self._get_manager(),
                "ou="+CN_TYPES.USER+","+LDAP_DC,
                LDAP_MANAGER_PASSWORD,
                cn,
                field)
            resp = commands.getstatusoutput(cmd)
            dic = {}
            dic[field] = ""

            if resp[0] == 0:
                init = resp[1].find(field)
                init2 = resp[1].find(field, init + 1)
                end = resp[1].find("\n", init2)

                if init2 > -1 and end > -1:
                    strng = resp[1][init2:end]
                    values = strng.split(": ")
                    dic[field] = values[1]

            else:

                raise LDAPMethodError(resp[0])

            return dic

        except Exception, e:
            raise LDAPError(e)

    def valid_range_group(self, gidNumber):
        """
        Validates that the gidNumber is in the range of group numbers

        :param gidNumber: Identifier of the Group.
        """
        is_valid = False
        if self.rangeGroups.count(int(gidNumber)) == 1:
            is_valid = True

        return is_valid

    def valid_range_user_external(self, uidNumber):
        """
        Validates that the uidNumber is in the range of user external numbers

        :param uidNumber: Identifier of the User.
        """
        is_valid = False
        if self.rangeUsersExternal.count(int(uidNumber)) == 1:
            is_valid = True

        return is_valid

    def valid_range_user_internal(self, uidNumber):
        """
        Validates that the uidNumber is in the range of user internal numbers

        :param uidNumber: Identifier of the User.

        """
        is_valid = False
        if self.rangeUsers.count(int(uidNumber)) == 1:
            is_valid = True

        return is_valid

    def get_groups(self):
        """
        Returns all groups from LDAP
        """
        try:
            conn = self._get_conn()

            gps = conn.search_ext_s(
                self._get_str_ou(CN_TYPES.GROUP), ldap.SCOPE_ONELEVEL)

            groups = {}
            for g in gps:

                dic = {}
                for k in g[1]:

                    if len(g[1][k]) == 1 and k != "memberUid":
                        dic[k] = g[1][k][0]
                    else:
                        dic[k] = g[1][k]

                if self.valid_range_group(dic["gidNumber"]):
                    groups[int(dic["gidNumber"])] = dic

            return groups

        except Exception, e:
            self.logger.error("get_groups exception %s" % e)
            raise LDAPError(e)

    def rem_group(self, cn):
        """
        Remove groups in LDAP

        :param cn: cn of Group.
        """
        try:
            conn = self._get_conn_manager()

            dn = self._get_str(cn, CN_TYPES.GROUP)

            self.get_group(cn)

            conn.delete_s(dn)

            self.logger.info(
                "LDAP - %s removeu o grupo %s com sucesso." % (self.user, cn))

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s removia grupo %s na base ldap." % (self.user, cn))
            raise LDAPError(e)

    def rem_group_user(self, cn, group):
        """
        Remove user of group in LDAP

        :param cn: cn of User.
        :param group: cn of Group.
        """
        try:
            dn = self.get_group(group)

            groups = dn['memberUid']

            groups.remove(cn)

            memberUid = self._parse_groups(groups)

            self._alter_cn(group, CN_TYPES.GROUP, {'memberUid': memberUid})

            self.logger.info(
                "LDAP - %s removeu o usuário %s do  grupo %s com sucesso." % (self.user, cn, group))

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s removia o usuário %s do  grupo %s na base ldap." % (self.user, cn, group))
            raise LDAPError(e)

    def add_group(self, cn, gid_number, member_uid=None):
        """
        Add new group in LDAP

        :param cn: cn of Group.
        :param gid_number: Identifier of the Group.
        :param member_uid: List of identifiers of the Users of Group.
        """
        try:
            conn = self._get_conn_manager()

            # There are 2 DNs by the requirement of the solutions adopted
            dn = self._get_str(cn, CN_TYPES.GROUP)

            attrs = {}
            attrs['objectclass'] = ['top', 'posixGroup']
            attrs['cn'] = cn
            attrs['gidNumber'] = gid_number

            memberUid = self._parse_groups(member_uid)

            if len(memberUid) > 0:
                attrs['memberUid'] = memberUid

            # Convert our dict to nice syntax for the add-function using
            # modlist-module
            ldif = modlist.addModlist(attrs)

            # Do the actual synchronous add-operation to the ldapserver
            conn.add_s(dn, ldif)

            self.logger.info(
                "LDAP - %s criou o grupo %s com sucesso." % (self.user, cn))

        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s adicionava grupo %s na base ldap." % (self.user, cn))
            raise LDAPError(e)
        finally:
            try:
                conn.unbind_s()
            except:
                pass

    def edit_group(self, cn, gid_number, member_uid=None):
        """
        Edit group in LDAP

        :param cn: cn of Group.
        :param gid_number: Identifier of the Group.
        :param member_uid: List of identifiers of the Users of Group.
        """
        try:

            memberUid = self._parse_groups(member_uid)

            attrs = {}
            attrs['memberUid'] = memberUid

            self._alter_cn(cn, CN_TYPES.GROUP, attrs)

            self.logger.info(
                "LDAP - %s alterou o grupo %s com sucesso." % (self.user, cn))

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s alterava grupo %s na base ldap." % (self.user, cn))
            raise LDAPMethodError(e)

    def get_users(self, lock=False, policy=False):
        """
        Returns all users from LDAP

        :param lock: True or False, determines whether data will be fetched lock
        :param policy: True or False, determines whether data will be fetched policies

        """
        try:
            conn = self._get_conn()

            us = conn.search_ext_s(
                self._get_str_ou(CN_TYPES.USER), ldap.SCOPE_ONELEVEL)

            users = {}
            for u in us:
                dic = {}
                for k in u[1]:
                    if len(u[1][k]) == 1:
                        dic[k] = u[1][k][0]
                    else:
                        dic[k] = u[1][k]

                "GLOBO - BLOCK"
                if policy:

                    pol = self._cmd_line(dic['cn'], "pwdPolicySubentry")
                    polName = pol["pwdPolicySubentry"].split("=")[1]
                    polName = polName.split(",")[0]
                    dic["pwdPolicySubentry"] = pol["pwdPolicySubentry"]
                    dic["policy"] = polName

                if lock:

                    lockTimeArray = []
                    lock = self._cmd_line(dic['cn'], "pwdAccountLockedTime")
                    lockTime = lock["pwdAccountLockedTime"]
                    if not lockTime == "":
                        if lockTime == "000001010000Z":
                            lockTimeArray = [0, 0, 0, 0, 0, 0]
                        else:
                            lockTime = lockTime[0:(len(lockTime) - 1)]
                            lockTimeData = datetime(int(lockTime[0:4]), int(lockTime[4:6]), int(
                                lockTime[6:8]), int(lockTime[8:10]), int(lockTime[10:12]), int(lockTime[12:14]))
                            lockTimeData = lockTimeData - timedelta(hours=3)
                            lockTimeArray = [lockTimeData.strftime("%Y"), lockTimeData.strftime("%m"), lockTimeData.strftime(
                                "%d"), lockTimeData.strftime("%H"), lockTimeData.strftime("%M"), lockTimeData.strftime("%S")]
                    dic["pwdAccountLockedTime"] = lockTimeArray

                users[int(dic['uidNumber'])] = dic

            return users

        except Exception, e:
            raise LDAPError(e)

    def get_sudoers(self):
        """
        Returns all Sudoers from LDAP
        """
        try:
            conn = self._get_conn()

            sds = conn.search_ext_s(
                self._get_str_ou(CN_TYPES.SUDOERS), ldap.SCOPE_ONELEVEL)

            sudoers = {}
            for sud in sds:
                dic = {}
                for k in sud[1]:
                    if len(sud[1][k]) == 1 and k != "sudoCommand" and k != "sudoUser":
                        dic[k] = sud[1][k][0]
                    else:
                        dic[k] = sud[1][k]

                sudoers[dic['cn']] = dic

            return sudoers

        except Exception, e:
            raise LDAPError(e)

    def add_sudoer(self, cn, sudoHost, sudoUser=None, sudoCommand=None):
        """
        Add new sudoer in LDAP

        :param cn: cn of Sudoer.
        :param sudoHost: Identifier of the Group.
        :param sudoUser: List of identifiers of the Group of Sudoer.
        :param sudoCommand: List of commands.
        """
        try:
            conn = self._get_conn_manager()

            dn = self._get_str(cn, CN_TYPES.SUDOERS)

            # A dict to help build the "body" of the object
            attrs = {}
            attrs['objectClass'] = ['top', 'sudoRole']
            attrs['cn'] = cn
            attrs['sudoHost'] = sudoHost

            groups, cmds = self._parse_sudoers(sudoUser, sudoCommand)

            if len(groups) > 0:
                attrs['sudoUser'] = groups

            if len(cmds) > 0:
                attrs['sudoCommand'] = cmds

            # Convert our dict to nice syntax for the add-function using
            # modlist-module
            ldif = modlist.addModlist(attrs)

            # Do the actual synchronous add-operation to the ldapserver
            conn.add_s(dn, ldif)

            self.logger.info(
                "LDAP - %s criou a regra de sudo %s com sucesso." % (self.user, cn))

        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s adicionava a regra de sudo %s na base ldap." % (self.user, cn))
            raise LDAPError(e)
        finally:
            try:
                conn.unbind_s()
            except:
                pass

    def edit_sudoer(self, cn, sudoHost, sudoUser=None, sudoCommand=None):
        """
        Edit sudoer in LDAP

        :param cn: cn of Sudoer.
        :param sudoHost: Identifier of the Group.
        :param sudoUser: List of identifiers of the Group of Sudoer.
        :param sudoCommand:List of commands.
        """
        try:
            # A dict to help build the "body" of the object
            attrs = {}
            attrs['sudoHost'] = sudoHost

            groups, cmds = self._parse_sudoers(sudoUser, sudoCommand)

            if len(groups) > 0:
                attrs['sudoUser'] = groups

            if len(cmds) > 0:
                attrs['sudoCommand'] = cmds

            self._alter_cn(cn, CN_TYPES.SUDOERS, attrs)

            self.logger.info(
                "LDAP - %s alterou a regra de sudo  %s com sucesso." % (self.user, cn))

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s alterava a regra de sudo  %s na base ldap." % (self.user, cn))
            raise LDAPError(e)

    def rem_sudoer(self, cn):
        """
        Remove sudoer in LDAP

        :param cn: cn of Sudoer.
        """
        try:
            conn = self._get_conn_manager()

            dn = self._get_str(cn, CN_TYPES.SUDOERS)

            self.get_sudoer(cn)

            conn.delete_s(dn)

            self.logger.info(
                "LDAP - %s removeu a regra de sudo %s com sucesso." % (self.user, cn))

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s removia a regra de sudo %s na base ldap." % (self.user, cn))
            raise LDAPError(e)

    def get_policies(self):
        """
        Returns all Policies from LDAP
        """
        try:
            conn = self._get_conn()

            pols = conn.search_ext_s(
                self._get_str_ou(CN_TYPES.POLICY), ldap.SCOPE_ONELEVEL)

            policies = {}
            for pol in pols:
                dic = {}
                for k in pol[1]:
                    if len(pol[1][k]) == 1 and k != "memberUid":
                        dic[k] = pol[1][k][0]
                    else:
                        dic[k] = pol[1][k]

                policies[dic['cn']] = dic

            return policies

        except Exception, e:
            raise LDAPError(e)

    def get_groups_user(self, cn):
        """
        Returns all Groups by user from LDAP

        :param cn: cn of User.
        """
        try:
            gps = self.get_groups()

            groups = []
            for group in gps:
                gp = gps[group]
                if gp.has_key("memberUid"):
                    uids = gp["memberUid"]
                    for uid in uids:
                        if uid == cn:
                            groups.append(gp['cn'])

            return groups

        except Exception, e:
            raise LDAPError(e)

    def get_users_group(self, gid, exclude_list=[]):
        """
        Returns the users from the group from LDAP

        :param gid: gidNumber of group.
        """
        try:
            gps = self.get_groups()

            out = []
            gp = gps[int(gid)]
            if gp.has_key("memberUid"):
                out = list(set(gp["memberUid"]) - set(exclude_list))
                for ldap_usr in out:
                    try:
                        usr = self.get_user(ldap_usr)
                        if usr['givenName'] == None or usr['givenName'] == '' or (usr.get('nsaccountlock') != None and usr['nsaccountlock'] == 'TRUE'):
                            out.remove(ldap_usr)
                    except Exception:
                        out.remove(ldap_usr)

            return out

        except Exception, e:
            raise LDAPError(e)

    def add_user(self, cn, uidNumber, groupPattern, homeDirectory, givenName, initials, sn, mail, homePhone, mobile, street, description, employeeNumber, employeeType, loginShell, shadowLastChange, shadowMin, shadowMax, shadowWarning, policy, groups):
        """
        Add new user in LDAP

        :param cn: cn of Sudoer.
        :param uidNumber: Identifier of the User.
        :param groupPattern: groupPattern.
        :param homeDirectory: homeDirectory.
        :param givenName: givenName.
        :param initials: initials.
        :param sn: sn.
        :param mail: mail.
        :param homePhone: homePhone.
        :param mobile: street.
        :param street: street.
        :param description: description.
        :param employeeNumber: employeeNumber.
        :param employeeType: employeeType.
        :param loginShell: loginShell.
        :param shadowLastChange: shadowLastChange.
        :param shadowMin: shadowMin.
        :param shadowMax: shadowMax.
        :param shadowWarning: shadowWarning.
        :param policy: List of identifiers of the Policies.
        :param groups: List of identifiers of the Group.
        """
        try:

            conn = self._get_conn_manager()

            dn = self._get_str(cn, CN_TYPES.USER)

            if groupPattern == self.groupStandard:
                groupStandardCn = self.groupStandardCn
                home = homeDirectory

            elif groupPattern == self.groupStandardExternal:
                groupStandardCn = self.groupStandardExternalCn
                home = "/"

            # A dict to help build the "body" of the object
            attrs = {}
            attrs['objectclass'] = [
                'posixAccount', 'inetOrgPerson', 'top', 'shadowAccount']
            attrs['cn'] = cn
            attrs['uid'] = cn
            attrs['givenName'] = givenName
            attrs['initials'] = initials
            attrs['sn'] = sn
            attrs['mail'] = mail
            attrs['homePhone'] = homePhone
            attrs['mobile'] = mobile
            attrs['street'] = street
            attrs['description'] = description
            attrs['employeeNumber'] = employeeNumber
            attrs['employeeType'] = employeeType
            attrs['uidNumber'] = uidNumber
            attrs['gidNumber'] = uidNumber
            attrs['homeDirectory'] = home
            attrs['loginShell'] = loginShell
            attrs['userPassword'] = LDAP_PASSWORD_DEFAULT_HASH
            attrs['shadowLastChange'] = shadowLastChange
            attrs['shadowMin'] = shadowMin
            attrs['shadowMax'] = shadowMax
            attrs['shadowWarning'] = shadowWarning
            attrs['pwdPolicySubentry'] = self._get_str(policy, CN_TYPES.POLICY)

            ldif = modlist.addModlist(attrs)
            conn.add_s(dn, ldif)

            self.logger.info(
                "LDAP - %s adicionou o usuario %s a base Ldap." % (self.user, cn))

            self.add_group(cn, uidNumber, cn)

            self._add_user_in_group(cn, groupStandardCn)

            # Groups
            for group in groups:
                self._add_user_in_group(cn, group)

        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s adicionava o usuário %s na base ldap." % (self.user, cn))
            raise LDAPError(e)
        finally:
            try:
                conn.unbind_s()
            except:
                pass

    def edit_user(self, cn, uidNumber, groupPattern, homeDirectory, givenName, initials, sn, mail, homePhone, mobile, street, description, employeeNumber, employeeType, loginShell, shadowLastChange, shadowMin, shadowMax, shadowWarning, policy, groups):
        """
        Edit new user in LDAP

        :param cn: cn of Sudoer.
        :param uidNumber: Identifier of the User.
        :param groupPattern: groupPattern.
        :param homeDirectory: homeDirectory.
        :param givenName: givenName.
        :param initials: initials.
        :param sn: sn.
        :param mail: mail.
        :param homePhone: homePhone.
        :param mobile: street.
        :param street: street.
        :param description: description.
        :param employeeNumber: employeeNumber.
        :param employeeType: employeeType.
        :param loginShell: loginShell.
        :param shadowLastChange: shadowLastChange.
        :param shadowMin: shadowMin.
        :param shadowMax: shadowMax.
        :param shadowWarning: shadowWarning.
        :param policy: List of identifiers of the Policies.
        :param groups: List of identifiers of the Group.
        """
        try:

            # A dict to help build the "body" of the object
            attrs = {}
            attrs['givenName'] = givenName
            attrs['initials'] = initials
            attrs['sn'] = sn
            attrs['mail'] = mail
            attrs['homePhone'] = homePhone
            attrs['mobile'] = mobile
            attrs['street'] = street
            attrs['description'] = description
            attrs['employeeNumber'] = employeeNumber
            attrs['employeeType'] = employeeType
            attrs['homeDirectory'] = homeDirectory
            attrs['loginShell'] = loginShell
            attrs['shadowLastChange'] = shadowLastChange
            attrs['shadowMin'] = shadowMin
            attrs['shadowMax'] = shadowMax
            attrs['shadowWarning'] = shadowWarning
            attrs['pwdPolicySubentry'] = self._get_str(policy, CN_TYPES.POLICY)

            self._alter_cn(cn, CN_TYPES.USER, attrs)

            self.logger.info(
                "LDAP - %s alterou o usuario %s a base Ldap." % (self.user, cn))

            groups_user = self.get_groups_user(cn)

            # Groups
            for group in groups_user:

                if group in groups:
                    groups.remove(group)

                else:
                    try:
                        if group != self.groupStandardCn and group != cn:
                            self.rem_group_user(cn, group)
                    except:
                        pass

            for group in groups:
                self._add_user_in_group(cn, group)

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s alterava o usuário %s na base ldap." % (self.user, cn))
            raise LDAPError(e)

    def _add_user_in_group(self, user, group):
        """
        User join the group in LDAP

        :param user: cn of User.
        :param group: cn of Group.

        """
        try:

            self._conn = None

            grp = self.get_group(group)

            groups = []
            if grp.has_key('memberUid'):
                groups = grp['memberUid']
                if type(groups) != type([]):
                    groups = [groups]

            groups.append(user)

            memberUid = self._parse_groups(groups)

            self._alter_cn(group, CN_TYPES.GROUP, {'memberUid': memberUid})

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s adicionava o usuário %s no grupo %s na base ldap." % (self.user, user, group))
            raise LDAPError(e)

    def rem_user(self, cn):
        """
        Remove user in LDAP

        :param cn: cn of User.

        """
        try:
            conn = self._get_conn_manager()

            dn = self._get_str(cn, CN_TYPES.USER)

            self.get_user(cn)

            conn.delete_s(dn)

            self.logger.info(
                "LDAP - %s removeu o usuário %s com sucesso." % (self.user, cn))

            # Remove Groups
            groups = self.get_groups_user(cn)
            for group in groups:
                self.rem_group_user(cn, group)

            self.rem_group(cn)

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s removia usuário %s na base ldap." % (self.user, cn))
            raise LDAPError(e)

    def reset_pwd(self, cn):
        """
        Reset the password for the User default password Globo.com

        :param cn: cn of User.
        """
        try:
            conn = self._get_conn_manager()

            dn = self._get_str(cn, CN_TYPES.USER)

            user = self.get_user(cn)

            mod_attrs = [(ldap.MOD_REPLACE, "userPassword", LDAP_PASSWORD_DEFAULT_HASH),
                         (ldap.MOD_REPLACE, "shadowLastChange", "1")]  # senha globocom em md5

            conn.modify_ext_s(dn, mod_attrs)

            self.logger.info(
                "LDAP - %s resetou a senha do usuario %s com sucesso." % (self.user, cn))

            "Se estava lockado, vai deslocar. Remove o lock de ssh tb, caso exista."
            user = self.get_user(cn)
            home = user["homeDirectory"]
            cmd1 = commands.getstatusoutput(COMMAND_TYPES.LOCK % home)
            if cmd1[0] != 0:
                self.logger.warning(
                    "LDAP - Retorno do comando para unlock de chave ssh(ldapResetPwd): %s - %s" % (cmd1[0], cmd1[1]))

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s removia a regra de sudo %s na base ldap." % (self.user, cn))
            raise LDAPError(e)

    def lock_user(self, cn):
        """
        Lock User in LDAP.

        :param cn: cn of User.
        """
        try:
            conn = self._get_conn_manager()

            dn = self._get_str(cn, CN_TYPES.USER)

            user = self.get_user(cn)

            home = user["homeDirectory"]
            cmd1 = commands.getstatusoutput(COMMAND_TYPES.UNLOCK % home)
            if cmd1[0] != 0:
                self.logger.warning(
                    "LDAP - Retorno do comando para lock de chave ssh(ldapLockUser): %s - %s" % (cmd1[0], cmd1[1]))

            mod_attrs = [(ldap.MOD_REPLACE, "pwdAccountLockedTime",
                          "000001010000Z"), (ldap.MOD_REPLACE, "nsAccountLock", "TRUE")]
            conn.modify_ext_s(dn, mod_attrs)

            self.logger.info(
                "LDAP - %s bloqueou o usuário %s com sucesso." % (self.user, cn))

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s bloqueava o usuário  %s na base ldap." % (self.user, cn))
            raise LDAPError(e)

    def unlock_user(self, cn):
        """
        Unlock User in LDAP.

        :param cn: cn of User.
        """
        try:
            conn = self._get_conn_manager()

            dn = self._get_str(cn, CN_TYPES.USER)

            user = self.get_user(cn)

            home = user["homeDirectory"]

            cmd1 = commands.getstatusoutput(COMMAND_TYPES.LOCK % home)
            if cmd1[0] != 0:
                self.logger.warning(
                    "LDAP - Retorno do comando para unlock de chave ssh(ldapUnlockUser): %s - %s" % (cmd1[0], cmd1[1]))

            lock = self._cmd_line(cn, "pwdAccountLockedTime")

            mod_attrs = [(ldap.MOD_DELETE, "pwdAccountLockedTime", lock[
                          "pwdAccountLockedTime"]), (ldap.MOD_REPLACE, "nsAccountLock", "FALSE")]
            conn.modify_ext_s(dn, mod_attrs)

            self.logger.info(
                "LDAP - %s desbloqueou o usuário %s com sucesso." % (self.user, cn))

        except LDAPNotFoundError, e:
            raise e
        except Exception, e:
            self.logger.error(
                "LDAP - Erro quando %s desbloqueava o usuário  %s na base ldap." % (self.user, cn))
            raise LDAPError(e)
