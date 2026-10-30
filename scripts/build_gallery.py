# -*- coding: utf-8 -*-
"""构建 ai-pose-gallery-cn 站点

产出：
  index.html                单文件画廊（数据内嵌，file:// 可直接打开）
  data/pose-zh.json         中文记录（供复用/校对）
  data/meta.json            系列 / 分类 / 视角元数据
  data/translations.csv     日⇄中对照表
  robots.txt / sitemap.xml / 404.html

用法：
  SITE_URL=https://your-domain.com python build_gallery.py
"""
import json, os, sys, csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations import SERIES_ZH, CAT_ZH, ANG_ZH, NAME_ZH, UI

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = json.load(open(os.path.join(root, "manifest.json"), encoding="utf-8"))

# 站点地址：部署前用环境变量覆盖，否则 canonical / sitemap 会指向占位域名
SITE_URL = os.environ.get("SITE_URL", "https://example.com").rstrip("/")

ANG_ORDER = ["正面", "横", "斜め", "上から", "下から"]
SERIES_ORDER = ["全身1人・セクシー系", "全身1人・標準系", "上半身1人", "2人絡み"]

poses = {}
for r in rows:
    key = (r["系列"], r["分類"], r["编号"])
    if key not in poses:
        poses[key] = {"s": r["系列"], "c": r["分類"], "p": r["编号"], "n": r["姿势名"],
                      "z": NAME_ZH.get(r["姿势名"], r["姿势名"]), "v": []}
    poses[key]["v"].append({
        "a": r["视角"],
        "t": r["thumb_path"].replace("\\", "/"),
        "f": r["full_path"].replace("\\", "/"),
    })

for p in poses.values():
    p["v"].sort(key=lambda v: ANG_ORDER.index(v["a"]) if v["a"] in ANG_ORDER else 99)

data = list(poses.values())
data.sort(key=lambda p: (SERIES_ORDER.index(p["s"]) if p["s"] in SERIES_ORDER else 99, p["p"]))

series_list = [s for s in SERIES_ORDER if any(p["s"] == s for p in data)]
cats = sorted({p["c"] for p in data})

flat = []
for p in data:
    for v in p["v"]:
        flat.append({"s": p["s"], "c": p["c"], "p": p["p"], "n": p["n"], "z": p["z"],
                     "a": v["a"], "t": v["t"], "f": v["f"]})

payload = json.dumps({
    "poses": data, "flat": flat, "series": series_list, "cats": cats, "angs": ANG_ORDER,
    "seriesZh": SERIES_ZH, "catZh": CAT_ZH, "angZh": ANG_ZH,
    "ui": UI,
}, ensure_ascii=False, separators=(",", ":"))

