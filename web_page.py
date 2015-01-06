#!/usr/bin/env python

import re
import wxdb

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
        else:
            return ''

    def webpage_user(self):
        if self.query['action'] == 'signup':
            open_id = self.query['open_id']
            db = wxdb.wxdb(self.merc, open_id)

            if self.r_method == 'GET':
                """
                generate sign up page for user as they requested
                """
                if db.has_user():
                    return self.page_member(open_id)
                return self.page_signup()
            elif self.r_method == 'POST':
                """
                check user info then commit it in database, return a comfirm page
                """
                f_data = self.env['wsgi.input'].read()
		msg = check_get(f_data)
		try:
			user_name = msg['username']
			telephone = msg['telephone']
			gender = msg['gender']
		except IndexError:
			return self.page_signup()

		if db.has_user() :
			return self.page_member(open_id)
		else:
			re = db.create_user(name = user_name, tel = telephone, gend = gender)
			if re :
				return self.page_member(open_id)
			else:
				return self.page_signup()
            else:
                return ''
        elif self.query['action'] == 'get_card':
            pass

    def page_signup(self):
        fp = PAGE_PATH + 'signup.html'

        with open(fp) as f:
            out = f.read()

        return out

    def page_member(self, open_id):
        fp = PAGE_PATH + 'member.html'
        with open(fp) as f:
            out = f.read()

        return out
