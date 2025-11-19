from pathlib import Path
import re

p = Path(__file__).resolve().parent.parent.parent / "templates" / "Home" / "base.html"
if not p.exists():
    print("File not found:", p)
    raise SystemExit(1)
text = p.read_text(encoding="utf-8")
lines = text.splitlines()
print("Scanning:", p)
for i, l in enumerate(lines, 1):
    if re.search(r"{%\s*(block|endblock)\b", l):
        print(f"{i:03}: {l.strip()}")
print("\n-- Summary --")
opens = re.findall(r"{%\s*block\s+([A-Za-z0-9_]+)\s*%}", text)
closes = re.findall(r"{%\s*endblock\b", text)
print("Total block openings:", len(opens))
print("Total block closings:", len(closes))
print("Block names and counts:")
from collections import Counter

print("\n".join(f"{name}: {count}" for name, count in Counter(opens).items()))