html = r"""<!doctype html>
<html lang="zh-CN" data-theme="light" data-lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>姿势集 POSE-DB-01 · 离线索引</title>
<meta name="description" content="AI 绘画人体姿势参考图库中文版：288 个姿势、1439 张多视角参考图，含正面・侧面・斜角・俯视・仰视，支持中日双语与浅深主题切换。">
<meta name="keywords" content="AI姿势参考,人体姿势,姿势图库,绘画参考,构图参考,pose reference,マネキン">
<meta name="author" content="Brilliant666">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="__SITE__/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="姿势集 POSE-DB-01">
<meta property="og:title" content="姿势集 POSE-DB-01 · 288 姿势 / 1439 张参考图">
<meta property="og:description" content="AI 绘画人体姿势参考图库中文版。每个姿势提供正面・侧面・斜角・俯视・仰视五个视角。">
<meta property="og:url" content="__SITE__/">
<meta property="og:image" content="__SITE__/og-cover.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="zh_CN">
<meta property="og:locale:alternate" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="姿势集 POSE-DB-01 · 288 姿势 / 1439 张参考图">
<meta name="twitter:description" content="AI 绘画人体姿势参考图库中文版。每个姿势提供五个视角。">
<meta name="twitter:image" content="__SITE__/og-cover.jpg">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%238fb4ff'/%3E%3Ctext x='16' y='23' font-size='19' font-family='sans-serif' font-weight='700' text-anchor='middle' fill='%230d0f12'%3EP%3C/text%3E%3C/svg%3E">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"ImageGallery","name":"姿势集 POSE-DB-01","alternateName":"AI Pose Gallery 中文版","url":"__SITE__/","inLanguage":["zh-CN","ja"],"numberOfItems":1439,"about":"AI 绘画・3D・插画的人体姿势参考","isAccessibleForFree":true,"creator":{"@type":"Person","name":"ギア","url":"https://x.com/giaaibusi"}}
</script>
<script>
/* 首帧前套用已存偏好，避免闪白/闪日文 */
(function(){
  try{
    var t=localStorage.getItem('pg.theme'); if(t==='light'||t==='dark') document.documentElement.dataset.theme=t;
    var l=localStorage.getItem('pg.lang');  if(l==='ja'||l==='zh')      document.documentElement.dataset.lang=l;
  }catch(e){}
})();
</script>
<style>
:root{
  --r:14px;
  --f:system-ui,-apple-system,"Segoe UI","Hiragino Sans","Noto Sans SC","Microsoft YaHei",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --imgbg:#f3f3f1;
}
/* ── 深色（默认，同原站） ── */
html[data-theme="dark"]{
  --bg:#0d0f12;--bg2:#14171c;--panel:#1a1e24;--line:#272c34;--line2:#343a44;
  --tx:#e9ecf1;--tx2:#a3abb8;--tx3:#6c7482;
  --ac:#8fb4ff;--ac2:#c3d5ff;--on-ac:#0b1220;
  --hover:#232831;--hover-border:#3b4350;
  --sh:0 10px 30px rgba(0,0,0,.45);
  --tools-bg:rgba(13,15,18,.86);
  --title-grad:linear-gradient(90deg,var(--ac2),#e3c8ff);
  --scrim:rgba(5,6,8,.9);
  --badge-bg:rgba(13,15,18,.78);
  --dots-bg:rgba(13,15,18,.72);
  --glow1:#1b2433;--glow2:#211a2b;
  --close-border:#5a6270;
  --nav-bg:rgba(13,15,18,.68);--nav-bg-h:rgba(13,15,18,.9);
}
/* ── 浅色 ── */
html[data-theme="light"]{
  --bg:#f4f6f9;--bg2:#ffffff;--panel:#ffffff;--line:#e3e7ed;--line2:#ccd4e0;
  --tx:#16191f;--tx2:#525b6a;--tx3:#8a93a3;
  --ac:#2563eb;--ac2:#1e40af;--on-ac:#ffffff;
  --hover:#eef1f6;--hover-border:#b9c3d2;
  --sh:0 8px 24px rgba(16,24,40,.10);
  --tools-bg:rgba(255,255,255,.88);
  --title-grad:linear-gradient(90deg,#2563eb,#7c3aed);
  --scrim:rgba(15,23,42,.55);
  --badge-bg:rgba(22,25,31,.78);
  --dots-bg:rgba(22,25,31,.72);
  --glow1:#e6eefc;--glow2:#f0e9fb;
  --close-border:#b9c3d2;
  --nav-bg:rgba(22,25,31,.62);--nav-bg-h:rgba(22,25,31,.88);
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--tx);font-family:var(--f);-webkit-font-smoothing:antialiased;
  min-height:100vh;
  background-image:radial-gradient(1200px 500px at 15% -10%,var(--glow1) 0,transparent 60%),
                   radial-gradient(900px 400px at 100% 0,var(--glow2) 0,transparent 55%);
  transition:background-color .22s ease,color .22s ease}
button,select,input{font:inherit;color:inherit}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-thumb{background:var(--line2);border-radius:6px}
::-webkit-scrollbar-track{background:transparent}

/* ── hero ── */
.hero{padding:34px clamp(16px,4vw,48px) 18px;max-width:1600px;margin:0 auto}
.eyebrow{font-size:11.5px;letter-spacing:.22em;color:var(--tx3);text-transform:uppercase}
.hero h1{margin:8px 0 6px;font-size:clamp(25px,3.4vw,38px);font-weight:700;letter-spacing:.02em}
.hero h1 span{background:var(--title-grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--tx2);font-size:13.5px;margin:0;line-height:1.75;max-width:820px}
.sub p{margin:0}
.stats{display:flex;gap:26px;margin-top:18px;flex-wrap:wrap}
.stats div{display:flex;flex-direction:column;gap:2px}
.stats b{font-size:20px;font-weight:700;font-variant-numeric:tabular-nums}
.stats span{font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--tx3)}

/* ── tools ── */
.tools{position:sticky;top:0;z-index:30;background:var(--tools-bg);backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--line);transition:background-color .22s ease}
.tools-in{max-width:1600px;margin:0 auto;padding:10px clamp(16px,4vw,48px)}
.tabs{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px}
.tabs::-webkit-scrollbar{display:none}
.tab{flex:0 0 auto;display:flex;align-items:center;gap:8px;height:36px;padding:0 15px;border:1px solid var(--line2);
  border-radius:10px;background:transparent;color:var(--tx2);font-size:13px;cursor:pointer;white-space:nowrap;transition:.15s}
.tab:hover{background:var(--hover);color:var(--tx)}
.tab[aria-selected="true"]{background:var(--ac);border-color:var(--ac);color:var(--on-ac);font-weight:700}
.tab .n{font-size:11px;opacity:.62;font-variant-numeric:tabular-nums}
.tab[aria-selected="true"] .n{opacity:.8}
.row2{display:flex;align-items:center;gap:10px;margin-top:10px;flex-wrap:wrap}
.search{position:relative;display:flex;align-items:center}
.search svg{position:absolute;left:11px;color:var(--tx3);pointer-events:none}
.search input{width:250px;height:36px;padding:0 12px 0 34px;border:1px solid var(--line2);border-radius:10px;
  background:var(--bg2);font-size:13px;outline:none;transition:.15s}
.search input::placeholder{color:var(--tx3)}
.search input:focus{border-color:var(--ac);box-shadow:0 0 0 3px color-mix(in srgb,var(--ac) 18%,transparent)}
.ftog{height:36px;padding:0 13px;display:flex;align-items:center;gap:7px;border:1px solid var(--line2);
  border-radius:10px;background:transparent;color:var(--tx2);font-size:13px;cursor:pointer;transition:.15s;white-space:nowrap}
.ftog:hover{background:var(--hover);color:var(--tx)}
.ftog[aria-expanded="true"]{border-color:var(--ac);color:var(--ac)}
.ftog b{font-size:11px;min-width:16px;height:16px;display:none;align-items:center;justify-content:center;
  border-radius:8px;background:var(--ac);color:var(--on-ac);font-weight:700;padding:0 4px}
.ftog b.on{display:inline-flex}
.more{display:none;align-items:center;gap:9px;flex-wrap:wrap;flex:1 1 auto}
.more.open{display:flex}
select{height:36px;padding:0 30px 0 11px;border:1px solid var(--line2);border-radius:10px;background:var(--bg2);
  font-size:12.5px;cursor:pointer;outline:none;appearance:none;max-width:220px;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%238a93a3' stroke-width='2.5'><path d='m6 9 6 6 6-6'/></svg>");
  background-repeat:no-repeat;background-position:right 9px center}
select:focus{border-color:var(--ac)}
.seg{display:flex;border:1px solid var(--line2);border-radius:10px;overflow:hidden;background:var(--bg2)}
.seg button{height:34px;padding:0 11px;border:0;background:transparent;color:var(--tx2);font-size:12px;cursor:pointer;
  white-space:nowrap;transition:.13s}
.seg button+button{border-left:1px solid var(--line2)}
.seg button:hover{background:var(--hover);color:var(--tx)}
.seg button[aria-pressed="true"]{background:var(--ac);color:var(--on-ac);font-weight:700}
.count{margin-left:auto;font-size:12.5px;color:var(--tx3);font-variant-numeric:tabular-nums;white-space:nowrap}
.count b{color:var(--tx);font-weight:700}

/* ── 右上角开关组 ── */
.switches{display:flex;gap:8px;align-items:center}
.switch{display:flex;border:1px solid var(--line2);border-radius:10px;overflow:hidden;background:var(--bg2)}
.switch button{height:34px;min-width:34px;padding:0 9px;border:0;background:transparent;color:var(--tx2);
  font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:5px;
  transition:.13s;white-space:nowrap}
.switch button+button{border-left:1px solid var(--line2)}
.switch button:hover{background:var(--hover);color:var(--tx)}
.switch button[aria-pressed="true"]{background:var(--ac);color:var(--on-ac);font-weight:700}
.switch svg{width:14px;height:14px;display:block}

/* ── grid / card ── */
main{max-width:1600px;margin:0 auto;padding:22px clamp(16px,4vw,48px) 90px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(244px,1fr));gap:18px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;cursor:pointer;
  transition:transform .18s ease,box-shadow .18s ease,border-color .18s;outline:none}
.card:hover,.card:focus-visible{transform:translateY(-4px);box-shadow:var(--sh);border-color:var(--hover-border)}
.card:focus-visible{box-shadow:0 0 0 2px var(--ac)}
.ph{position:relative;aspect-ratio:3/4;background:var(--imgbg);overflow:hidden}
.ph img{width:100%;height:100%;object-fit:contain;display:block}
/* 卡片图片渐显：加载完成前透明，避免硬切 */
.card img{opacity:0;transition:opacity .32s ease}
.card img.ld{opacity:1}
.badge{position:absolute;top:10px;left:10px;display:flex;gap:6px}
.badge span{background:var(--badge-bg);color:#fff;font-size:11px;padding:3px 8px;border-radius:99px;
  backdrop-filter:blur(4px);font-variant-numeric:tabular-nums}
.badge span.alt{background:var(--ac);color:var(--on-ac);font-weight:700}
.meta{padding:12px 14px 13px}
.meta h3{margin:0;font-size:14.5px;font-weight:600;line-height:1.4;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.8em}
.meta .id{font-family:var(--mono);font-size:10.5px;color:var(--tx3);margin-top:3px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.meta .cat{font-size:11.5px;color:var(--tx2);margin-top:6px;display:inline-block;
  padding:2px 8px;border-radius:5px;background:var(--hover)}
.strip{display:grid;grid-template-columns:repeat(5,1fr);gap:4px;padding:0 10px 10px}
.strip button{padding:0;border:1px solid var(--line2);border-radius:6px;overflow:hidden;background:var(--imgbg);
  aspect-ratio:3/4;cursor:pointer;position:relative;transition:.13s}
.strip button img{width:100%;height:100%;object-fit:contain;display:block}
.strip button span{position:absolute;left:0;right:0;bottom:0;font-size:9px;background:var(--dots-bg);
  color:#ddd;text-align:center;line-height:1.55}
.strip button:hover{border-color:var(--ac)}
.strip button.on{outline:2px solid var(--ac);outline-offset:1px}
.strip button.on span{background:var(--ac);color:var(--on-ac);font-weight:700}
.empty{grid-column:1/-1;padding:90px 0;text-align:center;color:var(--tx3);font-size:14px;line-height:1.9}
/* 分页：每页 60 组（360 图）/ 120 张单图 */
.loadmore{display:block;margin:34px auto 0;height:46px;padding:0 30px;border:1px solid var(--line2);
  border-radius:12px;background:var(--panel);color:var(--tx2);font-size:13.5px;cursor:pointer;transition:.15s}
.loadmore:hover{border-color:var(--ac);color:var(--ac)}
.loadmore[hidden]{display:none}
.empty b{display:block;color:var(--tx2);font-size:15px;margin-bottom:6px}

/* ── modal ── */
.modal{position:fixed;inset:0;z-index:60;background:var(--scrim);backdrop-filter:blur(6px);
  display:none;align-items:center;justify-content:center;padding:max(12px,env(safe-area-inset-top)) 12px}
.modal.open{display:flex}
.mbox{width:min(1200px,100%);max-height:100%;display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:18px;
  background:var(--bg2);border:1px solid var(--line);border-radius:18px;padding:16px;box-shadow:var(--sh)}
.mimg{position:relative;background:var(--imgbg);border-radius:12px;display:flex;align-items:center;
  justify-content:center;min-height:0;height:min(78vh,900px);overflow:hidden}
.mimg img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.nav{position:absolute;top:50%;transform:translateY(-50%);width:54px;height:54px;border-radius:50%;border:0;
  background:var(--nav-bg);color:#fff;font-size:21px;cursor:pointer;transition:.15s;
  display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.nav:hover{background:var(--nav-bg-h)}
.nav.l{left:10px}.nav.r{right:10px}
.nav:disabled{opacity:.25;cursor:default}
.mside{display:flex;flex-direction:column;gap:13px;min-width:0;overflow:auto}
.mside h2{margin:0;font-size:19px;line-height:1.35;font-weight:700}
.mside .mid{font-family:var(--mono);font-size:11.5px;color:var(--tx3);word-break:break-all;margin-top:4px}
.mkv{display:grid;grid-template-columns:auto 1fr;gap:7px 12px;margin:0;font-size:12.5px}
.mkv dt{color:var(--tx3);white-space:nowrap}
.mkv dd{margin:0;color:var(--tx);text-align:right;overflow:hidden;text-overflow:ellipsis}
.mang{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}
.mang button{padding:0;border:1px solid var(--line2);background:var(--imgbg);border-radius:8px;overflow:hidden;
  cursor:pointer;aspect-ratio:3/4;position:relative;transition:.13s}
.mang button img{width:100%;height:100%;object-fit:contain;display:block}
.mang button span{position:absolute;bottom:0;left:0;right:0;font-size:10px;background:var(--dots-bg);
  color:#eee;text-align:center;line-height:1.6}
.mang button:hover{border-color:var(--ac)}
.mang button.on{outline:2px solid var(--ac);outline-offset:1px}
.mang button.on span{background:var(--ac);color:var(--on-ac);font-weight:700}
.macts{display:flex;flex-direction:column;gap:8px;margin-top:auto}
.macts a,.macts button{height:38px;display:flex;align-items:center;justify-content:center;border-radius:10px;
  border:1px solid var(--line2);background:var(--panel);color:var(--tx);font-size:13px;text-decoration:none;
  cursor:pointer;transition:.15s}
.macts a:hover,.macts button:hover{border-color:var(--ac);color:var(--ac)}
.mclose{position:absolute;top:14px;right:16px;width:50px;height:50px;border-radius:50%;border:1px solid var(--close-border);
  background:var(--panel);color:var(--tx);font-size:22px;cursor:pointer;z-index:2;transition:.15s;line-height:1}
.mclose:hover{background:var(--hover)}
.hint{font-size:11px;color:var(--tx3);line-height:1.7}
.hint kbd{font-family:var(--mono);font-size:10px;padding:1px 5px;border:1px solid var(--line2);border-radius:4px;
  background:var(--panel);color:var(--tx2)}
footer{max-width:1600px;margin:0 auto;padding:0 clamp(16px,4vw,48px) 60px;color:var(--tx3);font-size:12px;line-height:1.9}
footer a{color:var(--tx3)}
footer a:hover{color:var(--ac)}

@media(max-width:1080px){
  .count{margin-left:0}
  .switches{margin-left:auto}
}
@media(max-width:980px){
  .mbox{grid-template-columns:1fr;overflow:auto;padding:12px}
  .mimg{height:52vh}
  .mside{overflow:visible}
}
@media(max-width:560px){
  .grid{grid-template-columns:repeat(2,1fr);gap:10px}
  .meta{padding:9px 10px 10px}
  .meta h3{font-size:12.5px}
  .meta .cat{display:none}
  .strip{gap:3px;padding:0 6px 8px}
  .strip button span{display:none}
  .search input{width:100%}
  .search{flex:1 1 100%}
  .switch button{padding:0 7px;font-size:11px}
}
</style>
</head>
<body>

<header class="hero">
  <div class="eyebrow" data-i18n="eyebrow">POSE-DB-01</div>
  <h1><span data-i18n="brand1">姿势集</span> <em data-i18n="brand2" style="font-style:normal">数据库</em></h1>
  <div class="sub"><p data-i18n="sub1"></p><p data-i18n="sub2" style="margin-top:6px"></p></div>
  <div class="stats">
    <div><b id="stPose">0</b><span data-i18n="statPose">姿势</span></div>
    <div><b id="stImg">0</b><span data-i18n="statImg">图片</span></div>
    <div><b id="stSer">0</b><span data-i18n="statSer">系列</span></div>
    <div><b id="stCat">0</b><span data-i18n="statCat">分类</span></div>
  </div>
</header>

<div class="tools">
  <div class="tools-in">
    <div class="tabs" id="tabs" role="tablist"></div>
    <div class="row2">
      <label class="search">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input id="q" type="search" autocomplete="off">
      </label>
      <button class="ftog" id="ftog" aria-expanded="false"><span data-i18n="filter">筛选</span><b id="fn"></b></button>
      <div class="more" id="more">
        <select id="cat" aria-label="cat"></select>
        <select id="sort" aria-label="sort">
          <option value="series" data-i18n="sortSeries"></option>
          <option value="pid" data-i18n="sortPid"></option>
          <option value="cat" data-i18n="sortCat"></option>
          <option value="name" data-i18n="sortName"></option>
        </select>
        <div class="seg" id="ang" role="group"></div>
        <div class="seg" id="view" role="group">
          <button data-v="pose" aria-pressed="true" data-i18n="viewPose">按姿势</button>
          <button data-v="card" aria-pressed="false" data-i18n="viewCard">单张</button>
        </div>
      </div>
      <span class="count" id="count"></span>
      <div class="switches">
        <div class="switch" id="themeSw" role="group" data-i18n-aria="themeAria">
          <button data-t="light" title="Light" aria-label="Light">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>
          </button>
          <button data-t="dark" title="Dark" aria-label="Dark">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
          </button>
        </div>
        <div class="switch" id="langSw" role="group" data-i18n-aria="langAria">
          <button data-l="zh">中文</button>
          <button data-l="ja">日本語</button>
        </div>
      </div>
    </div>
  </div>
</div>

<main><div class="grid" id="grid"></div><button class="loadmore" id="more" hidden></button></main>

<footer id="foot"></footer>

<div class="modal" id="modal" role="dialog" aria-modal="true">
  <div class="mbox">
    <button class="mclose" id="mclose" aria-label="close">×</button>
    <div class="mimg">
      <img id="mimg" alt="">
      <button class="nav l" id="mprev" aria-label="prev">‹</button>
      <button class="nav r" id="mnext" aria-label="next">›</button>
    </div>
    <div class="mside">
      <div>
        <h2 id="mtitle"></h2>
        <div class="mid" id="mid"></div>
      </div>
      <dl class="mkv" id="mkv"></dl>
      <div class="mang" id="mang"></div>
      <div class="macts">
        <a id="mfull" href="#" target="_blank" rel="noopener" data-i18n="openFull">打开原寸 PNG</a>
        <button id="mcopy" data-i18n="copyPath">复制本地路径</button>
      </div>
      <div class="hint" id="mhint"></div>
    </div>
  </div>
</div>

<script>
const DB = __PAYLOAD__;
const POSES = DB.poses, SERIES = DB.series, CATS = DB.cats, ANGS = DB.angs;
const SZ = DB.seriesZh, CZ = DB.catZh, AZ = DB.angZh, UI = DB.ui;

const $ = s => document.querySelector(s);
const esc = s => String(s==null?'':s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

let LANG  = document.documentElement.dataset.lang  || 'zh';
let THEME = document.documentElement.dataset.theme || 'light';
const PAGE_POSE = 60;    // 每组卡片含 6 张图，60 组 = 360 请求
const PAGE_IMG  = 120;   // 单图视图每卡 1 张
const S = {series:null, cat:null, ang:null, sort:'series', view:'pose', q:'', n:PAGE_POSE};

/* ══ 语言工具 ══ */
const t = k => (UI[LANG] && UI[LANG][k]) || (UI.ja[k] || k);
const isZh = () => LANG === 'zh';
const nS = s => isZh() ? (SZ[s]||s) : s;          // 系列名
const nC = c => isZh() ? (CZ[c]||c) : c;          // 分类名
const nA = a => isZh() ? (AZ[a]||a) : a;          // 视角名
const nN = p => isZh() ? (p.z||p.n) : p.n;        // 姿势名

/* ══ 静态文案 ══ */
function applyStatic(){
  document.documentElement.lang = isZh() ? 'zh-CN' : 'ja';
  document.title = t('title');
  document.querySelectorAll('[data-i18n]').forEach(el=>{ el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll('[data-i18n-aria]').forEach(el=>{ el.setAttribute('aria-label', t(el.dataset.i18nAria)); });
  $('#q').placeholder = t('search');
  $('#mhint').innerHTML = t('hint');
  $('#foot').innerHTML = t('footer');
  $('#stPose').textContent = POSES.length;
  $('#stImg').textContent = POSES.reduce((a,p)=>a+p.v.length,0);
  $('#stSer').textContent = SERIES.length;
  $('#stCat').textContent = CATS.length;
  // 开关状态
  document.querySelectorAll('#themeSw button').forEach(b=>b.setAttribute('aria-pressed', b.dataset.t===THEME?'true':'false'));
  document.querySelectorAll('#langSw button').forEach(b=>b.setAttribute('aria-pressed', b.dataset.l===LANG?'true':'false'));
}

/* ══ 主题 / 语言切换 ══ */
$('#themeSw').addEventListener('click', e=>{
  const b = e.target.closest('button'); if(!b) return;
  THEME = b.dataset.t;
  document.documentElement.dataset.theme = THEME;
  try{ localStorage.setItem('pg.theme', THEME); }catch(_){}
  applyStatic();
});
$('#langSw').addEventListener('click', e=>{
  const b = e.target.closest('button'); if(!b) return;
  LANG = b.dataset.l;
  document.documentElement.dataset.lang = LANG;
  try{ localStorage.setItem('pg.lang', LANG); }catch(_){}
  applyStatic(); drawTabs(); drawCats(); drawAng(); draw();
  if($('#modal').classList.contains('open')) showM();
});

/* ══ 排序 ══ */
const SERIES_IDX = s => { const i = SERIES.indexOf(s); return i<0?99:i; };
const SORTERS = {
  series: (a,b)=> (SERIES_IDX(a.s)-SERIES_IDX(b.s)) || a.p.localeCompare(b.p),
  pid:    (a,b)=> a.p.localeCompare(b.p) || (SERIES_IDX(a.s)-SERIES_IDX(b.s)),
  cat:    (a,b)=> nC(a.c).localeCompare(nC(b.c),'ja') || a.p.localeCompare(b.p),
  name:   (a,b)=> nN(a).localeCompare(nN(b),'ja')
};

/* ══ 系列 tabs ══ */
function drawTabs(){
  const box = $('#tabs'); box.innerHTML='';
  const mk = (k, label, n) => {
    const b=document.createElement('button');
    b.className='tab'; b.setAttribute('role','tab');
    b.setAttribute('aria-selected', S.series===k?'true':'false');
    b.innerHTML='<span>'+esc(label)+'</span><span class="n">'+n+'</span>';
    b.onclick=()=>{ S.series=k; S.cat=null; drawTabs(); drawCats(); draw(); };
    box.appendChild(b);
  };
  mk(null, t('all'), POSES.length);
  SERIES.forEach(s=>mk(s, nS(s), POSES.filter(p=>p.s===s).length));
}

/* ══ 分类 select ══ */
function drawCats(){
  const sel=$('#cat');
  const pool = POSES.filter(p=>!S.series||p.s===S.series);
  const avail = CATS.filter(c=>pool.some(p=>p.c===c));
  sel.innerHTML='';
  const add=(v,label)=>{const o=document.createElement('option');o.value=v;o.textContent=label;sel.appendChild(o)};
  add('', t('catAll')+' ('+pool.length+')');
  avail.forEach(c=>add(c, nC(c)+' ('+pool.filter(p=>p.c===c).length+')'));
  if(S.cat && !avail.includes(S.cat)) S.cat=null;
  sel.value = S.cat||'';
}

/* ══ 视角 seg ══ */
function drawAng(){
  const box=$('#ang'); box.innerHTML='';
  [['',t('angAll')],...ANGS.map(a=>[a,nA(a)])].forEach(([k,label])=>{
    const b=document.createElement('button');
    b.textContent=label;
    b.setAttribute('aria-pressed',(S.ang||'')===k?'true':'false');
    b.onclick=()=>{ S.ang=k||null; drawAng(); draw(); };
    box.appendChild(b);
  });
}

/* ══ 交互绑定 ══ */
$('#view').addEventListener('click', e=>{
  const b=e.target.closest('button'); if(!b) return;
  S.view=b.dataset.v;
  [...e.currentTarget.children].forEach(x=>x.setAttribute('aria-pressed', x===b?'true':'false'));
  draw();
});
$('#sort').addEventListener('change', e=>{ S.sort=e.target.value; draw(); });
$('#cat').addEventListener('change', e=>{ S.cat=e.target.value||null; draw(); });
const ftog=$('#ftog'), more=$('#more');
ftog.onclick=()=>{ const o=more.classList.toggle('open'); ftog.setAttribute('aria-expanded', o?'true':'false'); };
let tid=null;
$('#q').addEventListener('input', e=>{
  clearTimeout(tid);
  tid=setTimeout(()=>{ S.q=e.target.value.trim().toLowerCase(); draw(); },130);
});

/* ══ 过滤 ══ */
function hitPose(p){
  if(S.series && p.s!==S.series) return false;
  if(S.cat && p.c!==S.cat) return false;
  if(S.ang && !p.v.some(v=>v.a===S.ang)) return false;
  if(S.q){
    const hay=(p.n+' '+p.z+' '+p.p+' '+p.c+' '+nC(p.c)+' '+p.s+' '+nS(p.s)).toLowerCase();
    if(!hay.includes(S.q)) return false;
  }
  return true;
}
function hitImg(x){
  if(S.series && x.s!==S.series) return false;
  if(S.cat && x.c!==S.cat) return false;
  if(S.ang && x.a!==S.ang) return false;
  if(S.q){
    const hay=(x.n+' '+x.z+' '+x.p+' '+x.c+' '+nC(x.c)+' '+x.s+' '+nS(x.s)+' '+x.a+' '+nA(x.a)).toLowerCase();
    if(!hay.includes(S.q)) return false;
  }
  return true;
}
function badge(){
  const n=[S.cat,S.ang].filter(Boolean).length + (S.view==='card'?1:0) + (S.sort!=='series'?1:0);
  const el=$('#fn'); el.textContent=n||''; el.classList.toggle('on', n>0);
}

/* ══ 渲染 ══ */
const grid=$('#grid'), countEl=$('#count'), moreEl=$('#more');
let VIEWLIST=[];

function pageSize(){ return S.view==='pose' ? PAGE_POSE : PAGE_IMG; }

function draw(){
  const ORDERED = POSES.slice().sort(SORTERS[S.sort] || SORTERS.series);

  if(S.view==='pose'){
    const ps = ORDERED.filter(hitPose);
    VIEWLIST = ps.map(p=>({p, d:(S.ang && p.v.find(v=>v.a===S.ang)) || p.v[0]}));
    const imgN = ps.reduce((a,p)=>a+(S.ang?p.v.filter(v=>v.a===S.ang).length:p.v.length),0);
    countEl.innerHTML = t('countPose').replace('{n}',ps.length).replace('{m}',imgN);
  } else {
    const ds = ORDERED.flatMap(p=>p.v.map(v=>({p,v}))).filter(o=>hitImg({s:o.p.s,c:o.p.c,p:o.p.p,n:o.p.n,z:o.p.z,a:o.v.a}));
    VIEWLIST = ds.map(o=>({p:o.p, d:o.v}));
    countEl.innerHTML = t('countImg').replace('{n}',ds.length);
  }

  if(!VIEWLIST.length){
    grid.innerHTML = '<div class="empty"><b>'+esc(t('emptyTitle'))+'</b>'+esc(t('emptyDesc'))+'</div>';
    moreEl.hidden = true;
    badge(); return;
  }

  // 筛选/排序/视图变化都回到第一页
  S.n = pageSize();
  grid.innerHTML = VIEWLIST.slice(0, S.n).map(renderCard).join('');
  sweepLoaded(); syncMore(); badge();
}

function renderCard({p,d}, i){
  return S.view==='pose' ? cardPose(p,d,i) : cardImg(p,d,i);
}

function addMore(){
  if(S.n >= VIEWLIST.length) return;
  const from = S.n;
  S.n = Math.min(S.n + pageSize(), VIEWLIST.length);
  grid.insertAdjacentHTML('beforeend', VIEWLIST.slice(from, S.n).map((o,k)=>renderCard(o, from+k)).join(''));
  sweepLoaded(); syncMore();
}

// 已在缓存中的图片不会触发 load，直接补渐显类
function sweepLoaded(){
  grid.querySelectorAll('img').forEach(im=>{ if(im.complete) im.classList.add('ld'); });
}

function syncMore(){
  const rest = VIEWLIST.length - S.n;
  moreEl.hidden = rest <= 0;
  moreEl.textContent = rest > 0 ? ('加载更多（剩余 ' + rest + ' 组）') : '';
}

function cardPose(p, d, i){
  const strip = p.v.map(v=>
    '<button data-a="'+esc(v.a)+'" class="'+(v.a===d.a?'on':'')+'" title="'+esc(nA(v.a))+'">'+
      '<img loading="lazy" decoding="async" src="'+esc(v.t)+'" alt="'+esc(nA(v.a))+'"><span>'+esc(nA(v.a))+'</span>'+
    '</button>').join('');
  return '<article class="card" tabindex="0" data-i="'+i+'">'+
    '<div class="ph"><img'+(i<12?' fetchpriority="high"':' loading="lazy"')+' decoding="async" src="'+esc(d.t)+'" alt="'+esc(nN(p))+'">'+
      '<div class="badge"><span>'+esc(p.p)+'</span></div></div>'+
    '<div class="meta"><h3>'+esc(nN(p))+'</h3>'+
      '<div class="id">'+esc(nS(p.s))+' · '+esc(p.p)+'</div>'+
      '<div class="cat">'+esc(nC(p.c))+'</div></div>'+
    '<div class="strip">'+strip+'</div></article>';
}

function cardImg(p, v, i){
  return '<article class="card" tabindex="0" data-i="'+i+'">'+
    '<div class="ph"><img'+(i<12?' fetchpriority="high"':' loading="lazy"')+' decoding="async" src="'+esc(v.t)+'" alt="'+esc(nN(p))+'">'+
      '<div class="badge"><span class="alt">'+esc(nA(v.a))+'</span></div></div>'+
    '<div class="meta"><h3>'+esc(nN(p))+'</h3>'+
      '<div class="id">'+esc(p.p)+' · '+esc(nA(v.a))+'</div>'+
      '<div class="cat">'+esc(nS(p.s))+' · '+esc(nC(p.c))+'</div></div></article>';
}

/* ══ 卡片交互 ══ */
grid.addEventListener('mouseover', e=>{
  const b=e.target.closest('.strip button'); if(!b) return;
  const c=b.closest('.card'), it=VIEWLIST[+c.dataset.i]; if(!it) return;
  const v=it.p.v.find(x=>x.a===b.dataset.a); if(!v) return;
  c.querySelector('.ph img').src=v.t;
  c.querySelectorAll('.strip button').forEach(x=>x.classList.toggle('on', x===b));
});
moreEl.onclick = addMore;
if('IntersectionObserver' in window){
  new IntersectionObserver(es=>{ if(es.some(e=>e.isIntersecting)) addMore(); }, {rootMargin:'800px'}).observe(moreEl);
}
grid.addEventListener('load', e=>{ if(e.target.tagName==='IMG') e.target.classList.add('ld'); }, true);
grid.addEventListener('error', e=>{ if(e.target.tagName==='IMG') e.target.classList.add('ld'); }, true);
grid.addEventListener('click', e=>{
  const c=e.target.closest('.card'); if(!c) return;
  const it=VIEWLIST[+c.dataset.i]; if(!it) return;
  const b=e.target.closest('.strip button');
  const v = b ? it.p.v.find(x=>x.a===b.dataset.a) : it.d;
  openM(+c.dataset.i, v || it.d);
});
grid.addEventListener('keydown', e=>{
  if(e.key!=='Enter' && e.key!==' ') return;
  const c=e.target.closest('.card'); if(!c) return;
  e.preventDefault(); openM(+c.dataset.i, VIEWLIST[+c.dataset.i].d);
});

/* ══ 灯箱 ══ */
const modal=$('#modal'), mimg=$('#mimg');
let M={i:0, d:null};

function openM(i, v){
  M={i, d:v};
  modal.classList.add('open');
  document.body.style.overflow='hidden';
  showM();
  $('#mclose').focus();
}
function closeM(){
  modal.classList.remove('open');
  document.body.style.overflow='';
  mimg.removeAttribute('src');
  const c=document.querySelector('.card[data-i="'+M.i+'"]');
  if(c) c.focus();
}
function showM(){
  const it=VIEWLIST[M.i]; if(!it) return;
  const p=it.p, v=M.d||it.d;

  mimg.src = v.t;
  const full=new Image();
  full.onload=()=>{ if(M.d===v) mimg.src=v.f; };
  full.src = v.f;
  mimg.alt = nN(p)+' '+nA(v.a);

  $('#mtitle').textContent = nN(p);
  $('#mid').textContent = p.p + ' · ' + nA(v.a);
  $('#mfull').href = v.f;

  $('#mkv').innerHTML = [
    [t('kSeries'), nS(p.s)],
    [t('kCat'), nC(p.c)],
    [t('kPid'), p.p],
    [t('kAng'), nA(v.a)],
    [t('kAngN'), p.v.length + ' ' + t('angUnit')]
  ].map(([k,val])=>'<dt>'+esc(k)+'</dt><dd>'+esc(val)+'</dd>').join('');

  $('#mang').innerHTML = p.v.map(x=>
    '<button data-a="'+esc(x.a)+'" class="'+(x.a===v.a?'on':'')+'" title="'+esc(nA(x.a))+'">'+
      '<img src="'+esc(x.t)+'" alt="'+esc(nA(x.a))+'"><span>'+esc(nA(x.a))+'</span></button>').join('');

  const single = p.v.length<2;
  $('#mprev').disabled = single;
  $('#mnext').disabled = single;
}

$('#mang').onclick = e=>{
  const b=e.target.closest('button'); if(!b) return;
  const it=VIEWLIST[M.i];
  const v=it.p.v.find(x=>x.a===b.dataset.a);
  if(v){ M.d=v; showM(); }
};
$('#mprev').onclick = ()=>stepA(-1);
$('#mnext').onclick = ()=>stepA(1);
$('#mclose').onclick = closeM;
modal.onclick = e=>{ if(e.target===modal) closeM(); };

function stepA(n){
  const it=VIEWLIST[M.i]; if(!it) return;
  const order=it.p.v; if(order.length<2) return;
  const cur=order.findIndex(x=>x.a===(M.d||it.d).a);
  M.d = order[(cur+n+order.length)%order.length];
  showM();
}
function stepP(n){
  const j=M.i+n; if(j<0||j>=VIEWLIST.length) return;
  const np=VIEWLIST[j].p;
  const same=np.v.find(x=>x.a===(M.d||VIEWLIST[M.i].d).a);
  M={i:j, d:same||np.v[0]};
  showM();
}

document.addEventListener('keydown', e=>{
  if(!modal.classList.contains('open')) return;
  if(e.key==='Escape') closeM();
  else if(e.key==='ArrowRight'){ e.preventDefault(); stepA(1); }
  else if(e.key==='ArrowLeft'){ e.preventDefault(); stepA(-1); }
  else if(e.key==='ArrowDown'){ e.preventDefault(); stepP(1); }
  else if(e.key==='ArrowUp'){ e.preventDefault(); stepP(-1); }
});

let tx=null;
mimg.addEventListener('touchstart', e=>{ tx=e.touches[0].clientX; }, {passive:true});
mimg.addEventListener('touchend', e=>{
  if(tx===null) return;
  const dx=e.changedTouches[0].clientX-tx;
  if(Math.abs(dx)>40) stepA(dx<0?1:-1);
  tx=null;
}, {passive:true});

$('#mcopy').onclick = function(){
  const it=VIEWLIST[M.i]; if(!it) return;
  const v=M.d||it.d;
  const done=ok=>{ this.textContent = ok?t('copied'):t('copyFail'); setTimeout(()=>{ this.textContent=t('copyPath'); },1400); };
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(v.f).then(()=>done(true)).catch(()=>done(false));
  } else { done(false); }
};

applyStatic(); drawTabs(); drawCats(); drawAng(); draw();
</script>
</body>
</html>"""

