# comskip_to_html

## 何するの？

comskipでCM検出したときのブロック分割情報をもとに誤検出の訂正をしたり、その訂正結果を元にffmpegによる分割・結合シェルスクリプトを出力したりとかします。

## 必要なもの

### Linuxの場合

* python-3.4
* ffms2

適当にapt-getとかで入れてください。yumは知りません。

* ffms(python)
* Jinja2
* numpy
* Pillow

pip で入れてください。

### Windowsの場合

* python-3.3

公式から落としてください。ffmsのバイナリが3.3なので3.3を落としてくださいな。


* pip

なんか、get-pip.pyというのを落としてpython3.3で実行すればよいみたいです（大雑把）。

* [ffms-0.3a](https://bitbucket.org/spirit/ffms/downloads)
* Jinja2
* numpy
* Pillow
* pywin32

ffmsはwin32/win-amd64のmsiを実行してインストール。他は[Unofficial Windows Binaries for Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/)のバイナリを
使えば良いんじゃないでしょうか。


## 使い方

事前にcomskipでtsの解析をして.logを出力させておきます。
`python comskip_to_html.py path/to/movie.ts`すると、tsとlogを読んでhtmlを出力します。

HTMLをブラウザ（firefoxでしか確認してないです）で開くとブラウザ上でボタンを押したりラジオボタンを選択したりすれば誤判定を修正できます。
下のほうの「生成」というボタンを押せばffmpegとavidemuxのスクリプトが出力されます。
