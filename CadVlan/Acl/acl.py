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

from CadVlan.Util.git import Git, GITCommandError
from CadVlan.Util.file import File, FileError
from CadVlan.Util.Enum import Enum
from CadVlan.settings import PATH_ACL
from CadVlan.Util.Enum import NETWORK_TYPES
import logging
import os
from time import strftime
import commands
from os import listdir
from os.path import isfile, join
from CadVlan.Util.utility import IP_VERSION

logger = logging.getLogger(__name__)

EXTENTION_FILE = ".txt"

PATH_ACL_TEMPLATES = "/templates/"

PATH_TYPES = Enum(["ACL", "TEMPLATE"])

DIVISON_DC = Enum(["FE", "BE", "DEV_QA_FE", "DEV_QA",
                   "BORDA", "BE_POP_SP", "FE_POP_SP", "BORDA_POP_SP"])

ENVIRONMENT_LOGICAL = Enum(
    ["APLICATIVOS", "PORTAL", "HOMOLOGACAO", "PRODUCAO", "BORDA"])

TEMPLATES = Enum(
    ["BE", "BEHO", "FE_APLICATIVOS", "FE_DEV_QA", "FE_PORTAL", "FE_STAGING"])

PREFIX_TEMPLATES = "ACL_PADRAO_"

hexa = lambda x: hex(x)[2:]


def mkdir_divison_dc(divison_dc, user, acl_path=None):
    '''Creates the directory division dc in git

    :param divison_dc: division dc to be created
    :param user: user

    :raise GITCommandError: Failed to execute
    '''
    folder = ""
    try:

        divison_dc = str(divison_dc).upper()

        os.chdir(PATH_ACL)

        if divison_dc == DIVISON_DC.BORDA:
            divison_dc = "Borda"

        directory = divison_dc

        if acl_path:
            directory = acl_path

        Git.synchronization()

        # Set path - Ipv4 - Ipv6
        list_path = []
        list_path.append("%s%s/" % (PATH_ACL, 'v4'))
        list_path.append("%s%s/" % (PATH_ACL, 'v6'))

        for path in list_path:

            os.chdir(path)

            folders = directory.split("/")

            for folder in folders:
                if folder:
                    if not os.path.exists(folder):
                        os.mkdir(folder)
                        logger.info(
                            "%s criou no Git o diretório: %s/%s" % (user.get_username(), path, folder))

                    path = "%s/%s" % (path, folder)
                    os.chdir(path)

    except Exception, e:
        logger.error("Erro quando o usuário %s tentou criar o diretório: %s no Git" % (
            user.get_username(), path+folder))
        logger.error(e)
        raise GITCommandError(e)


def script_template(environment_logical, divison_dc, group_l3, template_name):
    '''Validates that can use a script to create the ACL.

    :param environment_logical: environment logical
    :param divison_dc: divison dc
    :param group_l3: group l3
    :param template_name: Template name
    '''
    script = False

    if template_name:
        script = True
    else:
        if divison_dc == DIVISON_DC.FE:

            if environment_logical == ENVIRONMENT_LOGICAL.APLICATIVOS or environment_logical == ENVIRONMENT_LOGICAL.PORTAL or environment_logical == ENVIRONMENT_LOGICAL.HOMOLOGACAO:

                if group_l3 == "CORE/DENSIDADE":

                    script = True

        elif divison_dc == DIVISON_DC.BE:

            if environment_logical == ENVIRONMENT_LOGICAL.PRODUCAO or environment_logical == ENVIRONMENT_LOGICAL.HOMOLOGACAO:

                if group_l3 == "CORE/DENSIDADE":

                    script = True

    return script


def chdir(type_path, network, path=None):
    '''Change the current working directory to path.

    :param type_path: type path
    :param network: v4 or v6
    :param path: path

    :raise GITCommandError:  Failed to execute command
    '''
    try:

        if type_path == PATH_TYPES.ACL:
            path = "%s%s/%s" % (PATH_ACL, network, path)

        elif type_path == PATH_TYPES.TEMPLATE:
            path = "%s%s/%s" % (PATH_ACL, network, PATH_ACL_TEMPLATES)

        os.chdir(path)

    except Exception, e:
        logger.error(e)
        raise Exception(e)


