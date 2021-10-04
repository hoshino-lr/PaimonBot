# PaimonBot

A qqbot for Genshin_Impact (and other usage :)

## 简介

**PaimonBot:** 基于 [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) 框架，开源、无公害、非转基因的QQ机器人。

**版本：** 1.5.0

## 功能介绍

PaimonBot 的功能开发以服务 [原神](https://ys.mihoyo.com/) 玩家为核心，主要功能有：

- **猜原神头像**：猜立绘
- **原神猜头像**：通过文字描述信息猜人
- **原神猜武器**：通过文字描述信息猜武器
- **猜原神武器**：猜武器图片
- **派蒙猜色图**：猜色图(诶嘿嘿)
- **Genshin_ImpactBot**：使用了HoshinoBot的原神插件
- **原神运势**：开发不完善（文案还没写完）
- **戳一戳集卡**
- **兑换商店**：开发中（通过flask框架开发，预计完成时间 2021年10月底）
- **圣遗物评分**：开发中（需要自己训练ocr模型，咕咕咕 预计完成时间 2022年2月）
- ****

> 由于bot的功能会快速迭代开发，使用方式这里不进行具体的说明，请向bot发送"help"或移步[此文件](hoshino/modules/botmanage/help.py)查看详细(还没写完)。

PaimonBot 还具有以下通用功能：

- **入群欢迎**&**退群提醒**
- **复读**
- **反馈发送**：反馈内容将由bot私聊发送给维护组


### 功能模块控制

Paimon的功能繁多，各群可根据自己的需要进行开关控制，群管理发送 `lssv` 即可查看功能模块的启用状态，使用以下命令进行控制：

```
启用 service-name
禁用 service-name
```


## ~~部署指南~~

登录框架使用[go-cqhttp](https://docs.go-cqhttp.org/)

### 部署步骤

#### Windows 部署

1. 参照[xcwbot](https://cn.pcrbot.com/deploy-a-priconne-bot-on-linux)部署方案部署go-cqhttp模型

2. 打开一个合适的文件夹，点击资源管理器左上角的 `文件 -> 打开Windows Powershell`

3. 输入以下命令克隆本仓库并安装依赖

    ```powershell
    git clone -b v1.5.0 https://github.com/hoshino-lr/PaimonBot.git
    cd HoshinoBot
    py -m pip install -r requirements.txt
    ```
    >若此处有报错信息，请务必解决，将错误信息复制到百度搜索一般即可找到解决办法。  
    >
    >若安装python依赖库时下载速度缓慢，可以尝试使用`py -3.8 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

4. 回到资源管理器，进入`hoshino`文件夹，将`config_example`文件夹重命名为`config`，然后右键使用Notepad++打开其中的`__bot__.py`，按照其中的注释说明进行编辑。

    > 如果您不清楚某项设置的作用，请保持默认
    
5. 回到powershell，启动 Hoshino

    ```powershell
    py run.py
    ```

    私聊机器人发送`在？`，若机器人有回复，恭喜您！您已经成功搭建起HoshinoBot了。之后您可以尝试在群内发送`!帮助`以查看会战管理的相关说明，发送`help`查看其他一般功能的相关说明，发送`pcr速查`查看常用网址等。

    注意，此时您的机器人功能还不完全，部分功能可能无法正常工作。若希望您的机器人可以发送图片，或使用其他进阶功能，请参考本章**更进一步**的对应小节。





#### Linux 部署

1. 参照[xcwbot](https://cn.pcrbot.com/deploy-a-priconne-bot-on-linux)部署方案部署go-cqhttp模型

2. 回到我们熟悉的命令行，安装 Python (≥3.8)

    ```bash
    # Ubuntu or Debian
    sudo apt install python3.8
    ```
    > 若您的包管理工具（如`yum`）尚不支持`python3.8`，你可以尝试从源码安装。  
    >
    > Google will help you greatly : )

3. 克隆本仓库并安装依赖包
    ```bash
    git clone -b v1.5.0 https://github.com/hoshino-lr/PaimonBot.git
    cd HoshinoBot
    python3.8 -m pip install -r requirements.txt
    ```

4. 编辑配置文件
    ```bash
    mv hoshino/config_example hoshino/config
    nano hoshino/config/__bot__.py
    ```
    > 配置文件内有相应注释，请根据您的实际配置填写，HoshinoBot仅支持反向ws通信
    >
    > 您也可以使用`vim`编辑器，若您从未使用过，我推荐您使用 `nano` : )
5. 运行bot
    ```bash
    python3.8 run.py
    ```
    
    私聊机器人发送`在？`，若机器人有回复，恭喜您！您已经成功搭建起HoshinoBot了。之后您可以尝试在群内发送`!帮助`以查看会战管理的相关说明，发送`help`查看其他一般功能的相关说明，发送`pcr速查`查看常用网址等。
    

### 注意事项
1. [原神运势]功能开发不太完善，请不要使用，会在1.6版本进行更新
2. 如果连接失效，请参照[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)的部署方案进行部署，效果相同
3. res文件中保留了一些pcr或bot的表情包或图片，大家可以删掉
4. 在戳一戳使用了小红帽碎片（这个是我自己整活用的自己的头像做的），碎片系统将保留，大家可以修改[我的头像文件](res/Genshin_Impact_icon/1006.jpg)
    （把图片替换成其他图片就行，名字不变即可）
## 友情链接

[HoshinoBot插件仓库](https://github.com/pcrbot/HoshinoBot-plugins-index)

[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)

[go-cqhttp](https://docs.go-cqhttp.org/)

[xcwbot](https://cn.pcrbot.com/deploy-a-priconne-bot-on-linux)