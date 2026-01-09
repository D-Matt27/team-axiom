import re
import json
import os
from dataclasses import dataclass

# ====================================================
# CONFIG
# ====================================================

DATA_FILE = "tasks.json"

# ====================================================
# DATA MODEL
# ====================================================

@dataclass
class Task:
    raw_text: str
    deadline: str
    priority: str

# ====================================================
# NLP RULES
# ====================================================

PRIORITY_KEYWORDS = {
    "high": ("urgent", "important", "asap", "immediately", "critical", "today"),
    "medium": ("soon", "this week", "next few days"),
}

LOW_PRIORITY_PHRASES = (
    "not urgent",
    "no urgency",
    "low priority",
    "not important"
)

DEADLINE_PATTERNS = (
    r"today",
    r"tomorrow",
    r"within \d+ (?:day|days|week|weeks|month|months)",
    r"by (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
    r"this (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
    r"next (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
    r"next (?:week|month)"
)

DEADLINE_REGEXES = [re.compile(p) for p in DEADLINE_PATTERNS]

# ====================================================
# STORAGE (BACKWARD-COMPATIBLE, CRASH-PROOF)
# ====================================================

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([task.__dict__ for task in tasks], f, indent=4)


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        tasks = []
        for item in data:
            if "raw_text" in item:
                tasks.append(Task(**item))
            elif "description" in item:  # old schema
                tasks.append(Task(
                    raw_text=item["description"],
                    deadline=item.get("deadline", "unspecified"),
                    priority=item.get("priority", "medium")
                ))
        return tasks

    except (json.JSONDecodeError, TypeError, KeyError):
        return []

# ====================================================
# PARSING (FAST O(n))
# ====================================================

def extract_deadline(text):
    text = text.lower()
    for regex in DEADLINE_REGEXES:
        m = regex.search(text)
        if m:
            return m.group()
    return "unspecified"


def extract_priority(text):
    text = text.lower()

    for phrase in LOW_PRIORITY_PHRASES:
        if phrase in text:
            return "low"

    for word in PRIORITY_KEYWORDS["high"]:
        if word in text:
            return "high"

    for word in PRIORITY_KEYWORDS["medium"]:
        if word in text:
            return "medium"

    return "medium"


def parse_task(user_input):
    return Task(
        raw_text=user_input.strip(),
        deadline=extract_deadline(user_input),
        priority=extract_priority(user_input)
    )

# ====================================================
# TASK OPS
# ====================================================

def add_task(tasks):
    text = input("\nEnter task: ").strip()
    if not text:
        print("⚠️ Task cannot be empty.\n")
        return
    tasks.append(parse_task(text))
    save_tasks(tasks)
    print("✅ Task added.\n")


def view_tasks(tasks):
    if not tasks:
        print("\n📭 No tasks.\n")
        return

    print("\n📋 TASKS")
    print("-" * 60)
    for i, t in enumerate(tasks, 1):
        print(f"{i}. {t.raw_text}")
        print(f"   Deadline : {t.deadline}")
        print(f"   Priority : {t.priority.upper()}")
        print("-" * 60)
    print()


def delete_task(tasks):
    if not tasks:
        print("\n❌ No tasks to delete.\n")
        return

    view_tasks(tasks)
    try:
        idx = int(input("Delete task number: "))
        if 1 <= idx <= len(tasks):
            removed = tasks.pop(idx - 1)
            save_tasks(tasks)
            print(f"🗑️ Deleted: {removed.raw_text}\n")
        else:
            print("⚠️ Invalid number.\n")
    except ValueError:
        print("⚠️ Enter a number.\n")


def focus_mode(tasks):
    high = [t for t in tasks if t.priority == "high"]

    if not high:
        print("\n🧘 No high-priority tasks.\n")
        return

    print("\n🔥 FOCUS MODE")
    print("-" * 60)
    for i, t in enumerate(high, 1):
        print(f"{i}. {t.raw_text}")
        print(f"   Deadline : {t.deadline}")
        print("-" * 60)
    print()

# ====================================================
# MAIN LOOP
# ====================================================

def main():
    tasks = load_tasks()

    while True:
        print("""
==================== TO-DO MANAGER ====================
1. Add Task
2. View Tasks
3. Delete Task
4. Focus Mode
5. Exit
======================================================
""")
        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            delete_task(tasks)
        elif choice == "4":
            focus_mode(tasks)
        elif choice == "5":
            print("\n👋 Exiting.\n")
            break
        else:
            print("\n⚠️ Invalid choice.\n")

# ====================================================
# ENTRY
# ====================================================

if __name__ == "__main__":
    main()
