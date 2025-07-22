import os
from datetime import datetime

# --- CONFIGURATION ---
VAULT_PATH = "/path/to/your/ObsidianVault"  # Change this to your Obsidian vault path
SUBFOLDER = "MCP Notes"                      # Subfolder for notes (created if missing)
FILENAME_FORMAT = "%Y-%m-%d_%H-%M-%S.md"    # e.g. 2024-07-16_21-11-31.md
CONTENT_TYPE = "all"  # or "logs", "chat", etc.


def create_obsidian_note(content, vault_path=VAULT_PATH, subfolder=SUBFOLDER, filename_format=FILENAME_FORMAT):
    """
    Create a new Obsidian note with the given content.
    The note will be placed in the specified subfolder of your vault.
    """
    folder_path = os.path.join(vault_path, subfolder)
    os.makedirs(folder_path, exist_ok=True)
    filename = datetime.now().strftime(filename_format)
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Note created: {file_path}")


# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # Replace this with your actual log/chat/code content
    content = "# MCP Log\n\n2025-07-16 21:11:31,060 - Server ready\n..."
    create_obsidian_note(content) 