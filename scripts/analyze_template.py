from pathlib import Path

p = Path(r"D:/Attendence/templates/Teachers/teacher-marks.html")
s = p.read_text(encoding="utf-8")
print("if count", s.count("{% if"))
print("endif count", s.count("{% endif"))
print("for count", s.count("{% for"))
print("endfor count", s.count("{% endfor"))
print("block count", s.count("{% block"))
print("endblock count", s.count("{% endblock"))
print("\n--- lines 1-60 ---")
for i, l in enumerate(s.splitlines(), 1):
    if i <= 60:
        print(f"{i:03}: {l}")
print("\n--- lines 61-120 ---")
for i, l in enumerate(s.splitlines(), 1):
    if 61 <= i <= 120:
        print(f"{i:03}: {l}")
print("\n--- lines 121-200 ---")
for i, l in enumerate(s.splitlines(), 1):
    if i >= 121:
        print(f"{i:03}: {l}")
