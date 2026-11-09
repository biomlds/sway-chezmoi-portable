#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
fail=0
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT HUP INT TERM
ok() { printf 'ok: %s\n' "$1"; }
bad() { printf 'FAIL: %s\n' "$1" >&2; fail=1; }

[ "$(cat .chezmoiroot)" = dotfiles ] && ok '.chezmoiroot points to dotfiles' || bad '.chezmoiroot'
[ -f dotfiles/.chezmoidata.yaml ] && [ -d dotfiles/.chezmoitemplates ] && ok 'chezmoi data/templates present' || bad 'chezmoi data/templates'

for f in packages/install.sh dotfiles/private_dot_local/bin/executable_*; do
    case "$f" in *desktop-idle|*desktop-open-browser) continue ;; esac
    sh -n "$f" || bad "shell syntax: $f"
    [ -x "$f" ] || bad "not executable: $f"
done
ok 'plain shell scripts parse and are executable'

for f in dotfiles/private_dot_local/bin/*.tmpl dotfiles/run_*.tmpl; do
    tmp=$(mktemp)
    sed '/^[[:space:]]*{{.*}}[[:space:]]*$/d; s/{{[^}]*}}/value/g' "$f" > "$tmp"
    sh -n "$tmp" || bad "templated shell syntax: $f"
    rm -f "$tmp"
done
ok 'templated shell files pass reduced shell parse'

for distro in debian ubuntu fedora; do
    packages/install.sh --dry-run --distro "$distro" --tier optional > "$tmpdir/$distro.txt" || bad "$distro package resolution"
    grep -q '^sway$' "$tmpdir/$distro.txt" && grep -q '^waybar$' "$tmpdir/$distro.txt" || bad "$distro core mappings"
    ok "$distro mapping resolves"
done

awk -F '\t' 'NR==1 { if (NF != 6) exit 1; next } NF != 6 || ($2!="required" && $2!="recommended" && $2!="optional") || $3=="" || $4=="" || $5=="" { exit 1 }' packages/components.tsv \
    && ok 'package manifest shape and tiers' || bad 'package manifest shape and tiers'

python3 - <<'PY' || exit 1
import json
json.load(open('dotfiles/dot_config/waybar/config'))
print('ok: Waybar strict JSON')
PY

python3 - <<'PY' || exit 1
from pathlib import Path
for p in Path('dotfiles').rglob('*.tmpl'):
    s=p.read_text()
    if s.count('{{') != s.count('}}'):
        raise SystemExit(f'unbalanced template actions: {p}')
for p in list(Path('dotfiles').rglob('*.css'))+list(Path('dotfiles').rglob('*.css.tmpl')):
    s=p.read_text()
    if s.count('{') != s.count('}'):
        raise SystemExit(f'unbalanced CSS braces: {p}')
p=Path('dotfiles/private_dot_local/share/backgrounds/sway-aurora.png')
if p.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
    raise SystemExit('invalid PNG signature')
print('ok: template delimiters, CSS braces, and PNG signature')
PY

for name in $(grep -Rho '~/.local/bin/desktop-[a-z-]*' dotfiles/dot_config/sway | sed 's#~/.local/bin/##' | sort -u); do
    [ -f "dotfiles/private_dot_local/bin/executable_$name" ] || [ -f "dotfiles/private_dot_local/bin/executable_$name.tmpl" ] || bad "missing helper: $name"
done
ok 'Sway helper references resolve'

for command in sway waybar wofi foot mako swaylock swayidle swaybg grim slurp wl-copy wl-paste wpctl brightnessctl playerctl; do
    case "$command" in
      wl-copy|wl-paste) component=clipboard ;;
      wpctl) component=audio-session ;;
      playerctl) component=media-keys ;;
      brightnessctl) component=brightness ;;
      mako) component=notifications ;;
      foot) component=terminal ;;
      wofi) component=launcher ;;
      swaylock) component=lock ;;
      swayidle) component=idle ;;
      swaybg) component=wallpaper ;;
      grim) component=screenshot-full ;;
      slurp) component=screenshot-region ;;
      sway) component=sway ;;
      waybar) component=status-bar ;;
    esac
    awk -F '\t' -v c="$component" 'NR>1 && $1==c {found=1} END {exit !found}' packages/components.tsv || bad "unmapped command: $command"
done
ok 'referenced desktop commands have package components'

if command -v chezmoi >/dev/null 2>&1; then
    printf 'note: chezmoi found; run the documented init/diff workflow in a disposable HOME for full rendering\n'
else
    printf 'skip: chezmoi binary not installed; source-state rendering requires a supported host\n'
fi
if command -v sway >/dev/null 2>&1; then printf 'note: sway found; full validation requires a rendered HOME and runtime seat\n'; else printf 'skip: sway binary not installed; syntax validation is static only\n'; fi
python3 scripts/test-desktop.py

[ "$fail" -eq 0 ] || exit 1
printf 'Validation completed successfully.\n'
