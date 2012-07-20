# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''
from CadVlan.Util.cvs import Cvs, CVSCommandError
from CadVlan.Util.file import File, FileError
from CadVlan.Util.Enum import Enum
from CadVlan.settings import PATH_ACL
from CadVlan.Util.Enum import NETWORK_TYPES
import logging
import os
from time import strftime
import commands

logger = logging.getLogger(__name__)

EXTENTION_FILE = ".txt"

PATH_ACL_TEMPLATES = "/templates/"

PATH_TYPES =  Enum(["ACL", "TEMPLATE"])

DIVISON_DC =  Enum(["FE", "BE", "DEV_QA_FE", "DEV_QA", "BORDA"])

ENVIRONMENT_LOGICAL =  Enum(["APLICATIVOS", "PORTAL", "HOMOLOGACAO"])

TEMPLATES =  Enum(["BE", "BEHO", "FE_APLICATIVOS", "FE_DEV_QA", "FE_PORTAL", "FE_STAGING"])

PREFIX_TEMPLATES = "ACL_PADRAO_"


def mkdir_divison_dc(divison_dc, user):
    '''Creates the directory division dc in cvs
    
    @param divison_dc: division dc to be created
    @param user: user
    
    @raise CVSCommandError: Failed to execute 
    '''
    try:
        
        
        divison_dc = str(divison_dc).upper()
        
        os.chdir(PATH_ACL)
        
        Cvs.synchronization()
        
        if not os.path.exists(divison_dc):
            
            os.mkdir(divison_dc)
            
            Cvs.add(divison_dc)
            
            Cvs.commit(divison_dc, "Criação do diretório de divisão dc %s pelo usuário: %s" % ( divison_dc, user.get_username()))
            
            logger.info("%s criou no CVS o diretório: %s" % (user.get_username(), divison_dc) )
        
    except Exception, e:
        logger.error("Erro quando o usuário %s tentou criar o diretório: %s no Cvs" % (user.get_username(), divison_dc))
        logger.error(e)
        raise CVSCommandError(e)

def script_template(environment_logical, divison_dc, group_l3):
    '''Validates that can use a script to create the ACL.
    
    @param environment_logical: environment logical
    @param divison_dc: divison dc
    @param group_l3: group l3
    '''
    script = False
    
    if divison_dc == DIVISON_DC.FE:
        
        if environment_logical == ENVIRONMENT_LOGICAL.APLICATIVOS or environment_logical == ENVIRONMENT_LOGICAL.PORTAL or environment_logical == ENVIRONMENT_LOGICAL.HOMOLOGACAO:
            
            if group_l3 == "CORE/DENSIDADE":
                
                script = True
                
    elif divison_dc == DIVISON_DC.BE:
    
        if environment_logical == ENVIRONMENT_LOGICAL.APLICATIVOS or environment_logical == ENVIRONMENT_LOGICAL.HOMOLOGACAO:
            
            if group_l3 == "CORE/DENSIDADE":
                
                script = True
                
    return script
    
def chdir(type_path, path = None):
    '''Change the current working directory to path.
    
    @param type_path: type path
    @param path: path
    
    @raise CVSCommandError:  Failed to execute command
    '''
    try:
        
        if type_path == PATH_TYPES.ACL:
            path = PATH_ACL + path
        
        elif type_path == PATH_TYPES.TEMPLATE:
            path = PATH_ACL + PATH_ACL_TEMPLATES
        
        os.chdir(path)
        
    except Exception, e:
        logger.error(e)
        raise Exception(e)
    
def check_name_file(acl_file_name, extention = True):
    '''Validates the filename do acl has point and space and adds extension
    
    @param acl_file_name: name is validaded
    @param extention: True case add extention
    '''
    acl = ""
    for caracter in acl_file_name:
        if ((caracter == ".") or (caracter == " ")):
            pass
        else:
            acl += caracter
            
    if extention == True:
        acl = acl + EXTENTION_FILE
        
    return acl 

def check_name_file_bkp(acl_file_name):
    '''Validates the filename do acl has point and space and adds extension and suffix bkp
    
    @param acl_file_name: name is validaded
    '''
    acl = ""
    for caracter in acl_file_name:
        if ((caracter == ".") or (caracter == " ")):
            pass
        else:
            acl += caracter
        
    return acl + "_bkp_" + strftime("%Y%m%d%H%M%S") + EXTENTION_FILE

