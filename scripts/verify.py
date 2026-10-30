import json, os, sys, struct

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = json.load(open(os.path.join(root, "manifest.json"), encoding="utf-8"))

def dims(path):
    with open(path, "rb") as f:
        head = f.read(32)
    if head[:2] == b"\xff\xd8":
        with open(path, "rb") as f:
            d = f.read()
        i = 2
        while i < len(d) - 9:
            if d[i] != 0xFF:
                i += 1
                continue
            m = d[i+1]
            if m in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", d[i+5:i+9])
                return w, h
            if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
                i += 2
                continue
            i += 2 + struct.unpack(">H", d[i+2:i+4])[0]
        return None
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", head[16:24])
        return w, h
    return None

report = {"thumb": {"ok": 0, "missing": [], "bad": [], "bytes": 0, "dims": {}},
          "full": {"ok": 0, "missing": [], "bad": [], "bytes": 0, "dims": {}}}

for r in rows:
    for tier, key in (("thumb", "thumb_path"), ("full", "full_path")):
        p = os.path.join(root, r[key])
        if not os.path.exists(p):
            report[tier]["missing"].append(r[key])
            continue
        sz = os.path.getsize(p)
        if sz < 1024:
            report[tier]["bad"].append((r[key], "size %d" % sz))
            continue
        d = dims(p)
        if d is None:
            report[tier]["bad"].append((r[key], "not an image"))
            continue
        report[tier]["ok"] += 1
        report[tier]["bytes"] += sz
        report[tier]["dims"]["%dx%d" % d] = report[tier]["dims"].get("%dx%d" % d, 0) + 1

print("总条目:", len(rows), "\n")
for tier in ("thumb", "full"):
    t = report[tier]
    print("[%s] 完好 %d / %d  |  %.1f MB" % (tier, t["ok"], len(rows), t["bytes"]/1048576))
    print("   分辨率分布:", t["dims"])
    if t["missing"]:
        print("   缺失 %d:" % len(t["missing"]))
        for m in t["missing"][:15]:
            print("     ", m)
    if t["bad"]:
        print("   损坏 %d:" % len(t["bad"]))
        for m in t["bad"][:15]:
            print("     ", m)
    print()

# folder tree summary
from collections import Counter
c = Counter()
for r in rows:
    c[os.path.dirname(r["thumb_path"])] = c[os.path.dirname(r["thumb_path"])]
dirs = set(os.path.dirname(r["thumb_path"]) for r in rows)
print("姿势目录数:", len(dirs))
print("系列目录数:", len(set(d.replace("\\", "/").split("/")[1] for d in dirs)))

total_ok = sum(report[k]["ok"] for k in report)
if total_ok == 0:
    print("提示：所有文件都缺失，说明还没下载素材。请先运行：")
    print("  python scripts/download.py thumb 16    # 缩略图，约 22 MB")
    print("  python scripts/download.py full 14     # 原图，约 638 MB")
    print("下载完成后重新运行本脚本即可校验。")


# [deploy-patch] 存在缺失或损坏文件时返回非零退出码
_missing = sum(len(report[k]["missing"]) for k in report)
_bad = sum(len(report[k]["bad"]) for k in report)
if _missing or _bad:
    print()
    print("校验失败：缺失 %d 项，损坏 %d 项" % (_missing, _bad))
    sys.exit(1)
print()
print("校验通过：全部文件存在且可解码")
