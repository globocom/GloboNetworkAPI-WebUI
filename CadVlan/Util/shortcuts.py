# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.http import HttpResponse
from django.template import loader, RequestContext
from Json import Json
import json

JSON = 'json'

def render_to_response_ajax(*args, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling ajax
    
    return render_to_response_ajax(templates.LOGIN, {'form': form }, context_instance=RequestContext(request))
    
    ou
    
    return render_to_response_ajax( json = Json('', redirect, uri)) 
    
    """
    
    if  kwargs.get(JSON) is None:
        return HttpResponse(loader.render_to_string(*args, **kwargs))
    
    else:
        return HttpResponse(json.dumps(kwargs.get(JSON).__dict__))