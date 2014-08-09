# -*- coding:utf-8 -*-
'''
Created on Jun 25, 2012

@author: tromero
'''


def to_complete_list(user_list, group_list):

    user_list = user_list.get("usuario")
    group_list = user_list.get('grupo')

    if type(user_list) == dict:
        user_list = [user_list]

    if type(group_list) == dict:
        group_list = [group_list]
