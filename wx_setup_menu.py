#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import wx_token

SERVER_URL = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s'

def setup_menu(merc, menu):
    token = wx_token.wx_token(merc)
    if token:
        url = SERVER_URL % token 
        req = urllib2.Request(url, data = str(msg))

        e_msg = urllib2.urlopen(req).read()

    return e_msg

if __name__ == '__main__':
    import sys
    m = sys.argv[1]
    u = sys.argv[2]

    with open(u) as f:
        msg = f.read()

    print(setup_menu(m, msg))