def check_name_file(acl_file_name, extention=True):
    '''Validates the filename do acl has point and space and adds extension

    :param acl_file_name: name is validaded
    :param extention: True case add extention
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

    :param acl_file_name: name is validaded
    '''
    acl = ""
    for caracter in acl_file_name:
        if ((caracter == ".") or (caracter == " ")):
            pass
        else:
            acl += caracter

    return acl + "_bkp_" + strftime("%Y%m%d%H%M%S") + EXTENTION_FILE


def path_acl(environment_logical, divison_dc, acl_path=None):
    '''Creates the path depending on the parameters of environment

    :param environment_logical: environment logical
    :param divison_dc: divison dc
    '''
    path = divison_dc

    if environment_logical == ENVIRONMENT_LOGICAL.HOMOLOGACAO:

        if divison_dc == DIVISON_DC.FE:
            path = DIVISON_DC.DEV_QA_FE

        else:
            path = DIVISON_DC.DEV_QA

    elif environment_logical == ENVIRONMENT_LOGICAL.PRODUCAO:

        if divison_dc == replace_to_correct(DIVISON_DC.BE_POP_SP):
            path = replace_to_correct(DIVISON_DC.BE_POP_SP)

        elif divison_dc == replace_to_correct(DIVISON_DC.FE_POP_SP):
            path = replace_to_correct(DIVISON_DC.FE_POP_SP)

    elif environment_logical == ENVIRONMENT_LOGICAL.BORDA:

        if divison_dc == replace_to_correct(DIVISON_DC.BORDA_POP_SP):
            path = replace_to_correct(DIVISON_DC.BORDA_POP_SP)
        else:
            path = divison_dc

    if path == DIVISON_DC.BORDA:
        path = "Borda"

    if acl_path:
        path = acl_path

    return path


def replace_to_correct(value):
    return value.replace('_', '-')


def checkAclGit(acl_file_name, environment, network, user):
    '''Validates if the file is created acl.

    :param acl_file_name: acl name
    :param environment: Environment
    :param network: v4 or v6
    :param user: user

    :raise GITCommandError:  Failed to execute command

    :return: True case created
    '''
    try:
        acl = check_name_file(acl_file_name)

        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"],
                        environment["acl_path"])

        mkdir_divison_dc(
            environment["nome_divisao"], user, environment["acl_path"])

        chdir(PATH_TYPES.ACL, network, path)

        Git.synchronization()

        return os.path.exists(acl)

    except (GITCommandError, Exception), e:
        logger.error(
            "Erro quando o usuário %s tentou sincronizar no Git" % (user.get_username()))
        logger.error(e)
        raise GITCommandError(e)


def getAclGit(acl_file_name, environment, network, user):
    '''Retrieves the contents of the file acl.

    :param acl_file_name: acl name
    :param environment: Environment
    :param network: v4 or v6
    :param user: user

    :raise GITCommandError:  Failed to execute command
    '''
    try:

        acl = check_name_file(acl_file_name)

        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"],
                        environment["acl_path"])

        mkdir_divison_dc(
            environment["nome_divisao"], user, environment["acl_path"])

        chdir(PATH_TYPES.ACL, network, path)

        Git.synchronization()

        content = File.read(acl)

        return content

    except (GITCommandError, FileError, Exception), e:
        logger.error(
            "Erro quando o usuário %s tentou sincronizar no Git" % (user.get_username()))
        logger.error(e)
        raise GITCommandError(e)


