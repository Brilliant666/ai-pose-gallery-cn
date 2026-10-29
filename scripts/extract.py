import json, re, os, sys

import json, os, re, sys

base = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(base)

SRC = os.path.join(root, "raw", "index.html")
if not os.path.exists(SRC):
    sys.exit(
        "找不到 raw/index.html。\n"
        "\n"
        "这是原站的整站存档，包含原作者的全部数据与样式，\n"
        "因版权原因不随仓库分发，因此新克隆的仓库里没有这个文件。\n"
        "\n"
        "本脚本仅在需要重新从原站解析数据时使用，普通使用不需要它：\n"
        "  - 仓库已包含解析好的 data/pose.json（或 data/costume.json）\n"
        "  - 想直接看画廊，只需运行 scripts/download.py 下载图片\n"
        "\n"
        "若确实要重新解析，请自行访问原站并保存其 HTML 到 raw/index.html。"
    )

# 原站存档不随仓库分发，只在本地产物里保留
html = open(SRC, encoding="utf-8").read()

def grab_array(src, name):
    key = "const %s=[" % name
    i = src.find(key)
    if i < 0:
        key = "const %s = [" % name
        i = src.find(key)
    if i < 0:
        return None
    j = src.index("[", i)
    depth = 0
    in_str = False
    esc = False
    quote = ""
    for k in range(j, len(src)):
        ch = src[k]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                in_str = False
            continue
        if ch in "\"'":
            in_str = True
            quote = ch
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return src[j:k+1]
    return None

def to_json(s):
    # JS object literal -> JSON: quote bare keys
    s = re.sub(r'([{,]\s*)([A-Za-z_\u3040-\u30ff\u4e00-\u9fff][A-Za-z0-9_\u3040-\u30ff\u4e00-\u9fff]*)\s*:', r'\1"\2":', s)
    s = s.replace("'", '"')
    s = re.sub(r',(\s*[\]}])', r'\1', s)
    return json.loads(s)

out = {}
for name in ["D", "ANG", "POSES", "t", "c", "n", "tabs"]:
    arr = grab_array(html, name)
    if arr is None:
        print("MISS", name)
        continue
    try:
        data = to_json(arr)
        out[name] = data
        print("OK", name, "len=", len(data))
    except Exception as e:
        print("FAIL", name, e, arr[:200])

os.makedirs(os.path.join(root, "data"), exist_ok=True)
json.dump(out, open(os.path.join(root, "data", "pose.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n写出 data/pose.json")
print("--- sample D[0] ---")
print(json.dumps(out["D"][0], ensure_ascii=False, indent=1))
