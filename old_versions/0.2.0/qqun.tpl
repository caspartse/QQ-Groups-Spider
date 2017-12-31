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
        background: rgba(0, 0, 0, .25);
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
    </style>
    <link href="/static/css/font-awesome-4.7.0/css/font-awesome.min.css" rel="stylesheet" type="text/css">
    <script type="text/javascript" src="/static/js/jquery.min.js?v=3.2.1"></script>
    <link href="/static/favicon.ico" rel="shortcut icon" type="image/x-icon" />
    <title>QQ Groups Spider</title>
</head>

<body>
    <div class="wrapper">
        <div class="qr_login">
            <div id="qr_area" class="qr_area">
                <img id="qrcode" class="qrcode" src="" alt="" title="点击可刷新" onclick="qrRefresh()" />
                <span id="login_success" class="login_success" onclick="qrRefresh()">
                    <i class="fa fa-check" aria-hidden="true" title="登录成功，点击可刷新"></i>
                </span>
                <span id="qr_invalid" class="qr_invalid" onclick="qrRefresh()">
                    <i class="fa fa-refresh" aria-hidden="true" title="二维码失效，请点击刷新"></i>
                </span>
            </div>
            <p id="tips" class="tips">手机 QQ 扫描二维码</p>
        </div>
        <div class="alacarte">
            <form method="post" action="/qqun" onsubmit="loginCheck()">
                <p>
                    <label for="sort">
                        <strong>排序方式</strong>
                        <input type="radio" id="sort_1" name="sort" value="0" checked="checked" />默认
                        <input type="radio" id="sort_2" name="sort" value="1" />群人数
                        <input type="radio" id="sort_4" name="sort" value="2" />群活跃度
                    </label>
                </p>
                <p>
                    <label for="pn">
                        <strong>抓取数量</strong>
                        <input type="radio" id="pn_5" name="pn" value="5" checked="checked" />120&nbsp;&nbsp;
                        <input type="radio" id="pn_10" name="pn" value="10" />240&nbsp;&nbsp;
                        <input type="radio" id="pn_15" name="pn" value="15" />360&nbsp;&nbsp;
                        <input type="radio" id="pn_20" name="pn" value="20" />480
                    </label>
                </p>
                <p>
                    <label for="ft">
                        <strong>导出格式</strong>
                        <input type="radio" id="ft_xls" name="ft" value="xls" checked="checked" />XLS&nbsp;
                        <input type="radio" id="ft_xlsx" name="ft" value="xlsx" />XLSX&nbsp;
                        <input type="radio" id="ft_csv" name="ft" value="csv" />CSV (UTF-8)&nbsp;
                        <input type="radio" id="ft_json" name="ft" value="json" />JSON
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
    var _auth = false;

    function changeStatus(status) {
        switch (status) {
            case 0:
                $('#tips').text('手机 QQ 扫描二维码');
                break;
            case 1:
                $('#tips').text('二维码认证中...');
                break;
            case 2:
                $('#login_success').css('display', 'inline-block');
                $('#tips').text('登录成功，点击可刷新');
                _auth = true;
                break;
            case 3:
                $('#qr_invalid').css('display', 'inline-block');
                $('#tips').text('二维码失效，请点击刷新');
                _auth = false;
                break;
            default:
                console.log(status);
        }
    }

    function qrLoginQuery() {
        function trigger() {
            var url = '/qrlogin?t=' + (new Date().getTime());
            $.ajax({
                url: url,
                cache: false,
                dataType: "json",
                success: function(obj) {
                    var status = JSON.parse(JSON.stringify(obj)).status;
                    changeStatus(status);
                    if ([2, 3].includes(status)) {
                        clearInterval(window.queryTimmer);
                    }
                }
            });
        }
        window.queryTimmer = setInterval(trigger, 2000);
    }

    function qrRefresh() {
        _auth = false;
        clearInterval(window.queryTimmer);
        $('#qrcode').attr('src', '');
        var src = '/getqrcode?r=' + Math.random();
        $('#qrcode').attr('src', src);
        $('#login_success').css('display', 'none');
        $('#qr_invalid').css('display', 'none');
        $('#tips').text('手机 QQ 扫描二维码');
        qrLoginQuery();
    }

    function loginCheck() {
        if (!_auth) {
            alert('请先授权登录');
        }
    }

    (function() {
        qrRefresh();
    })();
    </script>
</body>

</html>