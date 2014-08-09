# -*- coding:utf-8 -*-
'''
Created on 23/07/2012
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from CadVlan.messages import equipment_type_messages
from CadVlan.templates import EQUIPMENTTYPE_FORM
import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.EquipmentType.forms import TipoEquipamentoForm

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{'permission': EQUIPMENT_MANAGEMENT, "write": True}])
def equipment_type_form(request):

    lists = dict()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        if request.method == 'POST':

            form = TipoEquipamentoForm(request.POST)
            lists['form'] = form

            if form.is_valid():

                nome = form.cleaned_data['nome']

                client.create_tipo_equipamento().inserir(nome)

                messages.add_message(
                    request, messages.SUCCESS, equipment_type_messages.get('success_create'))

                lists['form'] = TipoEquipamentoForm()

        # GET METHOD
        else:
            lists['form'] = TipoEquipamentoForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(EQUIPMENTTYPE_FORM, lists, context_instance=RequestContext(request))
