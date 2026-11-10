"""Compare hard-coded Cloudflare IP ranges in LeilaoMi repos with cloudflare.com/ips-v4|v6.

Each target lists the raw file and which families it must match. v4: the file's
set of IPv4 CIDRs must equal the official list. v6: every official IPv6 CIDR
must appear in the file (files may carry extra hot /48 sub-ranges).
Prints a markdown report; exit 1 on drift.
"""

import json
import re
import sys
import urllib.request

OFFICIAL = "https://api.cloudflare.com/client/v4/ips"  # public, no auth; same data as cloudflare.com/ips-v4|v6
RAW = "https://raw.githubusercontent.com/LeilaoMi/{}/HEAD/{}"
TARGETS = [
    ("cf-best-ip", "src/cidr.js", (4, 6)),
    ("cf-termux-pick", "cf-pick.py", (4, 6)),
    ("doh-proxy", "src/doh.js", (4, 6)),
    ("preferred-sub-generator", "scripts/lib/candidates.js", (4,)),
]
V4 = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}/\d{1,2}\b")
V6 = re.compile(r"\b[0-9a-f]{1,4}:[0-9a-f:]*::/\d{1,3}\b")


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "LeilaoMi-cf-ranges-check"})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 - fixed https hosts
        return r.read().decode()


def main() -> int:
    res = json.loads(get(OFFICIAL))["result"]
    official = {4: set(res["ipv4_cidrs"]), 6: set(res["ipv6_cidrs"])}
    problems = []
    for repo, path, fams in TARGETS:
        text = get(RAW.format(repo, path))
        if 4 in fams:
            found = set(V4.findall(text))
            if found != official[4]:
                problems.append(
                    f"- {repo}/{path} IPv4: missing {sorted(official[4] - found)}, extra {sorted(found - official[4])}"
                )
        if 6 in fams:
            missing = official[6] - set(V6.findall(text))
            if missing:
                problems.append(f"- {repo}/{path} IPv6: missing {sorted(missing)}")
    if problems:
        print("Cloudflare IP ranges drifted:\n\n" + "\n".join(problems))
        return 1
    print("All hard-coded Cloudflare ranges match cloudflare.com/ips-v4 and ips-v6.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
