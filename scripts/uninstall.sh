#!/usr/bin/env bash
set -euo pipefail

# Uninstaller script for aaaav multi-platform plugin
# Supports: Antigravity (agy), Claude Code (claude), OpenAI Codex (codex)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TARGET="all"
DRY_RUN=false

usage() {
    cat <<EOU
Usage: $(basename "$0") [OPTIONS]

Options:
  --target <all|agy|claude|codex>   Target platform to uninstall from (default: all)
  --dry-run                         Show actions without modifying filesystem
  -h, --help                        Show this help message
EOU
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)
            TARGET="$2"
            shift 2
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

remove_target() {
    local target="$1"
    if [ -e "$target" ] || [ -L "$target" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "[DRY RUN] Would remove $target"
        else
            rm -rf "$target"
            echo "Removed: $target"
        fi
    fi
}

uninstall_agy() {
    echo "=== Uninstalling from Antigravity ==="
    remove_target "$HOME/.gemini/config/plugins/aaaav"
    remove_target "$HOME/.gemini/config/plugins/aaaavr"
    remove_target "$HOME/.gemini/config/plugins/aaaav-loop-boot"
    remove_target "$HOME/.gemini/config/plugins/weihung-loop-boot"
}

uninstall_claude() {
    echo "=== Uninstalling from Claude Code ==="
    if command -v claude >/dev/null 2>&1; then
        if [ "$DRY_RUN" = true ]; then
            echo "[DRY RUN] Would uninstall aaaav and old plugins via claude CLI"
        else
            claude plugin uninstall aaaav@aaaav 2>/dev/null || true
            claude plugin marketplace remove aaaav 2>/dev/null || true
            claude plugin uninstall aaaavr@aaaavr 2>/dev/null || true
            claude plugin marketplace remove aaaavr 2>/dev/null || true
            claude plugin uninstall aaaav-loop-boot@aaaav-loop-boot 2>/dev/null || true
            claude plugin marketplace remove aaaav-loop-boot 2>/dev/null || true
            claude plugin uninstall weihung-loop-boot@weihung-loop-boot 2>/dev/null || true
            claude plugin marketplace remove weihung-loop-boot 2>/dev/null || true
        fi
    fi
    remove_target "$HOME/.claude/plugins/aaaav"
    remove_target "$HOME/.claude/plugins/aaaavr"
    remove_target "$HOME/.claude/plugins/aaaav-loop-boot"
    remove_target "$HOME/.claude/plugins/weihung-loop-boot"
}

uninstall_codex() {
    echo "=== Uninstalling from Codex ==="
    local codex_skills_dir="$HOME/.codex/skills"
    for skill_path in "$REPO_ROOT"/skills/*; do
        if [ -d "$skill_path" ]; then
            local skill_name
            skill_name="$(basename "$skill_path")"
            remove_target "$codex_skills_dir/$skill_name"
        fi
    done
}

case "$TARGET" in
    agy)
        uninstall_agy
        ;;
    claude)
        uninstall_claude
        ;;
    codex)
        uninstall_codex
        ;;
    all)
        uninstall_agy
        uninstall_claude
        uninstall_codex
        ;;
    *)
        echo "Invalid target: $TARGET" >&2
        usage
        ;;
esac

echo "Uninstall complete."
