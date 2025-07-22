# Obsidian Background Note Automation (Python)

This folder contains scripts and knowledge for automating note creation in Obsidian using Python. You can use these tools to log, archive, or save any content (logs, chat, code, etc.) directly into your Obsidian vault in the background.

## Features
- **Automatic Note Creation:** Save content to Obsidian notes as Markdown files.
- **Configurable:** Set vault path, subfolder, filename format, and content type.
- **Background Operation:** Can run as a script, daemon, or on a schedule.
- **Extensible:** Integrate with log watchers, HTTP endpoints, or other automations.

## Basic Usage

1. **Edit the configuration** in `obsidian_note.py`:
   - `VAULT_PATH`: Path to your Obsidian vault
   - `SUBFOLDER`: Subfolder for notes (created if missing)
   - `FILENAME_FORMAT`: Filename timestamp format

2. **Run the script** to create a note:
   ```bash
   python obsidian_note.py
   ```

3. **Integrate** with your workflow:
   - Call `create_obsidian_note()` from other scripts
   - Use as a log watcher or event handler

## Advanced Options
- **Log Watching:** Use `watchdog` to monitor files and write updates to Obsidian
- **HTTP Endpoint:** Use Flask to receive data and save notes
- **Scheduling:** Use cron (Linux/macOS) or Task Scheduler (Windows) for periodic notes

See `obsidian_note.py` for a starting point and expand as needed! 