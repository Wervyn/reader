#!/usr/bin/env python3
import argparse
import json
import os
import re
from docx import Document
from docx.oxml.ns import qn


def is_chapter_heading(text, style_name, chapter_re=None):
    if chapter_re and re.search(chapter_re, text, re.IGNORECASE):
        return True
    if style_name:
        n = style_name.lower()
        if 'chapter' in n:
            return True
    t = (text or '').strip().lower()
    if t.startswith('chapter') or t.startswith('chapter-'):
        return True
    return False


def fmt_paragraph(paragraph):
    parts = []
    for run in paragraph.runs:
        text = run.text or ''
        if not text:
            continue
        # Italic: wrap in __ to create alternating spans
        if run.italic and not run.bold:
            text = f"__{text}__"
        # Bold: wrap inside asterisk within spans: __*text*__
        elif run.bold and not run.italic:
            text = f"__*{text}*__"
        # Bold+Italic: prefer explicit ** marker inside spans so renderer applies both
        elif run.bold and run.italic:
            text = f"__**{text}**__"
        parts.append(text)
    if parts:
        return ''.join(parts)
    return paragraph.text


def extract_first_hyperlink(paragraph):
    """Return (text, url) for the first hyperlink in the paragraph if any."""
    try:
        for hl in paragraph._p.xpath('.//w:hyperlink'):
            rid = hl.get(qn('r:id'))
            # visible text inside the hyperlink (joined w:t nodes)
            texts = [t.text for t in hl.xpath('.//w:t', namespaces=paragraph._p.nsmap) if t.text]
            text = ''.join(texts).strip()
            url = None
            if rid:
                rel = paragraph.part.rels.get(rid)
                if rel:
                    # rel.target_ref is usually the URL
                    url = rel.target_ref
            if text or url:
                return text or None, url or None
    except Exception:
        return None, None
    return None, None


def split_docx(path, chapter_re=None):
    doc = Document(path)
    chapters = []
    cur = None

    footer_mode = None
    saw_first_real_chapter = False

    for para in doc.paragraphs:
        text = (para.text or '').strip()
        try:
            style = (para.style.name or '')
        except Exception:
            style = ''

        if is_chapter_heading(text, style, chapter_re):
            # Only treat this as a real chapter if it contains a hyperlink (per your spec)
            link_text, link_url = extract_first_hyperlink(para)
            if not (link_text or link_url):
                # ignore non-linked headings (part title, etc.)
                continue

            # start new chapter
            if cur:
                chapters.append(cur)

            saw_first_real_chapter = True
            footer_mode = None

            # prefer link text for title, fallback to next non-empty paragraph if needed
            title = link_text or ''
            titlelink = link_url or ''

            cur = {'title': title, 'titlelink': titlelink, 'metadata': {}, 'content': [], 'endnotes': [], 'footnotes': []}
            continue

        # before first real chapter, skip content
        if not saw_first_real_chapter:
            continue

        # handle footer text specially (endnotes/footnotes)
        if cur is not None and 'footer' in style.lower():
            # label paragraphs like "Author's Note:" or "Translator's Note:"
            if re.search(r"^\s*(Author\b|Author’s\b|Author's\b).*", text, re.I):
                footer_mode = 'endnotes'
                # skip the label itself
                continue
            if re.search(r"^\s*(Translator\b|Translator’s\b|Translator's\b).*", text, re.I):
                footer_mode = 'footnotes'
                continue

            if footer_mode:
                cur[footer_mode].append(text)
            else:
                # Unlabeled footer text — append to endnotes by default
                cur['endnotes'].append(text)
            continue

        # regular content paragraph
        if cur is None:
            # this shouldn't happen after saw_first_real_chapter but guard anyway
            continue

        cur['content'].append(fmt_paragraph(para))

    if cur:
        chapters.append(cur)

    # Normalize chapters before returning:
    # - Remove runs of 4+ underscores (likely broken italic runs) without converting them to __
    # - Trim leading/trailing empty paragraphs from `content` (keep internal empty paragraphs)
    # - Strip and drop empty entries in `endnotes` and `footnotes`
    def _normalize_paragraph_text(s):
        if not isinstance(s, str):
            return s
        # remove sequences of 4 or more underscores (no-op artifact)
        s = re.sub(r'_{4,}', '', s)
        return s

    for ch in chapters:
        # normalize content paragraphs
        cont = [ _normalize_paragraph_text(p) for p in ch.get('content', []) ]
        # trim leading/trailing empty paragraphs (but keep internal empty paragraphs)
        while cont and (not isinstance(cont[0], str) or cont[0].strip() == ''):
            cont.pop(0)
        while cont and (not isinstance(cont[-1], str) or cont[-1].strip() == ''):
            cont.pop()
        ch['content'] = cont

        # normalize endnotes: strip and drop empties
        ends = []
        for e in ch.get('endnotes', []):
            if not isinstance(e, str):
                continue
            e2 = _normalize_paragraph_text(e).strip()
            if e2 != '':
                ends.append(e2)
        if ends: ch['endnotes'] = ends

        # normalize footnotes similarly
        fnotes = []
        for f in ch.get('footnotes', []):
            if not isinstance(f, str):
                continue
            f2 = _normalize_paragraph_text(f).strip()
            if f2 != '':
                fnotes.append(f2)
        if fnotes: ch['footnotes'] = fnotes

    return chapters


