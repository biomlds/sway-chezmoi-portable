# Host overrides

Add an unmanaged `~/.config/sway/hosts/<hostname>.conf` for connector modes,
positions, device identifiers, or machine-specific startup commands. Files here
are loaded after shared modules and are intentionally not generated per host.
Example (replace every value with output from `swaymsg -t get_outputs`):

    output DP-1 mode 2560x1440@144Hz position 0 0
    output eDP-1 position 2560 0 scale 1.25

Chezmoi does not remove unmanaged files, so this survives updates without
putting machine-specific identifiers in version control.
