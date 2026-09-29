#!/usr/bin/env bash
# Waydroid Extras Script (Fork) 一键准备脚本
# 仓库：https://github.com/Grant-Felix/waydroid_script_fork
#
# 用法：
#   bash setup.sh                          # 克隆/更新 + 建 venv + 装依赖，然后打印后续命令
#   bash setup.sh install magisk           # 准备完直接执行 main.py install magisk
#   bash setup.sh -d ~/wds install magisk  # 指定安装目录
set -euo pipefail

REPO="https://github.com/Grant-Felix/waydroid_script_fork.git"
DIR="${WAYDROID_SCRIPT_DIR:-$PWD/waydroid_script_fork}"

usage() { sed -n '2,9p' "$0"; }

while getopts "d:h" opt; do
  case "$opt" in
    d) DIR="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done
shift $((OPTIND - 1))

command -v git >/dev/null || { echo "缺少 git" >&2; exit 1; }
command -v python3 >/dev/null || { echo "缺少 python3" >&2; exit 1; }
command -v lzip >/dev/null || echo "提示：未找到 lzip，部分解压会失败（Debian: sudo apt install lzip / Arch: sudo pacman -S lzip）"

echo "==> 目标目录：$DIR"
if [ -d "$DIR/.git" ]; then
  echo "==> 更新仓库"
  git -C "$DIR" pull --ff-only
else
  echo "==> 克隆 $REPO"
  git clone --depth 1 "$REPO" "$DIR"
fi

cd "$DIR"
[ -d venv ] || { echo "==> 创建 venv"; python3 -m venv venv; }
echo "==> 安装 Python 依赖"
venv/bin/pip install -q --upgrade pip
venv/bin/pip install -q -r requirements.txt

MAGISK_NOTE="注意：从旧的 Delta 26.3 / Kitsune 31.0-kitsune 切换过来时，签名不同，请先卸载旧管理器：
  sudo waydroid shell pm uninstall io.github.huskydg.magisk"

if [ "$#" -gt 0 ]; then
  echo "==> 执行：sudo venv/bin/python3 main.py $*"
  exec sudo venv/bin/python3 main.py "$@"
fi

cat <<EOF

准备完成。接下来可以：

  cd "$DIR"
  sudo venv/bin/python3 main.py                    # 交互界面
  sudo venv/bin/python3 main.py install magisk     # 安装 Kitsune Mask v27.2-kitsune-4（自建 release 下载）

$MAGISK_NOTE
EOF
