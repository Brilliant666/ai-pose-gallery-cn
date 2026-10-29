import json, os, re, sys, csv

base = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(base)
data = json.load(open(os.path.join(root, "data", "pose.json"), encoding="utf-8"))
D = data["D"]

def safe(s):
    s = re.sub(r'[\\/:*?"<>|]', "_", s)
    return s.strip().rstrip(".")

rows = []
for d in D:
    series = safe(d["系統"])
    cat = safe(d["分類"])
    pid = safe(d["ポーズ番号"])
    ang = safe(d["アングル"])
    # 固定用正斜杠，避免在 Windows 上生成反斜杠路径（Linux 上无法使用）
    rel_thumb = "/".join(["thumbs", series, cat, pid, ang + ".jpg"])
    rel_full = "/".join(["img", series, cat, pid, ang + ".png"])
    rows.append({
        "id": d["id"], "系列": d["系統"], "分類": d["分類"], "编号": d["ポーズ番号"],
        "姿势名": d["ポーズ名"], "视角": d["アングル"],
        "thumb_url": "https://ai-pose-gallery.pages.dev/" + d["サムネ"],
        "full_url": "https://ai-pose-gallery.pages.dev/" + d["原寸"],
        "thumb_path": rel_thumb, "full_path": rel_full,
    })

# manifest json
json.dump(rows, open(os.path.join(root, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# csv (utf-8-sig for Excel)
with open(os.path.join(root, "manifest.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "系列", "分類", "编号", "姿势名", "视角", "thumb_url", "full_url", "thumb_path", "full_path"])
    w.writeheader()
    w.writerows(rows)

# stats
from collections import Counter, defaultdict
print("总条目:", len(rows))
print("\n系列分布:")
for k, v in Counter(r["系列"] for r in rows).most_common():
    print(f"  {k}: {v}")
print("\n分类分布:")
for k, v in Counter(r["分類"] for r in rows).most_common():
    print(f"  {k}: {v}")
print("\n系列 × 分类:")
for s in Counter(r["系列"] for r in rows):
    cats = Counter(r["分類"] for r in rows if r["系列"] == s)
    print(f"  [{s}] " + " / ".join(f"{c}:{n}" for c, n in cats.most_common()))

poses = {(r["系列"], r["分类"] if "分类" in r else r["分類"], r["编号"]) for r in rows}
print("\n唯一姿势数(系列+分类+编号):", len(poses))
uniq_pose_id = {(r["系列"], r["编号"]) for r in rows}
print("唯一姿势数(系列+编号):", len(uniq_pose_id))
