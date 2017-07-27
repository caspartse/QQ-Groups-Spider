#!/usr/bin/env python
# -*- coding:utf-8 -*
import os
import sys
app_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(app_root, 'vendor'))
from bottle import *
import requests
from time import time, sleep
from random import random
import simplejson as json
from io import BytesIO
import pyexcel as pe
import unicodecsv as csv
import re
#import sae


class QQGroups(object):
    """QQ Groups Spider"""

    def __init__(self):
        super(QQGroups, self).__init__()
        self.js_ver = '10226'
        self.newSession()

    def newSession(self):
        self.sess = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.59 QQ/8.9.3.21169 Safari/537.36'
        }
        self.sess.headers.update(headers)
        return

    def getQRCode(self):
        self.newSession()
        try:
            url = 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=715030901&daid=73&pt_no_auth=1&s_url=http%3A%2F%2Ffind.qq.com%2Findex.html%3Fversion%3D1%26im_version%3D5533%26width%3D910%26height%3D610%26search_target%3D0'
            resp = self.sess.get(url, timeout=1000)
            pattern = r'imgcache\.qq\.com/ptlogin/ver/(\d+)/js'
            try:
                self.js_ver = re.search(pattern, resp.content).group(1)
            except:
                pass
            self.sess.headers.update({'Referer': url})
            url = 'http://ptlogin2.qq.com/ptqrshow'
            params = {
                'appid': '715030901',
                'e': '2',
                'l': 'M',
                's': '3',
                'd': '72',
                'v': '4',
                't': '%.17f' % (random()),
                'daid': '73'
            }
            resp = self.sess.get(url, params=params, timeout=1000)
            response.set_header('Content-Type', 'image/png')
            response.add_header('Cache-Control', 'no-cache, no-store')
            response.add_header('Pragma', 'no-cache')
        except:
            resp = None
        return resp

    def qrLogin(self):
        login_sig = self.sess.cookies.get_dict().get('pt_login_sig', '')
        qrsig = self.sess.cookies.get_dict().get('qrsig', '')
        status = -1
        errorMsg = ''
        if all([login_sig, qrsig]):
            url = 'http://ptlogin2.qq.com/ptqrlogin'
            params = {
                'u1': 'http://find.qq.com/index.html?version=1&im_version=5533&width=910&height=610&search_target=0',
                'ptqrtoken': self.genqrtoken(qrsig),
                'ptredirect': '1',
                'h': '1',
                't': '1',
                'g': '1',
                'from_ui': '1',
                'ptlang': '2052',
                'action': '0-0-%d' % (time() * 1000),
                'js_ver': self.js_ver,
                'js_type': '1',
                'login_sig': login_sig,
                'pt_uistyle': '40',
                'aid': '715030901',
                'daid': '73'
            }
            try:
                resp = self.sess.get(url, params=params, timeout=1000)
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
                    errorMsg = str(result.text)
            except:
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

    def qqunSearch(self, request):
        sort = request.forms.get('sort')
        pn = int(request.forms.get('pn'))
        ft = request.forms.get('ft')
        kw = request.forms.get('kw').strip()
        if not kw:
            redirect('/qqun')
        self.sess.headers.update(
            {
                'Referer': 'http://find.qq.com/index.html?version=1&im_version=5533&width=910&height=610&search_target=0'
            }
        )
        skey = self.sess.cookies.get_dict().get('skey', '')
        groups = [(u'群名称', u'群号', u'群人数', u'群上限',
                   u'群主', u'地域', u'分类', u'标签', u'群简介')]
        gListRaw = []
        try:
            for page in xrange(0, pn):
                # sort type: 0 deafult, 1 menber, 2 active
                url = 'http://qun.qq.com/cgi-bin/group_search/pc_group_search'
                data = {
                    'k': u'交友',
                    'n': '8',
                    'st': '1',
                    'iso': '1',
                    'src': '1',
                    'v': '4903',
                    'bkn': self.genbkn(skey),
                    'isRecommend': 'false',
                    'city_id': '0',
                    'from': '1',
                    'keyword': kw,
                    'sort': sort,
                    'wantnum': '24',
                    'page': page,
                    'ldw': self.genbkn(skey)
                }
                resp = self.sess.post(url, data=data, timeout=1000)
                if resp.status_code != 200:
                    print '%s\n%s' % (resp.status_code, resp.text)
                result = json.loads(resp.content)
                gList = result.get('group_list')
                gListRaw.extend(gList)
                for g in gList:
                    name = self.rmWTS(g['name'])
                    code = g['code']
                    member_num = g['member_num']
                    max_member_num = g['max_member_num']
                    owner_uin = g['owner_uin']
                    qaddr = ' '.join(g['qaddr'])
                    try:
                        gcate = ' | '.join(g['gcate'])
                    except:
                        gcate = ''
                    try:
                        _labels = [l.get('label', '') for l in g['labels']]
                        labels = self.rmWTS(' | '.join(_labels))
                    except:
                        labels = ''
                    memo = self.rmWTS(g['memo'])
                    gMeta = (name, code, member_num, max_member_num,
                             owner_uin, qaddr, gcate, labels, memo)
                    groups.append(gMeta)
                sleep(2.5)
        except Exception, e:
            print e
        if len(groups) == 1:
            redirect('/qqun')
        f = BytesIO()
        if ft == 'xls':
            sheet = pe.Sheet(groups)
            f = sheet.save_to_memory('xls', f)
            response.set_header('Content-Type', 'application/vnd.ms-excel')
            filename = kw.replace(' ', '_') + '.xls'
            response.add_header(
                'Content-Disposition',
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
            for a, b, c, d, e, f, g, h, i in groups:
                worksheet.write(row, col, a)
                worksheet.write(row, col + 1, b)
                worksheet.write(row, col + 2, c)
                worksheet.write(row, col + 3, d)
                worksheet.write(row, col + 4, e)
                worksheet.write(row, col + 5, f)
                worksheet.write(row, col + 6, g)
                worksheet.write(row, col + 7, h)
                worksheet.write(row, col + 8, i)
                row += 1
            workbook.close()
            resp = static_file(
                filename,
                root=tempfile.gettempdir(),
                download=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            return resp
        elif ft == 'csv':
            writer = csv.writer(f, dialect='excel', encoding='utf-8')
            writer.writerows(groups)
            response.set_header('Content-Type', 'text/csv; charset=UTF-8')
            filename = kw.replace(' ', '_') + '.csv'
            response.add_header(
                'Content-Disposition',
                'attachment; filename="%s"' % (filename)
            )
            return f.getvalue()
        elif ft == 'json':
            json.dump(gListRaw, f, indent=4, sort_keys=True)
            response.set_header(
                'Content-Type', 'application/json; charset=UTF-8')
            filename = kw.replace(' ', '_') + '.json'
            response.add_header(
                'Content-Disposition',
                'attachment; filename="%s"' % (filename)
            )
            return f.getvalue()

    def genqrtoken(self, qrsig):
        e = 0
        for i in xrange(0, len(qrsig)):
            e += (e << 5) + ord(qrsig[i])
        qrtoken = (e & 2147483647)
        return str(qrtoken)

    def genbkn(self, skey):
        b = 5381
        for i in xrange(0, len(skey)):
            b += (b << 5) + ord(skey[i])
        bkn = (b & 2147483647)
        return str(bkn)

    def rmWTS(self, content):
        pattern = r'\[em\]e\d{4}\[/em\]|&nbsp;|<br>|[\r\n\t]'
        content = re.sub(pattern, ' ', content)
        content = content.replace('&amp;', '&').strip()
        return content


app = Bottle()
q = QQGroups()


@app.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')


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


### SAE ###
# debug(True)
# application = sae.create_wsgi_app(app)


### Local ###
if __name__ == '__main__':
    # https://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend
    # run(app, host='localhost', port=8080, debug=True, reloader=True)
    run(app, server='paste', host='localhost',
        port=8082, debug=True, reloader=True)
