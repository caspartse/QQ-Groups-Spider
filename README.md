# QQ-Groups-Spider (v0.2.0)

QQ Groups Spider（QQ 群爬虫）

批量抓取 QQ 群信息，包括群名称、群号、群人数、群主、地域、分类、标签、群简介等内容，最终生成 XLS(X) / CSV 结果文件。

## 代码说明

### 测试环境

* BunsenLabs GNU/Linux 8.7 (Hydrogen)
* Python (2.7)

### 第三方库支持

* [bottle](http://bottlepy.org/)
* [requests](http://python-requests.org)
* [pyexcel-xls](https://github.com/pyexcel/pyexcel-xls)
* [XlsxWriter](https://github.com/jmcnamara/XlsxWriter)（可选）
* [unicodecsv](https://github.com/jdunck/python-unicodecsv)

### 本地运行

``` $ python app.py ```

### SAE 上运行

参照 [https://www.sinacloud.com/doc/sae/python/tutorial.html#bottle](https://www.sinacloud.com/doc/sae/python/tutorial.html#bottle) 配置即可。

*(P.S. SAE 上 XlsxWriter 不可用。)*

## Demo

### 在线演示

[http://kagent.applinzi.com/qqun](http://kagent.applinzi.com/qqun)

### 截图示例


![](https://raw.githubusercontent.com/caspartse/QQ-Groups-Spider/master/screenshots/screenshot_01.jpg)


![](https://raw.githubusercontent.com/caspartse/QQ-Groups-Spider/master/screenshots/screenshot_02.jpg)

## 更新日志

* 2017-07-27  v0.2.0 更换新接口；优化模板页面；增加群上限、地域、分类、标签等字段；新增导出 JSON 格式。
* 2016-02-19  v0.1.2 更新二维码验证参数。
* 2016-08-19  v0.1.1 改善代码逻辑；加入 XlsxWriter 模块；增加本地运行支持。
* 2016-07-23  v0.1.0 初始化。
