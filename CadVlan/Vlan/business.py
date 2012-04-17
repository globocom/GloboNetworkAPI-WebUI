# -*- coding:utf-8 -*-
'''
Created on Apr 3, 2012

@author: tromero
'''

def montaIPRede(listaIPS, ip4 = True):
    '''
    Recebe uma lista com as partes de IPV4 ou IPV6 e os concatena gerando uma unica string com o ip
    @param listaIPS - lista com os ips
    @ip4 - padrao true, para diferenciar se é uma lista com ip4 ou ip6
    '''
    
    for item in listaIPS:
        if (ip4):
            item['net_ip_final'] = item.get('oct1')+ "." + item.get('oct2') + "." + item.get('oct3') + "." + item.get('oct4')
            item['mask_ip_final'] = item.get('mask_oct1')+ "." + item.get('mask_oct1') + "." + item.get('mask_oct1') + "." + item.get('mask_oct1')
            item['ip4'] = True
        else:
            item['net_ip_final'] = item.get('block1') + ":" + item.get('block2') + ":" + item.get('block3') + ":" + item.get('block4') + ":" + item.get('block5') + ":" + item.get('block6') + ":" + item.get('block7') + ":" + item.get('block8')
            item['mask_ip_final'] = item.get('mask1') + ":" + item.get('mask2') + ":" + item.get('mask3') + ":" + item.get('mask4') + ":" + item.get('mask5') + ":" + item.get('mask6') + ":" + item.get('mask7') + ":" + item.get('mask8')
            item['ip4'] = False
    return listaIPS
    