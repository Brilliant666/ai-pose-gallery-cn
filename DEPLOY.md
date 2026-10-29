# 部署手册 · 参考素材库上 VPS

> 本手册面向执行部署的对话/操作者，所有命令可直接复制执行。
> 覆盖两个站点：`ai-pose-gallery-cn` 与 `ai-costume-gallery-cn`。
>
> **在线地址**：<https://github.com/Brilliant666/ai-pose-gallery-cn/blob/main/DEPLOY.md>
> VPS 上可直接拉取：
> ```bash
> curl -fsSL https://raw.githubusercontent.com/Brilliant666/ai-pose-gallery-cn/main/DEPLOY.md -o DEPLOY.md
> ```
> 本文件由 `ai-pose-gallery-cn` 仓库维护，同时适用于 `ai-costume-gallery-cn`。

---

## 0. 前置条件

| 项 | 要求 | 说明 |
|---|---|---|
| 系统 | Ubuntu 20.04+ / Debian 11+ | 其他发行版需自行调整包管理器 |
| 权限 | root 或 sudo | 安装 nginx、写 `/var/www` |
| Python | 3.8+ | 仅用标准库，**无需 pip install** |
| 磁盘 | ≥ 3 GB 可用 | 图片共 2.1 GB |
| 内存 | ≥ 512 MB | 纯静态站点，无运行时 |
| 带宽 | ≥ 5 Mbps | 原图单张最大 1.8 MB，低于此体验差 |
| 域名 | 已解析到本机 IP | 签 HTTPS 证书必需 |

**检查命令：**

```bash
python3 --version          # 需 ≥ 3.8
df -h /var/www 2>/dev/null || df -h /
free -m | head -2
```

---

## 1. 部署路径选择

两种方式，**二选一**。

### 路径 A（推荐）：VPS 自己拉取

VPS 直接从 GitHub 克隆代码，再从原始站点下载图片。**不需要本地机器参与。**

- 优点：全自动，一条命令链路
- 前提：VPS 能访问 GitHub 与 `ai-pose-gallery.pages.dev`

### 路径 B：本地上传

在本地 Windows 机器执行 `deploy.sh`，用 scp 上传。

- 优点：VPS 不需要外网出口，适合国内受限环境
- 缺点：2.1 GB 走 SSH，耗时取决于上行带宽

> **判断方法**：先跑 `curl -sI https://ai-pose-gallery.pages.dev/ | head -1`，返回 `HTTP/2 200` 就走路径 A，超时就走路径 B。

---

## 2. 路径 A：VPS 自己拉取

### 2.1 安装依赖

```bash
apt update
apt install -y git python3 nginx
```

### 2.2 拉取代码

```bash
mkdir -p /var/www/refsite
cd /var/www/refsite

git clone https://github.com/Brilliant666/ai-pose-gallery-cn.git pose
git clone https://github.com/Brilliant666/ai-costume-gallery-cn.git costume
```

**预期**：两个目录各 25 个文件，**不含图片**（图片因版权原因不入库）。

```bash
find pose -type f -not -path '*/.git/*' | wc -l      # 应为 25
find costume -type f -not -path '*/.git/*' | wc -l   # 应为 25
ls pose/thumbs 2>/dev/null || echo "thumbs 不存在 —— 正常"
```

### 2.3 下载图片

```bash
cd /var/www/refsite/pose
python3 scripts/download.py thumb 16      # 1439 张 JPG，约 22 MB，约 50 秒
python3 scripts/download.py full 14       # 1439 张 PNG，约 638 MB，约 3-8 分钟

cd /var/www/refsite/costume
python3 scripts/download.py thumb 16      # 1407 张 webp，约 10 MB
python3 scripts/download.py img 14        # 1407 张 webp，约 114 MB
python3 scripts/download.py png 14        # 1407 张 PNG，约 1.33 GB，可选
```

> **`png` 是可选的**。只下 `thumb` + `img` 就能正常浏览（124 MB），`png` 只是原寸无损版。
> 若磁盘紧张，跳过 costume 的 `png`，省 1.33 GB。

**断点续传**：脚本会自动跳过已存在且大于 1 KB 的文件，中断后重跑同一条命令即可。

**预期输出**（最后三行）：

```
完成 1439/1439, 637.6 MB, 用时 XXXs
无失败
```

若出现 `失败 N 条`，重跑同一命令即可补传。

### 2.4 校验完整性

```bash
cd /var/www/refsite/pose && python3 scripts/verify.py
cd /var/www/refsite/costume && python3 scripts/verify.py
```

**预期**：

