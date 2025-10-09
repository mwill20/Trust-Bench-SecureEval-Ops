\
from . import inject_scan

def dangerous_command_label(text: str) -> str:
    """Return '[DANGEROUS]' if any command pattern hits; else ''."""
    hits = inject_scan.find_dangerous_commands(text)
    return "[DANGEROUS]" if hits else ""
