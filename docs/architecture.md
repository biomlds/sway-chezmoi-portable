# Architecture and extension guide

## Boundaries

1. **Repository infrastructure** — `.chezmoiroot`, `packages/`, `scripts/`, and `docs/` are not home-directory targets.
2. **Chezmoi source state** — `dotfiles/` contains only managed targets, templates, data, and lifecycle scripts.
3. **Shared Linux/Sway layer** — one Sway, Waybar, Wofi, Mako, Foot, GTK, Qt, portal, environment, helper, and wallpaper implementation is shared by every supported distribution.
4. **Distribution boundary** — `packages/components.tsv`, the package-manager case in `packages/install.sh`, `10-distro.conf.tmpl`, and the polkit path probe are the only distro-sensitive areas.
5. **Host boundary** — unmanaged `~/.config/sway/hosts/*.conf` files contain output/input identifiers and other physical-machine details.
6. **User data boundary** — safe non-secret preferences are source defaults in `.chezmoidata.yaml` and per-machine overrides in the user's chezmoi configuration. Secrets do not belong in either file.

## Why these decisions

- A root `.chezmoiroot` avoids treating repository docs/package tools as home files.
- A component table makes package intent reviewable and prevents apt/dnf commands from leaking into desktop scripts.
- Wofi was selected over Fuzzel because Ubuntu 24.04's standard index contains Wofi but not Fuzzel; this preserves the same launcher across all three first-class targets.
- Mako, Foot, swaylock, swayidle, grim, slurp, and wl-clipboard are small Wayland-native components available from standard repositories.
- A local power menu replaces wlogout, avoiding a nonessential dependency while retaining lock/logout/suspend/reboot/power-off workflows.
- Optional text clipboard history replaces cliphist. Disabled by default, it skips sensitive selections and stores at most 200 payloads of 1 MiB under the private XDG runtime directory; evicted payloads are deleted.
- Swaylock effects and compositor forks were rejected: the upstream lock screen, colors, and wallpaper provide visual consistency without a fragile source build.
- A runtime flock supervisor owns desktop daemons, watches compositor shutdown, and reaps its children on logout. Clipboard watcher/store locks are kernel-managed and recover after a crash. Waybar reloads in place via SIGUSR2.

## Layer flow

```text
shared chezmoi data + reusable palette
        |
        +-- Sway modules + helpers
        +-- Waybar/Wofi/Mako/Foot/GTK/Qt/portal config
        +-- common wallpaper and environment
        |
        +-- package component map
              +-- Debian apt column
              +-- Ubuntu apt column
              +-- Fedora dnf column
        |
        +-- optional unmanaged host overrides (loaded last)
```

## Adding another distribution

1. Add a package column to `packages/components.tsv`, mapping every required component. Use `-` only for a documented recommended/optional limitation; do not leave required components as placeholders.
2. Add the new `/etc/os-release` `ID` to the case in `packages/install.sh`, including its package manager and table column.
3. Add the ID to `dotfiles/dot_config/sway/config.d/10-distro.conf.tmpl`. Add desktop conditionals only if runtime behavior really differs.
4. If a binary path differs (for example, a polkit agent), extend the single probing helper instead of branching normal Sway configuration.
5. Run `./packages/install.sh --dry-run --distro <id> --tier optional`, update `scripts/validate.sh`, and verify actual package availability with that distribution's standard repository metadata.
6. Render/apply into a disposable home with that distribution's chezmoi package, run Sway's config validation where available, then test a live session and record the result in `docs/validation.md`.

No shared Sway tree should be copied.

## Host examples

Discover actual identifiers only on the target host:

```sh
swaymsg -t get_outputs
swaymsg -t get_inputs
```

Then create `~/.config/sway/hosts/<hostname>.conf`, for example:

```text
output DP-1 mode 2560x1440@144Hz position 0 0
output eDP-1 position 2560 0 scale 1.25
input "type:touchpad" natural_scroll disabled
```

The example names are illustrative and are not in the managed default configuration.
