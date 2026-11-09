# Default keybindings

`Mod` is the Super/Windows key. Arrow keys and Vim directions (`h/j/k/l`) are both supported for focus and movement.

| Binding | Action |
|---|---|
| `Mod+Enter` | Open Foot terminal |
| `Mod+d` | Open Wofi application launcher |
| `Mod+b` | Open `$BROWSER` or the default XDG browser |
| `Mod+Shift+q` | Close focused window |
| `Mod+g` / `Mod+v` | Horizontal / vertical split |
| `Mod+s` / `Mod+w` / `Mod+e` | Stacking / tabbed / toggle split layout |
| `Mod+f` | Toggle fullscreen |
| `Mod+Shift+Space` | Toggle floating |
| `Mod+Space` | Switch focus between tiling and floating |
| `Mod+Arrow` or `Mod+h/j/k/l` | Change focus |
| `Mod+Shift+Arrow` or `Mod+Shift+h/j/k/l` | Move focused container |
| `Mod+1..0` | Switch to workspace 1..10 |
| `Mod+Shift+1..0` | Move container to workspace 1..10 |
| `Mod+r` | Enter resize mode; arrows or h/j/k/l resize; Enter/Escape exits |
| `Print` | Full screenshot; save and copy PNG |
| `Shift+Print` | Region screenshot; save and copy PNG |
| `Mod+Shift+v` | Select from bounded clipboard history |
| Volume keys | Raise/lower/mute default sink using `wpctl` |
| Mic mute key | Toggle default source mute using `wpctl` |
| Media keys | Playerctl play/pause, previous, next when optional package is installed |
| Brightness keys | Change brightness by 5% when hardware/package exists |
| `Mod+Ctrl+l` | Lock |
| `Mod+Shift+e` | Open lock/logout/suspend/reboot/power-off menu |
| `Mod+Shift+c` | Reload Sway configuration |
| `Mod+Ctrl+b` | Reload the supervised Waybar process in place |

The idle helper locks after 5 minutes and powers outputs off after 10 minutes by default. Both values are chezmoi data and can be overridden per user/host.
