from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import textwrap
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path.cwd()
POSTS = ROOT / "_posts"
PEOPLE = ROOT / "_data" / "people.yml"
PUBLICATIONS = ROOT / "publications.md"
BLANK_IMAGE = "https://raw.githubusercontent.com/ndl-ntu/ndl-ntu.github.io/master/assets/img/blank.png"
DIMENSIONS_SCRIPT = '<script async src="https://badge.dimensions.ai/badge.js" charset="utf-8"></script>'


def die(message: str) -> None:
    raise SystemExit(f"Error: {message}")


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "post"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def run_build() -> None:
    if not (ROOT / "Gemfile").exists():
        return
    try:
        subprocess.run(["bundle", "exec", "jekyll", "build"], cwd=ROOT, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Note: Jekyll build was not completed. Please run `bundle exec jekyll build` manually.", file=sys.stderr)


def run_checked(command: list[str], label: str) -> None:
    try:
        subprocess.run(command, cwd=ROOT, check=True)
    except FileNotFoundError:
        die(f"{label} failed because `{command[0]}` was not found.")
    except subprocess.CalledProcessError as exc:
        die(f"{label} failed with exit code {exc.returncode}.")


def git_output(command: list[str]) -> str:
    try:
        result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    except FileNotFoundError:
        die("Git was not found. Please install Git for Windows first.")
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        die(f"Git command failed: {message}")
    return result.stdout.strip()


def publish_changes(args: argparse.Namespace) -> None:
    status = git_output(["git", "status", "--short"])
    if not status:
        print("No website changes to publish.")
        return

    print("\nFiles changed:")
    print(status)

    if not getattr(args, "skip_build", False):
        answer = "y" if getattr(args, "yes", False) else ask("Run Jekyll build before publishing? y/n", "y").lower()
        if answer.startswith("y"):
            run_build()

    message = getattr(args, "message", None) or ask("Commit message", "Update website")
    if not message.strip():
        die("Commit message cannot be blank.")

    if not getattr(args, "yes", False):
        confirm = ask("Commit all changed files and push to GitHub? y/n", "n").lower()
        if not confirm.startswith("y"):
            print("Cancelled. No commit or push was made.")
            return

    run_checked(["git", "add", "-A"], "Git add")
    run_checked(["git", "commit", "-m", message], "Git commit")
    branch = git_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    run_checked(["git", "push", "origin", branch], "Git push")
    print(f"Published changes to GitHub branch: {branch}")


def add_post(args: argparse.Namespace) -> None:
    POSTS.mkdir(exist_ok=True)
    date = args.date or dt.date.today().isoformat()
    try:
        dt.date.fromisoformat(date)
    except ValueError:
        die("--date must use YYYY-MM-DD")

    slug = args.slug or slugify(args.title)
    path = POSTS / f"{date}-{slug}.md"
    if path.exists() and not args.force:
        die(f"{path} already exists. Re-run with --force to overwrite.")

    body = args.body or "Write the news content here."
    content = f"""---
title: {args.title}
date: {date}
layout: post
---

{body.rstrip()}
"""
    write(path, content)
    print(f"Created news post: {path}")


def person_block(section: str, name: str, about: str, image: str, link: str | None, ratio: str, orcid: str | None, scholar: str | None) -> str:
    heading = f'<a href="{link}">{name}</a>' if link else name
    lines = [
        f"    - link: {image}",
        f"      alt: {name}",
        "      description: |-",
        f"        ### {heading}",
    ]
    if orcid:
        lines.append(f"        [![ORCID](/assets/img/orcid.logo.icon.svg){{:.orcid-icon}}](https://orcid.org/{orcid})")
    if scholar:
        lines.append(f"        [![](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Google_Scholar_logo.svg/32px-Google_Scholar_logo.svg.png)]({scholar})")
    lines.extend([
        "        #### About",
        f"        {about}",
        f"      ratio: {ratio}",
    ])
    return "\n".join(lines) + "\n"


def find_section(lines: list[str], section: str) -> tuple[int, int]:
    start = None
    for i, line in enumerate(lines):
        if line == f"- title: {section}":
            start = i
            break
    if start is None:
        die(f"section not found: {section}")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("- title: "):
            end = i
            break
    return start, end


def add_person(args: argparse.Namespace) -> None:
    section_map = {
        "staff": "Research Staff",
        "student": "Graduate Research Student",
        "alumni": "Alumni",
        "intern": "Undergraduate Intern",
    }
    section = section_map.get(args.section.lower(), args.section)
    lines = read(PEOPLE).splitlines()
    start, end = find_section(lines, section)
    insert_at = None
    for i in range(start + 1, end):
        if lines[i].strip() == "images:":
            insert_at = i + 1
            break
    if insert_at is None:
        die(f"section has no images list: {section}")
    block = person_block(section, args.name, args.about, args.image, args.link, args.ratio, args.orcid, args.scholar).splitlines()
    lines[insert_at:insert_at] = block
    write(PEOPLE, "\n".join(lines) + "\n")
    print(f"Added {args.name} to {section}.")


def remove_person(args: argparse.Namespace) -> None:
    lines = read(PEOPLE).splitlines()
    needle = args.name.lower()
    remove_start = None
    remove_end = None
    for i, line in enumerate(lines):
        if line.startswith("    - link: "):
            j = i + 1
            block = [line]
            while j < len(lines) and not lines[j].startswith("    - link: ") and not lines[j].startswith("- title: "):
                block.append(lines[j])
                j += 1
            if needle in "\n".join(block).lower():
                remove_start, remove_end = i, j
                break
    if remove_start is None:
        die(f"person not found: {args.name}")
    del lines[remove_start:remove_end]
    write(PEOPLE, "\n".join(lines) + "\n")
    print(f"Removed profile matching: {args.name}")


def fetch_crossref(doi: str) -> dict:
    encoded = urllib.parse.quote(doi)
    url = f"https://api.crossref.org/works/{encoded}"
    with urllib.request.urlopen(url, timeout=20) as response:
        data = json.load(response)
    return data["message"]


def format_authors(authors: list[dict]) -> str:
    names = []
    for author in authors[:8]:
        given = author.get("given", "").strip()
        family = author.get("family", "").strip()
        if given and family:
            initials = " ".join(part[0] + "." for part in given.replace("-", " ").split() if part)
            names.append(f"{initials} {family}")
        elif family:
            names.append(family)
    if len(authors) > 8:
        names.append("...")
    return ", ".join(names) if names else "Authors"


def publication_line_from_doi(doi: str) -> tuple[str, int]:
    item = fetch_crossref(doi)
    title = (item.get("title") or ["Untitled"])[0].rstrip(".")
    journal = (item.get("container-title") or [""])[0]
    authors = format_authors(item.get("author", []))
    year = None
    for key in ("published-print", "published-online", "published", "created"):
        parts = item.get(key, {}).get("date-parts")
        if parts and parts[0]:
            year = int(parts[0][0])
            break
    if not year:
        year = dt.date.today().year
    clean_doi = item.get("DOI", doi)
    journal_part = f" **{journal}**." if journal else ""
    metric = f'<span class="publication-metrics"><span class="__dimensions_badge_embed__" data-doi="{clean_doi}" data-style="small_rectangle" data-hide-zero-citations="true"></span></span>'
    line = f"* {authors}. {title}.{journal_part} {year}. [doi: {clean_doi}](https://doi.org/{clean_doi}){{:target=\"_blank\"}} {metric}"
    return line, year


def add_publication(args: argparse.Namespace) -> None:
    line, year = publication_line_from_doi(args.doi)
    text = read(PUBLICATIONS)
    if args.doi.lower() in text.lower():
        die(f"DOI already appears in publications.md: {args.doi}")
    year_heading = f"### {args.year or year}"
    if year_heading not in text:
        marker = "The full publication list is organized by year below. DOI links and citation badges are included where publication identifiers are available."
        idx = text.find(marker)
        if idx == -1:
            die("full publication list intro not found")
        idx = text.find("<div class=\"publication-list\" markdown=\"1\">", idx)
        if idx == -1:
            die("full publication list wrapper not found")
        insert = idx + len("<div class=\"publication-list\" markdown=\"1\">")
        text = text[:insert] + f"\n\n{year_heading}\n\n{line}\n" + text[insert:]
    else:
        idx = text.find(year_heading)
        next_heading = re.search(r"\n### \d{4}|\n# Before 2016", text[idx + len(year_heading):])
        insert = idx + len(year_heading)
        if next_heading:
            insert = idx + len(year_heading) + next_heading.start()
        text = text[:insert].rstrip() + "\n\n" + line + "\n" + text[insert:]
    if DIMENSIONS_SCRIPT not in text:
        text = text.rstrip() + "\n\n" + DIMENSIONS_SCRIPT + "\n"
    write(PUBLICATIONS, text)
    print(f"Added publication DOI {args.doi} under {year_heading}.")


def ask(prompt: str, default: str | None = None) -> str:
    label = f"{prompt} [{default}]: " if default else f"{prompt}: "
    value = input(label).strip()
    return value or (default or "")


def ask_optional(prompt: str) -> str | None:
    value = input(f"{prompt} (optional): ").strip()
    return value or None


def pause() -> None:
    input("\nPress Enter to continue...")


def maybe_build() -> None:
    answer = ask("Run Jekyll build now? y/n", "y").lower()
    if answer.startswith("y"):
        run_build()


def menu_new_post() -> None:
    title = ask("Post title")
    body = ask("Post body", "Write the news content here.")
    date = ask_optional("Date, YYYY-MM-DD")
    slug = ask_optional("Slug")
    add_post(argparse.Namespace(title=title, body=body, date=date, slug=slug, force=False))
    maybe_build()


def menu_add_person() -> None:
    print("\nSections: staff, student, alumni, intern")
    section = ask("Section", "student")
    name = ask("Display name, e.g. Mr. JIN Tian")
    about = ask("About sentence")
    image = ask("Image URL/path", BLANK_IMAGE)
    link = ask_optional("Personal/profile link")
    orcid = ask_optional("ORCID iD only, e.g. 0000-0000-0000-0000")
    scholar = ask_optional("Google Scholar URL")
    add_person(argparse.Namespace(
        section=section,
        name=name,
        about=about,
        image=image,
        link=link,
        ratio="is-16by9",
        orcid=orcid,
        scholar=scholar,
    ))
    maybe_build()


def menu_remove_person() -> None:
    name = ask("Name to remove")
    confirm = ask(f"Remove first profile matching '{name}'? y/n", "n").lower()
    if not confirm.startswith("y"):
        print("Cancelled.")
        return
    remove_person(argparse.Namespace(name=name))
    maybe_build()


def menu_add_publication() -> None:
    doi = ask("DOI")
    year_text = ask_optional("Force year")
    year = int(year_text) if year_text else None
    add_publication(argparse.Namespace(doi=doi, year=year))
    maybe_build()


def menu(args: argparse.Namespace) -> None:
    while True:
        print(textwrap.dedent("""

            NDL Site Maintenance
            1. Write a news post
            2. Add research staff/student/alumni
            3. Remove research staff/student/alumni
            4. Add publication by DOI
            5. Run Jekyll build
            6. Publish changes to GitHub
            0. Exit
            """).strip())
        choice = ask("Choose an option")
        try:
            if choice == "1":
                menu_new_post()
            elif choice == "2":
                menu_add_person()
            elif choice == "3":
                menu_remove_person()
            elif choice == "4":
                menu_add_publication()
            elif choice == "5":
                run_build()
            elif choice == "6":
                publish_changes(argparse.Namespace(message=None, skip_build=False, yes=False))
            elif choice == "0":
                return
            else:
                print("Please choose 0, 1, 2, 3, 4, 5, or 6.")
        except Exception as exc:
            print(f"\nError: {exc}", file=sys.stderr)
        pause()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Maintain the Neuromorphic Device Lab Jekyll site.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              scripts/ndl_site_tool.sh new-post --title "New award" --body "Congratulations..."
              scripts/ndl_site_tool.sh menu
              scripts/ndl_site_tool.sh add-person --section student --name "Mr. Example" --about "He is a PhD student."
              scripts/ndl_site_tool.sh remove-person --name "Mr. Example"
              scripts/ndl_site_tool.sh add-publication --doi 10.1039/D3NH00180F
              scripts/ndl_site_tool.sh publish --message "Update website"
            """
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("menu", help="Open an interactive guided menu.")
    p.set_defaults(func=menu)

    p = sub.add_parser("new-post", help="Create a Markdown news post in _posts.")
    p.add_argument("--title", required=True)
    p.add_argument("--body")
    p.add_argument("--date")
    p.add_argument("--slug")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=add_post)

    p = sub.add_parser("add-person", help="Add a research staff/student/alumni profile.")
    p.add_argument("--section", required=True, help="staff, student, alumni, intern, or exact section title")
    p.add_argument("--name", required=True)
    p.add_argument("--about", required=True)
    p.add_argument("--image", default=BLANK_IMAGE)
    p.add_argument("--link")
    p.add_argument("--ratio", default="is-16by9")
    p.add_argument("--orcid")
    p.add_argument("--scholar")
    p.set_defaults(func=add_person)

    p = sub.add_parser("remove-person", help="Remove the first profile matching a name.")
    p.add_argument("--name", required=True)
    p.set_defaults(func=remove_person)

    p = sub.add_parser("add-publication", help="Fetch Crossref metadata and add a publication by DOI.")
    p.add_argument("--doi", required=True)
    p.add_argument("--year", type=int)
    p.set_defaults(func=add_publication)

    p = sub.add_parser("publish", help="Commit all changed files and push to GitHub.")
    p.add_argument("--message", "-m")
    p.add_argument("--skip-build", action="store_true")
    p.add_argument("--yes", "-y", action="store_true", help="Do not ask for confirmation.")
    p.set_defaults(func=publish_changes)

    args = parser.parse_args()
    args.func(args)
    if getattr(args, "build", False):
        run_build()


if __name__ == "__main__":
    main()
