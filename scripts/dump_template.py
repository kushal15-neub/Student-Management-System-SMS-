from pathlib import Path

p = Path(r"D:/Attendence/templates/Teachers/teacher-marks.html")
print("File:", p)
text = p.read_text()
for i, line in enumerate(text.splitlines(), start=1):
    print(f"{i:03}: {line}")
