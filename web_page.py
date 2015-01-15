#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ast
import urllib

import wxdb

import merc_data

# It's better to set the absolutely sys path
PAGE_PATH = '/srv/www/mp.wx/web_pages/'

def check_get(data):
    d={}
    for pair in re.split(r'&', data):
        kv = re.split(r'=', pair)
        if len(kv) == 2:
            d[kv[0]] = kv[1]

    return d

class web_page:
    """
    the URI requested should be formated as one of
    '/web_page_r/merc?protocol=x&open_id=x&action=x&show_me=x&source=x&stage=x'
    """
    def __init__(self, merc, env):
        self.merc = merc
        self.query = check_get(env['QUERY_STRING'])
	self.r_method = env['REQUEST_METHOD']
	self.env = env

    def webpage_gen(self):
        if self.query['protocol'] == 'user':
            return self.webpage_user()
        elif self.query['protocol'] == 'merc':
            return self.webpage_merc()
        else:
            return ''

    def webpage_user(self):
        if self.query['action'] == 'signup':
            open_id = self.query['open_id']
            db_key = "%s:%s" % ('user', open_id)
            db = wxdb.wxdb(self.merc, db_key)

            if self.r_method == 'GET':
                """
                generate sign up page for user as they requested
                """
                if db.has_key():
                    return self.page_member(db_key)
                return self.page_signup()
            elif self.r_method == 'POST':
                """
                check user info then commit it in database, return a comfirm page
                """
                f_data = self.env['wsgi.input'].read()
		msg = check_get(f_data)
		try:
			user_name = urllib.unquote(msg['username']).decode('utf-8')
			telephone = msg['telephone']
			gender = msg['gender']
		except IndexError:
			return '0'

		if db.has_key() :
			return '1'
		else:
			db.create_user(name = user_name, tel = telephone, gend = gender)
			return '1'
            else:
                return '1'
        elif self.query['action'] == 'get_card':
            pass

    def webpage_merc(self):
        if self.query['action'] == 'reserv':
            return self.page_reserv()
        else:
            return ''

    def page_signup(self):
        fp = PAGE_PATH + 'signup.html'

        with open(fp) as f:
            out = f.read()

        return out

    def page_member(self, key):
        fp = PAGE_PATH + 'member.html'
        with open(fp) as f:
            out = f.read()

        try:
            minfo = merc_data.merc[self.merc]
        except KeyError:
            return ''

        db = wxdb.wxdb(self.merc, key)
        uinfo = ast.literal_eval(db.get_user())

        name = minfo['name']
        uname = name.encode("utf-8")

        out = out.replace('[[memid]]', uinfo['number'])
        out = out.replace('[[name]]', uname)
        out = out.replace('[[tel]]', minfo['tel'])
        out = out.replace('[[loc]]', minfo['loc'])

        return out

    def page_reserv(self):
        fp = PAGE_PATH + 'reservation.html'
        with open(fp) as f:
            out = f.read()

        return out
