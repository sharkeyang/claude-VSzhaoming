"""安装 Git 钩子（Windows 版）"""
import os
import shutil
import sys


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hooks_src = os.path.join(root, ".hooks")
    hooks_dst = os.path.join(root, ".git", "hooks")

    if not os.path.exists(hooks_src):
        print(f"错误: 找不到 .hooks 目录: {hooks_src}")
        sys.exit(1)

    installed = 0
    backed_up = 0
    for name in os.listdir(hooks_src):
        src = os.path.join(hooks_src, name)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(hooks_dst, name)
        if os.path.exists(dst) and not os.path.islink(dst):
            bak = dst + ".bak"
            shutil.move(dst, bak)
            print(f"  备份: {name} -> {name}.bak")
            backed_up += 1
        shutil.copy2(src, dst)
        print(f"  安装: {name}")
        installed += 1

    print(f"\n完成！已安装 {installed} 个钩子，备份 {backed_up} 个原有钩子")
    print("提示：在 CI/CD 环境中也需要运行此脚本")


if __name__ == "__main__":
    main()