html = html.replace("__PAYLOAD__", payload).replace("__SITE__", SITE_URL)
out = os.path.join(root, "index.html")
open(out, "w", encoding="utf-8").write(html)
print("wrote index.html", "%.1f KB" % (os.path.getsize(out) / 1024))
print("poses:", len(data), "| flat:", len(flat), "| series:", len(series_list), "| cats:", len(cats))

# ── 导出可复用的数据文件 ─────────────────────────────
data_dir = os.path.join(root, "data")
os.makedirs(data_dir, exist_ok=True)

# 中文记录（供复用与校对）
zh = []
for p in data:
    for v in p["v"]:
        zh.append({
            "id": p["p"] + "_" + v["a"],
            "系列": p["s"], "系列_zh": SERIES_ZH.get(p["s"], p["s"]),
            "分类": p["c"], "分类_zh": CAT_ZH.get(p["c"], p["c"]),
            "姿势编号": p["p"],
            "姿势名": p["n"], "姿势名_zh": p["z"],
            "视角": v["a"], "视角_zh": ANG_ZH.get(v["a"], v["a"]),
            "缩略图": v["t"], "原图": v["f"],
        })
json.dump(zh, open(os.path.join(data_dir, "pose-zh.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# 元数据
meta = {
    "site": "POSE-DB-01",
    "source": "https://ai-pose-gallery.pages.dev/",
    "author": "ギア (@giaaibusi)",
    "poses": len(data),
    "images": len(flat),
    "系列": [{"ja": s, "zh": SERIES_ZH.get(s, s),
              "poses": sum(1 for p in data if p["s"] == s)} for s in series_list],
    "分类": [{"ja": c, "zh": CAT_ZH.get(c, c),
              "poses": sum(1 for p in data if p["c"] == c)} for c in cats],
    "视角": [{"ja": a, "zh": ANG_ZH.get(a, a)} for a in ANG_ORDER],
}
json.dump(meta, open(os.path.join(data_dir, "meta.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# 日⇄中对照表
with open(os.path.join(data_dir, "translations.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["字段", "日文原文", "中文译文"])
    for k, v in SERIES_ZH.items():
        w.writerow(["系統", k, v])
    for k, v in CAT_ZH.items():
        w.writerow(["分類", k, v])
    for k, v in ANG_ZH.items():
        w.writerow(["アングル", k, v])
    for k, v in NAME_ZH.items():
        w.writerow(["ポーズ名", k, v])
print("wrote data/pose-zh.json, data/meta.json, data/translations.csv")

# ── SEO 附属文件 ─────────────────────────────────────
with open(os.path.join(root, "robots.txt"), "w", encoding="utf-8") as f:
    f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL)

with open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    f.write('  <url><loc>%s/</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>\n' % SITE_URL)
    f.write('</urlset>\n')

with open(os.path.join(root, "404.html"), "w", encoding="utf-8") as f:
    f.write("""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>404 · 页面不存在</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%238fb4ff'/%3E%3Ctext x='16' y='23' font-size='19' font-family='sans-serif' font-weight='700' text-anchor='middle' fill='%230d0f12'%3EP%3C/text%3E%3C/svg%3E">
<style>
html,body{margin:0;height:100%%}
body{background:#0d0f12;color:#e9ecf1;font-family:system-ui,-apple-system,"Noto Sans SC","Microsoft YaHei",sans-serif;
  display:flex;align-items:center;justify-content:center;text-align:center;
  background-image:radial-gradient(1200px 500px at 15%% -10%%,#1b2433 0,transparent 60%%),
                   radial-gradient(900px 400px at 100%% 0,#211a2b 0,transparent 55%%)}
.box{padding:24px}
h1{margin:0 0 10px;font-size:64px;font-weight:700;letter-spacing:.02em;
  background:linear-gradient(90deg,#c3d5ff,#e3c8ff);-webkit-background-clip:text;background-clip:text;color:transparent}
p{margin:0 0 22px;color:#a3abb8;font-size:14px;line-height:1.8}
a{display:inline-flex;align-items:center;height:40px;padding:0 20px;border-radius:10px;
  background:#8fb4ff;color:#0b1220;font-size:13.5px;font-weight:700;text-decoration:none}
a:hover{background:#c3d5ff}
</style></head>
<body><div class="box">
<h1>404</h1>
<p>页面不存在，或链接已失效。<br>Page not found.</p>
<a href="/">返回首页</a>
</div></body></html>
""")
print("wrote robots.txt, sitemap.xml, 404.html")
print("SITE_URL =", SITE_URL)
