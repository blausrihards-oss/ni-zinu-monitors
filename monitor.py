#!/usr/bin/env python3
"""
NĪ / būvniecības / arhitektūras ziņu monitors -> Telegram.

Katrā palaišanas reizē:
  1. Iet cauri visiem sources.yaml avotiem.
  2. Katram avotam paņem rakstu sarakstu (RSS, ja ir; citādi HTML scrape).
  3. Izmet visu, kas jau ir seen.json, un visu, kas neiztur atslēgvārdu filtru.
  4. Atlikušo nosūta Telegram čatā, pa vienai ziņai.
  5. Ieraksta jaunos URL seen.json.

Pirmā palaišana: --seed atzīmē visu kā redzētu un neko nesūta (citādi saņemtu 400 ziņas).
"""

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import feedparser
import requests
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
SOURCES_FILE = ROOT / "sources.yaml"
SEEN_FILE = ROOT / "seen.json"
SEEN_LIMIT = 8000

FEED_PATHS = ["/feed/", "/rss", "/rss.xml", "/feed", "/feed/rss/", "/atom.xml", "/index.xml"]

EMOJI = {
    "zinu-portali": "📰",
    "biznesa-mediji": "💼",
    "buvnieciba": "🏗",
    "arhitektura": "📐",
    "ni-portali": "🏠",
    "agenturas": "📊",
    "bankas": "🏦",
    "oficialie": "🏛",
}


# ---------------------------------------------------------------- palīgi

