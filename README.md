# QQ-Groups-Spider
QQ Groups Spider（QQ 群爬虫）

批量抓取 QQ 群信息，包括群名称、群号、群人数、群主、群简介等内容，最终生成 XLS(X) / CSV 结果文件。

# 代码说明

### 运行环境

* Python (2.7)
* [bottle](http://bottlepy.org/) (0.12.9)

### 第三方库支持

* [requests](http://python-requests.org)
* [pyexcel](https://github.com/pyexcel/pyexcel)
* [XlsxWriter](https://github.com/jmcnamara/XlsxWriter)
* [unicodecsv](https://github.com/jdunck/python-unicodecsv)

### 本地运行

``` $ python app.py ```

### SAE 上运行

参照 [https://www.sinacloud.com/doc/sae/python/tutorial.html#bottle](https://www.sinacloud.com/doc/sae/python/tutorial.html#bottle) 配置即可。

*(P.S. SAE 上 XlsxWriter 不可用。)*

# Demo

### 在线演示

[http://kagent.applinzi.com/qqun](http://kagent.applinzi.com/qqun)

### 截图示例


![](http://7xslb5.com1.z0.glb.clouddn.com/QQ-Groups-Spider-Demo01.jpg)


![](http://7xslb5.com1.z0.glb.clouddn.com/QQ-Groups-Spider-Demo02.jpg)

# 更新日志

* 2016-02-19  0.1.2 更新二维码验证参数。
* 2016-08-19  0.1.1 改善代码逻辑，加入 XlsxWriter 模块，增加本地运行支持。
* 2016-07-23  0.1.0 初始化。
