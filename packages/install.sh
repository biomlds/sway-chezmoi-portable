#!/bin/sh
set -eu

usage() {
    cat <<'USAGE'
Usage: packages/install.sh [--tier required|recommended|optional] [--dry-run]
                           [--list] [--verify-only] [--distro debian|ubuntu|fedora]

Normal operation detects ID from /etc/os-release. --distro exists for CI/static
validation only. Tier selection is cumulative: recommended includes required;
optional includes all three tiers.
USAGE
}

tier=recommended
dry_run=false
list_only=false
verify_only=false
distro_override=
while [ "$#" -gt 0 ]; do
    case "$1" in
        --tier) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; tier=$2; shift 2 ;;
        --dry-run) dry_run=true; shift ;;
        --list) list_only=true; shift ;;
        --verify-only) verify_only=true; shift ;;
        --distro) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; distro_override=$2; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done
case "$tier" in required|recommended|optional) ;; *) printf 'Invalid tier: %s\n' "$tier" >&2; exit 2 ;; esac

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
manifest=$script_dir/components.tsv
[ -r "$manifest" ] || { printf 'Missing manifest: %s\n' "$manifest" >&2; exit 1; }

if [ -n "$distro_override" ]; then
    distro=$distro_override
else
    [ -r /etc/os-release ] || { printf 'Cannot detect distribution: /etc/os-release is missing\n' >&2; exit 1; }
    # shellcheck disable=SC1091
    . /etc/os-release
    distro=${ID:-}
fi
case "$distro" in
    debian) column=3; manager=apt ;;
    ubuntu) column=4; manager=apt ;;
    fedora) column=5; manager=dnf ;;
    *) printf 'Unsupported distribution ID: %s (supported: debian, ubuntu, fedora)\n' "$distro" >&2; exit 1 ;;
esac

case "$tier" in required) max_rank=1 ;; recommended) max_rank=2 ;; optional) max_rank=3 ;; esac
packages=$(awk -F '\t' -v col="$column" -v max="$max_rank" '
    NR == 1 { next }
    $2 == "required" { rank=1 }
    $2 == "recommended" { rank=2 }
    $2 == "optional" { rank=3 }
    rank <= max && $col != "" && $col != "-" { print $col }
' "$manifest" | awk '!seen[$0]++')

[ -n "$packages" ] || { printf 'No packages mapped for %s/%s\n' "$distro" "$tier" >&2; exit 1; }
printf 'Distribution: %s; manager: %s; tier: %s\n' "$distro" "$manager" "$tier"
if $list_only || $dry_run; then
    printf '%s\n' "$packages"
    $list_only && exit 0
fi
if $dry_run; then exit 0; fi

if [ "$manager" = apt ]; then
    command -v apt-get >/dev/null 2>&1 || { printf 'apt-get is unavailable\n' >&2; exit 1; }
    command -v dpkg-query >/dev/null 2>&1 || { printf 'dpkg-query is unavailable\n' >&2; exit 1; }
    sudo_cmd=
    [ "$(id -u)" -eq 0 ] || sudo_cmd=sudo
    command -v ${sudo_cmd:-true} >/dev/null 2>&1 || { printf 'sudo is required for a non-root install\n' >&2; exit 1; }
    $sudo_cmd apt-get update
    unavailable=
    for pkg in $packages; do
        if ! apt-cache show "$pkg" >/dev/null 2>&1; then unavailable="$unavailable $pkg"; fi
    done
    [ -z "$unavailable" ] || { printf 'Unavailable in enabled standard APT repositories:%s\n' "$unavailable" >&2; exit 1; }
    $verify_only && exit 0
    missing=
    for pkg in $packages; do
        dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q 'ok installed' || missing="$missing $pkg"
    done
    if [ -n "$missing" ]; then $sudo_cmd apt-get install --no-install-recommends -y $missing; else printf 'All selected packages are already installed.\n'; fi
else
    command -v dnf >/dev/null 2>&1 || { printf 'dnf is unavailable\n' >&2; exit 1; }
    sudo_cmd=
    [ "$(id -u)" -eq 0 ] || sudo_cmd=sudo
    command -v ${sudo_cmd:-true} >/dev/null 2>&1 || { printf 'sudo is required for a non-root install\n' >&2; exit 1; }
    unavailable=
    for pkg in $packages; do
        if ! dnf -q list --available "$pkg" >/dev/null 2>&1 && ! rpm -q "$pkg" >/dev/null 2>&1; then unavailable="$unavailable $pkg"; fi
    done
    [ -z "$unavailable" ] || { printf 'Unavailable in enabled standard DNF repositories:%s\n' "$unavailable" >&2; exit 1; }
    $verify_only && exit 0
    missing=
    for pkg in $packages; do rpm -q "$pkg" >/dev/null 2>&1 || missing="$missing $pkg"; done
    if [ -n "$missing" ]; then $sudo_cmd dnf install -y $missing; else printf 'All selected packages are already installed.\n'; fi
fi
