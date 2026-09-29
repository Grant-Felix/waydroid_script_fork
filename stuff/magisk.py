import gzip
import os
import shutil
import re
import zipfile
from stuff.general import General
from tools.helper import download_file, get_data_dir, host
from tools.logger import Logger
from tools import container

class Magisk(General):
    id = "magisk delta"
    partition = "system"
    # Kitsune Mask (Magisk Delta) v27.2-kitsune-4 —— 该谱系最后一个真实版本号（MAGISK_VER_CODE=27002，保留内置 Zygisk）
    # 资源：Kitsune.Magisk.release.v27.2-kitsune-4.apk (12,770,643 bytes)
    # sha256: 818cfa02783ddae573cc953450fbc39ec3e5164b66e517c657ba11cf90963a89
    # 旧下载源（Delta 26.3，2024-01 构建，已停更）：https://github.com/mistrmochov/magiskdeltaorig/raw/main/app-release.apk
    dl_link = "https://github.com/Grant-Felix/KitsuneMagiskFork/releases/download/v27.2-kitsune-4/Kitsune.Magisk.release.v27.2-kitsune-4.apk"
    # 镜像（备用）：https://github.com/Grant-Felix/waydroid_script_fork/releases/download/magisk-v27.2-kitsune-4/Kitsune.Magisk.release.v27.2-kitsune-4.apk
    dl_file_name = "magisk.apk"
    extract_to = "/tmp/magisk_unpack"
    magisk_dir = os.path.join(partition, "etc", "init", "magisk")
    files = ["etc/init/magisk", "etc/init/bootanim.rc"]
    oringinal_bootanim = """
service bootanim /system/bin/bootanimation
    class core animation
    user graphics
    group graphics audio
    disabled
    oneshot
    ioprio rt 0
    task_profiles MaxPerformance
    
"""
    bootanim_component = f"""
on post-fs-data
    start logd
    exec u:r:su:s0 root root -- /system/etc/init/magisk/magiskpolicy --live --magisk
    exec u:r:magisk:s0 root root -- /system/etc/init/magisk/magiskpolicy --live --magisk
    exec u:r:update_engine:s0 root root -- /system/etc/init/magisk/magiskpolicy --live --magisk
    mkdir /dev/magisk_iqeoVo2mDrO 700
    exec u:r:su:s0 root root -- /system/etc/init/magisk/magisk64 --auto-selinux --setup-sbin /system/etc/init/magisk /dev/magisk_iqeoVo2mDrO
    exec u:r:su:s0 root root -- /dev/magisk_iqeoVo2mDrO/magisk --auto-selinux --post-fs-data

on nonencrypted
    exec u:r:su:s0 root root -- /dev/magisk_iqeoVo2mDrO/magisk --auto-selinux --service

on property:vold.decrypt=trigger_restart_framework
    exec u:r:su:s0 root root -- /dev/magisk_iqeoVo2mDrO/magisk --auto-selinux --service

on property:sys.boot_completed=1
    mkdir /data/adb/magisk 755
    exec u:r:su:s0 root root -- /dev/magisk_iqeoVo2mDrO/magisk --auto-selinux --boot-complete
   
on property:init.svc.zygote=restarting
    exec u:r:su:s0 root root -- /dev/magisk_iqeoVo2mDrO/magisk --auto-selinux --zygote-restart
   
on property:init.svc.zygote=stopped
    exec u:r:su:s0 root root -- /dev/magisk_iqeoVo2mDrO/magisk --auto-selinux --zygote-restart
    """

    def download(self):
        # 离线 / 镜像支持（网络受限时很有用）：
        #   WAYDROID_MAGISK_APK=/path/to/Kitsune.Magisk.release.v27.2-kitsune-4.apk
        #       直接用本地 APK，完全不联网
        #   WAYDROID_MAGISK_URLS="https://mirror1/x.apk,https://mirror2/x.apk"
        #       在 dl_link 之后依次尝试的备用地址，全部失败才报错
        local_apk = os.environ.get("WAYDROID_MAGISK_APK")
        if local_apk:
            if not os.path.isfile(local_apk):
                raise FileNotFoundError("WAYDROID_MAGISK_APK 指向的文件不存在: {}".format(local_apk))
            Logger.info("Using local Magisk APK: {} -> {}".format(local_apk, self.download_loc))
            shutil.copyfile(local_apk, self.download_loc)
            return

        if os.path.isfile(self.download_loc):
            os.remove(self.download_loc)

        urls = [self.dl_link]
        urls += [u.strip() for u in os.environ.get("WAYDROID_MAGISK_URLS", "").split(",") if u.strip()]

        last_error = None
        for url in urls:
            try:
                Logger.info("Downloading Magisk-Delta to {} now ...\n  from {}".format(self.download_loc, url))
                download_file(url, self.download_loc)
                # 简单校验：必须是带 AndroidManifest.xml 的完整 APK
                with zipfile.ZipFile(self.download_loc) as z:
                    if "AndroidManifest.xml" not in z.namelist():
                        raise ValueError("下载内容不是有效的 APK")
                return
            except Exception as e:
                last_error = e
                Logger.warning("下载失败（{}）：{}".format(url, e))
                if os.path.isfile(self.download_loc):
                    os.remove(self.download_loc)

        raise RuntimeError(
            "所有下载地址都失败，最后一个错误：{}\n"
            "可改用离线安装： WAYDROID_MAGISK_APK=/path/to/apk sudo -E venv/bin/python3 main.py install magisk\n"
            "或指定镜像： WAYDROID_MAGISK_URLS=\"https://your-mirror/x.apk\" sudo -E venv/bin/python3 main.py install magisk".format(last_error))

    # require additional setup
    def setup(self):
        Logger.info("Additional setup")
        magisk_absolute_dir = os.path.join(self.copy_dir, self.magisk_dir)
        data_dir = get_data_dir()
        shutil.copytree(magisk_absolute_dir, os.path.join(data_dir, "adb", "magisk"), dirs_exist_ok=True)

    def copy(self):
        magisk_absolute_dir = os.path.join(self.copy_dir, self.magisk_dir)
        if not os.path.exists(magisk_absolute_dir):
            os.makedirs(magisk_absolute_dir, exist_ok=True)

        if not os.path.exists(os.path.join(self.copy_dir, "sbin")):
            os.makedirs(os.path.join(self.copy_dir, "sbin"), exist_ok=True)

        Logger.info("Copying magisk libs now ...")
        
        lib_dir = os.path.join(self.extract_to, "lib", self.arch[0])
        for parent, dirnames, filenames in os.walk(lib_dir):
            for filename in filenames:
                o_path = os.path.join(lib_dir, filename)  
                filename = re.search('lib(.*)\.so', filename)
                n_path = os.path.join(magisk_absolute_dir, filename.group(1))
                shutil.copyfile(o_path, n_path)
        shutil.copyfile(self.download_loc, os.path.join(magisk_absolute_dir,"magisk.apk") )
        shutil.copytree(os.path.join(self.extract_to, "assets", "chromeos"), os.path.join(magisk_absolute_dir, "chromeos"), dirs_exist_ok=True)
        assets_files = [
            "addon.d.sh",
            "boot_patch.sh",
            "stub.apk",
            "util_functions.sh"
        ]
        for f in assets_files:
            shutil.copyfile(os.path.join(self.extract_to, "assets", f), os.path.join(magisk_absolute_dir, f))

        # Updating Magisk from Magisk manager will modify bootanim.rc, 
        # So it is necessary to backup the original bootanim.rc.
        bootanim_path = os.path.join(self.copy_dir, self.partition, "etc", "init", "bootanim.rc")
        gz_filename = os.path.join(bootanim_path)+".gz"
        with gzip.open(gz_filename,'wb') as f_gz:
            f_gz.write(self.oringinal_bootanim.encode('utf-8'))
        with open(bootanim_path, "w") as initfile:
            initfile.write(self.oringinal_bootanim+self.bootanim_component)

    def set_path_perm(self, path):
        if "magisk" in path.split("/"):
            perms = [0, 2000, 0o755, 0o755]
        else:
            perms = [0, 0, 0o755, 0o644]

        mode = os.stat(path).st_mode

        if os.path.isdir(path):
            mode |= perms[2]
        else:
            mode |= perms[3]

        os.chown(path, perms[0], perms[1])
        os.chmod(path, mode)

    def extra1(self):
        self.delete_upper()
        self.setup()
    
    # Delete the contents of upperdir
    def delete_upper(self):
        if container.use_overlayfs():
            sys_overlay_rw = "/var/lib/waydroid/overlay_rw"
            files = [
                "system/system/etc/init/bootanim.rc",
                "system/system/etc/init/bootanim.rc.gz",
                "system/system/etc/init/magisk",               
                "system/system/addon.d/99-magisk.sh",
                "vendor/etc/selinux/precompiled_sepolicy"
            ]

            for f in files:
                file = os.path.join(sys_overlay_rw, f)
                if os.path.isdir(file):
                    shutil.rmtree(file)
                elif os.path.isfile(file) or os.path.exists(file):
                    os.remove(file)
    
    def extra2(self):
        self.delete_upper()
        data_dir = get_data_dir()
        files = [
            os.path.join(data_dir, "adb/magisk.db"),
            os.path.join(data_dir, "adb/magisk")
        ]
        for file in files:
            if os.path.isdir(file):
                shutil.rmtree(file)
            elif os.path.isfile(file):
                os.remove(file)
        bootanim_path = os.path.join(self.copy_dir, self.partition, "etc", "init", "bootanim.rc")
        if container.use_overlayfs():
            if os.path.exists(bootanim_path):
                os.remove(bootanim_path)
        else:
            with open(bootanim_path, "w") as initfile:
                initfile.write(self.oringinal_bootanim)