def infer_published_from_title(title):
    # simple YYYY-MM-DD extractor
    m = re.search(r'(20\d{2}-\d{2}-\d{2})', title)
    return m.group(1) if m else None


# --- Web helpers for Japanese metadata ---
import requests
from bs4 import BeautifulSoup, NavigableString
from datetime import date
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Use a single session with browser-like headers to avoid simple anti-bot blocks
_session = requests.Session()
_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
})
# Configure retries for a few status codes and backoff
_retry = Retry(total=3, backoff_factor=0.3, status_forcelist=(429, 500, 502, 503, 504))
_session.mount('https://', HTTPAdapter(max_retries=_retry))
_session.mount('http://', HTTPAdapter(max_retries=_retry))

_cache_series = {}
_cache_series_base = {}  # cache per-series data (total chapters, last_page)
_cache_series_pages = {}  # cache specific TOC pages per (base, page)

# You can hardcode known totals for finished works here to avoid any web requests.
# Map the series base URL (no trailing slash) -> total chapters (int)
KNOWN_SERIES_TOTALS = {
    'https://ncode.syosetu.com/n4830bu': 677
}


def fetch_japanese_chapter_info(chapter_url, no_network=False):
    """Return (japanese_title, chapter_num, total_chapters, originally_published_date)

    originally_published_date is a YYYY-MM-DD string or None.
    This implementation avoids scanning many pages per chapter by:
    - Detecting the '最後へ' (last) page link to locate the final TOC page once per series
    - Fetching only the TOC page that should contain the chapter to get the original date
    """
    if no_network:
        return None, None, None, None

    if chapter_url in _cache_series:
        return _cache_series[chapter_url]

    # attempt to fetch chapter page and get the Japanese title
    jp_title = None
    chap_num = None
    orig_date = None
    total_chapters = None

    try:
        r = _session.get(chapter_url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'lxml')
        h1 = soup.select_one('h1.p-novel__title') or soup.find('h1')
        if h1:
            jp_title = h1.get_text(strip=True)
    except Exception:
        # can't fetch chapter page; continue to try TOC lookups if possible
        pass

    # chapter number from URL
    m = re.search(r'/([0-9]+)/?$', chapter_url)
    chap_num = int(m.group(1)) if m else None

    # series base url
    base = re.sub(r'/[0-9]+/?$', '', chapter_url)
    if base.endswith('/'):
        base = base[:-1]

    # get or compute series-level info
    base_info = _cache_series_base.get(base, {})
    total_chapters = base_info.get('total_chapters')
    last_page = base_info.get('last_page')

    # helper to fetch and cache a TOC page and build a mapping of chapter->date
    def fetch_toc_page(page_num):
        key = (base, page_num)
        if key in _cache_series_pages:
            return _cache_series_pages[key]
        url = f"{base}?p={page_num}"
        rr = _session.get(url, timeout=10)
        if rr.status_code == 403:
            time.sleep(0.3)
            _session.headers.update({'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8'})
            rr = _session.get(url, timeout=10)
        rr.raise_for_status()
        ss = BeautifulSoup(rr.content, 'lxml')

        # build a mapping of chapter number -> date (if present) for quick lookups
        chap_map = {}
        series_id = base.rsplit('/', 1)[-1]
        for a in ss.find_all('a', href=True):
            href = a['href']
            if series_id not in href:
                continue
            m2 = re.search(r'/([0-9]+)/?$', href)
            if not m2:
                continue
            num = int(m2.group(1))
            # Prefer the 'p-eplist__update' div text (exclude nested spans like '（改）')
            date_text = None
            parent = a.parent
            upd = None
            if parent:
                upd = parent.find('div', class_='p-eplist__update') or parent.find_next('div', class_='p-eplist__update')
            if upd:
                parts = [str(n).strip() for n in upd.contents if isinstance(n, NavigableString) and n.strip()]
                if parts:
                    date_text = ' '.join(parts).strip()

            # fallback: check <time> or nearby spans that contain a date
            if not date_text:
                time_tag = a.find_next('time')
                if time_tag and re.search(r'20\d{2}/\d{1,2}/\d{1,2}', time_tag.get_text() or ''):
                    date_text = time_tag.get_text(strip=True)
                else:
                    span_tag = a.find_next('span')
                    if span_tag and re.search(r'20\d{2}/\d{1,2}/\d{1,2}', span_tag.get_text() or ''):
                        date_text = span_tag.get_text(strip=True)

            # final fallback: scan parent text for a date
            if not date_text and parent:
                text = parent.get_text(' ', strip=True)
                if re.search(r'20\d{2}/\d{1,2}/\d{1,2}', text):
                    date_text = text

            dm = re.search(r'(20\d{2})/(\d{1,2})/(\d{1,2})', date_text or '')
            if dm:
                y, mo, da = dm.group(1), dm.group(2).zfill(2), dm.group(3).zfill(2)
                chap_map[num] = f"{y}-{mo}-{da}"
            else:
                chap_map[num] = None
        _cache_series_pages[key] = {'soup': ss, 'chap_map': chap_map}
        return _cache_series_pages[key]

    # If we don't know the total chapters yet, check for a hardcoded known value first
    if total_chapters is None:
        known = KNOWN_SERIES_TOTALS.get(base)
        if known:
            total_chapters = known
            base_info['total_chapters'] = total_chapters
            _cache_series_base[base] = base_info

    # If still unknown, try to discover total chapters using the TOC page for the chapter
    if total_chapters is None:
        try:
            # Determine which TOC page should contain this chapter (100 per page on syosetu)
            page_for_chap = (chap_num - 1) // 100 + 1 if chap_num else 1

            def fetch_toc_page(page_num):
                key = (base, page_num)
                if key in _cache_series_pages:
                    return _cache_series_pages[key]
                url = f"{base}?p={page_num}"
                rr = _session.get(url, timeout=10)
                if rr.status_code == 403:
                    time.sleep(0.3)
                    _session.headers.update({'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8'})
                    rr = _session.get(url, timeout=10)
                rr.raise_for_status()
                ss = BeautifulSoup(rr.content, 'lxml')

                # build a mapping of chapter number -> date (if present) for quick lookups
                chap_map = {}
                series_id = base.rsplit('/', 1)[-1]
                for a in ss.find_all('a', href=True):
                    href = a['href']
                    if series_id not in href:
                        continue
                    m2 = re.search(r'/([0-9]+)/?$', href)
                    if not m2:
                        continue
                    num = int(m2.group(1))
                    # Try to prefer the 'p-eplist__update' div text (exclude nested spans like '（改）')
                    date_text = None
                    parent = a.parent
                    upd = None
                    if parent:
                        upd = parent.find('div', class_='p-eplist__update') or parent.find_next('div', class_='p-eplist__update')
                    if upd:
                        parts = [str(n).strip() for n in upd.contents if isinstance(n, NavigableString) and n.strip()]
                        if parts:
                            date_text = ' '.join(parts).strip()

                    # fallback: check <time> or nearby spans that contain a date
                    if not date_text:
                        time_tag = a.find_next('time')
                        if time_tag and re.search(r'20\d{2}/\d{1,2}/\d{1,2}', time_tag.get_text() or ''):
                            date_text = time_tag.get_text(strip=True)
                        else:
                            span_tag = a.find_next('span')
                            if span_tag and re.search(r'20\d{2}/\d{1,2}/\d{1,2}', span_tag.get_text() or ''):
                                date_text = span_tag.get_text(strip=True)

                    # final fallback: scan parent text for a date
                    if not date_text and parent:
                        text = parent.get_text(' ', strip=True)
                        if re.search(r'20\d{2}/\d{1,2}/\d{1,2}', text):
                            date_text = text

                    # parse YYYY/MM/DD if present; store ISO date or None
                    dm = re.search(r'(20\d{2})/(\d{1,2})/(\d{1,2})', date_text or '')
                    if dm:
                        y, mo, da = dm.group(1), dm.group(2).zfill(2), dm.group(3).zfill(2)
                        chap_map[num] = f"{y}-{mo}-{da}"
                    else:
                        chap_map[num] = None
                _cache_series_pages[key] = {'soup': ss, 'chap_map': chap_map}
                return _cache_series_pages[key]

            # fetch the page that should contain the chapter
            page_data = fetch_toc_page(page_for_chap)
            ss = page_data['soup']
            chap_map = page_data['chap_map']

            # If the page contains a result stats element like 'エピソード 601 ～ 677 を表示中', extract the high number
            stats = ss.select_one('.c-pager__result-stats')
            if stats and stats.get_text(strip=True):
                txt = stats.get_text(strip=True)
                m = re.search(r'～\s*(\d+)', txt)
                if not m:
                    m = re.search(r'(\d+)\s*を表示中', txt)
                if m:
                    total_chapters = int(m.group(1))

            # look for a last-page link element (may be <a> or <span> with class 'c-pager__item--last')
            last_elem = ss.select_one('.c-pager__item--last')
            last_page = None
            if last_elem is not None:
                if last_elem.name == 'a' and last_elem.get('href'):
                    href = last_elem['href']
                    m2 = re.search(r'[?&]p=(\d+)', href)
                    if not m2:
                        m2 = re.search(r'p=(\d+)', href)
                    if m2:
                        last_page = int(m2.group(1))
                else:
                    # if it's a span, the current page is the last page
                    last_page = page_for_chap

            # If we found a candidate last_page but not total_chapters, fetch that page and compute the max chapter number there
            if total_chapters is None and last_page:
                last_data = fetch_toc_page(last_page)
                last_map = last_data['chap_map']
                if last_map:
                    total_chapters = max(last_map.keys())

            # if still missing, conservative fallback: if chap_num present, estimate
            if total_chapters is None and chap_num:
                total_chapters = (chap_num - 1) // 100 * 100 + max(chap_map.keys() or [chap_num])

            if total_chapters:
                base_info['total_chapters'] = total_chapters
                if last_page:
                    base_info['last_page'] = last_page
                _cache_series_base[base] = base_info
        except Exception:
            # best-effort only; leave values as None
            pass

    # To find the originally published date, use the TOC page mapping we cache per (series,page)
    try:
        if chap_num:
            page_for_chap = (chap_num - 1) // 100 + 1
            page_data = fetch_toc_page(page_for_chap)
            chap_map = page_data.get('chap_map', {})

            if chap_num in chap_map and chap_map[chap_num]:
                # chap_map stores ISO date when possible or raw date text
                d = chap_map[chap_num]
                # normalize YYYY/MM/DD to YYYY-MM-DD
                m = re.search(r'(20\d{2})/(\d{1,2})/(\d{1,2})', d or '')
                if m:
                    y, mo, da = m.group(1), m.group(2).zfill(2), m.group(3).zfill(2)
                    orig_date = f"{y}-{mo}-{da}"
                elif re.match(r'20\d{2}-\d{2}-\d{2}', d or ''):
                    orig_date = d
                else:
                    # leave raw text if not parseable
                    orig_date = d
            else:
                # chapter not found on expected page: try adjacent page(s) as a fallback
                for adj in (page_for_chap - 1, page_for_chap + 1):
                    if adj < 1:
                        continue
                    adj_data = fetch_toc_page(adj)
                    adj_map = adj_data.get('chap_map', {})
                    if chap_num in adj_map:
                        d = adj_map[chap_num]
                        m = re.search(r'(20\d{2})/(\d{1,2})/(\d{1,2})', d or '')
                        if m:
                            y, mo, da = m.group(1), m.group(2).zfill(2), m.group(3).zfill(2)
                            orig_date = f"{y}-{mo}-{da}"
                        else:
                            orig_date = d
                        break
    except Exception:
        pass

    _cache_series[chapter_url] = (jp_title, chap_num, total_chapters, orig_date)
    return jp_title, chap_num, total_chapters, orig_date