def path_acl(environment_logical, divison_dc):
    '''Creates the path depending on the parameters of environment 
    
    @param environment_logical: environment logical
    @param divison_dc: divison dc
    '''
    path = ""
    if environment_logical == ENVIRONMENT_LOGICAL.HOMOLOGACAO:

        if divison_dc == DIVISON_DC.FE:
            path = DIVISON_DC.DEV_QA_FE
            
        else:
            path = DIVISON_DC.DEV_QA

    else:
        path = divison_dc
    
    return path

def checkAclCvs(acl_file_name, environment, network, user):
    '''Validates if the file is created acl.
    
    @param acl_file_name: acl name
    @param environment: Environment
    @param network: v4 or v6
    @param user: user
    
    @raise CVSCommandError:  Failed to execute command
    
    @return: True case created
    '''
    try:
        
        acl = check_name_file(acl_file_name)
        
        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"])
        
        mkdir_divison_dc(environment["nome_divisao"], user)
        
        chdir(PATH_TYPES.ACL, path)
        
        Cvs.synchronization()
        
        File.read(acl)
        
        return True
    
    except FileError, e:
        return False
    
    except (CVSCommandError, Exception), e:
        logger.error("Erro quando o usuário %s tentou sincronizar no Cvs" % (user.get_username()) )
        logger.error(e)
        raise CVSCommandError(e)

