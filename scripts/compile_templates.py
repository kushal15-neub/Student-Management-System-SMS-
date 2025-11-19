from pathlib import Path
from django.template import TemplateSyntaxError
from django.template.loader import get_template
import re

# scripts directory is at D:/Attendence/Home/scripts, templates root is D:/Attendence/templates
root = Path(__file__).resolve().parent.parent.parent / "templates"
files = []
for p in sorted(root.rglob("*.html")):
    txt = p.read_text(encoding="utf-8")
    count = len(re.findall(r"{%\s*block\s+body\b", txt))
    if count:
        files.append((p.relative_to(root), count))

print("Found templates with block body:")
for f, count in files:
    print("-", f, "(body blocks:", count, ")")

print("\nCompiling each:")
for f, count in files:
    name = str(f).replace("\\", "/")
    try:
        get_template(name)
        print("OK:", name)
    except TemplateSyntaxError as e:
        print("ERROR compiling", name)
        print(e)
    except Exception as e:
        print("Other error for", name, e)
