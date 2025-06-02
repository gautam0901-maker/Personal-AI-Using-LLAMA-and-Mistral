# app/memory_manager.py

import json
import os

MEMORY_FILE = "data/memory.json"

# Ensure memory file exists and is valid JSON
def init_memory():
    # If file doesn't exist or is empty/corrupted, reset it
    if not os.path.exists(MEMORY_FILE) or os.path.getsize(MEMORY_FILE) == 0:
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)
    else:
        # Try reading it; if it fails, reset
        try:
            with open(MEMORY_FILE, "r") as f:
                json.load(f)
        except json.JSONDecodeError:
            with open(MEMORY_FILE, "w") as f:
                json.dump({}, f)

# Save key-value pair
def remember(key, value):
    init_memory()
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
    memory[key] = value
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# Retrieve value by key
def recall(key):
    init_memory()
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)

    return memory.get(key, "I don’t remember anything about that.")


# Append user-bot chat to memory (last 5 exchanges)
def append_chat_log(user, bot):
    init_memory()
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
    log = memory.get("chat_history", [])
    log.append({"user": user, "pekko": bot})
    memory["chat_history"] = log[-5:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)