| 站点 | 输出 |
|---|---|
| pose | `[thumb] 完好 1439 / 1439`、`[full] 完好 1439 / 1439` |
| costume | `[thumb] 1407 / 1407`、`[img] 1407 / 1407`、`[png] 1407 / 1407`（若已下） |

### 2.5 用真实域名重新构建

**这一步不能跳过。** 仓库里的 `canonical`、`og:url`、`sitemap.xml` 都指向占位域名 `example.com`，必须替换成真实域名，否则搜索引擎会收录错误地址。

```bash
export SITE_URL="https://你的域名.com"

cd /var/www/refsite/pose
SITE_URL="$SITE_URL" python3 scripts/build_gallery.py

cd /var/www/refsite/costume
SITE_URL="$SITE_URL" python3 scripts/build_gallery.py
```

**验证已生效：**

```bash
grep -o 'rel="canonical" href="[^"]*"' /var/www/refsite/pose/index.html
grep -o 'rel="canonical" href="[^"]*"' /var/www/refsite/costume/index.html
```

两条都应输出 `https://你的域名.com/`。

> 注意：两个站点的 canonical 都是各自根路径 `/`。因为它们是分别部署在 `/pose/` 和 `/costume/` 下的独立站点，
> 若希望 canonical 带上子路径，改用：
> `SITE_URL="https://你的域名.com/pose"`（costume 同理）。

---

## 3. 路径 B：本地上传（备选）

在**本地 Windows** 机器执行（Git Bash）：

```bash
cd <本项目所在目录>/deploy
./deploy.sh root@你的服务器IP /var/www/refsite
```

脚本会分 7 步上传，每步可独立重试。完成后在 VPS 上继续执行 §2.5（重建域名）与 §4（nginx）。

> 本机**没有 rsync**，脚本自动退化为 scp 分块传输，无断点续传。若中途断线，重跑即可（已传的文件会被跳过）。

---

## 4. 配置 nginx

### 4.1 写入站点配置

```bash
cat > /etc/nginx/sites-available/refsite <<'NGINX'
server {
    listen 80;
    listen [::]:80;
    server_name 你的域名.com;
    return 301 https://$host$request_uri;
}

server {
    # Ubuntu 20.04/22.04 自带 nginx 1.18，用下面这种写法
    # nginx ≥ 1.25.1 请改为：listen 443 ssl; listen [::]:443 ssl; http2 on;
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name 你的域名.com;

    ssl_certificate     /etc/letsencrypt/live/你的域名.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/你的域名.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_session_cache   shared:SSL:10m;

    root  /var/www/refsite;
    index index.html;

    charset utf-8;
    autoindex off;

    sendfile on;
    tcp_nopush on;
    keepalive_timeout 65;

    # 7000+ 小文件，开元数据缓存
    open_file_cache          max=10000 inactive=60s;
    open_file_cache_valid    120s;
    open_file_cache_min_uses 2;
    open_file_cache_errors   on;

    gzip on;
    gzip_vary on;
    gzip_comp_level 5;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/javascript application/json image/svg+xml;

    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy no-referrer always;
    add_header X-Frame-Options SAMEORIGIN always;

    # 图片：内容永不变，一年强缓存
    location ~ ^/(pose|costume)/(thumbs|img|png)/ {
        add_header Cache-Control "public, max-age=31536000, immutable" always;
        add_header X-Content-Type-Options nosniff always;
        access_log off;
        try_files $uri =404;
    }

    # 页面与清单：每次回源验证
    location ~* \.(html|json|csv|xml|txt)$ {
        add_header Cache-Control "no-cache, must-revalidate" always;
        add_header X-Content-Type-Options nosniff always;
        try_files $uri =404;
    }

    # 每个子站用自己的 404 页
    location /pose/ {
        try_files $uri $uri/ =404;
        error_page 404 /pose/404.html;
    }

    location /costume/ {
        try_files $uri $uri/ =404;
        error_page 404 /costume/404.html;
    }

    location / {
        try_files $uri $uri/ =404;
    }
}
NGINX
```

**把 `你的域名.com` 全部替换成真实域名**（共 4 处）：

```bash
sed -i 's/你的域名\.com/实际域名.com/g' /etc/nginx/sites-available/refsite
grep -c "实际域名.com" /etc/nginx/sites-available/refsite    # 应为 4
```

### 4.2 启用并测试

```bash
ln -sf /etc/nginx/sites-available/refsite /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
```

**`nginx -t` 必须输出 `syntax is ok` 和 `test is successful`。** 此时证书还不存在会报错——先做 §5 签证书，再回来 `nginx -t`。

