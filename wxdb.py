#!/usr/bin/env python

import redis
import time

merc_list = ['', 'ccss', 'bt8y']

class wxdb:
	def __init__(self, merc, open_id):
		self.user = "%s:%s" % ('user', open_id)
		if merc in merc_list :
			self.rd = redis.StrictRedis(db=merc_list.index(merc))
		else:
			"""db 0 is THE NULL"""
			self.rd = redis.StrictRedis(db=0)

	def pull(self):
		return str(self.rd.keys())
		
	def has_user(self):
		return self.rd.get(self.user)

	def create_user(self, name, tel, gend):
		info = {}
		info['name'] = name
		info['tel'] = tel
		info['gend'] = gend
		info['date'] = time.strftime("%I:%M:%S-%d/%m/%y:%z")
		
		self.rd.set(self.user, info)
