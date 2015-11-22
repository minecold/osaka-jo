#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.dom.minidom as md
import time
import ast
import urllib
import json
from mstranslator import Translator
import requests

import wxdb

import wx_service
import wx_token

rx_tag_list_full = ['ToUserName', 'FromUserName', 'CreateTime', 'MsgType', 'Content', 'MsgId', 'Event', 'EventKey']
rx_tag_list = ['ToUserName', 'FromUserName', 'CreateTime', 'MsgType', 'Content', 'MediaId']
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

        """
        try:
            if rx_dict['Event'] == 'CLICK':
                if rx_dict['EventKey'] == 'member':
                    return wx_msg_news_member(merc, rx_dict)

        except KeyError:
            pass
        """
        try:
            if rx_dict['MsgType'] == 'text':
	        if rx_dict['Content'] in ['1','2','8']:
	    	    """ show the member page """
	    	    return wx_msg_news_member(merc,rx_dict)
                else:
	            return wx_msg_text(rx_dict)
            elif rx_dict['MsgType'] == 'voice':
                return wx_msg_voice(rx_dict, merc)
            else:
                return;
		#ws.ws_textmsg(merc, rx_dict['FromUserName'], 'service online.')
        except KeyError:
            pass

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

        if reply[0] == '?':
            r = requests.get('http://www.microsofttranslator.com/dictionary.ashx?from=en&to=zh-CHS&text=%s' % (reply[1:]))
            reply = urllib.unquote(r.text.encode('utf-8')).decode('utf-8')
            reply = reply.replace('(decodeURIComponent("', '')
            reply = reply.replace('<span class="dictB">', '<*>')
            reply = reply.replace('</span>', '')
            reply = reply.replace('<br />', '\n')
        elif reply[0] == '!':
            translator = Translator('kylewang', 'R9nZ+mKTzSfFsB2nC2q+Owh1iRTuYaVAGiUXB9xlDmQ=')
            de = translator.detect_lang(reply)
            re = translator.speak(reply[1:], de)
            with open('/srv/www/mp.wx/web_pages/static/t/tmp.mp3', 'wb') as fd:
                fd.write(re)
            reply = 'http://wx-1196398119.ap-southeast-1.elb.amazonaws.com/static/t/tmp.mp3'
        else:

            translator = Translator('kylewang', 'R9nZ+mKTzSfFsB2nC2q+Owh1iRTuYaVAGiUXB9xlDmQ=')
            de = translator.detect_lang(reply)
            if de == 'en':
                des = 'zh'
            else:
                des = 'en'
            re = translator.get_translations(reply, de, des, 8)
            if len(re) > 0:
                jj = json.loads(json.dumps(re))
                for it in jj['Translations']:
                    reply = reply + '\n' + it['TranslatedText'] + '\t[' + str(it['MatchDegree']) + ']'
	gen_dict['Content'] = reply
	gen_dict['CreateTime'] = str(int(time.time()))

	#gen_dict['MsgType'] = 'transfer_customer_service'
	gen_dict['MsgType'] = 'text'

	return generate_xml(gen_dict)


def wx_msg_voice(roger, merc):
	"""
	should check Content
	"""
	gen_dict = {}
	try:
		gen_dict['ToUserName'], gen_dict['FromUserName'] = roger['FromUserName'], roger['ToUserName']
		reply = roger['MediaId']
	except KeyError:
		return ''

        access = wx_token.wx_token(merc)
        gen_dict['Content'] = 'http://file.api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s'%(access, reply)
	gen_dict['CreateTime'] = str(int(time.time()))

	#gen_dict['MsgType'] = 'transfer_customer_service'
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

        db = wxdb.wxdb(merc = merc, key = 'user:'+roger['FromUserName'])
        if db.has_key():
            uinfo = ast.literal_eval(db.get_user())
            uname = uinfo['name']
            gen = uinfo['gend']
            if gen == '1':
                desc = '%s %s\n%s' % (uname,u'先生，您好！', desc)
            elif gen == '2':
                desc = '%s %s\n%s' % (uname, u'女士 您好！', desc)
        else:
            desc = '%s' % (u'您还没有注册哦，点击马上注册吧！')


	return wx_msg_news(roger, title = title, desc = desc, pic = pic, url = url)
