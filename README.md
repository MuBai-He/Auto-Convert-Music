<div align="center">

<h1>Auto-Convert-Music</h1>

</div>

    这是一款全自动歌声转换软件，集成了网易云音乐下载、bilibili和YouTube音视频下载、歌声分离、歌声转换等功能。欢迎大家的使用，谢谢喵😊ヾ(≧▽≦*)

已部署项目演示：
[Ai吟美-泠鸢唱歌-哔哩哔哩直播](https://b23.tv/Yad4lKz)

### 一、环境要求

[必要🎄]  python版本要求：3.8、3.9、3.10，目前只在python3.10上测试过。推荐使用conda或miniconda创建虚拟环境, [安装教程](https://zhuanlan.zhihu.com/p/511233749), [pip换源教程](https://www.cnblogs.com/137point5/p/15000954.html)。

[必要🌴]  本项目使用了UVR5和so-vits-svc，请确保你有一张显存大于4G以上的NVIDIA GPU, 且安装了支持cuda版本的[torch、torchaudio](https://pytorch.org/), 因为bs_roformer的需求，必须安装2.0及以上版本。注：本项目目前已支持[UVR5 branch v5.6.0_roformer_add](https://github.com/Anjok07/ultimatevocalremovergui/tree/v5.6.0_roformer_add)的CIL

[可选🍀]  如果你想用NeteaseCloudMusicApi，请确保你已经安装了nodejs，[nodejs安装教程](https://blog.csdn.net/qq_42006801/article/details/124830995?spm=1001.2014.3001.5506)。

[可选🌵]  如果你想用bilibili音视频下载，请确保你已经安装了ffmpeg，并配置了环境变量，[ffmpeg安装教程](https://zhuanlan.zhihu.com/p/118362010)。

[可选🌾]  如果你想用youtube音视频下载，请确保你已经安装了ffmpeg，并配置了环境变量。


### 二、安装

#### 1. 安装Auto-Convert-Music

方式一：如果你安装了git，可以通过以下命令安装：
```bash
git clone https://github.com/MuBai-He/Auto-Convert-Music.git
```
方式二：如果没有安装git，可以直接下载zip文件，然后解压。
<div style="text-align: left;">
    <img src="assets\picture\git_download_zip.png" alt="Auto-Convert-Music" width="640px" title="安装方式" style="border: 1px solid pink; margin: 10px;" />
</div>

#### 2. 安装依赖

```bash
conda activate your_env
cd Auto-Convert-Music
pip install -r requirements.txt
```

#### 3. 配置UVR5
先运行tools.py下载[UVR5 branch v5.6.0_roformer_add](https://github.com/Anjok07/ultimatevocalremovergui/tree/v5.6.0_roformer_add)和[Music-Source-Separation-Training](https://github.com/ZFTurbo/Music-Source-Separation-Training)的源码。这里会自动复制assets下的UVR5的配置和我修改好的UVR-CLI.py、separate.py到ultimatevocalremovergui文件夹下，自动复制inference-opt.py和model_bs_roformer_ep_368_sdr_12.9628.yaml到Music-Source-Separation-Training文件夹下。还会自动下载一个model_bs_roformer_ep_368_sdr_12.9628.ckpt模型
```bash
python tools.py
```
然后运行ultimatevocalremovergui/UVR-CLI.py参照[教程](https://www.bilibili.com/read/cv27499700/)下载好所需的模型，也可自行配置
```bash
python ultimatevocalremovergui/UVR-CLI.py
```
#### 4. 部署NeteaseCloudMusicApi[可选]

如果你打算使用bilibili和YouTube音视频下载，可以跳过这一步。

如果你打算使用NeteaseCloudMusicApi，你需要部署[NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)项目。
但是这个项目已经于 2024.1 删库跑路了，所以你只能暂时选择一个别人[最近fork的版本的链接](https://github.com/Binaryify/NeteaseCloudMusicApi/forks?include=active&page=1&period=2y&sort_by=last_updated)，然后参考readme进行部署。

#### 5. 一些注意事项
[必要🍏] 在运行主程序之前，你需要先运行一次ultimatevocalremovergui\UVR-CLI.py，确保UVR-CLI下载了相关分离模型。这里已经帮你配置了一些模型的配置文件，你可以在`ultimatevocalremovergui\gui_data\saved_ensembles`和`ultimatevocalremovergui\gui_data\saved_settings`中查看，也可以参考[教程](https://www.bilibili.com/read/cv27499700/)自行配置。

[必要🎉] 在运行主程序之前，确保你已经至少训练了so-vits-svc-4.1的主模型，并填好一些配置和模型的路径

[可选🌼] 如果你打算使用NeteaseCloudMusicApi，你需要先运行NeteaseCloudMusicApi。注意：网易云音乐只支持传入歌曲名或歌曲名+歌手名(更精确)

[可选🍓] 如果你打算使用bilibili音视频下载。B站对各种语言的歌曲支持力度：中文>英文=日文>其他语言。注意：bilibili音视频下载支持传入这些：
<div style="text-align: left;">
    <img src="assets\picture\bili.png" alt="Auto-Convert-Music" width="640px" title="bilibili" style="border: 1px solid pink; margin: 10px;" />
</div>

[可选🌽] 如果你打算使用youtube音视频下载。注意：youtube音视频下载支持传入：关键字(歌曲名 歌手名)、链接。YouTube对各种语言的歌曲支持力度：英文>日文>其他语言(中文), 英文歌曲中关键词最好别出现其他语言，日文同理！否则会搜不到！

[注意1🧃] bs_roformer既支持[Music-Source-Separation-Training](https://github.com/ZFTurbo/Music-Source-Separation-Training)推理，也支持[UVR5 branch v5.6.0_roformer_add](https://github.com/Anjok07/ultimatevocalremovergui/tree/v5.6.0_roformer_add)的推理，推荐使用Music-Source-Separation-Training进行推理，会更好！

[注意2🍉] 歌曲的输入也可以是input下的文件名，如果是input文件夹下的文件名，转换的歌曲会直接使用input文件夹下的歌曲，而不会自动从网易云或bilibili和YouTube下载。歌曲文件输出在output的converted列表中的文件夹名，最终文件命名规则{converted}_{speaker}.wav文件

### 三、使用

    1、仅使用歌声转换功能，你可以直接运行AutoConvertMusic.py
    2、Q:如何自定义使用？A:你可以自行参考`AutoConvertMusic.py`、`send_uvr5cmd.py`、`bilibili.py` `youtube.py`中的`if __name__ == "__main__":`部分。
    3、api可参考Web_through.py，你可以通过这个api接入各种聊天机器人，比如qq机器人、微信机器人等。同时，也可以接入AI虚拟主播、数字人等。

### 四、鸣谢

歌声转换的项目是[so-vits-svc-4.1](https://github.com/svc-develop-team/so-vits-svc)，请给so-vits-svc-4.1一个star，谢谢喵😊ヾ(≧▽≦*)o 

歌声分离的项目是[UVR5 branch v5.6.0_roformer_add](https://github.com/Anjok07/ultimatevocalremovergui/tree/v5.6.0_roformer_add)和[Music-Source-Separation-Training](https://github.com/ZFTurbo/Music-Source-Separation-Training)，请给ultimatevocalremovergui-v5.6和Music-Source-Separation-Training一个star，谢谢喵😊ヾ(≧▽≦*)o 

关于ultimatevocalremovergui cli的命令行使用思路来自于[这里](https://github.com/Anjok07/ultimatevocalremovergui/issues/678)，非常感谢这位天才的思路😊。ヾ(≧▽≦*)o 

UVR5的使用可以参考bfloat16大佬分享的[教程](https://www.bilibili.com/read/cv27499700/)，请给这篇文章一键三连，谢谢喵😊ヾ(≧▽≦*)o 

网易云音乐下载支持来源于[NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)，请给NeteaseCloudMusicApi一个star，谢谢喵😊ヾ(≧▽≦*)o 

bilibili音视频下载支持来源于一个超可爱的项目[yutto](https://github.com/yutto-dev/yutto)，请给yutto一个可爱的star，谢谢喵😊ヾ(≧▽≦*)o 

youtube音视频下载支持来源于[yt-dlp](https://github.com/yt-dlp/yt-dlp), 请给yt-dlp一个star，谢谢喵😊ヾ(≧▽≦*)o

最后，非常感谢以上项目的作者和贡献者以及一些这里未列出的第三方pypi库的项目，请给他们一个可爱的star，请给他们一个可爱的star，请给他们一个可爱的star，谢谢喵🤗ヾ(≧▽≦*)o

### 五、问题反馈、建议和贡献  

如果你在使用过程中遇到任何问题，或者有任何建议，欢迎在[Issues](https://github.com/MuBai-He/Auto-Convert-Music/issues)中反馈给我们。
如果您有任何想法或建议，欢迎通过Issues或Pull Requests与我们分享。