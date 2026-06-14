# NDL Site Maintenance Tool

`ndl_site_tool.sh` is a small Bash helper for routine edits to the Jekyll site. Run it from the repository root.

## Requirements

- Bash
- Python 3
- Internet access for `add-publication`, because it reads DOI metadata from Crossref

On Windows, use Git Bash, WSL, or another Bash shell.

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

## After Running The Tool

Preview and check the site:

```bash
bundle exec jekyll build
```

Then review the changes:

```bash
git diff
```
