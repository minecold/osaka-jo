#!/usr/bin/env python

import os
import sys

import cert_dev
import wx_msg

import web_page

sys.path.append('/srv/www/mp.wx/application')

os.environ['PYTHON_EGG_CACHE'] = '/srv/www/mp.wx/.python-egg'

def portal(environ, start_response):
    status = '200 OK'
    output = ''

    try:
        prot = environ['PATH_INFO'].split('/')[1]
    except IndexError:
        prot = ''

    if prot == 'wx':
        output = wx_process(environ)
    elif prot == 'web_pages_r':
        output = web_process(environ)
    else:
        """
        protocol not supported.
        """
        pass 

    if output == '':
    	status = '404 NOT FOUND'

    response_headers = [('Content-type', 'text/html'),
                    ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return output

def wx_process(environ):
    output = cert_dev.cert_dev(environ['PATH_INFO'],environ['QUERY_STRING'])
    
    if environ['REQUEST_METHOD'] == 'GET':
        pass
    elif environ['REQUEST_METHOD'] == 'POST':
        if output == 'AUTHED':
                try:
                    merc = environ['PATH_INFO'].split('/')[2]
                except IndexError:
                    return ''

                msg = environ['wsgi.input'].read()
                output = wx_msg.wx_msg(merc,msg)
    else:
        pass

    return output

def web_process(environ):
    try:
        merc = environ['PATH_INFO'].split('/')[2]
    except IndexError:
        return ''
    
    wp = web_page.web_page(merc, environ)
    return wp.webpage_gen()
