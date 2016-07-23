<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <base href="/" />
        <style type="text/css">
            body {
                font-family: 'Helvetica Neue',Helvetica,'Nimbus Sans L','Segoe UI',Arial,'Liberation Sans','Hiragino Sans GB','Source Han Sans CN','Source Han Sans SC','Microsoft YaHei UI','Microsoft YaHei','Wenquanyi Micro Hei','WenQuanYi Zen Hei','ST Heiti',SimHei,sans-serif;
            }

            .wrapper {
                width: 100%;
                margin: 100px 0 0;
                text-align: center;
            }

            .qr_login {
                display: inline-block;
                width: 160px;
                border-right: solid 1px #DDD;
                text-align: center;
                font-size: 12px;
                vertical-align: middle;
                color: #666;
            }

            .qr_login p, .alacarte p {
                margin: 0;
            }

            .qr_area {
                display: inline-block;
                width: 80px;
                height: 80px;
                overflow: hidden;
            }

            .qrcode {
                width: 80px;
                height: 80px;
                margin: 0 auto;
                cursor: pointer;
            }

            .login_success,
            .qr_invalid {
                display: none;
                position: relative;
                top: -80px;
                width: 80px;
                height: 80px;
                margin-bottom: -80px;
                text-align: center;
                background: rgba(0,0,0,.25);
                cursor: pointer;
            }

            .login_success .fa,
            .qr_invalid .fa {
                display: inline-block;
                margin: -5px 0 0;
                overflow: hidden;
                font-size: 60px;
                line-height: 80px;
            }

            .login_success .fa-check {
                color: #74C328;
            }

            .qr_invalid .fa-refresh {
                color: #F39800;
            }

            .alacarte {
                display: inline-block;
                padding-left: 40px;
                text-align: left;
                line-height: 2.25em;
                vertical-align: middle;
                cursor: default;
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
                width: 20em;
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
                    <img id="qrcode" class="qrcode" src="/getqrcode" alt="QR Code" title="双击可刷新" ondblclick="qrRefresh()" />
                    <span id="login_success" class="login_success" ondblclick="qrRefresh()">
                        <i class="fa fa-check" aria-hidden="true" title="登录成功，双击可刷新"></i>
                    </span>
                    <span id="qr_invalid" class="qr_invalid" onclick="qrRefresh()">
                        <i class="fa fa-refresh" aria-hidden="true" title="二维码失效，请点击刷新"></i>
                    </span>
                </span>
                <p id="tips">手机 QQ 扫描二维码</p>
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
                            <input type="radio" id="pn_20" name="pn" value="20" />160
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
                    case 0:
                        $('#tips').text('手机 QQ 扫描二维码');
                        break;
                    case 1:
                        $('#tips').text('二维码认证中...');
                        break;
                    case 2:
                        $('#login_success').css('display', 'inline-block');$('#tips').text('登录成功，双击可刷新');
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
                qrLoginQuery();
            })();
        </script>
    </body>
</html>