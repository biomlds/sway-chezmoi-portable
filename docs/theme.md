# Tim-inspired workstation desktop

Reference: [timkicker/dotfiles](https://github.com/timkicker/dotfiles), especially
its dark-gray desktop, compact Waybar, Wofi layout and orange accent language.
This is an adaptation within the existing portable chezmoi implementation.

## Visual defaults

| Element | Choice |
| --- | --- |
| Background / raised surface | `#222222` / `#2a2a2a` |
| Separators | `#333333` |
| Text | `#bec1bf` |
| Focus / selection accent | Orange `#df970d` |
| Positive / secondary | Green `#6aaa64` |
| Urgency | Red `#c65d5d` |
| Waybar | 28px, monospace text, orange workspace underline, separated status groups |
| Wofi | Compact gray search/list, subtle border, orange selected text |
| Terminal | Foot with coordinated ANSI colors, pink/purple and green secondary tones |
| Lock | Solid dark background, orange ring, green key highlight |
| tmux | Dark status/pane borders, orange active window/session, green activity |
| Neovim | Native Lua colorscheme; orange normal, green insert, pink visual status accent |
| Yazi | Orange hovered file, blue directories, coordinated selection and permissions |
| Git | Orange current branch, green additions, red deletions, muted metadata |
| GTK / Qt | Distribution theme assets; custom app palettes are not injected |

Font defaults remain DejaVu from standard repositories. The bar uses text labels
so it works without a Nerd Font. Foot stays the terminal; the reference's Kitty,
Stow, notification center, editor plugins, shell and file-manager configuration
are not prerequisites for achieving the desktop look. Existing workstation
KeePassXC, SSH-agent, idle-lock and portal integration remains in place.

## Customize through chezmoi data

For example, in the user's chezmoi configuration:

```toml
[data.desktop.theme]
accent = "#df970d"
background = "#222222"

[data.desktop]
fontMono = "DejaVu Sans Mono"
```

Review `chezmoi diff`, apply, and log out/in to refresh all helpers. Lock colors
are now templated too. Foot may need a new terminal window to pick up changes.
Application GTK/Qt colors follow the selected distribution theme rather than
pretending that the shared palette recolors every toolkit.

## Terminal tools

The portable source now owns `~/.tmux.conf`, `~/.config/nvim`,
`~/.config/yazi` and `~/.config/git/config`. Review existing configs before apply;
the Neovim init file is a complete minimal configuration, so merge deliberately
if you already use a plugin setup. Neovim's colorscheme itself can also be reused
with an existing init via `colorscheme workstation`. No plugins are downloaded.

FAI already installs tmux/Neovim and builds Yazi. The portable optional package
tier includes tmux/Neovim; it does not fetch Yazi from a third-party source. Yazi
configuration can remain dormant on machines where it is not installed.

Reload tmux with `tmux source-file ~/.tmux.conf`, reopen Neovim/Yazi, and open a new
Foot window. Git reads the XDG config automatically; existing `~/.gitconfig` has
higher precedence. Color values are quoted because unquoted `#` starts a Git
config comment. Identity/remotes/signing are not managed by this theme.

Other ANSI-based tools (including htop's default terminal-color scheme, tree,
grep/ripgrep and existing shell prompts) inherit Foot's coordinated ANSI palette.
They are not each given a new config. Tools with true-color themes or explicit
user overrides can retain their own colors; this does not force application
preferences or replace your shell startup files.

To use the bundled wallpaper instead of the solid background, add to this
machine's unmanaged Sway host file:

```text
output * bg $wallpaper fill
```

The screenshot appearance still depends on font rendering, scaling and application
themes. Compare on an actual workstation after checking config validity and lock
behavior; template validation alone is not a visual acceptance test.
