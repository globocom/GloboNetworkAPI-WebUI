# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.conf.urls.defaults import patterns, url
import settings

handler404 = 'CadVlan.Auth.views.handler404'

urlpatterns = patterns('',
    # CSS - JS
    (r'^media/(.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT})
)

# URL's Auth
urlpatterns += patterns('CadVlan.Auth.views',
    url('^$', 'login', name='',),
    url('^login$', 'login', name='login',),
    url('^logout$', 'logout', name='logout',),
    url('^home$', 'home', name='home',)
)
