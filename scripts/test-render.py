#!/usr/bin/env python3
"""Render with real chezmoi in a disposable HOME; never use the caller's configs."""
import configparser
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which(os.environ.get("CHEZMOI", "chezmoi"))
if not CHEZMOI:
    raise SystemExit("chezmoi is required (or set CHEZMOI=/path/to/chezmoi)")


def run(args, env, **kwargs):
    return subprocess.run(args, env=env, check=True, **kwargs)


with tempfile.TemporaryDirectory(prefix="desktop-render-") as directory:
    base = Path(directory)
    home = base / "home with spaces"
    home.mkdir()
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("XDG_", "GIT_CONFIG"))
           and key not in {"SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY"}}
    env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"),
               XDG_CACHE_HOME=str(home / ".cache"), XDG_DATA_HOME=str(home / ".local/share"),
               XDG_STATE_HOME=str(home / ".local/state"))
    config = base / "chezmoi.toml"
    args = [CHEZMOI, "--source", str(ROOT), "--destination", str(home), "--config", str(config)]
    run(args + ["init"], env)
    for _ in range(2):
        run(args + ["apply"], env)
    assert not (home / ".local/state/sway-desktop/clipboard").exists()
    for path in (home / ".local/bin").iterdir():
        run(["sh", "-n", str(path)], env)
    json.loads((home / ".config/waybar/config").read_text())
    for path in (home / ".config/yazi").glob("*.toml"):
        tomllib.loads(path.read_text())
    theme = tomllib.loads((home / ".config/yazi/theme.toml").read_text())
    assert "current" in theme["indicator"] and "hovered" not in theme["mgr"]
    assert all("name" not in rule for rule in theme["filetype"]["rules"])
    foot = configparser.ConfigParser(interpolation=None)
    foot.read(home / ".config/foot/foot.ini")
    assert foot["colors"]["regular3"] == "df970d"
    color = subprocess.check_output(["git", "config", "--get-color", "color.branch.current"], env=env)
    assert b"38;2;223;151;13" in color

    # Verify a real user override propagates and opts into clipboard supervision.
    config.write_text(config.read_text() + '\n[data.desktop.theme]\naccent = "#abcdef"\n'
                      '\n[data.desktop.clipboard]\nhistory = true\n')
    run(args + ["apply"], env)
    for relative in (".tmux.conf", ".config/nvim/colors/workstation.lua",
                     ".config/yazi/theme.toml", ".config/git/config"):
        assert "#abcdef" in (home / relative).read_text(), relative
    assert "--clipboard" in (home / ".config/sway/config.d/80-autostart.conf").read_text()
    assert "--ring-color abcdefff" in (home / ".local/bin/desktop-lock").read_text()

    # swayidle runs supplied command strings through a shell. Exercise the
    # actual rendered string with a space-containing HOME, without locking.
    commands = base / "commands"
    commands.mkdir()
    idle = commands / "swayidle"
    idle.write_text('#!/bin/sh\n[ "$1" = -w ] && [ "$2" = timeout ] || exit 1\nexec sh -c "$4"\n')
    idle.chmod(0o700)
    lock = commands / "swaylock"
    lock.write_text('#!/bin/sh\nprintf locked\n')
    lock.chmod(0o700)
    output = subprocess.check_output(["sh", str(home / ".local/bin/desktop-idle")],
        env={**env, "PATH": str(commands) + ":" + env["PATH"]})
    assert output == b"locked"

    if shutil.which("nvim"):
        run(["nvim", "--headless", "+lua assert(vim.g.colors_name == 'workstation')",
             "+lua assert(vim.api.nvim_get_hl(0, {name='WorkstationMode'}).bg == 0xabcdef)",
             "+colorscheme default",
             "+lua vim.api.nvim_exec_autocmds('ModeChanged', {pattern='n:i'})",
             "+lua assert(#vim.api.nvim_get_autocmds({group='WorkstationTheme'}) == 0)", "+qa"], env)
        print("PASS native Neovim startup and theme")
    else:
        print("SKIP native Neovim: unavailable")
    if shutil.which("tmux"):
        socket = str(base / "tmux.sock")
        try:
            run(["tmux", "-S", socket, "-f", str(home / ".tmux.conf"),
                 "new-session", "-d", "-s", "validation", "sleep 20"], env)
            run(["tmux", "-S", socket, "source-file", str(home / ".tmux.conf")], env)
        finally:
            subprocess.run(["tmux", "-S", socket, "kill-server"], env=env, check=False)
        print("PASS native tmux config and reload")
    else:
        print("SKIP native tmux: unavailable")
    print("PASS rendering/apply twice, config parsing, palette overrides, private HOME with spaces")
