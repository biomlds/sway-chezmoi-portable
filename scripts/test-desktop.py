#!/usr/bin/env python3
"""Behavioral checks without a Wayland seat or changes to the real HOME."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "dotfiles/private_dot_local/bin"


class DesktopTests(unittest.TestCase):
    def test_supervisor_singleton_and_logout_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            commands = base / "commands"
            commands.mkdir()
            (base / ".local/bin").mkdir(parents=True)
            for name in ("desktop-idle", "desktop-polkit-agent"):
                helper = base / ".local/bin" / name
                helper.write_text("#!/bin/sh\nexec sleep 30\n")
                helper.chmod(0o700)
            for name, body in (
                ("mako", 'printf "started\\n" >> "$HOME/starts"; exec sleep 30'),
                ("swaymsg", 'while [ ! -e "$HOME/disconnect" ]; do sleep 0.02; done'),
                ("systemctl", "exit 0"), ("dbus-update-activation-environment", "exit 0"),
            ):
                command = commands / name
                command.write_text("#!/bin/sh\n" + body + "\n")
                command.chmod(0o700)
            env = {**os.environ, "HOME": directory, "XDG_RUNTIME_DIR": directory,
                   "SWAYSOCK": "fixture-socket", "PATH": str(commands) + ":" + os.environ["PATH"]}
            supervisor = subprocess.Popen(["sh", str(BIN / "executable_desktop-session-start")], env=env)
            try:
                for _ in range(100):
                    if (base / "starts").exists():
                        break
                    time.sleep(0.02)
                self.assertTrue((base / "starts").exists())
                subprocess.run(["sh", str(BIN / "executable_desktop-session-start")], env=env, check=True, timeout=3)
                self.assertEqual((base / "starts").read_text().splitlines(), ["started"])
                (base / "disconnect").touch()
                supervisor.wait(timeout=3)
                self.assertEqual(list((base / "sway-desktop").glob("*.pid")), [])
            finally:
                if supervisor.poll() is None:
                    supervisor.terminate()
                    supervisor.wait(timeout=3)

    def test_no_duplicate_default_bindings(self):
        variables = {"$left": "h", "$down": "j", "$up": "k", "$right": "l"}
        seen = set()
        mode = "default"
        for line in (ROOT / "dotfiles/dot_config/sway/config.d/60-bindings.conf").read_text().splitlines():
            if line.startswith('mode "'):
                mode = line.split('"')[1]
            if line == "}":
                mode = "default"
            match = re.match(r"\s*bindsym (\S+)", line)
            if not match:
                continue
            key = match[1]
            for variable, value in variables.items():
                key = key.replace(variable, value)
            self.assertNotIn((mode, key), seen, f"Duplicate binding: {key}")
            seen.add((mode, key))

    def test_clipboard_skips_secrets_bounds_storage_and_uses_private_modes(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            env = {**os.environ, "XDG_RUNTIME_DIR": directory}
            script = str(BIN / "executable_desktop-clipboard-store")
            for state in ("sensitive", "nil", "clear"):
                subprocess.run(["sh", script], input=b"private-value", env={**env, "CLIPBOARD_STATE": state}, check=True)
            self.assertFalse((runtime / "sway-desktop/clipboard/items").exists())
            subprocess.run(["sh", script], input=b"x" * 1048577, env=env, check=True)
            items = runtime / "sway-desktop/clipboard/items"
            self.assertEqual(list(items.iterdir()), [])
            # Exercise actual eviction rather than just an index-line limit.
            items.mkdir(parents=True, exist_ok=True)
            index = items.parent / "index.tsv"
            for number in range(200):
                name = f"{number:064x}"
                (items / name).write_text("old")
            index.write_text("".join(f"{n:064x}\told\n" for n in range(200)))
            subprocess.run(["sh", script], input=b"new clipboard", env=env, check=True)
            self.assertEqual(len(list(items.iterdir())), 200)
            self.assertFalse((items / f"{0:064x}").exists())
            self.assertEqual(index.stat().st_mode & 0o077, 0)

    def test_suspend_never_runs_after_lock_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            (home / ".local/bin").mkdir(parents=True)
            lock = home / ".local/bin/desktop-lock"
            lock.write_text("#!/bin/sh\nexit 1\n")
            lock.chmod(0o700)
            commands = home / "commands"
            commands.mkdir()
            for name, body in (("wofi", "printf Suspend"), ("systemctl", "printf UNSAFE_SUSPEND")):
                path = commands / name
                path.write_text("#!/bin/sh\n" + body + "\n")
                path.chmod(0o700)
            result = subprocess.run(["sh", str(BIN / "executable_desktop-power-menu")], capture_output=True,
                env={**os.environ, "HOME": str(home), "PATH": str(commands) + ":" + os.environ["PATH"]})
            self.assertNotIn(b"UNSAFE_SUSPEND", result.stdout)


if __name__ == "__main__":
    unittest.main()
