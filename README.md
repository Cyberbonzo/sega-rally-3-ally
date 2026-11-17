# SEGA Rally 3 â€” ROG Ally / Bazzite

Version 0.1.1. Launcher and handheld controls for your own copy of the 2008 arcade game. No game data, executable, dependency DLL, artwork or save is distributed here.

Runs through an existing GE-Proton11-12 installation. Uses the open Windows Arcade Loader Europa-R module to emulate cabinet inputs. The original Rally.exe stays unchanged.

Features: 1920Ã—1080 fullscreen at native 16:9, a 60 FPS cap, English, km/h, Very Easy difficulty by default, free play, offline cabinet settings, analog steering/pedals and an English pause screen. The pause excludes suspended time from the game's QPC, GetTickCount and timeGetTime clocks. Native high-score files stay in the game directory and receive versioned local backups. A checksum-validated checkpoint of the pointer-free native score table is saved automatically from memory and loaded on the next launch when newer than the native file. Names, cars, transmissions and times in those records are retained. This arcade edition has no cumulative points career or unlockable garage; available cars depend on the game mode. This is not a mid-race save state.

## Controls

| Ally control | Action |
|---|---|
| Left stick | Steer / select |
| RT | Accelerate / confirm selections |
| LT | Brake |
| A | Start |
| B | Handbrake |
| X | Change camera |
| LB / RB | Shift down / up |
| Menu | Pause / resume |
| A or B while paused | Resume |
| LB / RB while paused | Select difficulty for the next launch |

## Difficulty

Very Easy keeps the arcade Easy opponent settings. Each timed event starts with 20 extra seconds, and each checkpoint or lap that awards time grants 10 extra seconds. Each individual award is capped at 99 seconds. Lap and record times use the original clock.

Press Menu and use LB or RB to select Very Easy, Easy, Medium or Hard. Restart the game to apply your selection. The launcher verifies your own arcade database, backs it up in `saves/original` and restores it when you select a stock difficulty.

## Setup

Use an existing Linux installation with Python 3, Pillow, SDL2, Fontconfig and GE-Proton11-12 under `~/.local/share/Steam/compatibilitytools.d`. The scripts install no system packages. Add `jogar.sh` as a non-Steam game, without a Steam compatibility override; the launcher invokes its own Proton runner.

1. Place your own extracted game under `game`, preserving `game/Rally/Rally.exe` and `game/ShellData`.
2. Obtain the v0.1 runtime archive from [Windows Arcade Loader](https://github.com/aderumier/windowsarcadeloader/releases/tag/v0.1). Extract only `payloads/wal_europar.dll` and `systemprofiles/europar/sega-rally-3.yaml` into `dependencias`. Keep the upstream license with these private dependencies.
3. Back up your original `game/Rally/xinput1_3.dll`, then copy `dependencias/wal_europar.dll` to that location as `xinput1_3.dll`.
4. Run `chmod +x jogar.sh`, then launch it from Steam. The supported Rally.exe SHA-256 is `8eb7bdf01b8dc30ba40a43ac3d4065b9035cc59d58dd01b3c03113a1403171b5`.

The launcher maps `game/Rally/ShellData` to `game/ShellData`, matching the game file-system root so native reads and writes reach the supplied score directory. An existing different directory/link is never overwritten.

The upstream profile supplies its own revision-specific 1080p HUD adjustments at launch. Keep that profile and DLL from the same runtime release. Logs are in `logs`; backups are in `saves` and the latest memory checkpoint is in `state`. Preserve the whole private installation when migrating.

## Verification and limits

Tested on a ROG Ally running Bazzite: 1920Ã—1080 swapchain, gameplay observed at 60 FPS, physical controls confirmed by the user, pause/resume clock correction checked during a race. This does not guarantee 60 FPS on every track or validate an entire championship.

Valve Proton 11.0 produced an invalid video-texture size during loading in this setup. The already installed GE-Proton11-12 plays the videos and enters gameplay. Use the stated runner for this version. The game's unused internal pause screen is incomplete in this arcade build; this project uses its own pause window.

## Dependencies and rights

Project code: MIT. External cabinet module: [Windows Arcade Loader](https://github.com/aderumier/windowsarcadeloader), GPL-3.0, obtained separately. GE-Proton and its components retain their respective licenses. SEGA Rally 3 and its assets belong to their owners. This is an unofficial bring-your-own-game compatibility project, unaffiliated with SEGA.