def alterAclGit(acl_name, acl_content, environment, comment, network, user):
    '''Change the contents of the file acl.

    :param acl_name: acl name
    :param acl_content: acl content
    :param environment: Environment
    :param comment: comments of user
    :param network: v4 or v6
    :param user: user

    :raise GITCommandError:  Failed to execute command
    '''
    try:

        acl = check_name_file(acl_name)

        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"],
                        environment["acl_path"])

        chdir(PATH_TYPES.ACL, network, path)

        Git.synchronization()

        File.write(acl, acl_content)

        Git.commit(acl, "%s comentou: %s" % (user.get_username(), comment))
        Git.push()

        logger.info("%s alterou no GIT o arquivo: %s Comentário do Usuário: %s" % (
            user.get_username(), (path + acl), comment))

    except (GITCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou atualizar o arquivo: %s no Git" % (
            user.get_username(), (path + acl)))
        logger.error(e)
        raise GITCommandError(e)


def createAclGit(acl_name, environment, network, user):
    '''Create the file acl.

    :param acl_name: acl name
    :param environment: Environment
    :param network: v4 or v6
    :param user: user

    :raise GITCommandError:  Failed to execute command
    '''
    try:

        acl = check_name_file(acl_name)

        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"],
                        environment["acl_path"])

        mkdir_divison_dc(
            environment["nome_divisao"], user, environment["acl_path"])

        chdir(PATH_TYPES.ACL, network, path)

        Git.synchronization()

        File.create(acl)

        Git.add(acl)

        Git.commit(acl, "Criação do Arquivo %s pelo usuário: %s" %
                   (acl, user.get_username()))
        Git.push()

        logger.info("%s criou no GIT o arquivo: %s" %
                    (user.get_username(), (path + acl)))

    except (GITCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou criar o arquivo: %s no Git" % (
            user.get_username(), (path + acl)))
        logger.error(e)
        raise GITCommandError(e)


def deleteAclGit(acl_name, environment, network, user):
    '''Delete acl file

    :param acl_name: acl name
    :param environment: Environment
    :param network: v4 or v6
    :param user: user

    :raise GITCommandError:  Failed to execute command
    '''
    try:
        acl = check_name_file(acl_name)

        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"],
                        environment["acl_path"])

        os.chdir(PATH_ACL)

        Git.synchronization()

        path_to_acl = "%s/%s/%s" % (network, path, acl)
        Git.remove(path_to_acl)

        Git.commit(path_to_acl, "Exclusão do Arquivo %s pelo usuário:%s" %
                   (acl, user.get_username()))

        Git.push()

        logger.info("%s excluiu no GIT o arquivo: %s" %
                    (user.get_username(), (path + acl)))

    except (GITCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou excluiu o arquivo: %s no Git" % (
            user.get_username(), (path + acl)))
        logger.error(e)
        raise GITCommandError(e)


def applyAcl(equipments, vlan, environment, network, user):
    '''Apply the file acl in equipments

    :param equipments: list of equipments
    :param vlan: Vvlan
    :param environment: Environment
    :param network: v4 or v6
    :param user: user

    :raise Exception: Failed to apply acl

    :return: True case Apply and sysout of script
    '''
    try:

        key_acl = 'acl_file_name' if network == NETWORK_TYPES.v4 else 'acl_file_name_v6'

        acl = check_name_file(vlan[key_acl])

        path = path_acl(environment["nome_ambiente_logico"], environment["nome_divisao"],
                        environment["acl_path"])

        if path == DIVISON_DC.BORDA:
            path = "Borda"

        name_equipaments = ""
        for equip in equipments:

            if not equip in name_equipaments:

                if equip == equipments[0].get("equipamento").get("nome"):
                    name_equipaments += "%s" % equip
                else:
                    name_equipaments += ",%s" % equip

        (erro, result) = commands.getstatusoutput(
            "/usr/bin/backuper -T acl -b %s/%s -e -i %s" % (path, acl, name_equipaments))

        if erro:
            logger.error("Erro quando o usuário %s tentou aplicar ACL %s no equipamentos: %s erro: %s" % (
                user.get_username(), acl, equipments, result))
            return False, result

        for equip in equipments:
            logger.info("%s aplicou a ACL %s no Equipamento:%s" %
                        (user.get_username(), acl, equip))

        return True, result

    except Exception, e:
        logger.error("Erro quando o usuário %s tentou aplicar ACL %s no equipamentos: %s" % (
            user.get_username(), acl, equipments))
        logger.error(e)
        raise Exception(e)


