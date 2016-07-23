#!/usr/bin/env python
# -*- coding:utf-8 -*
import sys

reload(sys)
sys.setdefaultencoding('UTF-8')

import os

app_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(app_root, 'lib'))

import sae
from bottle import *
from uuid import uuid4
import requests
from random import random
import pylibmc
from time import time
import simplejson as json
from io import BytesIO
import pyexcel as pe
import csv


app = Bottle()


@app.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')


@app.route('/qqun')
@view('qqun')
def qqun():
    uid = request.get_cookie('_u')
    if not uid:
        uid = str(uuid4()).replace('-', '')
        expires = time() + 60 * 60 * 24 * 31
        response.set_cookie('_u', uid, expires=expires)
    return


@app.route('/getqrcode')
def getQRCode():
    uid = request.get_cookie('_u')
    uid_session = uid + '_session'
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Referer': 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=715030901&daid=73&pt_no_auth=1&s_url=http%3A%2F%2Fqqun.qq.com%2Fgroup%2Findex.html%3Fkeyword%3Dtencent',
    }
    session.headers.update(headers)
    try:
        url = 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=715030901&daid=73&pt_no_auth=1&s_url=http%3A%2F%2Fqqun.qq.com%2Fgroup%2Findex.html%3Fkeyword%3Dtencent'
        res = session.get(url, timeout=200)
        url = 'http://ptlogin2.qq.com/ptqrshow?appid=715030901&e=2&l=M&s=3&d=72&v=4&t=%.16f&daid=73' % (random())
        res = session.get(url, timeout=200)
        response.set_header('Content-Type', 'image/png')
        response.add_header('Cache-Control', 'no-cache, no-store')
        response.add_header('Pragma', 'no-cache')
        mc = pylibmc.Client()
        mc.set(uid_session, session)
        return res
    except:
        return static_file('img/progress.gif', root='static')


@app.route('/qrlogin')
def qrLogin():
    uid = request.get_cookie('_u')
    uid_session = uid + '_session'
    mc = pylibmc.Client()
    session = mc.get(uid_session)
    u1 = 'http%3A%2F%2Fqqun.qq.com%2Fgroup%2Findex.html%3Fkeyword%3Dtencent'
    timeStamp = time() * 1000
    login_sig = session.cookies.get_dict()['pt_login_sig']
    url = 'http://ptlogin2.qq.com/ptqrlogin?u1=%s&ptredirect=1&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-0-%d&js_ver=10167&js_type=1&login_sig=%s&pt_uistyle=40&aid=715030901&daid=73&' % (u1, timeStamp, login_sig)
    try:
        res = session.get(url, timeout=200)
        result = res.text
        if u'二维码未失效' in result:
            status = 0
        elif u'二维码认证中' in result:
            status = 1
        elif u'登录成功' in result:
            status = 2
        elif u'二维码已失效' in result:
            status = 3
        else:
            status = 4
    except:
        status = -1
    response.set_header('Content-Type', 'application/json; charset=UTF-8')
    mc.set(uid_session, session)
    return json.dumps({'status': status, 'time': time()})


def genbkn(skey):
    b = 5381
    for i in xrange(0, len(skey)):
        b += (b << 5) + ord(skey[i])
    bkn = (b & 2147483647)
    return str(bkn)


@app.route('/qqun', method='POST')
@view('qqun')
def qqunSearch():
    st = request.forms.get('st')
    pn = int(request.forms.get('pn'))
    ft = request.forms.get('ft')
    kw = request.forms.get('kw').strip()
    if not kw:
        redirect('http://yourdomain.com/qqun')
    uid = request.get_cookie('_u')
    uid_session = uid + '_session'
    mc = pylibmc.Client()
    session = mc.get(uid_session)
    skey = session.cookies.get_dict().get('skey')
    groups = [(u'群名称', u'群号', u'群人数', u'群主', u'群简介')]
    try:
        for page in xrange(0, pn):
            url = 'http://qqun.qq.com/cgi-bin/qun_search/search_group?k=%s&t=&c=1&p=%s&n=8&st=%s&d=1&r=%.17f&bkn=%s&s=3&v=0' % (kw, page, st, random(), genbkn(skey))
            res = session.get(url, timeout=100)
            result = res.json()
            gList = result.get('gList')
            for item in gList:
                gName = item['gName'].strip()
                gc = item['gc']
                gMemNum = item['gMemNum']
                gIntro = item['gIntro'].strip()
                gOwner = item['gOwner']
                gData = (gName, gc, gMemNum, gOwner, gIntro)
                groups.append(gData)
            sleep(2.5)
    except:
        if len(groups) == 1:
            redirect('http://yourdomain.com/qqun')
    f = BytesIO()
    if ft == 'xls':
        sheet = pe.Sheet(groups)
        f = sheet.save_to_memory('xls', f)
        response.set_header('Content-Type', 'application/vnd.ms-excel')
        filename = kw.replace(' ', '_') + '.xls'
    else:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(groups)
        response.set_header('Content-Type', 'text/csv; charset=UTF-8')
        filename = kw.replace(' ', '_') + '.csv'
    response.add_header('Content-Disposition', 'attachment; filename="%s"' % (filename))
    return f.getvalue()


debug(True)
application = sae.create_wsgi_app(app)
