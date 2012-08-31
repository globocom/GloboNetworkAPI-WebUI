# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''
import  ldap, logging
from datetime import datetime
from datetime import timedelta
from ldap import modlist, SERVER_DOWN, NO_SUCH_OBJECT
from CadVlan.settings import LDAP_INITIALIZE, LDAP_DC, LDAP_CREDENTIALS_USER, LDAP_CREDENTIALS_PWD, LDAP_MANAGER_PWD

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
        LDAPError.__init__(self, u"Invalid parameter: %s. Value: %s." % (param, value))
        self.param = param
        self.value = value
        
class CN_TYPES():
    USER    = ("usuario", "Usuarios")
    GROUP1  = ("grupo", "Grupos")
    GROUP2  = ("group", "groups")
    SUDOERS = ("sudoers", "Sudoers")
    
class Ldap():
    
    logger = logging.getLogger(__name__)
    
    def __init__(self, user):
        self.rangeUsers = range(40000,44000)
        self.rangeGroups = range(44002,45001)
        self.rangeUsersExternal = range(50000,52001)
        self.grupoPadraoGlobo_id = 44000
        self.grupoPadraoExterno_id = 44001
        self.user = user
        self._conn = None
    
    def _get_conn(self, manager=False):
        """
        Returns LDAP connection
        """
        try:
            
            if self._conn is None or manager:
            
                self._conn = ldap.initialize(LDAP_INITIALIZE)
                
                self._conn.protocol_version = ldap.VERSION3
                self._conn.simple_bind_s(self._get_str(LDAP_CREDENTIALS_USER, CN_TYPES.USER[1]), LDAP_CREDENTIALS_PWD)
                
            return self._conn
        
        except SERVER_DOWN, e:
            raise LDAPConnectionError()
        except LDAPError, e:
            raise e
        except Exception, e:
            raise LDAPMethodError(e)
        
    def _get_conn_manager(self):
        """
        Returns LDAP manager connection
        """
        try:
            
            
            conn = self._get_conn(True)
            
            conn.simple_bind_s(self._get_manager(), LDAP_MANAGER_PWD)
            
            return conn

        except SERVER_DOWN, e:
            raise LDAPConnectionError()
        except LDAPError, e:
            raise e
        except Exception, e:
            raise LDAPMethodError(e)
        
    def _get_manager(self):
        strng = "cn=Manager,%s" %  LDAP_DC
        return strng
     
    def _get_str(self, cn, ou):
        strng = "cn=%s,%s" % ( cn , self._get_str_ou(ou) )
        return strng
        
    def _get_str_ou(self, ou):
        strng = "ou=%s,%s"% ( ou , LDAP_DC )
        return strng
    
    def get_group(self, cn):
        return self._get_cn(cn, CN_TYPES.GROUP1[0])
    
    def _get_cn(self, cn, cn_type):
        """
        Returns CN of a cn_type existing in LDAP
        If cn_type is USER, aditional data will be searched
        
        @param cn: String with CN to be searched
        @param cn_type: Type of CN to be searched (CN_TYPES) 
        """
        
        try:
            
            conn = self._get_conn()
            
            if cn_type == CN_TYPES.USER[0]:
                dn = self._get_str(cn, CN_TYPES.USER[1])
            elif cn_type == CN_TYPES.GROUP1[0]:
                dn = self._get_str(cn, CN_TYPES.GROUP1[1])
            elif cn_type == CN_TYPES.GROUP2[0]:
                dn = self._get_str(cn, CN_TYPES.GROUP2[1])
            elif cn_type == CN_TYPES.SUDOERS[0]:
                dn = self._get_str(cn, CN_TYPES.SUDOERS[1])
            else:
                raise LDAPInvalidParameterError("cn_type", cn_type)
            
            ob = conn.search_ext_s(dn, ldap.SCOPE_BASE)[0]
            
            dic = {}
            for k in ob[1]:
                
                if cn_type == CN_TYPES.SUDOERS[0]:
                    if len(ob[1][k]) == 1 and k != "sudoCommand" and k != "sudoUser":
                        dic[k] = ob[1][k][0]
                    else:
                        dic[k] = ob[1][k]
                else:
                    if len(ob[1][k]) == 1:
                        dic[k] = ob[1][k][0]
                    else:
                        dic[k] = ob[1][k]
                        
            if cn_type == CN_TYPES.USER[0]:
                
                pol = self._cmd_line(cn, "pwdPolicySubentry")
                
                polName = pol["pwdPolicySubentry"].split("=")[1]
                polName = polName.split(",")[0]
                dic["pwdPolicySubentry"] = pol["pwdPolicySubentry"]
                dic["policy"] = polName
                
            return dic
        
        except NO_SUCH_OBJECT, e:
            raise LDAPNotFoundError(e)
        except LDAPError, e:
            raise e
        except Exception, e:
            raise LDAPMethodError(e)
        
    def _parse_groups(self, member_uid):
        """
        Assemble the two lists with information from User.
        
        @param member_uid: List of identifiers of the Users of Group.
        """
        memberUid = []
        member = []
        if member_uid:

            if type(member_uid) == type([]):

                for i in range(len(member_uid)):
                    mem = str(member_uid[i])
                    memberUid.append(mem)
                    member.append(self._get_str(mem, CN_TYPES.USER[1]))

            else:
                mem = str(member_uid)
                memberUid.append(mem)
                member.append(self._get_str(mem, CN_TYPES.USER[1]))
                
        return memberUid, member
        
    def _alter_cn(self, cn, cn_type, dicNew):
        """
        Modifies a cn from a dictionary containing the fields to be changed.
        
        @param cn: String with CN to be searched
        @param cn_type: Type of CN to be searched (CN_TYPES)
        @param dicNew: Dictionary containing the fields to be changed
        
        """
        try:
        
            conn = self._get_conn_manager()
            
            if cn_type == CN_TYPES.USER[0]:
                dn = self._get_str(cn, CN_TYPES.USER[1])
            elif cn_type == CN_TYPES.GROUP1[0]:
                dn = self._get_str(cn, CN_TYPES.GROUP1[1])
            elif cn_type == CN_TYPES.GROUP2[0]:
                dn = self._get_str(cn, CN_TYPES.GROUP2[1])
            elif cn_type == CN_TYPES.SUDOERS[0]:
                dn = self._get_str(cn, CN_TYPES.SUDOERS[1])
            else:
                raise LDAPInvalidParameterError("cn_type", cn_type)
    
            cn = self._get_cn(cn, cn_type)
    
            dicOld = {}
            for k in dicNew:
                if cn.has_key(k):
                    dicOld[k] = cn[k]
            
            "Policy"
            if cn_type == CN_TYPES.USER[0] and dicOld.has_key("pwdPolicySubentry"):
                
                if dicOld["pwdPolicySubentry"] != dicNew["pwdPolicySubentry"]:
                    
                    mod_attrs = [(ldap.MOD_REPLACE, "pwdPolicySubentry", dicNew["pwdPolicySubentry"])]
                    
                    try:
                        conn.modify_ext_s(dn, mod_attrs)
                    except Exception, e:
                        self.logger.error("LDAP - Erro quando %s modificava politica do usuarios na base ldap:" % self.user )
                        self.logger.error("LDAP - %s" % str(e))
                        raise LDAPMethodError(e)
                    
                del dicOld["pwdPolicySubentry"]
                del dicNew["pwdPolicySubentry"]
                
            ldif = modlist.modifyModlist(dicOld,dicNew)
        
            conn.modify_s(dn,ldif)
            
        except LDAPError, e:
            raise e
        except Exception, e:
            raise LDAPMethodError(e)
        finally:
            try:
                conn.unbind_s()
            except:
                pass
            
    def valid_range_group(self, gidNumber):
        """
        Validates that the gidNumber is in the range of group numbers
        
        @param gidNumber: Identifier of the Group.
        
        """
        is_valid = False
        if self.rangeGroups.count(int(gidNumber)) == 1:
            is_valid = True
           
        return is_valid
    
    def get_groups(self):
        """
        Returns all groups from LDAP
        """
        try:
            conn = self._get_conn()
            
            gps = conn.search_ext_s(self._get_str_ou(CN_TYPES.GROUP1[1]), ldap.SCOPE_ONELEVEL)
            
            groups = {}
            for g in gps:
                
                dic = {}
                for k in g[1]:
                    
                    if len(g[1][k]) == 1 and k != "memberUid":
                        dic[k] = g[1][k][0]
                    else:
                        dic[k] = g[1][k]
                
                if self.valid_range_group(dic["gidNumber"]):
                    groups[ int(dic["gidNumber"]) ] = dic
                    
            return groups

        except LDAPError, e:
            raise e
        except Exception, e:
            raise LDAPMethodError(e)
        
    def rem_group(self, cn):
        """
        Remove group in LDAP
        
        @param cn: cn of Group.
        
        """
        try:
            conn = self._get_conn_manager()

            dn  = self._get_str(cn, CN_TYPES.GROUP1[1])
            dn2 = self._get_str(cn, CN_TYPES.GROUP2[1])

            conn.delete_s(dn)
            conn.delete_s(dn2)
            
            self.logger.info("LDAP - %s removeu o grupo %s com sucesso." % ( self.user, cn ) )

        except LDAPError, e:
            raise e
        except Exception, e:
            self.logger.error("LDAP - Erro quando %s removia grupo %s na base ldap." % ( self.user, cn ) )
            raise LDAPMethodError(e)
        
    def add_group(self, cn, gid_number, member_uid = None):
        """
        Add new group in LDAP
        
        @param cn: cn of Group.
        @param gid_number: Identifier of the Group.
        @param member_uid: List of identifiers of the Users of Group.
        """
        try:
            conn = self._get_conn_manager()
            
            # There are 2 DNs by the requirement of the solutions adopted
            dn = self._get_str(cn, CN_TYPES.GROUP1[1])
            dn2 = self._get_str(cn, CN_TYPES.GROUP2[1])
            
            attrs = {}
            attrs['objectclass'] = ['top', 'posixGroup']
            attrs['cn'] = cn
            attrs['gidNumber'] = gid_number
            attrs2 = {}
            attrs2['objectclass'] = ['groupOfNames']
            attrs2['cn'] = cn
            
            memberUid, member = self._parse_groups(member_uid)
                    
            if len(memberUid) > 0:
                attrs['memberUid'] = memberUid
                attrs2['member'] = member
                
            # Convert our dict to nice syntax for the add-function using modlist-module
            ldif = modlist.addModlist(attrs)
            ldif2 = modlist.addModlist(attrs2)
            
            # Do the actual synchronous add-operation to the ldapserver
            conn.add_s(dn, ldif)
            conn.add_s(dn2, ldif2)
            
            self.logger.info("LDAP - %s criou o grupo %s com sucesso." % ( self.user, cn ) )
            
        except LDAPError, e:
            raise e
        except Exception, e:
            self.logger.error("LDAP - Erro quando %s adicionava grupo %s na base ldap." % ( self.user, cn ) )
            raise LDAPMethodError(e)
        finally:
            try:
                conn.unbind_s()
            except:
                pass
        
    def edit_group(self, cn, gid_number, member_uid = None):
        """
        Edit group in LDAP
        
        @param cn: cn of Group.
        @param gid_number: Identifier of the Group.
        @param member_uid: List of identifiers of the Users of Group.
        """
        try:
            attrs = {}
            attrs['cn'] = cn
            attrs['gidNumber'] = gid_number
            attrs2 = {}
            attrs2['cn'] = cn
            
            memberUid, member = self._parse_groups(member_uid)
            
            attrs['memberUid'] = memberUid
            attrs2['member'] = member
            
            self._alter_cn(cn, CN_TYPES.GROUP1[0], attrs)
            self._alter_cn(cn, CN_TYPES.GROUP2[0], attrs2)
            
            self.logger.info("LDAP - %s alterou o grupo %s com sucesso." % ( self.user, cn ) )
            
        except LDAPError, e:
            raise e
        except Exception, e:
            self.logger.error("LDAP - Erro quando %s alterava grupo %s na base ldap." % ( self.user, cn ) )
            raise LDAPMethodError(e)
        
    def get_users(self, lock=False, policy=False):
        """
        Returns all users from LDAP
        
        @param lock: True or False, determines whether data will be fetched lock
        @param policy: True or False, determines whether data will be fetched policies
        
        """
        try:
            conn = self._get_conn()
            
            us = conn.search_ext_s(self._get_str_ou(CN_TYPES.USER[1]), ldap.SCOPE_ONELEVEL)        
        
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
                    
                    pol = self.ldapCmdLine(dic['cn'] ,"pwdPolicySubentry")
                    if pol == None:
                        raise LDAPMethodError("Erro já logado na função ldapCmdLine")

                    polName = pol["pwdPolicySubentry"].split("=")[1]
                    polName = polName.split(",")[0]
                    dic["pwdPolicySubentry"] = pol["pwdPolicySubentry"]
                    dic["policy"] = polName
            
                if lock:
                    
                    lockTimeArray = []
                    lock = self.ldapCmdLine(dic['cn'], "pwdAccountLockedTime")
                    if lock == None:
                        raise LDAPMethodError("Erro já logado na função ldapCmdLine")
                    
                    lockTime = lock["pwdAccountLockedTime"]
                    if not lockTime == "":    
                        if lockTime == "000001010000Z":
                            lockTimeArray = [0,0,0,0,0,0]
                        else:
                            lockTime = lockTime[0:(len(lockTime)-1)]
                            lockTimeData = datetime(int(lockTime[0:4]),int(lockTime[4:6]),int(lockTime[6:8]),int(lockTime[8:10]),int(lockTime[10:12]),int(lockTime[12:14]))
                            lockTimeData = lockTimeData - timedelta(hours=3)
                            lockTimeArray = [lockTimeData.strftime("%Y"),lockTimeData.strftime("%m"),lockTimeData.strftime("%d"),lockTimeData.strftime("%H"),lockTimeData.strftime("%M"),lockTimeData.strftime("%S")]
                    dic["pwdAccountLockedTime"] = lockTimeArray
                
                users[ int(dic['uidNumber']) ] = dic
        
            return users
    
        except LDAPError, e:
            raise e
        except Exception, e:
            raise LDAPMethodError(e)
