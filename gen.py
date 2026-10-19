#!/usr/bin/env python3
"""Generate AltStore/Feather source JSON from this repo's releases.

source.json            -> default bundle id (io.nekohasekai.sfamt)
source-<bundle_id>.json -> builds made with a custom bundle_id
"""
import json, os, re, urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "Ti800/sfi-builder")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
DEFAULT_BID = "io.nekohasekai.sfamt"
RAW = f"https://raw.githubusercontent.com/{REPO}/main"
KEEP = 10


def api(path):
    req = urllib.request.Request(f"https://api.github.com/{path}")
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


releases = []
page = 1
while True:
    batch = api(f"repos/{REPO}/releases?per_page=100&page={page}")
    releases += batch
    if len(batch) < 100:
        break
    page += 1

groups = {}
for rel in releases:
    if rel.get("draft"):
        continue
    body = rel.get("body") or ""
    m = re.search(r"Bundle ID: `([^`]+)`", body)
    bid = m.group(1) if m else DEFAULT_BID
    m = re.search(r"App version: `([^`]+)`", body)
    ipa = next((a for a in rel["assets"] if a["name"].endswith(".ipa")), None)
    if not ipa:
        continue
    version = m.group(1) if m else rel["tag_name"].lstrip("v").split("-" + bid)[0]
    groups.setdefault(bid, []).append({
        "version": version,
        "date": rel["published_at"],
        "localizedDescription": f"sing-box {rel['tag_name'].split('-' + bid)[0]}"
                                + (" (pre-release)" if rel["prerelease"] else ""),
        "downloadURL": ipa["browser_download_url"],
        "size": ipa["size"],
        "minOSVersion": "15.0",
    })

if DEFAULT_BID not in groups:
    groups[DEFAULT_BID] = []

for bid, versions in groups.items():
    versions.sort(key=lambda v: v["date"], reverse=True)
    versions = versions[:KEEP]
    app = {
        "name": "sing-box",
        "bundleIdentifier": bid,
        "developerName": "SagerNet",
        "subtitle": "The universal proxy platform",
        "localizedDescription": "Official sing-box (SFI) built from SagerNet source, full version with all extensions, unsigned.",
        "iconURL": f"{RAW}/icon.png",
        "tintColor": "#2D7FF9",
        "category": "utilities",
        "versions": versions,
        "appPermissions": {"entitlements": [], "privacy": {}},
    }
    if versions:
        v = versions[0]
        app.update(version=v["version"], versionDate=v["date"], downloadURL=v["downloadURL"],
                   size=v["size"], versionDescription=v["localizedDescription"])
    src = {
        "name": "sing-box (SFI builds)" + ("" if bid == DEFAULT_BID else f" - {bid}"),
        "identifier": "io.github.ti800.sfi-builder" + ("" if bid == DEFAULT_BID else "." + bid),
        "subtitle": "Unsigned full SFI IPA from official source",
        "website": f"https://github.com/{REPO}",
        "iconURL": f"{RAW}/icon.png",
        "tintColor": "#2D7FF9",
        "apps": [app],
        "news": [],
    }
    fn = "source.json" if bid == DEFAULT_BID else f"source-{bid}.json"
    with open(fn, "w") as f:
        json.dump(src, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(fn, [v["version"] for v in versions])