def scriptAclGit(acl_name, vlan, environment, network, user, template_name):
    '''Generates the acl based on a template

    :param acl_name: acl name
    :param vlan: Vvlan
    :param environment: Environment
    :param network: v4 or v6
    :param user: user
    :param temple_name: Template Name

    :raise GITCommandError:  Failed to execute command
    '''
    try:

        acl = check_name_file(acl_name)
        acl_name = check_name_file(acl_name, extention=False)

        if template_name:

            path_env = environment['acl_path'] if environment[
                'acl_path'] else environment['nome_divisao']

            chdir(PATH_TYPES.ACL, network, path_env)

            Git.synchronization()

            arquivo = open("./%s" % acl, "w")

            chdir(PATH_TYPES.TEMPLATE, network)

            file_template = open(template_name, "r")

            content_template = file_template.read()

            nova_acl = replace_template(
                acl_name, vlan, content_template, network)

            chdir(PATH_TYPES.ACL, network, path_env)

            arquivo.write("%s" % nova_acl)
            arquivo.close()
            file_template.close()

            Git.commit(acl, "%s gerou Script para a acl %s" %
                       (user.get_username(), acl))
            Git.push()

            logger.info("%s alterou no GIT o arquivo: %s" %
                        (user.get_username(), acl))

        else:
            if ((environment["nome_divisao"] == "BE") and (environment["nome_ambiente_logico"] == "PRODUCAO") and (environment["nome_grupo_l3"] == "CORE/DENSIDADE")):

                path_env = environment['acl_path'] if environment[
                    'acl_path'] else DIVISON_DC.BE

                chdir(PATH_TYPES.ACL, network, path_env)

                Git.synchronization()

                arquivo = open("./%s" % acl, "w")

                chdir(PATH_TYPES.TEMPLATE, network)

                file_template = open(
                    PREFIX_TEMPLATES + TEMPLATES.BE + EXTENTION_FILE, "r")

                content_template = file_template.read()

                nova_acl = replace_template(
                    acl_name, vlan, content_template, network)

                chdir(PATH_TYPES.ACL, network, path_env)

                arquivo.write("%s" % nova_acl)
                arquivo.close()
                file_template.close()

                Git.commit(acl, "%s gerou Script para a acl %s" %
                           (user.get_username(), acl))
                Git.push()

                logger.info("%s alterou no GIT o arquivo: %s" %
                            (user.get_username(), acl))

            if ((environment["nome_divisao"] == DIVISON_DC.FE) and (environment["nome_ambiente_logico"] == ENVIRONMENT_LOGICAL.HOMOLOGACAO) and (environment["nome_grupo_l3"] == "CORE/DENSIDADE")):

                path_env = environment['acl_path'] if environment[
                    'acl_path'] else DIVISON_DC.DEV_QA_FE

                chdir(PATH_TYPES.ACL, network, path_env)

                Git.synchronization()

                arquivo = open("./%s" % acl, "w")

                chdir(PATH_TYPES.TEMPLATE, network)

                file_template = open(
                    PREFIX_TEMPLATES + TEMPLATES.FE_DEV_QA + EXTENTION_FILE, "r")

                content_template = file_template.read()

                nova_acl = replace_template(
                    acl_name, vlan, content_template, network)

                chdir(PATH_TYPES.ACL, network, path_env)

                arquivo.write("%s" % nova_acl)
                arquivo.close()
                file_template.close()

                Git.commit(acl, "%s gerou Script para a acl %s" %
                           (user.get_username(), acl))
                Git.push()

                logger.info("%s alterou no GIT o arquivo: %s" %
                            (user.get_username(), acl))

            if ((environment["nome_divisao"] == DIVISON_DC.FE) and (environment["nome_ambiente_logico"] == ENVIRONMENT_LOGICAL.PORTAL) and (environment["nome_grupo_l3"] == "CORE/DENSIDADE")):

                path_env = environment['acl_path'] if environment[
                    'acl_path'] else DIVISON_DC.FE

                chdir(PATH_TYPES.ACL, network, path_env)

                Git.synchronization()

                arquivo = open("./%s" % acl, "w")

                chdir(PATH_TYPES.TEMPLATE, network)

                if "staging" in acl.lower():
                    file_template = open(
                        PREFIX_TEMPLATES + TEMPLATES.FE_STAGING + EXTENTION_FILE, "r")
                else:
                    file_template = open(
                        PREFIX_TEMPLATES + TEMPLATES.FE_PORTAL + EXTENTION_FILE, "r")

                content_template = file_template.read()

                nova_acl = replace_template(
                    acl_name, vlan, content_template, network)

                chdir(PATH_TYPES.ACL, network, path_env)

                arquivo.write("%s" % nova_acl)
                arquivo.close()
                file_template.close()

                Git.commit(acl, "%s gerou Script para a acl %s" %
                           (user.get_username(), acl))
                Git.push()

                logger.info("%s alterou no GIT o arquivo: %s" %
                            (user.get_username(), acl))

            if ((environment["nome_divisao"] == DIVISON_DC.FE) and (environment["nome_ambiente_logico"] == ENVIRONMENT_LOGICAL.APLICATIVOS) and (environment["nome_grupo_l3"] == "CORE/DENSIDADE")):

                path_env = environment['acl_path'] if environment[
                    'acl_path'] else DIVISON_DC.FE

                chdir(PATH_TYPES.ACL, network, path_env)

                Git.synchronization()

                arquivo = open("./%s" % acl, "w")

                chdir(PATH_TYPES.TEMPLATE, network)

                file_template = open(
                    PREFIX_TEMPLATES + TEMPLATES.FE_APLICATIVOS + EXTENTION_FILE, "r")

                content_template = file_template.read()

                nova_acl = replace_template(
                    acl_name, vlan, content_template, network)

                chdir(PATH_TYPES.ACL, network, path_env)

                arquivo.write("%s" % nova_acl)
                arquivo.close()
                file_template.close()

                Git.commit(acl, "%s gerou Script para a acl %s" %
                           (user.get_username(), acl))
                Git.push()

                logger.info("%s alterou no GIT o arquivo: %s" %
                            (user.get_username(), acl))

            if ((environment["nome_divisao"] == DIVISON_DC.BE) and (environment["nome_ambiente_logico"] == ENVIRONMENT_LOGICAL.HOMOLOGACAO) and (environment["nome_grupo_l3"] == "CORE/DENSIDADE")):

                path_env = environment['acl_path'] if environment[
                    'acl_path'] else DIVISON_DC.DEV_QA

                chdir(PATH_TYPES.ACL, network, path_env)

                Git.synchronization()

                arquivo = open("./%s" % acl, "w")

                chdir(PATH_TYPES.TEMPLATE, network)

                file_template = open(
                    PREFIX_TEMPLATES + TEMPLATES.BEHO + EXTENTION_FILE, "r")

                content_template = file_template.read()

                nova_acl = replace_template(
                    acl_name, vlan, content_template, network)

                chdir(PATH_TYPES.ACL, network, path_env)

                arquivo.write("%s" % nova_acl)
                arquivo.close()
                file_template.close()

                Git.commit(acl, "%s gerou Script para a acl %s" %
                           (user.get_username(), acl))
                Git.push()

                logger.info("%s alterou no GIT o arquivo: %s" %
                            (user.get_username(), acl))

    except (GITCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou gerar o arquivo: %s no Git" % (
            user.get_username(), acl))
        logger.error(e)
        raise GITCommandError(e)


