#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import wx_token

SERVER_URL = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s'

def ws_textmsg(merc, touser, content):
    msg = {}

    msg['touser'] = touser
    msg['type'] = 'text'
    msg['text'] = {'content':content}

    token = wx_token.ws_get_atoken(merc)
    if token:
        url = SERVER_URL % token 
        req = urllib2.Request(url, data = str(msg))

        token = urllib2.urlopen(req).read()

    return token