> 顺序建议：先只启用 HTTP 块签证书（certbot 会自动改配置），或临时注释掉 443 块。

**最简做法**：先写一个只有 80 端口的配置，签完证书让 certbot 自动补 443 块：

```bash
cat > /etc/nginx/sites-available/refsite <<'NGINX'
server {
    listen 80;
    server_name 实际域名.com;
    root /var/www/refsite;
    index index.html;
    charset utf-8;
    autoindex off;
    location / { try_files $uri $uri/ =404; }
}
NGINX
ln -sf /etc/nginx/sites-available/refsite /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

签完证书（§5）后，再把 §4.1 的完整配置写回去。

---

### 4.3 访问控制（推荐：私有）

**部署前先想清楚这一节。** 图片著作权归原作者，原站条款禁止再分发；站点一旦公开可访问，
任何人就能批量抓走全部原图，性质上等于你再分发了它们。

若只需自己或团队访问，加一层 Basic Auth 即可规避，代价只有两行配置。

```bash
apt install -y apache2-utils
htpasswd -c /etc/nginx/.htpasswd 你的用户名
# 按提示输入两次密码（-c 表示新建文件，之后再加用户要去掉 -c）
```

然后在 `/etc/nginx/sites-available/refsite` 的 **443 server{} 块内**，紧跟 `index index.html;` 之后插入两行：

```nginx
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
```

```bash
nginx -t && systemctl reload nginx
curl -sI https://实际域名.com/pose/ | head -1    # 应返回 401
```

浏览器再次访问会弹出登录框。

> **替代方案：IP 白名单**。只从固定 IP 访问时更简单，在同一个 server{} 块内加：
> ```nginx
> allow 你的固定IP;
> deny all;
> ```
> 注意：家用宽带 IP 会变，不适合长期使用。

> **若确实要公开**，请先阅读 §11 版权提示，并了解风险由你承担。

---

## 5. HTTPS 证书

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d 实际域名.com --agree-tos -m 你的邮箱@example.com --redirect
```

**预期**：输出 `Congratulations! You have successfully enabled HTTPS`。

**自动续期检查：**

```bash
systemctl list-timers | grep certbot
certbot renew --dry-run
```

---

## 6. 可选：入口页

一个把两个画廊并列展示的首页，放在站点根目录。**可选，不影响两个画廊独立访问。**

本地文件位置：`deploy/index.html`（约 12 KB）。上传方式：

```bash
# 在本地执行
scp deploy/index.html root@服务器IP:/var/www/refsite/index.html
```

页面里的封面图指向 `./pose/thumbs/...` 与 `./costume/thumbs/...`，只要两个画廊在对应子目录就能正常显示。

> 该页面的封面图会显示真实缩略图。若不希望公开，可跳过本节，直接访问 `/pose/` 和 `/costume/`。

---

## 7. 验证清单

逐项执行，全部通过才算部署成功。

### 7.1 文件与体积

```bash
du -sh /var/www/refsite/pose /var/www/refsite/costume
```

| 站点 | 预期 |
|---|---|
| pose | 约 660 MB |
| costume | 约 1.45 GB（未下 png 则约 125 MB） |

```bash
find /var/www/refsite/pose -name '*.jpg' | wc -l      # 1439
find /var/www/refsite/pose -name '*.png' | wc -l      # 1439
find /var/www/refsite/costume -name '*.webp' | wc -l  # 2814（thumb + img）
```

### 7.2 HTTP 响应

```bash
curl -sI https://实际域名.com/pose/ | head -1        # HTTP/2 200
curl -sI https://实际域名.com/costume/ | head -1     # HTTP/2 200
curl -sI https://实际域名.com/robots.txt | head -1   # 200
```

### 7.3 缓存头是否正确

```bash
# 图片：应为 immutable，max-age 一年
curl -sI "https://实际域名.com/pose/thumbs/全身1人・セクシー系/立ち/P001/正面.jpg" | grep -i cache-control

# 页面：应为 no-cache
curl -sI https://实际域名.com/pose/ | grep -i cache-control
```

预期分别输出 `Cache-Control: public, max-age=31536000, immutable` 与 `Cache-Control: no-cache, must-revalidate`。

### 7.4 域名是否已替换

```bash
curl -s https://实际域名.com/pose/ | grep -o 'rel="canonical" href="[^"]*"'
curl -s https://实际域名.com/costume/ | grep -o 'og:image" content="[^"]*"'
```

**不应出现 `example.com`。** 若出现，回到 §2.5 重新构建。

### 7.5 浏览器实测