def fold(text: str) -> str:
    """Mazie burti bez diakritikas - lai 'Būvniecība' sakrīt ar 'buvniec'."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower()


def key(url: str) -> str:
    """Stabila atslēga URL - bez utm parametriem un beigu slīpsvītras."""
    url = re.sub(r"[?&](utm_[^=]+|fbclid|gclid)=[^&]*", "", url)
    url = url.rstrip("/?&")
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def load_seen() -> dict:
    if SEEN_FILE.exists():
        try:
            return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("! seen.json bojāts, sāku no nulles", file=sys.stderr)
    return {"keys": [], "updated": None}


def save_seen(seen: dict) -> None:
    seen["keys"] = seen["keys"][-SEEN_LIMIT:]
    seen["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    SEEN_FILE.write_text(json.dumps(seen, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- ievākšana

class Fetcher:
    def __init__(self, settings: dict):
        self.timeout = settings.get("request_timeout", 20)
        self.session = requests.Session()
        self.session.headers["User-Agent"] = settings.get("user_agent", "zinu-monitors/1.0")
        self.session.headers["Accept-Language"] = "lv,en;q=0.8"

    def get(self, url: str):
        try:
            r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            if r.status_code == 200:
                return r
        except requests.RequestException as e:
            print(f"    ! {url}: {type(e).__name__}", file=sys.stderr)
        return None

    def discover_feed(self, home: str, candidates: list[str]) -> str | None:
        """Meklē RSS: vispirms dotie kandidāti, tad <link rel=alternate>, tad tipiskie ceļi."""
        for url in candidates:
            if self._is_feed(url):
                return url

        r = self.get(home)
        if r is not None:
            soup = BeautifulSoup(r.text, "lxml")
            for link in soup.find_all("link", rel=lambda v: v and "alternate" in v):
                t = (link.get("type") or "").lower()
                if "rss" in t or "atom" in t or "xml" in t:
                    href = urljoin(home, link.get("href", ""))
                    if href and self._is_feed(href):
                        return href

        base = f"{urlparse(home).scheme}://{urlparse(home).netloc}"
        for path in FEED_PATHS:
            if self._is_feed(base + path):
                return base + path
        return None

    def _is_feed(self, url: str) -> bool:
        r = self.get(url)
        if r is None:
            return False
        head = r.text[:600].lstrip().lower()
        return "<rss" in head or "<feed" in head or "<rdf" in head


def from_feed(fetcher: Fetcher, feed_url: str, limit: int) -> list[dict]:
    r = fetcher.get(feed_url)
    if r is None:
        return []
    parsed = feedparser.parse(r.content)
    out = []
    for entry in parsed.entries[: limit * 4]:
        link = entry.get("link")
        title = (entry.get("title") or "").strip()
        if not link or not title:
            continue
        summary = BeautifulSoup(entry.get("summary", ""), "lxml").get_text(" ", strip=True)
        out.append({"url": link, "title": title, "summary": summary[:300]})
    return out


def from_scrape(fetcher: Fetcher, cfg: dict, limit: int) -> list[dict]:
    url = cfg["url"]
    r = fetcher.get(url)
    if r is None:
        return []
    soup = BeautifulSoup(r.text, "lxml")
    pattern = re.compile(cfg.get("link_contains", ".")) if cfg.get("link_contains") else None

    out, seen_here = [], set()
    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"].strip())
        if not href.startswith("http"):
            continue
        if pattern and not pattern.search(href):
            continue
        title = a.get_text(" ", strip=True)
        # virsraksts, ne navigācijas poga
        if len(title) < 25 or len(title) > 250:
            continue
        k = key(href)
        if k in seen_here:
            continue
        seen_here.add(k)
        out.append({"url": href, "title": title, "summary": ""})
        if len(out) >= limit * 4:
            break
    return out


# ---------------------------------------------------------------- Telegram

def send(token: str, chat_id: str, text: str) -> bool:
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=25,
    )
    if r.status_code == 429:
        wait = r.json().get("parameters", {}).get("retry_after", 5)
        print(f"    . Telegram rate limit, gaidu {wait}s", file=sys.stderr)
        time.sleep(wait + 1)
        return send(token, chat_id, text)
    if not r.ok:
        print(f"    ! Telegram {r.status_code}: {r.text[:200]}", file=sys.stderr)
    return r.ok


# ---------------------------------------------------------------- galvenais

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", action="store_true",
                    help="atzīmē visu esošo kā redzētu, nesūta neko (pirmajai reizei)")
    ap.add_argument("--dry-run", action="store_true",
                    help="parāda, ko sūtītu, bet nesūta un neraksta seen.json")
    ap.add_argument("--only", help="palaist tikai šo avotu (id no sources.yaml)")
    args = ap.parse_args()

    cfg = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8"))
    settings = cfg.get("settings", {})
    keywords = [fold(k) for k in cfg.get("keywords", [])]
    sources = cfg["sources"]
    if args.only:
        sources = [s for s in sources if s["id"] == args.only]
        if not sources:
            print(f"nav tāda avota: {args.only}", file=sys.stderr)
            return 1

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    live = not (args.seed or args.dry_run)
    if live and not (token and chat_id):
        print("! trūkst TELEGRAM_BOT_TOKEN vai TELEGRAM_CHAT_ID", file=sys.stderr)
        return 1

    seen = load_seen()
    known = set(seen["keys"])
    fetcher = Fetcher(settings)
    per_source = settings.get("max_per_source", 12)
    per_run = settings.get("max_per_run", 25)

    queue, stats = [], []

    for src in sources:
        name = src["name"]
        print(f"-> {name}")
        items: list[dict] = []

        feed_url = src.get("feed")
        if not feed_url and src.get("auto"):
            feed_url = fetcher.discover_feed(src["home"], src.get("feed_candidates", []))
            if feed_url:
                print(f"    feed atrasts: {feed_url}")

        if feed_url:
            items = from_feed(fetcher, feed_url, per_source)

        if not items and src.get("scrape"):
            items = from_scrape(fetcher, src["scrape"], per_source)
            if items:
                print(f"    scrape: {len(items)} saites")

        if not items:
            stats.append((name, 0, "NEIZDEVĀS"))
            continue

        fresh = []
        for item in items:
            k = key(item["url"])
            if k in known:
                continue
            if src.get("filter"):
                blob = fold(item["title"] + " " + item["summary"])
                if not any(kw in blob for kw in keywords):
                    continue
            known.add(k)
            seen["keys"].append(k)
            item["source"] = name
            item["emoji"] = EMOJI.get(src.get("category", ""), "•")
            fresh.append(item)
            if len(fresh) >= per_source:
                break

        stats.append((name, len(fresh), "ok"))
        queue.extend(fresh)

    print(f"\n=== {len(queue)} jauni raksti ===")
    for name, n, status in stats:
        mark = "!" if status != "ok" else " "
        print(f" {mark} {name}: {n if status == 'ok' else status}")

    if args.seed:
        save_seen(seen)
        print(f"\nSEED: {len(seen['keys'])} URL atzīmēti kā redzēti, nekas nav sūtīts.")
        return 0

    if args.dry_run:
        for item in queue[:per_run]:
            print(f"\n{item['emoji']} {item['source']}\n{item['title']}\n{item['url']}")
        return 0

    sent = 0
    for item in queue[:per_run]:
        text = (
            f"{item['emoji']} <b>{html.escape(item['source'])}</b>\n"
            f'<a href="{html.escape(item["url"], quote=True)}">{html.escape(item["title"])}</a>'
        )
        if send(token, chat_id, text):
            sent += 1
        time.sleep(1.2)  # Telegram: ~20 ziņas minūtē vienā čatā

    if len(queue) > per_run:
        send(token, chat_id,
             f"… un vēl {len(queue) - per_run} raksti - nāks nākamajā ciklā.")

    failed = [n for n, _, s in stats if s != "ok"]
    if failed:
        print(f"\nNeizdevās: {', '.join(failed)}", file=sys.stderr)

    save_seen(seen)
    print(f"\nNosūtīts: {sent}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
