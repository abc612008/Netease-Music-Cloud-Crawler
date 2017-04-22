# 网易云音乐用户爬虫

这是个能跑出来某首歌被用户喜欢（加入到“我喜欢的音乐”）次数的爬虫。测试于Python 3.5.2。

警告：本脚本内部混乱，可能给阅读者带来不适（雾）。

原理：在URL遍历用户ID，所以其实改改可以做更多功能的。

对惹，别问我结果是啥，因为做出来之后发现要几十个小时才能跑完，而且跑着跑着可能还会banip啥的（虽然其实这个是支持代理的，不过用了速度更慢）……所以就懒得爬结果了Orz。如果谁有空跑出来结果了希望可以发给我一份OwO。

## 用法

要用这个爬虫的话，你需要requests和pycrypto。理论上可以使用setup.py安装（虽然我还没测试过能不能用orz），也可以手动用pip安装。

装好之后，你需要一些用于加密请求的密钥，像这样生成；

```
python3 ./generate_keys.py 10000
```

10000是要生成的个数，一般来说比线程数量大十几倍就可以了。（我这里平均生成一个要5s）

然后就可以用爬虫了：

```
python3 ./main.py
```

有两个可选的选项：

* --verbose: 输出调试信息
* --proxy: 用代理池，需要[IPProxyPool](https://github.com/qiyeboy/IPProxyPool).

main.py里还有些常数可以改，大概在第110行左右(我懒的用argparse了orz):

* THREAD_NUM: 线程数量
* TASK_LENGTH: 每个任务要跑的用户数量
* TASK_NUM: 一轮要跑多少个任务（每轮过后都会保存一次）

结果会保存到 `data` 文件里，这是个pickle文件，其结构为：[collections.Counter, int, [int]].

查看结果的方法：``python3 -m pickle ./data``（或者自己写一个脚本辣）

## License

MIT License. 用了来自 [darknessmoi/musicbox](https://github.com/darknessomi/musicbox/wiki/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%96%B0%E7%89%88WebAPI%E5%88%86%E6%9E%90%E3%80%82)里的一些代码，还参考了[metowolf/NeteaseCloudMusicApi](https://github.com/metowolf/NeteaseCloudMusicApi/wiki/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90API%E5%88%86%E6%9E%90---weapi)里的一些文档。