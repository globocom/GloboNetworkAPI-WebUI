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

from CadVlan.Util.Decorators import cache_function
from CadVlan.settings import CACHE_EQUIPMENTS_TIMEOUT


@cache_function(CACHE_EQUIPMENTS_TIMEOUT)
def cache_list_equipment(equipment):
    equipments = equipment.list_all()
    elist = dict()
    elist["list"] = equipments["equipamentos"]
    return elist

@cache_function(CACHE_EQUIPMENTS_TIMEOUT)
def cache_equipment_list(equipment):
    equipment_list = dict(list=equipment)
    return equipment_list

@cache_function(CACHE_EQUIPMENTS_TIMEOUT)
def cache_list_equipment_all(equipment):
    equipments = equipment.get_all()
    return equipments["equipamentos"]


def get_group_by_id(grupos, id_grupo):

    for grupo in grupos:
        if grupo['id'] == id_grupo:
            return grupo

    return None


def get_ambiente_by_id(ambientes, id_ambiente):

    for ambiente in ambientes:
        if ambiente['id'] == id_ambiente:
            return ambiente

    return None


def list_users(user):
    users = user.listar()
    ulist = dict()
    ulist["list_from_model"] = users["usuario"]
    user_list = []

    for list in ulist["list_from_model"]:
        user_list.append(str(list['nome']) + ' - ' + str(list['user']))

    ulist['list'] = user_list
    return ulist