def parse_template(vlan, network):

    try:

        net = None
        block = None
        wmasc = None
        special_1 = None
        special_2 = None

        if vlan["redeipv4"] is not None and vlan["redeipv4"] != "" and vlan["redeipv4"] and network == NETWORK_TYPES.v4:
            network = vlan["redeipv4"][0]

            net = "%s.%s.%s.%s" % (
                network["oct1"], network["oct2"], network["oct3"], network["oct4"])

            wmasc_1 = int(network["mask_oct1"]) ^ 255
            wmasc_2 = int(network["mask_oct2"]) ^ 255
            wmasc_3 = int(network["mask_oct3"]) ^ 255
            wmasc_4 = int(network["mask_oct4"]) ^ 255

            wmasc = "%s.%s.%s.%s" % (wmasc_1, wmasc_2, wmasc_3, wmasc_4)

            ipEsp_1 = int(network["oct1"]) | wmasc_1
            ipEsp_2 = int(network["oct2"]) | wmasc_2
            ipEsp_3 = int(network["oct3"]) | wmasc_3
            ipEsp_4 = int(network["oct4"]) | wmasc_4

            special_1 = "%s.%s.%s.%s" % (
                ipEsp_1, ipEsp_2, ipEsp_3, (ipEsp_4 - 1))
            special_2 = "%s.%s.%s.%s" % (
                ipEsp_1, ipEsp_2, ipEsp_3, (ipEsp_4 - 2))

            block = "%s" % (network['block'])

        elif vlan["redeipv6"] is not None and vlan["redeipv6"] != "" and vlan["redeipv6"] and network == NETWORK_TYPES.v6:
            network = vlan["redeipv6"][0]

            net = "%s:%s:%s:%s:%s:%s:%s:%s" % (network["block1"], network["block2"], network["block3"], network[
                                               "block4"], network["block5"], network["block6"], network["block7"], network["block8"])

            wmasc_1 = mask_ipv6(network["mask1"])
            wmasc_2 = mask_ipv6(network["mask2"])
            wmasc_3 = mask_ipv6(network["mask3"])
            wmasc_4 = mask_ipv6(network["mask4"])
            wmasc_5 = mask_ipv6(network["mask5"])
            wmasc_6 = mask_ipv6(network["mask6"])
            wmasc_7 = mask_ipv6(network["mask7"])
            wmasc_8 = mask_ipv6(network["mask8"])

            wmasc = "%s:%s:%s:%s:%s:%s:%s:%s" % (
                wmasc_1, wmasc_2, wmasc_3, wmasc_4, wmasc_5, wmasc_6, wmasc_7, wmasc_8)

            ipEsp_1 = block_ipv6(network["block1"], wmasc_1)
            ipEsp_2 = block_ipv6(network["block2"], wmasc_2)
            ipEsp_3 = block_ipv6(network["block3"], wmasc_3)
            ipEsp_4 = block_ipv6(network["block4"], wmasc_4)
            ipEsp_5 = block_ipv6(network["block5"], wmasc_5)
            ipEsp_6 = block_ipv6(network["block6"], wmasc_6)
            ipEsp_7 = block_ipv6(network["block7"], wmasc_7)
            ipEsp_8 = block_ipv6(network["block8"], wmasc_8)

            sp1 = hexa(int(ipEsp_8, 16) - 1)
            sp2 = hexa(int(ipEsp_8, 16) - 2)

            special_1 = "%s:%s:%s:%s:%s:%s:%s:%s" % (
                ipEsp_1, ipEsp_2, ipEsp_3, ipEsp_4, ipEsp_5, ipEsp_6, ipEsp_7, sp1)
            special_2 = "%s:%s:%s:%s:%s:%s:%s:%s" % (
                ipEsp_1, ipEsp_2, ipEsp_3, ipEsp_4, ipEsp_5, ipEsp_6, ipEsp_7, sp2)

            block = "%s" % (network['block'])

        return net, block, wmasc, special_1, special_2

    except Exception, e:
        logger.error(
            "Erro quando realizava parse das variaveis da rede para o replace no template.")
        raise Exception(e)


