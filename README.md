<div align="center">

<h1>Auto-Convert-Music</h1>
 
</div>

这是一个令人兴奋的软件，它可以让AI自动唱歌！使用先进的音频处理技术，这个软件能够从您喜欢的歌曲中提取人声，并由AI进行演唱。（精神错乱的AI发言~
## 部署指南
### 环境要求
在开始使用之前，请确保您已经部署了[NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)项目。  
仅在Python==3.10环境测试过！

    from Auto-Convert-Music import convert_music

#### 创建实例
    music_moudle=convert_music()

#### 添加转换任务
    music_moudle.add_conversion_task(music_name="運命の人 『ユイカ』", vocal="刻晴[中]")
    music_moudle.add_conversion_task(music_name="ずっとずっとずっと", vocal="刻晴[中]")

#### 转换列表
    self.converting=[] #转换中队列，第零个是正在转换的内容。
    self.converted=[] #转换完成队列，通过判断转换完成队列来检测是否完成转换。
#### 输出
歌曲文件输出在output的converted列表中的文件夹名，最终文件命名规则{converted}_{vocal}.wav文件

### 鸣谢
*关于UVR5的命令行使用思路来自于[这里](https://github.com/Anjok07/ultimatevocalremovergui/issues/678),非常感谢这位天才的思路。*
*UVR5的使用可以参考bfloat16大佬分享的[教程](https://www.bilibili.com/read/cv27499700/)*


### 贡献  
如果您有任何想法或建议，欢迎通过Issues或Pull Requests与我们分享。

