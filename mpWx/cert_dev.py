#!/usr/bin/env python

import hashlib
import re

def cert_dev(path, query_str):
	paras_get = check_get(query_str)

	try:
		s = paras_get['signature']
		t = paras_get['timestamp']
		n = paras_get['nonce']
	except KeyError:
		return ''

	token = path.replace('/', '')

	listp = [token, t, n]
	listp.sort()

	sha1 = hashlib.sha1()
	map(sha1.update, listp)
	hcode = sha1.hexdigest()

	if hcode == s:
		if 'echostr' in paras_get.keys():
			"""
			first time auth.
			"""
			return paras_get['echostr']
		else:
			return 'AUTHED'
	else:
		return ''

def check_get(data):
	d={}
	for pair in re.split(r'&', data):
		kv = re.split(r'=', pair)
		if len(kv) == 2:
			d[kv[0]] = kv[1]

	return d
