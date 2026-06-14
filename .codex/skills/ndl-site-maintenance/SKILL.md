# NDL Site Maintenance Skill

Use this skill when maintaining the Neuromorphic Device Lab GitHub Pages repository `ndl-ntu.github.io`.

## Site Model

This is a Ruby/Jekyll GitHub Pages site. Treat source files as the authority and do not edit generated output in `_site/`.

- Root Markdown pages become public pages: `index.md`, `people.md`, `highlights.md`, `publications.md`, `join-us.md`, `conferences.md`, `patents.md`, `files.md`, `request.md`, `contact.md`.
- `_posts/YYYY-MM-DD-title.md` files become news posts under `/blog/`.
- `_data/people.yml` controls profile cards shown by `people.md` through the gallery include.
- `_data/navigation.yml` controls the top navigation menu.
- `_data/example_footer_menu.yml` controls footer menu links.
- `assets/img/` contains local images, diagrams, logos, and placeholder images.
- `_sass/_layout.scss` contains most custom visual styling.
- `_sass/_main.scss` loads Bulma, site variables, and custom Sass.
- `_sass/vendor/` contains the minimal vendored Bulma Sass needed for GitHub Pages builds. Do not reintroduce tracked `node_modules`.
- `_layouts/` and `_includes/` contain shared templates and reusable components.
- `scripts/ndl_site_tool.py`, `scripts/ndl_site_tool.sh`, and `RUN_SITE_TOOL.bat` provide the click-to-run maintenance tool.
- `docs/site-guide.html` is the professor-readable guide.

## Editing Map

When asked to change visible content, use this map first:

- Homepage mission, theme blocks, selected recent papers, Join Us callout, PI biography: edit `index.md`.
- People page title or FYP lists: edit `people.md`.
- PI, research staff, graduate student, intern, alumni cards: edit `_data/people.yml`.
- Research theme page: edit `highlights.md`.
- Full publication list, selected publications, DOI/citation widgets: edit `publications.md`.
- Recruitment text: edit `join-us.md`.
- News: add or edit `_posts/YYYY-MM-DD-title.md`.
- Navbar links/order: edit `_data/navigation.yml`.
- Footer links: edit `_data/example_footer_menu.yml`.
- Images: add files to `assets/img/` and reference them with `/assets/img/name.ext`.
- Spacing, typography, profile cards, publication badge alignment: edit `_sass/_layout.scss`.
- Theme color or Sass imports: edit `_sass/_main.scss`.

## Preferred Routine Maintenance

For simple routine tasks, prefer the local tool:

```bash
scripts/ndl_site_tool.sh menu
```

On Windows, the user can double-click:

```text
RUN_SITE_TOOL.bat
```

The tool supports:

- Writing a news post.
- Adding a research staff/student/alumni profile.
- Removing a research staff/student/alumni profile.
- Adding a publication by DOI.
- Running a Jekyll build.

If the tool cannot express the requested change, edit the relevant source file directly.

## People Editing Rules

`_data/people.yml` is YAML. Preserve indentation exactly.

Sections currently include:

- `Principal Investigator`
- `Research Staff`
- `Graduate Research Student`
- `Undergraduate Intern`
- `Alumni`

Profile shape:

```yaml
- link: /assets/img/blank.png
  alt: Mr. Example Name
  description: |-
    ### Mr. Example Name
    #### About
    Mr. Example Name is now a PhD student at Nanyang Technological University, Singapore.
  ratio: is-16by9
```

Use `link:` for the displayed image. Use `large_link:` only when a separate large image is needed. Use `/assets/img/blank.png` when no headshot is available.

For ORCID inside descriptions, use:

```markdown
[![ORCID](/assets/img/orcid.logo.icon.svg){:.orcid-icon}](https://orcid.org/0000-0000-0000-0000)
```

After people edits, run a Jekyll build because YAML mistakes can break the whole site.

## Publication Editing Rules

`publications.md` is currently a hand-edited Markdown/HTML list.

Use one bullet per publication. Keep citation widgets inline:

```markdown
* Authors. Title. **Journal**. Year. [doi: 10.xxxx/example](https://doi.org/10.xxxx/example){:target="_blank"} <span class="publication-metrics"><span class="__dimensions_badge_embed__" data-doi="10.xxxx/example" data-style="small_rectangle" data-hide-zero-citations="true"></span></span>
```

For Selected Publications, include papers with more than 40 citations and tag them:

```html
<span class="tag is-warning is-light">Highly Cited</span>
```

When adding by DOI, prefer `scripts/ndl_site_tool.sh add-publication --doi DOI`. It fetches Crossref metadata and inserts the Dimensions widget.

Keep the DOI in the link and the DOI in `data-doi` identical.

## News Post Rules

News files live in `_posts/`.

Filename format:

```text
YYYY-MM-DD-short-title.md
```

Required front matter:

```markdown
---
title: News title
layout: post
author: NDL
---
```

The post date is taken from the filename. Posts are automatically listed in `blog/index.html`.

## Markdown And HTML Notes

Use Markdown for simple content:

- `## Heading` for section headings.
- `### Smaller Heading` for subsection headings.
- `* item` for bullets.
- `[text](https://example.com)` for links.
- `**text**` for bold text.
- `![alt text](/assets/img/file.png)` for images.

Use HTML only where the site already uses it, such as homepage cards, research theme blocks, and citation widgets.

## Build And Verification

Before committing, run:

```bash
bundle exec jekyll build --trace
git diff --check
```

Also run targeted reference checks after cleanup or file removal:

```bash
rg -n "removed-file-or-folder-name" --glob '!_site/**' .
```

Expected generated folders such as `_site/` and `.sass-cache/` should remain untracked.

## Git Rules For This Repo

- Work on the current branch unless the user asks for a new branch.
- Do not revert unrelated user changes.
- Use clear commits, for example `Update site maintenance guide`.
- Push to `origin master` when the user asks to update GitHub Pages or when continuing the established publish workflow.

Typical publish sequence:

```bash
git status
git add .
git commit -m "Update site content"
git push origin master
```

## Professor-Friendly Explanation To Preserve

The guide for non-programmers is `docs/site-guide.html`. Keep it written in plain language and update it whenever the repo structure or maintenance tool changes. It should explain:

- What GitHub Pages, Jekyll, Markdown, HTML, YAML, and Git mean.
- Which file changes which visible page.
- How to use `RUN_SITE_TOOL.bat`.
- How to preview and publish.
- Safety reminders about `_site/`, YAML indentation, DOI widgets, and image paths.
