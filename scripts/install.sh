#!/usr/bin/env bash
set -euo pipefail

# Installer script for weihung-loop-boot multi-platform plugin
# Supports: Antigravity (agy), Claude Code (claude), OpenAI Codex (codex)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TARGET="all"
FORCE=false
DRY_RUN=false

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --target <all|agy|claude|codex>   Target platform to install into (default: all)
  --force                           Replace existing installations safely
  --dry-run                         Show actions without modifying filesystem
  -h, --help                        Show this help message
EOF
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)
            TARGET="$2"
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage
            ;;
    esac
done

link_target() {
    local src="$1"
    local dest="$2"
    local dest_dir
    dest_dir="$(dirname "$dest")"

    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would link $src -> $dest"
        return
    fi

    mkdir -p "$dest_dir"

    if [ -e "$dest" ] || [ -L "$dest" ]; then
        if [ "$FORCE" = true ]; then
            echo "Replacing existing: $dest"
            rm -rf "$dest"
        else
            echo "Destination already exists (use --force to overwrite): $dest"
            return
        fi
    fi

    ln -s "$src" "$dest"
    echo "Linked: $dest -> $src"
}

# 1. Antigravity installation
install_agy() {
    echo "=== Installing for Antigravity ==="
    local agy_plugin_dir="$HOME/.gemini/config/plugins/weihung-loop-boot"
    link_target "$REPO_ROOT" "$agy_plugin_dir"
}

# 2. Claude Code installation
install_claude() {
    echo "=== Installing for Claude Code ==="
    local claude_plugin_dir="$HOME/.claude/plugins/weihung-loop-boot"
    link_target "$REPO_ROOT" "$claude_plugin_dir"
}

# 3. Codex installation
install_codex() {
    echo "=== Installing for Codex ==="
    local codex_skills_dir="$HOME/.codex/skills"
    mkdir -p "$codex_skills_dir"
    for skill_path in "$REPO_ROOT"/skills/*; do
        if [ -d "$skill_path" ]; then
            local skill_name
            skill_name="$(basename "$skill_path")"
            link_target "$skill_path" "$codex_skills_dir/$skill_name"
        fi
    done
}

case "$TARGET" in
    agy)
        install_agy
        ;;
    claude)
        install_claude
        ;;
    codex)
        install_codex
        ;;
    all)
        install_agy
        install_claude
        install_codex
        ;;
    *)
        echo "Invalid target: $TARGET" >&2
        usage
        ;;
esac

echo "Installation complete."
