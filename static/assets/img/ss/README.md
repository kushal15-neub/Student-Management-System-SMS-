Place your project screenshots and static images for the README here.

Guidance:

- Add files (png/jpg) into this folder locally.
- Then commit and push so they appear on GitHub and are included in deployment.

Example commands (PowerShell):

```powershell
# move or copy images into the folder (example)
Move-Item C:\path\to\screenshot1.png .\static\assets\img\ss\

# stage and commit
git add static/assets/img/ss/*
git commit -m "Add static screenshots"
git push origin main
```

Notes:

- Git does not track empty folders; `.gitkeep` is used to ensure the directory exists in the repo until you add real images.
- For production the `collectstatic` command will copy these into `STATIC_ROOT`.
