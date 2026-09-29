# Waydroid Extras Script

Script to add GApps and other stuff to Waydroid!

> 本仓库是 [casualsnek/waydroid_script](https://github.com/casualsnek/waydroid_script) 的 **Fork**，改动集中在 Magisk / Kitsune Mask 的安装源与文档，详见下面「本 Fork 的改动」。

## 本 Fork 的改动

- **Magisk 安装源**：从已停更 / 已失效的 Magisk Delta 渠道换成 **Kitsune Mask（Magisk Delta 续作）`v27.2-kitsune-4`**
  - 版本标识：`MAGISK_VER=v27.2-kitsune-4` / `MAGISK_VER_CODE=27002` —— 该谱系**最后一个真实版本号**，保留内置 Zygisk
  - 资产：`Kitsune.Magisk.release.v27.2-kitsune-4.apk`（12,770,643 字节）
  - sha256：`818cfa02783ddae573cc953450fbc39ec3e5164b66e517c657ba11cf90963a89`
  - 下载源（本仓库自建 release，写在 `stuff/magisk.py` 的 `dl_link`）：
    - 主：`https://github.com/Grant-Felix/KitsuneMagiskFork/releases/download/v27.2-kitsune-4/Kitsune.Magisk.release.v27.2-kitsune-4.apk`
    - 镜像：`https://github.com/Grant-Felix/waydroid_script_fork/releases/download/magisk-v27.2-kitsune-4/Kitsune.Magisk.release.v27.2-kitsune-4.apk`
- **为什么换**：原作者 HuskyDG 的仓库与账号已删除、官方更新服务器全部 404，脚本原先使用的 Delta 26.3（2024-01 构建）已无法升级。
- **一键准备**：仓库自带 [`setup.sh`](setup.sh)，一条命令克隆 + 建 venv + 装依赖（见下）。

# Installation/Usage

## 一键准备（可选）

```bash
bash setup.sh                      # 克隆/更新 + venv + 依赖，然后打印后续命令
bash setup.sh install magisk       # 准备完直接安装 Kitsune Mask v27.2-kitsune-4
```

## Interactive terminal interface

```
git clone https://github.com/Grant-Felix/waydroid_script_fork
cd waydroid_script_fork
python3 -m venv venv
venv/bin/pip install -r requirements.txt
sudo venv/bin/python3 main.py
```

![image-20230430013103883](assets/img/README/image-20230430013103883.png)

![image-20230430013119763](assets/img/README/image-20230430013119763.png)

![image-20230430013148814](assets/img/README/image-20230430013148814.png)



## Command Line

```bash
git clone https://github.com/Grant-Felix/waydroid_script_fork
cd waydroid_script_fork
python3 -m venv venv
venv/bin/pip install -r requirements.txt
# install something
sudo venv/bin/python3 main.py install {gapps, magisk, libndk, libhoudini, nodataperm, smartdock, microg, mitm}
# uninstall something
sudo venv/bin/python3 main.py uninstall {gapps, magisk, libndk, libhoudini, nodataperm, smartdock, microg}
# get Android device ID
sudo venv/bin/python3 main.py certified
# some hacks
sudo venv/bin/python3 main.py hack {nodataperm, hidestatusbar}
```

## Dependencies

"lzip" is required for this script to work, install it using your distribution's package manager:
### Arch, Manjaro and EndeavourOS based distributions:
	sudo pacman -S lzip
### Debian and Ubuntu based distributions:
	sudo apt install lzip
### RHEL, Fedora and Rocky based distributions:
	sudo dnf install lzip
### openSUSE based distributions:
	sudo zypper install lzip

## Install OpenGapps

![](assets/1.png)

Open terminal and switch to the directory where "main.py" is located then run:

    sudo venv/bin/python3 main.py install gapps

Then launch waydroid with:

    waydroid show-full-ui

After waydroid has finished booting, open terminal and switch to directory where "main.py" is located then run:

    sudo python3 main.py google
Copy the returned numeric ID, then open ["https://google.com/android/uncertified/?pli=1"](https://google.com/android/uncertified/?pli=1). Enter the ID and register it. Wait 10-20 minutes for device to get registered. Then clear Google Play Service's cache and try logging in!


## Install Magisk

![](assets/2.png)

Open terminal and switch to directory where "main.py" is located then run:

    sudo venv/bin/python3 main.py install magisk

本 Fork 安装的是 **Kitsune Mask（Magisk Delta 续作）v27.2-kitsune-4**（`MAGISK_VER_CODE=27002`，内置 Zygisk），从本仓库自建 release 下载；版本、sha256 与两个下载地址见上文「本 Fork 的改动」。

Magisk will be installed on next boot! 

Zygisk and modules like LSPosed should work now.

### 从旧版（Magisk Delta 26.3 / Kitsune 31.0-kitsune）切换过来

新旧签名不同（旧版为 HuskyDG 签名，本版为 `TestKey-2024`），**必须先卸载旧管理器**，否则管理器无法覆盖安装：

```bash
sudo waydroid shell pm uninstall io.github.huskydg.magisk
sudo venv/bin/python3 main.py uninstall magisk
sudo venv/bin/python3 main.py install magisk
```

重启 Waydroid 后验证：

```bash
sudo waydroid shell magisk -v   # 期望 v27.2-kitsune-4
sudo waydroid shell magisk -V   # 期望 27002
```

> 重装会清空 `/data/adb/magisk`（模块列表与授权记录会丢），升级前建议先备份 `/data/adb/modules`。

If you want to update Magisk, Please use `Direct Install into system partition` or run this sript again.

This script only focuses on Magisk installation, if you need more management, please check https://github.com/nitanmarcel/waydroid-magisk

## Install libndk arm translation 

libndk_translation from guybrush firmware. 

libndk seems to have better performance than libhoudini on AMD.

Open terminal and switch to directory where "main.py" is located then run:

    sudo venv/bin/python3 main.py install libndk

## Install libhoudini arm translation

Intel's libhoudini for intel/AMD x86 CPU, pulled from Microsoft's WSA 11 image

houdini version: 11.0.1b_y.38765.m

houdini64 version: 11.0.1b_z.38765.m

Open terminal and switch to directory where "main.py" is located then run:

    sudo venv/bin/python3 main.py install libhoudini

## Integrate Widevine DRM (L3)

![](assets/3.png)

Open terminal and switch to directory where "main.py" is located then run:

    sudo venv/bin/python3 main.py install widevine

## Install Smart Dock

![](assets/4.png)
![](assets/5.png)

Open terminal and switch to directory where "main.py" is located then run:

    sudo venv/bin/python3 main.py install smartdock

## Install a self-signed CA certificate

Open terminal and switch to directory where "main.py" is located then run:

    sudo venv/bin/python3 main.py install mitm --ca-cert mycert.pem

## Granting full permission for apps data (HACK)


This is a temporary hack to combat against the apps permission issue on Android 11. Whenever an app is open it will always enable a property (persist.sys.nodataperm) to make it execute a script to grant the data full permissions (777). The **correct** way is to use `sdcardfs` or `esdfs`, both need to recompile the kernel or WayDroid image.

Arknights, PUNISHING: GRAY RAVEN and other games won't freeze on the black screen.

![](assets/6.png)

Open terminal and switch to directory where "main.py" is located then run:

```
sudo venv/bin/python3 main.py hack nodataperm
```
**WARNING**: Tested on `lineage-18.1-20230128-VANILLA-waydroid_x86_64.img`. This script will replace `/system/framework/service.jar`, which may prevent WayDroid from booting. If so, run `sudo venv/bin/python3 main.py uninstall nodataperm` to remove it.


Or you can run the following commands directly in `sudo waydroid shell`. In this way, every time a new game is installed, you need to run it again, but it's much less risky.

```
chmod 777 -R /sdcard/Android
chmod 777 -R /data/media/0/Android 
chmod 777 -R /sdcard/Android/data
chmod 777 -R /data/media/0/Android/obb 
chmod 777 -R /mnt/*/*/*/*/Android/data
chmod 777 -R /mnt/*/*/*/*/Android/obb
```

- https://github.com/supremegamers/device_generic_common/commit/2d47891376c96011b2ee3c1ccef61cb48e15aed6  
- https://github.com/supremegamers/android_frameworks_base/commit/24a08bf800b2e461356a9d67d04572bb10b0e819

## Install microG, Aurora Store and Aurora Droid

![](assets/7.png)

```
sudo venv/bin/python3 main.py install microg
```

## Hide Status Bar
Before
![Before](assets/8.png)

After
![After](assets/9.png)

```
sudo venv/bin/python3 main.py hack hidestatusbar
```


## Get Android ID for device registration

You need to register you device with its it before being able to use gapps, this will print out your Android ID which you can use for device registration required for Google apps:
Open terminal and switch to directory where "main.py" is located then run:

    sudo venv/bin/python3 main.py certified

Star this repository if you find this useful, if you encounter problem create an issue on GitHub!

## Error handling  

- Magisk installed: N/A

Check [waydroid-magisk](https://github.com/nitanmarcel/waydroid-magisk)

## Credits
- [WayDroid](https://github.com/waydroid/waydroid)
- [Kitsune Mask（Magisk Delta 续作）· 本 Fork 所用 v27.2-kitsune-4 的上游](https://github.com/AndnixSH/KitsuneMagisk)
- [本 Fork 自建的 Magisk release](https://github.com/Grant-Felix/KitsuneMagiskFork/releases/tag/v27.2-kitsune-4)
- [microG Project](https://microg.org)
- [Open GApps](https://opengapps.org)
- [Smart Dock](https://github.com/axel358/smartdock)
- [wd-scripts](https://github.com/electrikjesus/wd-scripts/)