def replace_template(acl_name, vlan, content_template, network):

    network, block, wmasc, special_1, special_2 = parse_template(vlan, network)

    acl = content_template.replace('%ACL', acl_name)
    acl = acl.replace('%NUMERO', "%s" % (vlan["num_vlan"]))

    if network is not None and block is not None and wmasc is not None and special_1 is not None and special_2 is not None:

        acl = acl.replace('%REDE', network)
        acl = acl.replace('%BLOCO', block)
        acl = acl.replace('%WMASC', wmasc)
        acl = acl.replace('%ESPECIAL1', special_1)
        acl = acl.replace('%ESPECIAL2', special_2)

    return acl


def mask_ipv6(param):
    param = hexa(int(param, 16) ^ int('ffff', 16))
    if param == '0':
        param = '0000'

    return param


def block_ipv6(param, wmasc):
    param = hexa(int(param, 16) | int(wmasc, 16))
    if param == '0':
        param = '0000'

    return param


def get_templates(user, return_as_dict=False):
    """
    Get acl templates for list

    :param user: Instance of current user
    :param return_as_dict: If the method will return a dictionary or a list

    :return: list or dict of templates.

    ::

        list: [{'name': < template_name >, 'network': < template_network >},...]
        dict: {
        "ipv4": [{'name': < template_name >, 'network': < template_network >},...],
        "ipv6": [{'name': < template_name >, 'network': < template_network >},...]
        }

    :raise GITCommandError:  Failed to execute command
    """
    try:
        os.chdir(PATH_ACL)

        Git.synchronization()

        aux = dict()
        aux['ipv4'] = list()
        aux['ipv6'] = list()
        templates = list()

        path_v4 = "%s%s/%s" % (PATH_ACL,
                               IP_VERSION.IPv4[0], PATH_ACL_TEMPLATES)
        path_v6 = "%s%s/%s" % (PATH_ACL,
                               IP_VERSION.IPv6[0], PATH_ACL_TEMPLATES)

        if os.path.isdir(path_v4):
            templates += [{'name': f, 'network': IP_VERSION.IPv4[1]}
                          for f in listdir(path_v4) if isfile(join(path_v4, f))]
            if return_as_dict:
                aux['ipv4'] = templates
                templates = []

        if os.path.isdir(path_v6):
            templates += [{'name': f, 'network': IP_VERSION.IPv6[1]}
                          for f in listdir(path_v6) if isfile(join(path_v6, f))]
            if return_as_dict:
                aux['ipv6'] = templates
                templates = []

        templates = aux if return_as_dict else templates

        return templates

    except (GITCommandError, FileError, Exception), e:
        logger.error(
            "Erro quando o usuário %s tentou sincronizar no Git" % (user.get_username()))
        logger.error(e)
        raise GITCommandError(e)


