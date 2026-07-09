#!/bin/sh
# 自动安装钩子：链接 .hooks/ 到 .git/hooks/
# 在 Windows 上可能需要手动复制

HOOKS_DIR="$(git rev-parse --show-toplevel)/.hooks"
GIT_HOOKS_DIR="$(git rev-parse --show-toplevel)/.git/hooks"

for hook in "$HOOKS_DIR"/*; do
    name=$(basename "$hook")
    target="$GIT_HOOKS_DIR/$name"
    if [ -f "$target" ] && [ ! -L "$target" ]; then
        mv "$target" "$target.bak"
        echo "  备份已有钩子: $name.bak"
    fi
    ln -sf "../../.hooks/$name" "$target"
    echo "  安装: $name"
done
echo "钩子安装完成"