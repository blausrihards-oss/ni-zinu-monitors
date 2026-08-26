#!/usr/bin/env python3
"""
Vienreizējs pārbaudes skripts: iet cauri visiem sources.yaml avotiem un pasaka,
kuriem ir RSS, kuriem strādā scrape, un kuri vispār nedod neko.

Palaid to PIRMS monitor.py, lai zinātu, ko labot konfigurācijā:

    python discover.py

Rezultāts arī iet failā discover-report.md.
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from monitor import Fetcher, from_feed, from_scrape  # noqa: E402

ROOT = Path(__file__).parent


def main() -> int:
    cfg = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))
    fetcher = Fetcher(cfg.get("settings", {}))

    rows = []
    for src in cfg["sources"]:
        name, sid = src["name"], src["id"]
        print(f"-> {name} ...", flush=True)

        feed = src.get("feed")
        how, detail, n = "", "", 0

        if not feed and src.get("auto"):
            feed = fetcher.discover_feed(src["home"], src.get("feed_candidates", []))

        if feed:
            items = from_feed(fetcher, feed, 5)
            if items:
                how, detail, n = "RSS", feed, len(items)

        if not n and src.get("scrape"):
            items = from_scrape(fetcher, src["scrape"], 5)
            if items:
                how, detail, n = "scrape", src["scrape"]["url"], len(items)

        if not n:
            how, detail = "NEIZDEVĀS", src.get("home", "")

        sample = items[0]["title"][:70] if n else ""
        rows.append((sid, name, how, n, detail, sample))
        print(f"   {how} ({n})")

    ok = [r for r in rows if r[2] != "NEIZDEVĀS"]
    bad = [r for r in rows if r[2] == "NEIZDEVĀS"]

    lines = [
        "# Avotu pārbaude",
        "",
        f"Strādā: **{len(ok)}/{len(rows)}**. Neizdevās: **{len(bad)}**.",
        "",
        "| id | Avots | Kā | Rakstu | Avota adrese | Piemērs |",
        "|---|---|---|---|---|---|",
    ]
    for sid, name, how, n, detail, sample in rows:
        lines.append(f"| `{sid}` | {name} | {how} | {n} | `{detail}` | {sample} |")

    if bad:
        lines += [
            "",
            "## Ko darīt ar neizdevušajiem",
            "",
            "Katram no tiem `sources.yaml` jāielabo `scrape.url` uz reālo ziņu lapas adresi",
            "un `scrape.link_contains` uz to URL fragmentu, kas ir tikai rakstiem.",
            "Atver lapu pārlūkā, paskaties, kā izskatās viena raksta adrese, un ieliec fragmentu.",
            "",
        ]
        for sid, name, *_ in bad:
            lines.append(f"- `{sid}` - {name}")

    (ROOT / "discover-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nStrādā {len(ok)}/{len(rows)}. Atskaite: discover-report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