def get_template_edit(template_name, network, user):
    '''Retrieves the contents of the file template.

    :param template_name: template name
    :param network: IPv4 or IPv6
    :param user: user

    :raise GITCommandError:  Failed to execute command
    '''

    try:
        ip_version = IP_VERSION.IPv4[0] if network == IP_VERSION.IPv4[
            1] else IP_VERSION.IPv6[0]
        path = "%s%s/%s%s" % (PATH_ACL, ip_version,
                              PATH_ACL_TEMPLATES, template_name)

        chdir(PATH_TYPES.TEMPLATE, ip_version, path)

        Git.synchronization()

        content = File.read(template_name)

        return content

    except (GITCommandError, FileError, Exception), e:
        logger.error(
            "Erro quando o usuário %s tentou sincronizar no Git" % (user.get_username()))
        logger.error(e)
        raise GITCommandError(e)


def alter_template(template_name, network, content, user):
    '''Change the contents of the file acl.

    :param template_name: template name
    :param network: IPv4 or IPv6
    :param content: content
    :param user: user

    :raise GITCommandError:  Failed to execute command
    '''

    try:
        ip_version = IP_VERSION.IPv4[0] if network == IP_VERSION.IPv4[
            1] else IP_VERSION.IPv6[0]

        path = "%s%s/%s%s" % (PATH_ACL, ip_version,
                              PATH_ACL_TEMPLATES, template_name)

        chdir(PATH_TYPES.TEMPLATE, ip_version, path)

        Git.synchronization()

        File.write(template_name, content)

        Git.commit(template_name, "%s alterou o arquivo %s" %
                   (user.get_username(), template_name))
        Git.push()

        logger.info("%s alterou no GIT o arquivo: %s" %
                    (user.get_username(), (path + template_name)))

    except (GITCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou atualizar o arquivo: %s no Git" % (
            user.get_username(), (path + template_name)))
        logger.error(e)
        raise GITCommandError(e)