def getAclCvs(acl_file_name, environment, network, user):
    '''Retrieves the contents of the file acl.
    
    @param acl_file_name: acl name
    @param environment: Environment
    @param network: v4 or v6
    @param user: user
    
    @raise CVSCommandError:  Failed to execute command
    '''
    try:
        
        acl = check_name_file(acl_file_name)
        
        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"])
        
        mkdir_divison_dc(environment["nome_divisao"], user)
        
        chdir(PATH_TYPES.ACL, path)
        
        Cvs.synchronization()
        
        content = File.read(acl)
        
        return content
        
    except (CVSCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou sincronizar no Cvs" % (user.get_username()) )
        logger.error(e)
        raise CVSCommandError(e)
    
def alterAclCvs(acl_name, acl_content, environment,comment,  network, user):
    '''Change the contents of the file acl.
    
    @param acl_name: acl name
    @param acl_content: acl content
    @param environment: Environment
    @param comment: comments of user
    @param network: v4 or v6
    @param user: user
    
    @raise CVSCommandError:  Failed to execute command
    '''
    try:
        
        acl = check_name_file(acl_name)
        
        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"])
        
        chdir(PATH_TYPES.ACL, path)
            
        Cvs.synchronization()
        
        File.write(acl, acl_content)
        
        Cvs.commit(acl, "%s comentou: %s" % ( user.get_username(), comment ))
        
        logger.info("%s alterou no CVS o arquivo: %s Comentário do Usuário: %s" % (user.get_username(), (path + acl), comment) )
        
    except (CVSCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou atualizar o arquivo: %s no Cvs" % (user.get_username(), (path + acl)))
        logger.error(e)
        raise CVSCommandError(e)

def createAclCvs(acl_name, environment, network, user):
    '''Create the file acl.
    
    @param acl_name: acl name
    @param environment: Environment
    @param network: v4 or v6
    @param user: user
    
    @raise CVSCommandError:  Failed to execute command
    '''
    try:
        
        acl = check_name_file(acl_name)
        
        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"])
        
        mkdir_divison_dc(environment["nome_divisao"], user)
        
        chdir(PATH_TYPES.ACL, path)
        
        Cvs.synchronization()
        
        File.create(acl)
        
        Cvs.add(acl)
        
        Cvs.commit(acl, "Criação do Arquivo %s pelo usuário: %s" % ( acl, user.get_username()))
        
        logger.info("%s criou no CVS o arquivo: %s" % (user.get_username(), (path + acl)) )
    
    except (CVSCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou criar o arquivo: %s no Cvs" % (user.get_username(), (path + acl)))
        logger.error(e)
        raise CVSCommandError(e)
    
def deleteAclCvs(acl_name, environment, network, user):
    '''Delete acl file and creates a backup file
    
    @param acl_name: acl name
    @param environment: Environment
    @param network: v4 or v6
    @param user: user
    
    @raise CVSCommandError:  Failed to execute command
    '''
    try:
        
        acl = check_name_file(acl_name)
        
        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"])
        
        chdir(PATH_TYPES.ACL, path)
        
        Cvs.synchronization()
        
        content_bkp = File.read(acl)
        
        File.remove(acl)
        
        Cvs.remove(acl)
        
        Cvs.commit(acl, "Exclusão do Arquivo %s pelo usuário:%s" % ( acl, user.get_username()))
        
        Cvs.synchronization()
        
        logger.info("%s excluiu no CVS o arquivo: %s" % (user.get_username(), (path + acl)) )
        
        #Backup ACL
        acl_bkp = check_name_file_bkp(acl_name)
        
        File.create(acl_bkp)
        
        File.write(acl_bkp, content_bkp)
        
        Cvs.add(acl_bkp)
        
        Cvs.commit(acl_bkp, "Criação do Arquivo de Backup %s pelo usuário: %s" % ( acl, user.get_username()))
        
        logger.info("%s criou no CVS o arquivo de Backup: %s" % (user.get_username(), (path + acl)) )
        
    except (CVSCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou excluiu o arquivo: %s no Cvs" % (user.get_username(), (path + acl)))
        logger.error(e)
        raise CVSCommandError(e)
    
def applyAcl(equipments, vlan, environment, network, user):
    '''Apply the file acl in equipments
    
    @param equipments: list of equipments
    @param vlan: Vvlan
    @param environment: Environment
    @param network: v4 or v6
    @param user: user
    
    @raise Exception: Failed to apply acl
    
    @return: True case Apply and sysout of script
    '''
    try:
        
        acl = check_name_file(vlan["acl_file_name"])
        
        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"])
        
        if path ==  DIVISON_DC.BORDA:
            path = "Borda"
        
        name_equipaments = ""  
        for equip in equipments:

            if not  equip in name_equipaments:

                if equip == equipments[0]:
                    name_equipaments += "%s" % equip
                else:
                    name_equipaments += ",%s" % equip
            
        (erro,result) = commands.getstatusoutput("/usr/bin/backuper -T acl -b %s/%s -e -i %s"% (path, acl, name_equipaments))
        
        if erro:
            logger.error("Erro quando o usuário %s tentou aplicar ACL %s no equipamentos: %s erro: %s" % (user.get_username(), acl, equipments, result) )
            return False, result
        
        for equip in equipments:
            logger.info("%s aplicou a ACL %s no Equipamento:%s" % (user.get_username(), acl, equip) )
        
        return True, result
        
    except Exception, e:
        logger.error("Erro quando o usuário %s tentou aplicar ACL %s no equipamentos: %s" % (user.get_username(), acl, equipments) )
        logger.error(e)
        raise Exception(e)

def scriptAclCvs(vlan, environment, network, user):
    '''Generates the acl based on a template
    
    @param vlan: Vvlan
    @param environment: Environment
    @param network: v4 or v6
    @param user: user
    
    @raise CVSCommandError:  Failed to execute command
    '''
    try:    
    
        acl = check_name_file(vlan["acl_file_name"])
        acl_name = check_name_file(vlan["acl_file_name"], extention = False)
        
        #sufix v4 or v6
        network_ = "_" + network
        
        if ((environment["nome_divisao"] == "BE") and (environment["nome_ambiente_logico"] == "PRODUCAO") and (environment["nome_grupo_l3"] == "CORE/DENSIDADE")):
            
            chdir(PATH_TYPES.ACL, DIVISON_DC.BE)
            
            Cvs.synchronization()
            
            arquivo = open("./%s" % acl , "w")
            
            chdir(PATH_TYPES.TEMPLATE)
            
            file_template = open(PREFIX_TEMPLATES + TEMPLATES.BE + network_ + EXTENTION_FILE, "r")
            
            content_template = file_template.read()
            
            nova_acl = replace_template(acl_name, vlan, content_template, network)
            
            chdir(DIVISON_DC.BE, PATH_TYPES.ACL)
            
            arquivo.write("%s" % nova_acl)
            arquivo.close()
            file_template.close()
            
            Cvs.commit(acl, "%s gerou Script para a acl %s" % ( user.get_username(), acl ) )
            
            logger.info("%s alterou no CVS o arquivo: %s" % (user.get_username(), acl) )
            
        if ((environment["nome_divisao"] == DIVISON_DC.FE) and (environment["nome_ambiente_logico"] == ENVIRONMENT_LOGICAL.HOMOLOGACAO) and (environment["nome_grupo_l3"] == "CORE/DENSIDADE")):
            
            chdir(PATH_TYPES.ACL, DIVISON_DC.DEV_QA_FE)
            
            Cvs.synchronization()
            
            arquivo = open("./%s" % acl, "w")
            
            chdir(PATH_TYPES.TEMPLATE)
            
            file_template = open(PREFIX_TEMPLATES + TEMPLATES.FE_DEV_QA + network_ + EXTENTION_FILE, "r")
            
            content_template = file_template.read()
            
            nova_acl = replace_template(acl_name, vlan, content_template, network)
            
            chdir(PATH_TYPES.ACL, DIVISON_DC.DEV_QA_FE)
            
            arquivo.write("%s" % nova_acl)
            arquivo.close()
            file_template.close()
            
            Cvs.commit(acl, "%s gerou Script para a acl %s" % ( user.get_username(), acl) )
            
            logger.info("%s alterou no CVS o arquivo: %s" % (user.get_username(), acl ))
        
        if ((environment["nome_divisao"] ==  DIVISON_DC.FE ) and (environment["nome_ambiente_logico"] == ENVIRONMENT_LOGICAL.PORTAL) and (environment["nome_grupo_l3"] == "CORE/DENSIDADE")):
            
            chdir(PATH_TYPES.ACL, DIVISON_DC.FE)
            
            Cvs.synchronization()
            
            arquivo = open("./%s" % acl, "w")
            
            chdir(PATH_TYPES.TEMPLATE)
            
            if "staging" in acl.lower():
                file_template = open(PREFIX_TEMPLATES + TEMPLATES.FE_STAGING + network_ + EXTENTION_FILE, "r")
            else:
                file_template = open(PREFIX_TEMPLATES + TEMPLATES.FE_PORTAL + network_ + EXTENTION_FILE, "r")

            
            content_template = file_template.read()
            
            nova_acl = replace_template(acl_name, vlan, content_template, network)

            chdir(PATH_TYPES.ACL, DIVISON_DC.FE)
            
            arquivo.write("%s" % nova_acl)
            arquivo.close()
            file_template.close()
            
            Cvs.commit(acl, "%s gerou Script para a acl %s" % ( user.get_username(), acl) )
            
            logger.info("%s alterou no CVS o arquivo: %s" % (user.get_username(), acl) )
        
        if ((environment["nome_divisao"] == DIVISON_DC.FE) and (environment["nome_ambiente_logico"] == ENVIRONMENT_LOGICAL.APLICATIVOS) and (environment["nome_grupo_l3"] == "CORE/DENSIDADE")):
            
            chdir(PATH_TYPES.ACL, DIVISON_DC.FE)
            
            Cvs.synchronization()
            
            arquivo = open("./%s" % acl, "w")
            
            chdir(PATH_TYPES.TEMPLATE)
            
            file_template = open(PREFIX_TEMPLATES + TEMPLATES.FE_APLICATIVOS + network_ + EXTENTION_FILE, "r")
            
            content_template = file_template.read()
            
            nova_acl = replace_template(acl_name, vlan, content_template, network)
            
            chdir(PATH_TYPES.ACL, DIVISON_DC.FE)
            
            arquivo.write("%s" % nova_acl)
            arquivo.close()
            file_template.close()
            
            Cvs.commit(acl, "%s gerou Script para a acl %s" % ( user.get_username(), acl ) )
            
            logger.info("%s alterou no CVS o arquivo: %s" % (user.get_username(), acl) )
        
        if ((environment["nome_divisao"] == DIVISON_DC.BE) and (environment["nome_ambiente_logico"] == ENVIRONMENT_LOGICAL.HOMOLOGACAO) and (environment["nome_grupo_l3"] == "CORE/DENSIDADE")):
            
            chdir(PATH_TYPES.ACL, DIVISON_DC.DEV_QA)
            
            Cvs.synchronization()
            
            arquivo = open("./%s" % acl, "w")
            
            chdir(PATH_TYPES.TEMPLATE)
            
            file_template = open(PREFIX_TEMPLATES + TEMPLATES.BEHO + network_ + EXTENTION_FILE, "r")
            
            content_template = file_template.read()
            
            nova_acl = replace_template(acl_name, vlan, content_template, network)
            
            chdir(PATH_TYPES.ACL, DIVISON_DC.BE)
            
            arquivo.write("%s" % nova_acl)
            arquivo.close()
            file_template.close()
            
            Cvs.commit(acl, "%s gerou Script para a acl %s" % ( user.get_username(), acl ) )
            
            logger.info("%s alterou no CVS o arquivo: %s" % (user.get_username(), acl) )
        
    except (CVSCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou gerar o arquivo: %s no Cvs" % (user.get_username(), acl) )
        logger.error(e)
        raise CVSCommandError(e)
    
def parse_template(vlan, network):
    
    try: 
       
        net = None
        block = None
        wmasc = None
        special_1 = None
        special_2 = None
       
        if vlan["redeipv4"] is not None and vlan["redeipv4"] != "" and vlan["redeipv4"] and network == NETWORK_TYPES.v4:
            network = vlan["redeipv4"][0]
           
            net = "%s.%s.%s.%s" % (network["oct1"], network["oct2"], network["oct3"], network["oct4"])
            
            wmasc_1 = int(network["mask_oct1"]) ^ 255
            wmasc_2 = int(network["mask_oct2"]) ^ 255
            wmasc_3 = int(network["mask_oct3"]) ^ 255
            wmasc_4 = int(network["mask_oct4"]) ^ 255
            
            wmasc = "%s.%s.%s.%s" % (wmasc_1, wmasc_2, wmasc_3, wmasc_4)
            
            ipEsp_1 =  int(network["oct1"]) | wmasc_1
            ipEsp_2 =  int(network["oct2"]) | wmasc_2
            ipEsp_3 =  int(network["oct3"]) | wmasc_3
            ipEsp_4 =  int(network["oct4"]) | wmasc_4
             
            special_1 = "%s.%s.%s.%s" % (ipEsp_1, ipEsp_2, ipEsp_3, (ipEsp_4 - 1))
            special_2 = "%s.%s.%s.%s" % (ipEsp_1, ipEsp_2, ipEsp_3, (ipEsp_4 - 2))
             
            block = "%s" % (network['block'])
           
           
        elif vlan["redeipv6"] is not None and vlan["redeipv6"] != "" and vlan["redeipv6"] and network == NETWORK_TYPES.v6:
            network = vlan["redeipv6"][0]
            
            net = "%s:%s:%s:%s:%s:%s:%s:%s" % (network["block1"], network["block2"], network["block3"], network["block4"], network["block5"], network["block6"], network["block7"], network["block8"])
            
            wmasc_1 = int(network["mask1"]) ^ 255
            wmasc_2 = int(network["mask2"]) ^ 255
            wmasc_3 = int(network["mask3"]) ^ 255
            wmasc_4 = int(network["mask4"]) ^ 255
            wmasc_5 = int(network["mask5"]) ^ 255
            wmasc_6 = int(network["mask6"]) ^ 255
            wmasc_7 = int(network["mask7"]) ^ 255
            wmasc_8 = int(network["mask8"]) ^ 255
            
            wmasc = "%s:%s:%s:%s:%s:%s:%s:%s" % (wmasc_1, wmasc_2, wmasc_3, wmasc_4, wmasc_5, wmasc_6, wmasc_7, wmasc_8)
            
            ipEsp_1 =  int(network["block1"]) | wmasc_1
            ipEsp_2 =  int(network["block2"]) | wmasc_2
            ipEsp_3 =  int(network["block3"]) | wmasc_3
            ipEsp_4 =  int(network["block4"]) | wmasc_4
            ipEsp_5 =  int(network["block5"]) | wmasc_1
            ipEsp_6 =  int(network["block6"]) | wmasc_2
            ipEsp_7 =  int(network["block7"]) | wmasc_3
            ipEsp_8 =  int(network["block8"]) | wmasc_4
             
            special_1 = "%s:%s:%s:%s:%s:%s:%s:%s" % (ipEsp_1, ipEsp_2, ipEsp_3, ipEsp_4, ipEsp_5, ipEsp_6, ipEsp_7, (ipEsp_8 - 1) )
            special_2 = "%s:%s:%s:%s:%s:%s:%s:%s" % (ipEsp_1, ipEsp_2, ipEsp_3, ipEsp_4, ipEsp_5, ipEsp_6, ipEsp_7, (ipEsp_8 - 2) )
             
            block = "%s" % (network['block'])
        
           
        return net, block, wmasc, special_1, special_2

    except Exception, e:
        logger.error("Erro quando realizava parse das variaveis da rede para o replace no template.")
        raise Exception(e)
    
def replace_template(acl_name, vlan, content_template, network):
    
    network, block, wmasc, special_1, special_2 = parse_template(vlan, network)
    
    acl = content_template.replace('%ACL',acl_name)
    acl = acl.replace('%NUMERO', "%s"% (vlan["num_vlan"]) )
    
    if network is not None and block is not None and wmasc is not None and special_1 is not None  and special_2 is not None:
    
        acl = acl.replace('%REDE', network)
        acl = acl.replace('%BLOCO', block)
        acl = acl.replace('%WMASC', wmasc)
        acl = acl.replace('%ESPECIAL1', special_1)
        acl = acl.replace('%ESPECIAL2', special_2)
        
    return acl
