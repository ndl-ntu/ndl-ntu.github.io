# NDL Site Maintenance Tool

`ndl_site_tool.sh` is a small helper for routine edits to the Jekyll site.

## Easiest Use On Windows

Double-click this file in the repository folder:

```text
RUN_SITE_TOOL.bat
```

It opens a menu:

```text
1. Write a news post
2. Add research staff/student/alumni
3. Remove research staff/student/alumni
4. Add publication by DOI
5. Run Jekyll build
6. Publish changes to GitHub
0. Exit
```

Follow the prompts. The tool will ask for only the fields needed for that action.

## Command-Line Use

From Git Bash, WSL, macOS, or Linux:

```bash
scripts/ndl_site_tool.sh menu
```

Keep `scripts/ndl_site_tool.sh` and `scripts/ndl_site_tool.py` together; the Bash file launches the Python program.

## Requirements

- Bash, such as Git Bash on Windows
- Python 3
- Internet access for `add-publication`, because it reads DOI metadata from Crossref

For the double-click launcher on Windows, install Git for Windows so that `bash` is available.

## Create A News Post

```bash
scripts/ndl_site_tool.sh new-post \
  --title "New lab announcement" \
  --body "Write the news content here."
```

Optional:

```bash
scripts/ndl_site_tool.sh new-post \
  --title "New lab announcement" \
  --date 2026-06-14 \
  --slug new-lab-announcement
```

This creates a file in `_posts/`.

## Add A Person

Use `--section staff`, `--section student`, `--section alumni`, or `--section intern`.

```bash
scripts/ndl_site_tool.sh add-person \
  --section student \
  --name "Mr. Example Student" \
  --about "Mr. Example Student is now a PhD student at Nanyang Technological University, Singapore."
```

Optional fields:

```bash
scripts/ndl_site_tool.sh add-person \
  --section staff \
  --name "Dr. Example Researcher" \
  --about "Dr. Example Researcher works on neuromorphic memory devices." \
  --image "https://example.com/photo.jpg" \
  --link "https://example.com" \
  --orcid "0000-0000-0000-0000" \
  --scholar "https://scholar.google.com/citations?user=example"
```

## Remove A Person

```bash
scripts/ndl_site_tool.sh remove-person --name "Mr. Example Student"
```

The tool removes the first profile block that matches the name.

## Add A Publication By DOI

```bash
scripts/ndl_site_tool.sh add-publication --doi 10.1039/D3NH00180F
```

The tool fetches metadata from Crossref, formats a publication line, inserts it under the matching year in `publications.md`, and adds a Dimensions citation widget.

If the year should be forced:

```bash
scripts/ndl_site_tool.sh add-publication --doi 10.1039/D3NH00180F --year 2023
```

## Publish Changes To GitHub

From the menu, choose:

```text
6. Publish changes to GitHub
```

The tool will show the changed files, offer to run a Jekyll build, ask for a commit message, commit all changed files, and push to the current GitHub branch.

Command-line use:

```bash
scripts/ndl_site_tool.sh publish --message "Update website"
```

## After Running The Tool

Preview and check the site:

```bash
bundle exec jekyll build
```

Then review the changes:

```bash
git diff
```
