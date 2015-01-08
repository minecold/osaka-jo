#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wxdb
import urllib2

def get_mercinfo(merc):
    with open('./merc.data') as f:
        for line in f.readline():
            if merc in line:
                return list(line)[1], list(line)[2]

    return None,None
    
def ws_get_atoken(merc):
    appid, secret = get_mercinfo(merc)

    if appid and secret:
        client_c = 'wx' + merc
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=%s&appid=%s&secret=%s" % (client_c, appid, secret)
        msg = urllib2.urlopen(url).read()
        md = dict(msg)

        if 'access_token' in md:
            return md['access_token'],md['expires_in']
        else:
            return None,None

def ws_set_atoken(merc):
    atoken, etime = ws_get_atoken(merc)

    if atoken and etime:
        db_key = 'merc:' + merc
        db = wxdb.wxdb(db_key)
        db.create_token(atoken, etime)

        return db.get_token()
    else:
        return None

def ws_get_atoken(merc):
    db_key = 'merc:' + merc
    db = wxdb.wxdb(db_key)

    token = db.get_token()

    if not token:
        token = ws_set_atoken(merc)

    return token