def create_template(template_name, network, content, user):
    '''Create the file template.

    :param template_name: template name
    :param network: IPv4 or IPv6
    :param content: content
    :param user: user

    :raise GITCommandError:  Failed to execute command
    '''
    try:

        ip_version = IP_VERSION.IPv4[0] if network == IP_VERSION.IPv4[
            1] else IP_VERSION.IPv6[0]

        path = "%s%s/%s%s" % (PATH_ACL, ip_version,
                              PATH_ACL_TEMPLATES, template_name)

        chdir(PATH_TYPES.TEMPLATE, ip_version, path)

        Git.synchronization()

        File.create(template_name)

        Git.add(template_name)

        Git.commit(template_name, "Criação do Arquivo %s pelo usuário: %s" % (
            template_name, user.get_username()))
        Git.push()

        logger.info("%s criou no GIT o arquivo: %s" %
                    (user.get_username(), (path + template_name)))

        alter_template(template_name, network, content, user)

    except (GITCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou criar o arquivo: %s no Git" % (
            user.get_username(), (path + template_name)))
        logger.error(e)
        raise GITCommandError(e)


def check_template(template_name, network, user):
    '''Validates if the file is created template.

    :param template_name: template name
    :param network: IPv4 or IPv6
    :param user: user

    :raise GITCommandError:  Failed to execute command

    :return: True case created
    '''
    try:

        ip_version = IP_VERSION.IPv4[0] if network == IP_VERSION.IPv4[
            1] else IP_VERSION.IPv6[0]

        path = "%s%s/%s%s" % (PATH_ACL, ip_version,
                              PATH_ACL_TEMPLATES, template_name)

        path_net_version = "%s%s" % (PATH_ACL, ip_version)

        if not os.path.isdir(path_net_version + PATH_ACL_TEMPLATES):

            os.chdir(path_net_version)
            os.mkdir('templates')
            Git.add('templates')
            Git.commit('templates', "Criação ")
            Git.push()

        chdir(PATH_TYPES.TEMPLATE, ip_version, path)

        Git.synchronization()

        File.read(template_name)

        return True

    except FileError, e:
        return False

    except (GITCommandError, Exception), e:
        logger.error(
            "Erro quando o usuário %s tentou sincronizar no Git" % (user.get_username()))
        logger.error(e)
        raise GITCommandError(e)


def delete_template(template_name, network, user):
    '''Delete template file

    :param template_name: template name
    :param network: IPv4 or IPv6
    :param user: user

    :raise GITCommandError:  Failed to execute command
    '''
    try:

        ip_version = IP_VERSION.IPv4[0] if network == IP_VERSION.IPv4[
            1] else IP_VERSION.IPv6[0]

        path = "%s%s/%s%s" % (PATH_ACL, ip_version,
                              PATH_ACL_TEMPLATES, template_name)

        chdir(PATH_TYPES.TEMPLATE, ip_version, path)

        Git.synchronization()

        File.remove(template_name)

        Git.remove(template_name)

        Git.commit(template_name, "Exclusão do Arquivo %s pelo usuário:%s" % (
            template_name, user.get_username()))

        Git.push()

        logger.info("%s excluiu no GIT o arquivo: %s" %
                    (user.get_username(), (path + template_name)))

    except (GITCommandError, FileError, Exception), e:
        logger.error("Erro quando o usuário %s tentou excluiu o arquivo: %s no Git" % (
            user.get_username(), (path + template_name)))
        logger.error(e)
        raise GITCommandError(e)