def main():
    p = argparse.ArgumentParser()
    p.add_argument('docx')
    p.add_argument('--out', required=True, help='Output directory for chapter JSON files')
    p.add_argument('--pattern', default='chapter-{:03d}.json', help='Filename pattern with one format placeholder for index')
    p.add_argument('--chapter-re', default=None, help='Optional regex to detect chapter headings')
    p.add_argument('--start-index', type=int, default=0)
    p.add_argument('--no-network', action='store_true', help='Do not fetch metadata from the web')
    p.add_argument('--force', action='store_true')
    p.add_argument('--dry-run', action='store_true', help='Do not write files; print what would be done')
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    chapters = split_docx(args.docx, args.chapter_re)

    chapters_written = []
    for i, chap in enumerate(chapters, start=args.start_index):
        fname = os.path.join(args.out, args.pattern.format(i))

        # preserve existing metadata if file exists
        existing = None
        if os.path.exists(fname):
            try:
                with open(fname, 'r', encoding='utf-8') as fh:
                    existing = json.load(fh)
            except Exception:
                existing = None

        # If no existing Published, set to today
        if existing and existing.get('metadata') and existing['metadata'].get('Published'):
            chap['metadata']['Published'] = existing['metadata']['Published']
        else:
            chap['metadata']['Published'] = date.today().isoformat()

        # If missing Japanese Chapter or Originally Published, fetch if allowed
        if (not existing or not existing.get('metadata', {}).get('Japanese Chapter')) and chap.get('titlelink') and not args.no_network:
            jp_title, chap_num, total_chaps, orig_date = fetch_japanese_chapter_info(chap['titlelink'], no_network=args.no_network)
            if jp_title:
                if chap_num and total_chaps:
                    chap['metadata']['Japanese Chapter'] = f"{jp_title} ({chap_num}/{total_chaps})"
                elif chap_num:
                    chap['metadata']['Japanese Chapter'] = f"{jp_title} ({chap_num})"
                else:
                    chap['metadata']['Japanese Chapter'] = jp_title
            if not existing or not existing.get('metadata', {}).get('Originally Published'):
                if orig_date:
                    chap['metadata']['Originally Published'] = orig_date
        else:
            # preserve existing Japanese Chapter and Originally Published if present
            if existing and existing.get('metadata'):
                if existing['metadata'].get('Japanese Chapter'):
                    chap['metadata']['Japanese Chapter'] = existing['metadata']['Japanese Chapter']
                if existing['metadata'].get('Originally Published'):
                    chap['metadata']['Originally Published'] = existing['metadata']['Originally Published']

        if args.dry_run:
            snippet = ''
            if chap.get('content'):
                # find first non-empty content paragraph
                for c in chap['content']:
                    if c and c.strip():
                        snippet = c.strip()[:120]
                        break
            print(f'[DRY-RUN] Index={i} File={fname} Title={chap.get("title")} TitleLink={chap.get("titlelink")} Snippet="{snippet}"')
            # print metadata preview in dry-run
            meta_preview = ', '.join(f"{k}={v}" for k, v in chap.get('metadata', {}).items())
            print(f'         METADATA: {meta_preview}')
            continue

        if os.path.exists(fname) and not args.force:
            print(f'Skipping existing: {fname}')
            continue

        with open(fname, 'w', encoding='utf-8') as fh:
            json.dump(chap, fh, ensure_ascii=False, indent=4)
        print(f'Wrote: {fname}')
        chapters_written.append((fname, chap))

    # Update nav file: append new chapters if missing
    try:
        navfile = os.path.normpath(f"{args.out}-nav.json")
        if os.path.exists(navfile):
            print (f"Updating nav file: {navfile}")
            with open(navfile, 'r', encoding='utf-8') as fh:
                nav = json.load(fh)
            if 'chapters' not in nav:
                nav['chapters'] = []
            # map existing content filenames
            existing_contents = {c.get('content') for c in nav['chapters']}
            for fname, chap in chapters_written:
                rel = os.path.relpath(fname, os.path.dirname(navfile)).replace('\\','/')
                if rel not in existing_contents:
                    nav['chapters'].append({'title': chap.get('title'), 'content': os.path.basename(rel)})
                    print(f'Updated nav: added {os.path.basename(rel)}')
            with open(navfile, 'w', encoding='utf-8') as fh:
                json.dump(nav, fh, ensure_ascii=False, indent=4)
    except Exception as e:
        print('Failed to update nav:', e)

if __name__ == '__main__':
    main()
