#!/usr/bin/env bash
set -euo pipefail

# Installer script for aaaav multi-platform plugin
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
    rm -rf "$HOME/.gemini/config/plugins/aaaavr" "$HOME/.gemini/config/plugins/aaaav-loop-boot" "$HOME/.gemini/config/plugins/weihung-loop-boot"
    local agy_plugin_dir="$HOME/.gemini/config/plugins/aaaav"
    link_target "$REPO_ROOT" "$agy_plugin_dir"
}

# 2. Claude Code installation
install_claude() {
    echo "=== Installing for Claude Code ==="
    # Remove stale plugin artifacts
    rm -rf "$HOME/.claude/plugins/aaaavr" "$HOME/.claude/plugins/aaaav-loop-boot" "$HOME/.claude/plugins/weihung-loop-boot"
    if command -v claude >/dev/null 2>&1; then
        if [ "$DRY_RUN" = true ]; then
            echo "[DRY RUN] Would register marketplace and install aaaav plugin via claude CLI"
            return
        fi
        claude plugin uninstall aaaavr@aaaavr 2>/dev/null || true
        claude plugin marketplace remove aaaavr 2>/dev/null || true
        claude plugin uninstall weihung-loop-boot@weihung-loop-boot 2>/dev/null || true
        claude plugin marketplace remove weihung-loop-boot 2>/dev/null || true
        claude plugin uninstall aaaav-loop-boot@aaaav-loop-boot 2>/dev/null || true
        claude plugin marketplace remove aaaav-loop-boot 2>/dev/null || true
        claude plugin marketplace add "$REPO_ROOT" 2>/dev/null || true
        claude plugin marketplace update aaaav 2>/dev/null || true
        claude plugin install aaaav@aaaav 2>/dev/null || true
        claude plugin update aaaav@aaaav 2>/dev/null || true
        echo "Claude Code plugin registered via claude CLI."
    else
        local claude_plugin_dir="$HOME/.claude/plugins/aaaav"
        link_target "$REPO_ROOT" "$claude_plugin_dir"
    fi
}

# 3. Codex installation
# Codex loads aaaav skills from the installed aaaav@aaaav plugin cache, so this
# installer no longer symlinks skills into the deprecated ~/.codex/skills
# compatibility location. On machines where an earlier version of this
# installer created those symlinks, remove them so each skill is listed once.
cleanup_stale_codex_links() {
    local codex_skills_dir="$1"
    [ -d "$codex_skills_dir" ] || return 0

    local entry target
    while IFS= read -r -d '' entry; do
        target="$(readlink "$entry")"
        case "$target" in
            "$REPO_ROOT"/*)
                if [ "$DRY_RUN" = true ]; then
                    echo "[DRY RUN] Would remove stale Codex skill link: $entry -> $target"
                else
                    rm -f "$entry"
                    echo "Removed stale Codex skill link: $entry -> $target"
                fi
                ;;
        esac
    done < <(find "$codex_skills_dir" -maxdepth 1 -type l -print0)
}

install_codex() {
    echo "=== Installing for Codex ==="
    cleanup_stale_codex_links "$HOME/.codex/skills"
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
