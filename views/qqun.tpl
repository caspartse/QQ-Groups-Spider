<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <base href="/" />
        <style type="text/css">
            body {
                font-family: 'Helvetica Neue', Helvetica, 'Nimbus Sans L', 'Segoe UI', Arial, 'Liberation Sans', 'Source Han Sans CN', 'Source Han Sans SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', 'Wenquanyi Micro Hei', 'WenQuanYi Zen Hei', 'ST Heiti', SimHei, sans-serif;
            }

            .wrapper {
                width: 100%;
                margin: 100px 0 0;
                text-align: center;
            }

            .avatar {
                display: block;
                width: 100px;
                height: 100px;
                margin: 0 auto 25px;
                -webkit-border-radius: 50%;
                -moz-border-radius: 50%;
                border-radius: 50%;
            }

            .qr_login {
                display: inline-block;
                width: 180px;
                border-right: solid 1px #DDD;
                text-align: center;
                font-size: 14px;
                vertical-align: middle;
                color: #666;
            }

            .qr_login p {
                margin: 5px 0;
                line-height: 14px;
            }

            .qr_area {
                display: inline-block;
                width: 100px;
                height: 100px;
                overflow: hidden;
            }

            .qrcode {
                display: inline-block;
                vertical-align: top;
                width: 100px;
                height: 100px;
                margin: 0 auto;
                background: url('/static/img/progress.gif') center center no-repeat;
                cursor: pointer;
            }

            .login_success,
            .qr_invalid {
                display: none;
                vertical-align: top;
                position: relative;
                top: -100px;
                width: 100px;
                height: 100px;
                margin-bottom: -100px;
                text-align: center;
                background: rgba(0,0,0,.25);
                cursor: pointer;
            }

            .login_success .fa,
            .qr_invalid .fa {
                display: inline-block;
                height: 100px;
                overflow: hidden;
                font-size: 60px;
                line-height: 100px;
                overflow: hidden;
            }

            .login_success .fa-check {
                color: #74C328;
            }

            .qr_invalid .fa-refresh {
                color: #F39800;
            }

            .tips {
                color: #000;
            }

            .alacarte {
                display: inline-block;
                padding-left: 40px;
                text-align: left;
                line-height: 2em;
                vertical-align: middle;
                cursor: default;
            }

            .alacarte p {
                margin: 0;
            }

            .alacarte strong {
                font-style: normal;
                font-weight: 600;
                font-size: 100%;
            }

            .alacarte form input {
                display: inline-block;
                margin-left: .5em;
            }

            .alacarte form input[type=text] {
                width: 16.25em;
            }

            .alacarte form input[type=submit] {
                cursor: pointer;
                margin-left: 1em;
            }

            label strong {
                display: inline-block;
                margin-right: .75em;
            }

            .footer {
                margin-top: 100px;
            }

            .footer a {
                display: inline-block;
                margin: 0 .75em;
                text-decoration: none!important;
            }

            .footer a:first-child {
                color: #42C02E!important;
            }

            .footer a:last-child {
                color: #FD6062!important;
            }

            a,
            a:link {
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                color: #4285F4;
                cursor: pointer;
            }

            a:focus {
                outline: none;
                outline-style: none;
                -moz-outline-style: none;
            }

            a::-moz-focus-inner {
                border: 0;
            }

            a:hover {
                text-decoration: underline;
            }
        </style>
        <link href="/static/css/font-awesome-4.6.3/css/font-awesome.min.css" rel="stylesheet" type="text/css">
        <script type="text/javascript" src="/static/js/jquery.min.js?v=2.2.4"></script>
        <link href="/favicon.ico" rel="shortcut icon" type="image/x-icon"/>
        <title>QQ Groups Spider</title>
    </head>
    <body>
        <div class="wrapper">
             <div class="qr_login">
                <span id="qr_area" class="qr_area">
                    <img id="qrcode" class="qrcode" src="" alt="" title="点击可刷新" onclick="qrRefresh()" />
                    <span id="login_success" class="login_success" onclick="qrRefresh()">
                        <i class="fa fa-check" aria-hidden="true" title="登录成功，点击可刷新"></i>
                    </span>
                    <span id="qr_invalid" class="qr_invalid" onclick="qrRefresh()">
                        <i class="fa fa-refresh" aria-hidden="true" title="二维码失效，请点击刷新"></i>
                    </span>
                </span>
                <p id="tips" class="tips">手机 QQ 扫描二维码</p>
            </div>
            <div class="alacarte">
                <form method="post" action="/qqun" onsubmit="qrLoginCheck()">
                    <p>
                        <label for="st">
                            <strong>排序方式</strong>
                            <input type="radio" id="st_2" name="st" value="2" checked="checked" />群人数
                            <input type="radio" id="st_4" name="st" value="4" />群活跃度
                            <input type="radio" id="st_1" name="st" value="1" />默认
                        </label>
                    </p>
                    <p>
                        <label for="pn">
                            <strong>抓取数量</strong>
                            <input type="radio" id="pn_5" name="pn" value="5" checked="checked" />40&nbsp;&nbsp;
                            <input type="radio" id="pn_10" name="pn" value="10" />80&nbsp;&nbsp;
                            <input type="radio" id="pn_15" name="pn" value="15" />120&nbsp;&nbsp;
                            <input type="radio" id="pn_20" name="pn" value="20" />160&nbsp;&nbsp;
                            <input type="radio" id="pn_20" name="pn" value="25" />200
                        </label>
                    </p>
                    <p>
                        <label for="ft">
                            <strong>导出格式</strong>
                            <input type="radio" id="ft_xls" name="ft" value="xls" checked="checked" />Excel (.xls)&nbsp;
                            <input type="radio" id="ft_xlsx" name="ft" value="xlsx" />Excel (.xlsx)&nbsp;
                            <input type="radio" id="ft_csv" name="ft" value="csv" />CSV (UTF-8)
                        </label>
                    </p>
                    <p>
                        <label for="kw">
                            <strong>群关键词</strong>
                            <input type="text" id="kw" name="kw" placeholder="" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" />
                        </label>
                        <input value="Submit" type="submit" />
                    </p>
                </form>
            </div>
        </div>
        <a href="https://github.com/caspartse/QQ-Groups-Spider" target="_blank"><img style="position: absolute; top: 0; right: 0; border: 0;" src="/static/img/forkme_right_green_007200.png" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_green_007200.png"></a>
        <script type="text/javascript">
            function httpGetAsync(url, callback) {
                var xmlHttp = new XMLHttpRequest();
                xmlHttp.onreadystatechange = function () {
                    if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
                        callback(xmlHttp.responseText);
                    }
                };
                xmlHttp.open("GET", url, true);
                xmlHttp.send(null);
            }

            function changeStatus(obj) {
                var status = JSON.parse(obj).status;
                switch (status) {
                    case -1:
                        break;
                    case 0:
                        $('#tips').text('手机 QQ 扫描二维码');
                        break;
                    case 1:
                        $('#tips').text('二维码认证中...');
                        break;
                    case 2:
                        $('#login_success').css('display', 'inline-block');$('#tips').text('登录成功，点击可刷新');
                        break;
                    default:
                        $('#qr_invalid').css('display', 'inline-block');$('#tips').text('二维码失效，请点击刷新');
                }
            }

            function qrLoginQuery() {
                function trigger() {
                    var url = '/qrlogin?r=' + (new Date().getTime());
                    httpGetAsync(url, changeStatus);
                    if ($('#login_success').css('display') != 'none' || $('#qr_invalid').css('display') != 'none') {
                        clearInterval(queryTimmer);
                    }
                }
                var queryTimmer = setInterval(trigger, 2000);
            }

            function qrRefresh() {
                $('#qrcode').attr('src', '');
                var src = '/getqrcode?r=' + Math.random();
                $('#qrcode').attr('src', src);
                $('#login_success').css('display', 'none');
                $('#qr_invalid').css('display', 'none');
                $('#tips').text('手机 QQ 扫描二维码');
                qrLoginQuery();
            }

            function qrLoginCheck() {
                if ($('#login_success').css('display') == 'none') {
                    alert('请先授权登录');
                }
            }

            (function () {
                qrRefresh();
            })();
        </script>
    </body>
</html>