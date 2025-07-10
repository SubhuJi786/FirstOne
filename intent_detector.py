import re

def detect(command):
    command = command.lower()

    if "class" in command and "chapter" in command:
        class_match = re.search(r'class (\d+)', command)
        subject_match = re.search(r'(science|math|english)', command)
        chapter_match = re.search(r'chapter (\d+)', command)

        if class_match and subject_match and chapter_match:
            return "start_chapter", {
                "class": class_match.group(1),
                "subject": subject_match.group(1),
                "chapter": chapter_match.group(1)
            }

    elif "revise" in command or "repeat" in command:
        return "revise", {}

    elif "simplify" in command or "easy" in command:
        return "simplify", {}

    elif "next" in command:
        return "next", {}

    # ✅ ALWAYS return a fallback tuple
    return "unknown", {}