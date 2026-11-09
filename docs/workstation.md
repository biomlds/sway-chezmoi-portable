# Debian FAI workstation integration

## Ownership

Use this repository as the **single user desktop source**, applied explicitly by
the permanent user after installation. Keep the complete repository: `.chezmoiroot`
selects `dotfiles/`, while the package manifest and tooling remain alongside it.
Do not copy the desktop into FAI's minimal chezmoi skeleton or apply both trees.

FAI owns encryption, boot/recovery, accounts, system packages, LightDM, and the
`workstation-sway` SSH-agent session. This repository owns the user's compositor,
bar, launcher, notifications, themes, portals and helper scripts. Unmanaged
`~/.config/sway/hosts/*.conf` owns hardware-specific output/input settings.

The workstation session helper delegates to `desktop-sway-session` when installed.
That helper preserves the existing SSH agent and exports application environment
before starting Sway. The portable config includes `/etc/sway/config.d/*.conf`,
including the workstation KeePassXC autostart fragment and distribution portal
hooks. Choose **Workstation Sway** at LightDM; the packaged Sway entry does not
provide the workstation's agent lifecycle.

## First application

Do this in the normal installed system; root changes in recovery are ephemeral.
Use a reviewed local clone or a repository URL you control. The installer never
clones or executes the KDBX Chezmoi.Repository automatically.

1. Back up current user desktop configuration and review existing unmanaged
   `~/.config/sway/config.d/*.conf`, `hosts/*.conf` and Waybar files. Wildcard
   includes will load old fragments too; move conflicting fragments out yourself.
2. Review the package delta. FAI's SWAY class includes required/recommended desktop
   components; the manifest remains the portable package source of truth:

   ```sh
   cd /path/to/sway-chezmoi-portable
   ./packages/install.sh --dry-run --tier recommended
   # Only if packages are missing; APT work remains an explicit system operation:
   ./packages/install.sh --tier recommended
   ```

3. Keep the package hook disabled. If chezmoi already manages other dotfiles,
   merge this source into that repository deliberately; `init` changes the active
   source and can regenerate its config. Back up `~/.config/chezmoi` first.

   ```sh
   chezmoi init --source "$PWD"
   chezmoi --source "$PWD" status
   chezmoi --source "$PWD" diff
   chezmoi --source "$PWD" apply
   ```

4. Log out and select Workstation Sway again. Existing helper processes keep their
   old environment/code until logout. Apply validates/reloads an active Sway and
   reloads Mako/Waybar; it does not restart the agent or the session daemons.
5. Test terminal, Wofi, notifications, Wi-Fi tray, audio, lock/unlock and suspend.
   Enable KeePassXC agent integration as described in the FAI KEEPASSXC guide;
   verify database unlock adds a key and database lock removes it with `ssh-add -l`.
   Test screen sharing in the actual browser, including Flatpak if used.

## Defaults and deliberate choices

- Idle lock: 300 seconds; display off: 600 seconds. `Mod+Ctrl+l` locks explicitly.
  The power-menu suspend action requires a successful lock first. Swayidle's
  before-sleep hook also covers suspend initiated elsewhere while it is running.
- Clipboard history is **off**. Set `data.desktop.clipboard.history = true` in
  chezmoi config only if wanted, then apply and log out/in. History is private,
  runtime-only, skips compositor-marked sensitive selections, and retains at most
  200 text entries of 1 MiB. Applications may fail to mark secrets: disabling
  history is the stronger boundary. Remove any old persistent history under
  `~/.local/state/sway-desktop/clipboard` manually after reviewing it.
- Use `~/.config/sway/hosts/<hostname>.conf` for actual monitors and input devices.
  All host files are included, so retain only files intended for this machine.
- No browser association is forced. Set your preferred XDG browser after Flatpak
  installation completes; `Mod+b` uses the selected default.
- Qt platform plugins are recommended packages. qt5ct/qt6ct files alone do not
  activate their platform theme; choose a platform theme only after testing the
  installed Qt application versions.

## Updates and recovery

Review Git updates, package deltas, `chezmoi diff`, then apply as the user. Boot
stack upgrades still use `workstation-update`. Root snapshots do **not** roll back
the shared home; keep a separate backup of dotfiles and host overrides. To undo a
desktop change, restore your reviewed previous source revision and apply its diff,
or restore the backed-up user configs from a TTY. Avoid `chezmoi purge` as a rollback.

## Outstanding acceptance gates

Static tests do not establish a working Wayland login. Verify LightDM/PAM session,
Sway config parsing, Qt/KeePassXC startup, idle and before-sleep lock readiness,
logout cleanup, portal screen sharing, audio, and real laptop keys on the target.
