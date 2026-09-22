#!/usr/bin/env python3
"""Splice newly written sections into a PDF the learner has already annotated.

An accumulating document, such as a course notebook, grows one section at a time while the
learner reads and writes on their own copy and inserts pages of their own. That copy is the
only place their annotations exist, so the whole document is never regenerated. Only the new
sections are rendered, and they are inserted into the file the learner returns. Every page
that came from them is copied through untouched, with its annotations.

The source is one HTML file that also produces the live page, so the two cannot drift. It
must support a `?only=` query listing the section ids to render alone, with no shared chrome.

    python3 scripts/splice-notes-pdf.py --site path/to/site.html \\
        --master ~/Downloads/Notes.pdf --inventory

    python3 scripts/splice-notes-pdf.py --site path/to/site.html \\
        --master ~/Downloads/Notes.pdf --only chapter-7 --at 24

The ownership rule that keeps this safe: the contents page belongs to the document and may be
replaced whenever it goes stale, every other page belongs to the learner and is never
rewritten. A correction to an existing section is therefore a new page inserted after it, not
a replacement of it. `--replace` exists for the contents page and for pages the learner has
confirmed are unmarked; it warns when it is about to discard annotations.

Requires Python 3 with `pypdf`, and a Chromium-family browser for rendering. Set BROWSER_BIN
to override the browser path.

See `method/artifacts.md`, sections "Accumulating documents" and "Printing".
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    sys.exit("pypdf is required: pip install pypdf")

BROWSER_CANDIDATES = [
    os.environ.get("BROWSER_BIN", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
]


def browser():
    for path in BROWSER_CANDIDATES:
        if path and os.path.exists(path):
            return path
    sys.exit("No Chromium-family browser found. Set BROWSER_BIN to its path.")


def check_ids(site, only):
    """An unknown id renders a blank page instead of failing, so reject it up front."""
    with open(site, "r", encoding="utf-8") as fh:
        source = fh.read()
    missing = [i for i in (p.strip() for p in only.split(",")) if 'id="%s"' % i not in source]
    if missing:
        sys.exit("No section with id %s in %s" % (", ".join(missing), os.path.basename(site)))


def render(site, only, dest):
    """Render only the named sections of the source to a PDF."""
    subprocess.run(
        [
            browser(),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            # typesetting and figures are async; without a time budget the page is
            # captured before they finish
            "--virtual-time-budget=25000",
            "--run-all-compositor-stages-before-draw",
            "--no-pdf-header-footer",
            "--print-to-pdf=%s" % dest,
            "file://%s?only=%s" % (os.path.abspath(site), only),
        ],
        check=True,
        capture_output=True,
    )
    if not os.path.exists(dest):
        sys.exit("The browser produced no PDF for --only %s" % only)


def snippet(page, width=64):
    try:
        text = " ".join((page.extract_text() or "").split())
    except Exception:
        text = ""
    return text[:width] if text else "(no extractable text)"


def inventory(master):
    """List the learner's pages so new sections can be placed deliberately."""
    reader = PdfReader(master)
    print("%s, %d pages" % (os.path.basename(master), len(reader.pages)))
    for i, page in enumerate(reader.pages, start=1):
        marks = len(page.get("/Annots") or [])
        flag = "  [%d annotation%s]" % (marks, "" if marks == 1 else "s") if marks else ""
        print("  %3d  %s%s" % (i, snippet(page), flag))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True, help="the HTML source that renders the document")
    ap.add_argument("--master", required=True, help="the learner's annotated PDF")
    ap.add_argument("--only", help="section ids to render, comma separated")
    ap.add_argument("--at", type=int, help="insert after this page. Default: at the end")
    ap.add_argument("--replace", metavar="N:M",
                    help="replace pages N to M with the render instead of inserting. "
                         "Destructive: those pages and any annotation on them are discarded, "
                         "so it needs the learner's confirmation that they are unmarked")
    ap.add_argument("--inventory", action="store_true", help="list the learner's pages and stop")
    ap.add_argument("--out", help="output path. Default: overwrite the master in place")
    args = ap.parse_args()

    master = os.path.expanduser(args.master)
    if not os.path.exists(master):
        sys.exit("No master PDF at %s" % master)
    if not os.path.exists(args.site):
        sys.exit("No source at %s" % args.site)
    out = os.path.expanduser(args.out) if args.out else master

    if args.inventory:
        inventory(master)
        return
    if not args.only:
        sys.exit("Nothing to render. Pass --only, or --inventory to look first")
    if args.replace and args.at is not None:
        sys.exit("--replace and --at are alternatives; pass one")
    if args.only != "index":
        check_ids(args.site, args.only)

    old = list(PdfReader(master).pages)

    lo = hi = None
    if args.replace:
        try:
            lo, hi = (int(part) for part in args.replace.split(":", 1))
        except ValueError:
            sys.exit("--replace takes a page range like 1:1 or 4:6")
        if not 1 <= lo <= hi <= len(old):
            sys.exit("--replace %s is outside the %d page(s) in the master" % (args.replace, len(old)))
        dropped = sum(len(p.get("/Annots") or []) for p in old[lo - 1:hi])
        if dropped:
            print("warning: discarding %d annotation(s) on pages %d to %d" % (dropped, lo, hi),
                  file=sys.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        block = os.path.join(tmp, "new.pdf")
        render(args.site, args.only, block)
        new = list(PdfReader(block).pages)

        writer = PdfWriter()
        # add_page carries /Annots, so the learner's marks survive on every page copied over
        if args.replace:
            pages = old[:lo - 1] + new + old[hi:]
            kept = len(old) - (hi - lo + 1)
            where = "replaced pages %d to %d" % (lo, hi)
        else:
            cut = len(old) if args.at is None else args.at
            if not 0 <= cut <= len(old):
                sys.exit("--at %s is outside the %d page(s) in the master" % (args.at, len(old)))
            pages = old[:cut] + new + old[cut:]
            kept = len(old)
            where = ("inserted after page %d" % args.at) if args.at is not None else "appended at the end"
        for page in pages:
            writer.add_page(page)

        # stage first, so a failure cannot leave a half-written file over the master
        staged = os.path.join(tmp, "out.pdf")
        with open(staged, "wb") as fh:
            writer.write(fh)
        shutil.copy(staged, out)

    print("kept %d learner page(s), added %d new, %s -> %s" % (kept, len(new), where, out))


if __name__ == "__main__":
    main()
