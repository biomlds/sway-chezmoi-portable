# Validation record

## Latest polish pass

- `CHEZMOI=/path/to/chezmoi scripts/validate.sh` now runs the disposable-home
  rendering checks automatically, including a home path containing spaces,
  repeated apply, Git colors, Yazi TOML/schema contracts and palette overrides.
- Six behavioral tests pass, including private unique screenshots and cancellation
  cleanup as well as clipboard, bindings, suspend and daemon lifecycle checks.
- Native Neovim 0.11.5 headless startup, the rendered highlight color, and removal
  of the mode hook when switching colorschemes passed using a temporary tool
  installation outside the repositories.
- Corrected Yazi keys against upstream **v26.9.1**: hover styles are under
  `[indicator]`, filename rules use `url`, and MIME patterns match the current
  schema. Separator defaults avoid requiring Powerline glyphs.
- FAI configuration-contract tests and its manifest check pass. This pass did not
  change FAI sources or apply configuration to the real user home.
- Native tmux/Yazi/Foot/Sway/Waybar parsers and a live Wayland session remain
  unavailable. Package transactions and hardware/portal/lock acceptance still
  require the target workstation. Earlier entries below are historical results.

## Workstation integration follow-up

- Portable static validator and target-path audit pass.
- Chezmoi v2.73.2 was run with isolated HOME/config/data/state paths: real init and
  apply twice succeeded, package hooks stayed disabled, and rendered helpers
  passed shell syntax checks. No real home configuration was modified.
- Behavioral regressions cover expanded duplicate keybindings, sensitive/oversize
  clipboard exclusion, payload eviction and private index modes, and suspend
  refusal after lock failure.
- Cleanup regressions verify no persistent clipboard directory is created,
  runtime clipboard data is removed on logout, daemon children are reaped, and a
  failed Waybar is logged without terminating idle supervision. Five tests pass.
- The Tim-inspired orange/gray theme was rendered/applied twice with real chezmoi
  in a disposable HOME. Rendered shell syntax and matching Sway background,
  Waybar accent, terminal ANSI accent and lock-ring color were checked. No visual
  screenshot comparison or live compositor parsing was performed.
- Terminal extension: rendered/applied tmux, Neovim, Yazi and Git configs in a
  disposable HOME, parsed Yazi TOML and Git true-color values, and verified a
  shared accent override reaches those four tools plus Foot. Native tmux,
  Neovim and Yazi executables were unavailable, so their runtime parsers and
  interactive appearance remain target-system checks.
- No Sway executable or Wayland seat was available for live compositor, locking,
  supervisor logout, or portal validation. Cross-distro package transactions
  remain unexecuted. The historical build-container notes below describe the
  original validation, not the later chezmoi rendering check.

## Actually executed in the build container

The container identifies itself as Microsoft Azure Linux 3.0, not one of the three target distributions. The following checks were actually run:

- Inspected the task directory recursively; it contained the prompt/support metadata but no Git repository, Dockerfile, bootstrap script, manifest, or pre-existing project source.
- Reviewed the three reference repositories through their published GitHub pages and inventories. Direct Git clone/API access was blocked, so no reference files were copied.
- Ran `sh -n` on the installer and every non-templated helper script.
- Removed Go-template actions for a reduced `sh -n` pass over templated shell/run files.
- Parsed the Waybar configuration as strict JSON with Python.
- Checked CSS brace balance and Go-template delimiter balance.
- Verified the generated wallpaper PNG signature.
- Verified executable permission bits on package/helper scripts.
- Resolved required, recommended, and optional component mappings independently for `debian`, `ubuntu`, and `fedora` using installer dry-run mode.
- Validated six manifest columns, allowed tiers, nonempty mappings, de-duplication, and the three distro manager branches.
- Cross-checked each directly referenced desktop command against a package component.
- Checked each Sway-referenced local helper against a managed source file.
- Statically transformed the subset of chezmoi source naming used here into 38 unique target paths and checked key targets (`~/.config/sway/config`, Waybar, Foot, helpers, and wallpaper).
- Re-ran `./scripts/validate.sh` after corrections; it completed successfully.
- Verified package names against official Debian, Ubuntu, and Fedora package indexes for the core desktop and important naming differences. Ubuntu 24.04's official index confirmed Wofi; qt5ct/qt6ct were not present and are deliberately unmapped there.

## Static, not runtime, validation

- Chezmoi actions/templates were checked for balanced delimiters, recognized data references, source naming, reusable-template references, and target collisions. The actual `chezmoi` binary was not installed in this container, so this is not claimed as an executed chezmoi render/apply.
- Sway modules were inspected for ordering, generic identifiers, helper/package references, and common upstream syntax. Sway was not installed, so no compositor parser ran.
- Debian/Ubuntu/Fedora package sets were independently resolved from the table. No target distro container/VM or live apt/dnf transaction was available.

## Must be tested on target systems

For each of Debian, Ubuntu, and Fedora:

1. Enable only official standard repositories (Ubuntu also needs Universe).
2. Run `./packages/install.sh --verify-only --tier optional` to query enabled repository metadata without installing.
3. Initialize into a disposable user/home, run `chezmoi diff`, and inspect all rendered files.
4. Run `chezmoi apply --verbose`; confirm run-script behavior and modes.
5. If supported by the packaged version, run Sway's config validation against the rendered config.
6. Start an actual Sway session and test Waybar modules, Wofi, Mako, Foot, lock/idle, portals/screen sharing, clipboard watching, audio/mic, screenshots, display power, suspend, polkit prompts, NetworkManager, and session actions.
7. Test a desktop without battery/backlight and a laptop with both to confirm graceful module behavior.
8. Add real output/input overrides based on `swaymsg -t get_outputs` and `get_inputs`.

## Known boundaries

- No GPU-specific workaround is enabled. NVIDIA or unusual DRM stacks may require a host launch flag or environment override chosen by the owner.
- Output modes/positions/scales and input identifiers are intentionally unset.
- Default keyboard layout is `us` and should be overridden through chezmoi data if needed.
- The browser binding uses `$BROWSER` or `xdg-open`; the configuration does not install or select a browser.
- Ubuntu 24.04 lacks standard-repository qt5ct/qt6ct packages; core Qt Wayland/portal integration remains, but those style tools are not installed.
- Power actions depend on the host's logind/polkit policy.
- Clipboard history is disabled by default, runtime-only when enabled, capped at
  200 payloads of 1 MiB, and skips selections explicitly marked sensitive. Unmarked
  secrets may still be captured. Review/remove old persistent history manually.
