#!/usr/bin/env bash
# 收集 Waydroid 上 Kitsune/Magisk 安装失败的诊断信息（只读，不修改系统）
# 用法：bash diagnose_mask.sh            # 输出到屏幕
#      bash diagnose_mask.sh > /tmp/mask.log 2>&1   # 存成文件后发出来
set -uo pipefail

sec() { echo; echo "==================== $* ===================="; }

sec "1. 主机/版本信息"
uname -a
(head -2 /etc/os-release) 2>/dev/null
(waydroid --version) 2>&1 | head -2
(sudo waydroid status) 2>&1 | head -8

sec "2. waydroid 数据目录"
ls -la /var/lib/waydroid 2>&1 | head -15

sec "3. overlay 中的 magisk 目录 / bootanim.rc"
for d in /var/lib/waydroid/overlay /var/lib/waydroid/overlay_rw /tmp/waydroid; do
  [ -e "$d" ] || continue
  echo "-- $d"
  find "$d" -maxdepth 7 \( -path '*init/magisk*' -o -name 'bootanim.rc*' \) 2>/dev/null | head -15
done
echo "-- magisk 目录内容（取前 30 项，含大小）"
MAGISKDIR="$(find /var/lib/waydroid -maxdepth 8 -type d -path '*etc/init/magisk' 2>/dev/null | head -1)"
[ -n "${MAGISKDIR:-}" ] && ls -la "$MAGISKDIR" | head -30 || echo "   未找到 etc/init/magisk 目录"

sec "4. bootanim.rc 里的 magisk 钩子"
f="$(find /var/lib/waydroid -maxdepth 8 -name 'bootanim.rc' 2>/dev/null | head -1)"
if [ -n "${f:-}" ]; then echo "-- $f"; tail -30 "$f"; else echo "   未找到 bootanim.rc"; fi

sec "5. 宿主映射的 /data/adb"
for p in "$HOME/.local/share/waydroid/data/adb" /var/lib/waydroid/data/adb; do
  [ -e "$p" ] || continue
  echo "-- $p"
  ls -la "$p" | head
  [ -d "$p/magisk" ] && { echo "   -- magisk/"; ls -la "$p/magisk" | head -20; }
done

sec "6. 设备内的管理器与 magisk 目录"
sudo waydroid shell -- pm list packages 2>/dev/null | grep -iE 'huskydg|magisk|kitsune' || echo "   没有匹配的包（管理器未安装？）"
sudo waydroid shell -- ls -la /system/etc/init/magisk 2>&1 | head -20

sec "7. 设备内版本探测"
sudo waydroid shell -- /system/etc/init/magisk/magisk64 -c 2>&1 | head -3
sudo waydroid shell -- /data/adb/magisk/magisk64 -c 2>&1 | head -3
sudo waydroid shell -- magisk -v 2>&1 | head -3
sudo waydroid shell -- magisk -V 2>&1 | head -3

sec "8. 相关日志（logcat / dmesg，尾部）"
sudo waydroid shell -- logcat -d 2>/dev/null | grep -iE 'magisk|zygisk|selinux|init: ' | tail -60
sudo waydroid shell dmesg 2>/dev/null | grep -iE 'magisk|init:' | tail -40

sec "9. 安装日志（如已保存）"
ls -la /tmp/magisk_install*.log 2>/dev/null || echo "   无；建议下次用： sudo venv/bin/python3 main.py install magisk 2>&1 | tee /tmp/magisk_install.log"

sec "10. 当前脚本下载源"
grep -n 'dl_link' "${WAYDROID_SCRIPT_DIR:-$PWD}/stuff/magisk.py" 2>/dev/null || echo "   未在 $PWD 找到 stuff/magisk.py（请在脚本目录内运行，或设 WAYDROID_SCRIPT_DIR）"

echo
echo "===== 诊断收集完成，请把以上输出（或 /tmp/mask.log）发出来 ====="
