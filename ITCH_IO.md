# Publishing Pathfinder on itch.io

This game runs in the browser via [pygbag](https://github.com/pygame-web/pygbag) (Python → WebAssembly).

## Requirements

- **Python 3.12** (recommended for current pygbag)
- A modern browser (Chrome, Firefox, Edge) for testing

## Build the web version

From the project folder:

```bat
build_itch.bat
```

Or manually:

```bat
python -m pip install --user --upgrade pygbag
rmdir /s /q build
python -m pygbag --title Pathfinder --package pathfinder --build --archive .
```

Output: `build/web.zip`

## Upload to itch.io

1. Create a new project on [itch.io](https://itch.io).
2. **Kind of project:** HTML
3. Check **“This file will be played in the browser”**
4. Upload **`build/web.zip`** (do not unzip it).
5. Under **Embed options**, set viewport size to **900 × 700** (matches the game window).
6. Save and use **“Run game on page”** to test.

## Test locally before uploading

```bat
python -m pygbag .
```

Then open the URL shown (usually `http://localhost:8000`). Click the page once if audio does not start (browser autoplay rules).

## Audio (browser)

Web builds need **OGG** audio. This project uses `.ogg` files for sounds; original `.wav` / `.mp3` files are excluded from the web build via `pygbag.ini`. Desktop play also uses the OGG files.

## Desktop download (optional)

You can also offer a Windows `.exe` built with PyInstaller on the same itch page as a separate downloadable file; the HTML build above is only for playing in the browser.

## Troubleshooting

- Delete the `build` folder and run `build_itch.bat` again after code or asset changes.
- If the game worked before but broke on itch.io, upgrade pygbag and rebuild with Python 3.12.
- Use **Upload `web.zip`** from pygbag’s `--archive` flag; do not upload the `build/web` folder manually.
