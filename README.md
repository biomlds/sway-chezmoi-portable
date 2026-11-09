# Portable Sway desktop managed by chezmoi

This repository contains a real chezmoi source state for a cohesive Sway desktop on Debian, Ubuntu, and Fedora. Repository infrastructure stays at the top level; `.chezmoiroot` points chezmoi at `dotfiles/`, so unrelated repository files are never treated as home-directory content.

The default look is inspired by [timkicker/dotfiles](https://github.com/timkicker/dotfiles): dark-gray surfaces, orange `#df970d` focus accents, a compact 28px Waybar with workspace underlines and subtle separators, and coordinated launcher, notification, terminal and lock styling. Shared chezmoi data drives Sway, Waybar, Wofi, Mako, Foot and swaylock. GTK/Qt retain the distribution's Adwaita/Papirus styling. It uses standard-repository, Wayland-native components and no third-party repositories, download scripts, copied theme bundles, secrets, or hardware identifiers.

See [theme design](docs/theme.md) for the visual choices and customization. The
portable source also supplies matching tmux, Neovim, Yazi and Git color configs;
review existing editor/file-manager configs in `chezmoi diff` before applying.
The default background is solid dark gray; the bundled wallpaper is an optional
host override. The reference's README describes orange accents, while its current
Waybar CSS uses green focus in places; this adaptation deliberately uses orange
consistently.

## Layout

```text
.
├── .chezmoiroot                 # selects dotfiles/ as the source state
├── dotfiles/
│   ├── .chezmoi.toml.tmpl       # per-host chezmoi data defaults
│   ├── .chezmoidata.yaml        # shared desktop/theme data
│   ├── .chezmoiignore
│   ├── .chezmoitemplates/       # reusable Sway palette template
│   ├── run_once_before_*        # creates private screenshot/host directories
│   ├── run_onchange_before_*    # optional package hook (disabled by default)
│   ├── run_after_*              # validates/refreshes an active session
│   ├── dot_config/
│   │   ├── sway/config.d/       # variables, distro, input, output, appearance,
│   │   │                        # workspaces, bindings, rules, autostart
│   │   ├── waybar/  wofi/  mako/  foot/
│   │   ├── nvim/  yazi/  git/   # coordinated terminal tools
│   │   ├── gtk-3.0/ gtk-4.0/ qt5ct/ qt6ct/
│   │   ├── environment.d/       # Wayland/XDG application environment
│   │   └── xdg-desktop-portal/
│   └── private_dot_local/
│       ├── bin/                 # session, lock, idle, screenshot, clipboard,
│       │                        # power, media, polkit and Waybar helpers
│       └── share/backgrounds/   # generated PNG; no remote asset dependency
├── packages/
│   ├── components.tsv           # required/recommended/optional mappings
│   └── install.sh               # apt/dnf abstraction and runtime verification
├── scripts/
│   ├── list-targets.py          # static chezmoi target-path audit
│   └── validate.sh              # static/cross-distro validation
└── docs/
    ├── architecture.md
    ├── keybindings.md
    └── validation.md
```

## Selected desktop components

| Area | Choice | Rationale |
|---|---|---|
| Compositor | Sway | Mature, i3-compatible, Wayland-native |
| Bar | Waybar | Portable modules; hardware modules auto-discover devices |
| Launcher/power menu | Wofi | Native Wayland; available in Debian, Ubuntu 24.04 Universe, and Fedora standard repositories |
| Notifications | Mako | Small Wayland-native daemon; `mako-notifier` package on apt, `mako` on Fedora |
| Terminal | Foot | Fast and native Wayland with a small dependency surface |
| Lock/idle | swaylock + swayidle | Upstream, portable, no effects fork |
| Screenshots | grim + slurp | Full-screen and selected-region capture |
| Clipboard | wl-clipboard + local bounded history | Avoids a clipboard-manager package unavailable on every target |
| Audio | PipeWire/WirePlumber (`wpctl`) | Sink/source volume and microphone control without PulseAudio CLI tools |
| Wallpaper | swaybg + repository PNG | No network fetch or host path |
| GTK/icons | Adwaita-dark + Papirus | Standard repositories; clean fallback when optional assets are absent |
| Qt | Native Wayland platform + qt5ct/qt6ct configs | Optional on Debian/Fedora; Ubuntu 24.04 limitation is documented |
| Portals | xdg-desktop-portal-wlr + GTK fallback | Screen sharing and desktop file chooser integration |

Laptop modules do not name a battery or backlight. Waybar hides unavailable hardware modules, and brightness/power packages are recommended rather than required for a desktop.

## Fresh-system workflow

Install `git` and `chezmoi` from the distribution's standard repository first. On Ubuntu, enable the official **Universe** component if it is disabled; Sway, Waybar, Wofi, Mako, Foot and related packages live there. No third-party repository is required.

From a local clone:

```sh
git clone https://github.com/biomlds/sway-chezmoi-portable.git
cd sway-chezmoi-portable

# Inspect the exact resolved package set without changing the system.
./packages/install.sh --dry-run --tier recommended

# Install required + recommended packages. Safe to rerun: installed packages
# are detected; package availability is checked before installation.
./packages/install.sh --tier recommended

# Initialize from this repository. .chezmoiroot selects ./dotfiles.
chezmoi init --source "$PWD"

# Review every home-directory change before application.
chezmoi --source "$PWD" status
chezmoi --source "$PWD" diff

# Apply and run the idempotent chezmoi hooks.
chezmoi --source "$PWD" apply --verbose

# From a TTY, use the wrapper so application environment variables are exported.
~/.local/bin/desktop-sway-session
```

A display manager's packaged Sway session can also be selected, but session
environment inheritance depends on its integration. Prefer the wrapper when
starting from a TTY, and **Workstation Sway** on FAI. The environment.d file
configures user-manager applications; it does not retroactively export variables
into an already running compositor.

Package tiers are cumulative. Use `--tier required` for the minimum, `--tier recommended` for the intended experience, or `--tier optional` for all mapped extras. The chezmoi package hook is deliberately disabled by default so package installation remains explicit. To opt in, set `data.packages.install = true` and the desired tier in the user's chezmoi config.

## Updating

```sh
cd /path/to/this/repository
git pull --ff-only
./packages/install.sh --dry-run --tier recommended
./packages/install.sh --tier recommended
chezmoi --source "$PWD" status
chezmoi --source "$PWD" diff
chezmoi --source "$PWD" apply --verbose
```

The package installer only requests missing packages. A runtime-locked session supervisor owns desktop daemons and stops them when the compositor disconnects. Every apply validates/reloads an active Sway session; helper/idle-policy changes take effect after logout/login.

For the Debian FAI workstation, follow [workstation integration](docs/workstation.md).
Keep its **Workstation Sway** login to preserve the existing SSH-agent lifecycle.
Clipboard history is disabled by default; opt in with
`data.desktop.clipboard.history = true`, then apply and log out/in. History is
runtime-only and skips selections marked sensitive; unmarked secrets can still
be captured. Old persistent history is not automatically deleted.

## Packages

The component-to-package source of truth is `packages/components.tsv`. The installer reads `/etc/os-release` (`ID=debian`, `ubuntu`, or `fedora`) and selects apt for Debian/Ubuntu or dnf for Fedora. `--distro` exists only for CI/static validation.

### Required

- **Debian/Ubuntu:** `sway`, `waybar`, `wofi`, `mako-notifier`, `foot`, `swaylock`, `swayidle`, `swaybg`, `grim`, `slurp`, `wl-clipboard`, `wireplumber`, `pipewire-pulse`, `xdg-utils`, `xdg-desktop-portal-wlr`, `xdg-desktop-portal-gtk`, `fonts-dejavu-core`.
- **Fedora:** the same logical components, with `mako`, `pipewire-pulseaudio`, `dejavu-sans-fonts`, and `dejavu-sans-mono-fonts` replacing apt package names.

### Recommended

`policykit-1-gnome` / `polkit-gnome`, `network-manager-gnome` / `network-manager-applet`, `brightnessctl`, `power-profiles-daemon`, `pavucontrol`, `xdg-user-dirs`, `papirus-icon-theme`, `gnome-themes-extra`, and Qt5/Qt6 Wayland platform plugins.

### Optional

`playerctl`, `blueman`, desktop notification CLI (`libnotify-bin` on apt, `libnotify` on Fedora), plus `qt5ct` and `qt6ct` on Debian/Fedora. Ubuntu 24.04 does not provide qt5ct/qt6ct in its standard package index, so those two cells are intentionally `-`; Qt still uses Wayland and the XDG portal, but qt5ct/qt6ct-specific styling requires a later Ubuntu release or a user-chosen, separately trusted source.

The optional tier also includes tmux and Neovim. Yazi themes target **26.9.1+**,
matching FAI's build pin; Yazi itself is not downloaded by this project.

At real install time, `apt-cache show` or `dnf list --available` re-verifies every selected package before any install transaction. The script never adds repositories.

## Distribution behavior

- **Debian:** apt mappings, `mako-notifier`, `pipewire-pulse`, `policykit-1-gnome`, and DejaVu's consolidated font package.
- **Ubuntu:** the Debian mappings; official Universe must be enabled. qt5ct/qt6ct remain unavailable on Ubuntu 24.04. The visible Sway configuration is otherwise identical.
- **Fedora:** dnf mappings isolate naming differences (`mako`, `pipewire-pulseaudio`, `polkit-gnome`, `network-manager-applet`, split DejaVu fonts). The polkit helper probes Fedora's `/usr/libexec` path.

Chezmoi templates use `.chezmoi.osRelease.id` for the small generated distro module; package installation uses `/etc/os-release` independently. See `docs/architecture.md` for adding a distribution.

## Hardware and user overrides

No connector, mode, resolution, GPU flag, input identifier, hostname, interface, audio endpoint, battery, or backlight is hard-coded. Add an unmanaged file at:

```text
~/.config/sway/hosts/<hostname>.conf
```

It is loaded last and can contain output layout or device-specific commands. Chezmoi leaves unmanaged files in that directory alone. Shared user defaults such as keyboard layout, idle times, palette, fonts, icon theme, and start URL are in `dotfiles/.chezmoidata.yaml`; override them in the user's chezmoi config rather than editing generated targets. No secret fields exist, and secrets must not be added to source data.

## Reference synthesis

- **timkicker/dotfiles (primary):** adopted the broad, integrated desktop scope; compact Waybar; Wofi workflow; cohesive palette; helper scripts; screenshot, clipboard, power and laptop concerns; and clear distro package intent. Replaced per-distro install scripts and Stow with a single component map and chezmoi. Omitted author-specific sound hooks, ydotool, Neovim/ranger/shell preferences, LIDM files, udiskie, and wlogout where simpler standard components suffice.
- **sandov/sway-configs-2023:** adopted the small understandable Sway/Waybar/Wofi/Foot surface and preference for direct configuration rather than a framework. Kept the Sway tree modular only where concepts have independent maintenance value.
- **Ruixi-rebirth/sway-dotfiles:** adopted a coordinated dark visual language, Mako, icon/GTK/Qt attention, lock-screen consistency, and launcher/bar theming. Rejected sway-effects, swaylock-effects, manually copied theme trees, browser-profile changes, obsolete Neofetch-style decoration, duplicate notification daemons, and author-specific media stacks.

## Validation and limits

Run:

```sh
./scripts/validate.sh
./scripts/list-targets.py
# Also render/apply in a disposable HOME when chezmoi is available:
CHEZMOI=/path/to/chezmoi ./scripts/validate.sh
```

Validation covers shell syntax, executable modes, strict Waybar JSON, template/CSS
balance, PNG signature, package shape/resolution, helper coverage, target paths,
and behavioral regression tests. Follow-up validation ran actual chezmoi init and
apply twice in a disposable HOME; this is now a repeatable test in
`scripts/test-render.py`. Native Neovim startup/theme checks also passed. Sway parsing, package transactions, screen
locking, portals and hardware behavior still require target-system checks. See
`docs/validation.md` for the exact boundary.

Important bindings are summarized in `docs/keybindings.md`.
