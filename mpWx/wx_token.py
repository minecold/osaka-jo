#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wxdb
import urllib2
import json

MERC_DATA = '/srv/www/mp.wx/application/meta/merc_data.json'

def get_mercinfo(merc):
    minfo = json.load(file(MERC_DATA))[merc]

    if minfo:
        return minfo['appid'], minfo['appsecret']

    return None,None
    
def wx_get_atoken(merc):
    appid, secret = get_mercinfo(merc)

    if appid and secret:
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (appid, secret)
        msg = urllib2.urlopen(url).read()
        md = json.loads(msg)

        if 'access_token' in md:
            return md['access_token'],md['expires_in']
        else:
            print(msg)
            return None,None

def wx_set_atoken(merc):
    atoken, etime = wx_get_atoken(merc)

    if atoken and etime:
        db_key = 'merc:' + merc
        db = wxdb.wxdb(db_key)
        db.create_token(atoken, etime)

        return db.get_token()
    else:
        return None

def wx_token(merc):
    db_key = 'merc:' + merc
    db = wxdb.wxdb(db_key)

    token = db.get_token()

    if not token:
        token = wx_set_atoken(merc)

    return token

if __name__ == '__main__':
    import sys
    m = sys.argv[1]
    print(wx_token(m))
