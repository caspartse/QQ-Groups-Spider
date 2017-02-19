#!/usr/bin/env python
# -*- coding:utf-8 -*
import os
import sys
app_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(app_root, 'lib'))
from bottle import *
import requests
from time import time, sleep
from random import random
import simplejson as json
import urllib
from io import BytesIO
import pyexcel as pe
import unicodecsv as csv
import re
#import sae


app = Bottle()


@app.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')


class QQGroups(object):
    """QQ Groups Spider"""

    def __init__(self):
        super(QQGroups, self).__init__()
        self.session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Referer': 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=715030901&daid=73&pt_no_auth=1&s_url=http%3A%2F%2Fqqun.qq.com%2Fgroup%2Findex.html%3Fkeyword%3Dtencent',
        }
        self.session.headers.update(headers)
        self.js_ver = '10196'

    def getQRCode(self):
        try:
            url = 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=715030901&daid=73&pt_no_auth=1&s_url=http%3A%2F%2Fqqun.qq.com%2Fgroup%2Findex.html%3Fkeyword%3Dtencent'
            self.session.get(url, timeout=200)
            try:
                pattern = r'ptuiV\("(\d+)"\);'
                self.js_ver = re.search(pattern, resp.content).group(1)
            except:
                pass
            url = 'http://ptlogin2.qq.com/ptqrshow?appid=715030901&e=2&l=M&s=3&d=72&v=4&t=%.17f&daid=73' % (
                random())
            resp = self.session.get(url, timeout=200)
            response.set_header('Content-Type', 'image/png')
            response.add_header('Cache-Control', 'no-cache, no-store')
            response.add_header('Pragma', 'no-cache')
        except:
            resp = None
        return resp

    def qrLogin(self):
        u1 = 'http%3A%2F%2Fqqun.qq.com%2Fgroup%2Findex.html%3Fkeyword%3Dtencent'
        login_sig = self.session.cookies.get_dict().get('pt_login_sig', '')
        qrsig = self.session.cookies.get_dict().get('qrsig', '')
        url = 'http://ptlogin2.qq.com/ptqrlogin?u1=%s&ptqrtoken=%s&ptredirect=1&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-0-%d&js_ver=%s&js_type=1&login_sig=%s&pt_uistyle=40&aid=715030901&daid=73&' % (
            u1,
            self.hash33(qrsig),
            time() * 1000,
            self.js_ver,
            login_sig
        )
        try:
            errorMsg = ''
            resp = self.session.get(url, timeout=200)
            result = resp.content
            if '二维码未失效' in result:
                status = 0
            elif '二维码认证中' in result:
                status = 1
            elif '登录成功' in result:
                status = 2
            elif '二维码已失效' in result:
                status = 3
            else:
                status = 4
                errorMsg = str(result.text)
        except:
            status = -1
            try:
                errorMsg = resp.status_code
            except:
                pass
        loginResult = {
            'status': status,
            'time': time(),
            'errorMsg': errorMsg,
        }
        resp = json.dumps(loginResult)
        response.set_header('Content-Type', 'application/json; charset=UTF-8')
        response.add_header('Cache-Control', 'no-cache; must-revalidate')
        response.add_header('Expires', '-1')
        return resp

    def hash33(self, t):
        e = 0
        for i in xrange(0, len(t)):
            e += (e << 5) + ord(t[i])
        t = (e & 2147483647)
        return str(t)

    def genbkn(self, skey):
        b = 5381
        for i in xrange(0, len(skey)):
            b += (b << 5) + ord(skey[i])
        bkn = (b & 2147483647)
        return str(bkn)

    def qqunSearch(self, request):
        st = request.forms.get('st')
        pn = int(request.forms.get('pn'))
        ft = request.forms.get('ft')
        kw = request.forms.get('kw').strip()
        if not kw:
            redirect('/qqun')
        skey = self.session.cookies.get_dict().get('skey', '')
        groups = [(u'群名称', u'群号', u'群人数', u'群主', u'群简介')]
        try:
            for page in xrange(0, pn):
                # sort type: 1 deafult, 2 menber, 4 active
                url = 'http://qqun.qq.com/cgi-bin/qun_search/search_group?k=%s&t=&c=1&p=%s&n=8&st=%s&d=1&r=%.17f&bkn=%s&s=3&v=0' % (
                    urllib.quote(kw),
                    page,
                    st,
                    random(),
                    self.genbkn(skey)
                )
                resp = self.session.get(url, timeout=100)
                result = resp.json()
                gList = result.get('gList')
                for item in gList:
                    gName = item['gName'].strip()
                    gc = item['gc']
                    gMemNum = item['gMemNum']
                    gOwner = item['gOwner']
                    gIntro = item['gIntro'].strip()
                    gMeta = (gName, gc, gMemNum, gOwner, gIntro)
                    groups.append(gMeta)
                sleep(2.5)
        except Exception, e:
            # return e
            if len(groups) == 1:
                redirect('/qqun')
        f = BytesIO()
        if ft == 'xls':
            sheet = pe.Sheet(groups)
            f = sheet.save_to_memory('xls', f)
            response.set_header('Content-Type', 'application/vnd.ms-excel')
            filename = kw.replace(' ', '_') + '.xls'
            response.add_header('Content-Disposition',
                                'attachment; filename="%s"' % (filename))
            return f.getvalue()
        elif ft == 'csv':
            writer = csv.writer(f, dialect='excel', encoding='utf-8')
            writer.writerows(groups)
            response.set_header('Content-Type', 'text/csv; charset=UTF-8')
            filename = kw.replace(' ', '_') + '.csv'
            response.add_header('Content-Disposition',
                                'attachment; filename="%s"' % (filename)
                                )
            return f.getvalue()
        elif ft == 'xlsx':
            import tempfile
            import xlsxwriter
            filename = kw.replace(' ', '_') + '.xlsx'
            workbook = xlsxwriter.Workbook(
                tempfile.gettempdir() + '/' + filename)
            worksheet = workbook.add_worksheet()
            row = 0
            col = 0
            for gName, gc, gMemNum, gOwner, gIntro in groups:
                worksheet.write(row, col, gName)
                worksheet.write(row, col + 1, gc)
                worksheet.write(row, col + 2, gMemNum)
                worksheet.write(row, col + 3, gOwner)
                worksheet.write(row, col + 4, gIntro)
                row += 1
            workbook.close()
            resp = static_file(
                filename,
                root=tempfile.gettempdir(),
                download=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            return resp


q = QQGroups()


@app.route('/')
def home():
    redirect('/qqun')


@app.route('/qqun', method='ANY')
@view('qqun')
def qqun():
    if request.method == 'GET':
        response.set_header('Content-Type', 'text/html; charset=UTF-8')
        response.add_header('Cache-Control', 'no-cache')
        return
    elif request.method == 'POST':
        return q.qqunSearch(request)


@app.route('/getqrcode')
def getQRCode():
    return q.getQRCode()


@app.route('/qrlogin')
def qrLogin():
    return q.qrLogin()

### Local ###
run(app, server='paste', host='localhost', port=8080, debug=True, reloader=True)
#run(app, host='localhost', port=8080, debug=True, reloader=True)

### SAE ###
# debug(True)
#application = sae.create_wsgi_app(app)
