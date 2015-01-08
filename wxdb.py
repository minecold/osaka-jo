#!/usr/bin/env python

import redis
import time

merc_list = ['', 'ccss', 'bt8y']

class wxdb:
	def __init__(self, merc='', key=''):
		self.key = key
		if merc in merc_list :
			self.rd = redis.StrictRedis(db=merc_list.index(merc))
		else:
			"""db 0 is THE NULL"""
			self.rd = redis.StrictRedis(db=0)

	def pull(self):
		return str(self.rd.keys())
		
	def has_key(self):
		return self.rd.get(self.key)

	def create_user(self, name, tel, gend):
		info = {}
		info['name'] = name
		info['tel'] = tel
		info['gend'] = gend
		info['date'] = time.strftime("%I:%M:%S-%d/%m/%y:%z")
		
                no = self.rd.dbsize()
                info['number'] = str(no + 68000001)
		self.rd.set(self.key, info)

	def create_token(self, atoken, etime):
		self.rd.set(self.key, atoken)
		self.rd.expire(self.key, int(etime))

	def get_token(self):
		return self.rd.get(self.key)

	def get_user(self):
		return self.rd.get(self.key)