打开 `https://实际域名.com/pose/`，确认：

- [ ] 卡片能显示缩略图（不是灰块）
- [ ] 鼠标悬停卡片底部的角度条，主图会切换
- [ ] 点击卡片能打开灯箱，图片是原寸 PNG
- [ ] `←` `→` 切视角、`↑` `↓` 换姿势、`Esc` 关闭都有效
- [ ] 右上角 ☀/☾ 能切换主题
- [ ] 右上角 日本語/中文 能切换语言
- [ ] 刷新页面后主题与语言选择保留

costume 站额外确认：点击「筛选」能展开 6 组标签，选中后列表数量减少。

---

## 8. 更新与回滚

### 更新代码

```bash
cd /var/www/refsite/pose && git pull
# 若页面有改动，重新构建
SITE_URL="https://实际域名.com" python3 scripts/build_gallery.py
```

图片不需要重新下载（`download.py` 会跳过已存在的）。

### 回滚

```bash
cd /var/www/refsite/pose
git log --oneline -5
git reset --hard <目标提交>
SITE_URL="https://实际域名.com" python3 scripts/build_gallery.py
```

### 备份

图片 2.1 GB 不值得反复备份，只需备份配置与页面：

```bash
tar czf /root/refsite-backup-$(date +%F).tar.gz \
  /etc/nginx/sites-available/refsite \
  /var/www/refsite/pose/index.html \
  /var/www/refsite/costume/index.html
```

---

## 9. 常见问题

| 现象 | 原因 | 解决 |
|---|---|---|
| `git clone` 超时 | VPS 无法访问 GitHub | 改用路径 B 本地上传 |
| `download.py` 大量失败 | VPS 无法访问原站，或被限速 | 降低并发：`python3 scripts/download.py thumb 4`；仍失败则用路径 B |
| 页面打开空白 | 图片未下载 | 跑 `download.py`，再 `verify.py` 确认 |
| 图片 404 | 目录层级不对 | `thumbs/` `img/` 必须与 `index.html` 同级 |
| 缩略图有、点开无大图 | 只下了 `thumb` | 补下 `full`（pose）或 `img`（costume） |
| 中文模式看到日文 | 该条缺译 | 正常回退，不报错 |
| `nginx -t` 报证书不存在 | 还没签证书 | 先做 §5，或先用 §4.2 的临时 80 端口配置 |
| 打开很慢 | VPS 带宽不足 | 原图单张 1.8 MB，建议 ≥ 5 Mbps；或只下 thumb+img |
| canonical 还是 example.com | 没做 §2.5 | 带 `SITE_URL` 重新构建 |
| 更新后仍是旧页面 | 浏览器缓存 HTML | nginx 已设 `no-cache`，强制刷新即可 |

---

## 10. 部署后自检脚本

一次性跑完所有检查：

```bash
#!/usr/bin/env bash
D="实际域名.com"
echo "=== 体积 ==="
du -sh /var/www/refsite/pose /var/www/refsite/costume
echo "=== 图片数 ==="
echo "pose jpg: $(find /var/www/refsite/pose -name '*.jpg' | wc -l)  期望 1439"
echo "pose png: $(find /var/www/refsite/pose -name '*.png' | wc -l)  期望 1439"
echo "cost webp: $(find /var/www/refsite/costume -name '*.webp' | wc -l)  期望 2814"
echo "=== HTTP ==="
for p in /pose/ /costume/ /robots.txt; do
  printf "%-14s " "$p"; curl -s -o /dev/null -w "%{http_code}\n" "https://$D$p"
done
echo "=== 域名替换 ==="
echo -n "pose canonical: "; curl -s "https://$D/pose/" | grep -o 'rel="canonical" href="[^"]*"'
echo -n "costume canonical: "; curl -s "https://$D/costume/" | grep -o 'rel="canonical" href="[^"]*"'
echo "=== 残留占位 ==="
grep -rl "example.com" /var/www/refsite/pose/index.html /var/www/refsite/costume/index.html 2>/dev/null || echo "无（正确）"
```

---

## 11. 版权提示（部署后须知）

- 图片著作权归原作者 **ギア**（[@giaaibusi](https://x.com/giaaibusi)）所有
- 原站条款：**禁止再分发、转载、转售图片文件本身**
- 允许：作品创作、商用创作、编辑、参考
- 两个仓库均不含图片；图片是部署时从原站拉取的，仅作个人参考用途
- 公开部署在性质上接近「再分发」，风险由部署者承担
- **如原作者提出异议，应立即下线**

详见各仓库的 `NOTICE.md`。
