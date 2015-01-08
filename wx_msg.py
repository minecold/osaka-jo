#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.dom.minidom as md
import time

import wxdb
import wx_service

rx_tag_list = ['ToUserName', 'FromUserName', 'CreateTime', 'MsgType', 'Content', 'MsgId']
tx_tag_list = ['ToUserName', 'FromUserName', 'CreateTime', 'MsgType']

text_tag_d = {'Content':''}
image_tag_d = {'Image':['MediaId']}
voice_tag_d = {'Voice':['MediaId']}
video_tag_d = {'Video':['MediaId', 'Title', 'Description']}
music_tag_d = {'Music':['Title', 'Description', 'MusicUrl', 'HQMusicUrl', 'ThumbMediaId']}
news_tag_d = {'Articles':{'item':['Title', 'Description', 'PicUrl', 'Url']}}
 
""" location,link can only from request, news can only uesed in response. """
msg_type_list = ['text', 'image', 'voice', 'video', 'location', 'link', 'news']

def wx_msg(merc, msg):
	fd = md.parseString(msg)
	root = fd.documentElement

	rx_dict = {}
	for tag in rx_tag_list:
		node = root.getElementsByTagName(tag)
		try:
			rx_dict[tag] = node[0].childNodes[0].nodeValue
		except IndexError:
			pass

	if rx_dict['Content'] in ['1','2']:
		""" show the member page """
		return wx_msg_news_member(merc,rx_dict)
	else:
		return wx_msg_text(rx_dict)
		#ws.ws_textmsg(merc, rx_dict['FromUserName'], 'service online.')

def wx_msg_text(roger):
	"""
	should check Content
	"""
	gen_dict = {}
	try:
		gen_dict['ToUserName'], gen_dict['FromUserName'] = roger['FromUserName'], roger['ToUserName']
		reply = roger['Content']
	except KeyError:
		return ''

	gen_dict['Content'] = reply
	gen_dict['CreateTime'] = str(int(time.time()))

	gen_dict['MsgType'] = 'text'

	return generate_xml(gen_dict)

def wx_msg_news(roger, title='', desc='', pic='', url=''):
	"""
	should check Content
	"""
	gen_dict = {}
	try:
		gen_dict['ToUserName'], gen_dict['FromUserName'] = roger['FromUserName'], roger['ToUserName']
	except KeyError:
		return ''

	gen_dict['CreateTime'] = str(int(time.time()))

	gen_dict['MsgType'] = 'news'
	gen_dict['ArticleCount'] = '1'
	gen_dict['Title'] = title 
	gen_dict['Description'] = desc
	gen_dict['PicUrl'] = pic 
	gen_dict['Url'] = url

	return generate_xml(gen_dict)

def generate_xml(d):
	impl = md.getDOMImplementation()
	dom = impl.createDocument(None, 'xml', None)
	root = dom.documentElement  

	for key in d:
		"""
		generate common element 
		"""
		if key in tx_tag_list:
			nameE=dom.createElement(key)
			nameT=dom.createCDATASection(d[key])
			nameE.appendChild(nameT)
			root.appendChild(nameE)

	mt = d['MsgType']
	if  mt == 'text':
		content_e = dom.createElement('Content')
		content_e.appendChild(dom.createCDATASection(d['Content']))
		root.appendChild(content_e)
	elif mt == 'news':
		ac_e = dom.createElement('ArticleCount')
		ac_e.appendChild(dom.createCDATASection(d['ArticleCount']))
		root.appendChild(ac_e)

		cnt = int(d['ArticleCount'])
		article_e = dom.createElement('Articles')
		for i in range(cnt):
			item_e = dom.createElement('item')

			i_e = dom.createElement('Title')
			i_d = dom.createCDATASection(d['Title'])
			i_e.appendChild(i_d)
			item_e.appendChild(i_e)

			i_e = dom.createElement('Description')
			i_d = dom.createCDATASection(d['Description'])
			i_e.appendChild(i_d)
			item_e.appendChild(i_e)

			i_e = dom.createElement('PicUrl')
			i_d = dom.createCDATASection(d['PicUrl'])
			i_e.appendChild(i_d)
			item_e.appendChild(i_e)

			i_e = dom.createElement('Url')
			i_d = dom.createCDATASection(d['Url'])
			i_e.appendChild(i_d)
			item_e.appendChild(i_e)

			article_e.appendChild(item_e)
		root.appendChild(article_e)
	else:
		""" FIXME """
		pass
	return dom.toxml(encoding='utf-8')

def wx_msg_news_member(merc, roger):
	title = u'微信VIP会员卡'
	desc = u'点击进入微信会员中心'
	pic = 'http://www.yourdomainname.com/static/img/card_bg01.png'
	url = "http://www.yourdomainname.com/web_pages_r/%s?protocol=user&open_id=%s&action=signup" % (merc, roger['FromUserName'])

	return wx_msg_news(roger, title = title, desc = desc, pic = pic, url = url)
