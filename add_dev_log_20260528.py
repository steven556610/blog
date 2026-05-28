"""
add_dev_log_20260528.py
========================
一次性腳本：將 2026-05-28 的開發日誌寫入 Blog 資料庫
執行後可刪除此檔案
"""

from app import app
from models import db, Post
from datetime import datetime

LOG_ENTRIES = [
    Post(
        title="🌊 全站海洋主題改版 — Ocean Hub 重新設計",
        content="""## 改版動機

原本的 Matrix 駭客綠風格雖然有趣，但整體視覺比較單調。
這次以「**藍色海洋、潛水世界、月亮意象**」為主軸，重新設計整個網站的視覺系統。

## 主要改動

### 🎨 全新 CSS 設計系統 (`style.css`)
- 引入 **Inter + Space Mono** 雙字型系統（Google Fonts）
- 建立完整 CSS 變數體系：`--ocean-deep`、`--biolum`（生物螢光綠）、`--moon-silver` 等
- 設計 **GlassMorphism** 卡片、技能進度條動畫、Hover 微動畫

### 🌊 深海背景動畫 (`base.html`)
- 用 Canvas 實作三層背景動畫：
  1. **光束**：從水面穿透的丁達爾效應光柱
  2. **月光粒子**：上半部緩慢漂移的星塵
  3. **氣泡**：帶有物理漂移和反光高光的上升氣泡
- 取代原本的 Matrix 字元雨

### 🏠 首頁大改版 (`index.html`)
- 新增 Hero Section 含打字效果標題
- 整合系統資訊卡片（原本在 About 頁）
- 加入即時狀態列表（Active / Done / Planned）
- 研究領域四格展示
- 近期專案快覽卡片

### 👤 About 頁面更新 (`about.html`)
- 加入完整工作經歷（Acer 癌症疫苗研發）
- 技能樹更新：HLA / GNN / RAG / LLM / LangChain
- 移除過時的 Mutect2 項目
- 更新研究領域描述

### 📁 Projects 頁面更新 (`projects.html`)
- 移除 Mutect2 Analysis Pipeline
- 新增 **CAFA-6 蛋白功能預測**（Kaggle 競賽）
- 新增 **HLA Presentation Pipeline**（Acer 工作項目）
- 整體改為 Ocean 主題 project-card 設計

## Tech Stack 補充
- 字型：Inter, Space Mono via Google Fonts
- 動畫：純 Vanilla Canvas JS
- 色調：深海藍 (#020d1a) + 生物螢光 (#00f5d4) + 月銀 (#c8dff5)
""",
        tag="Dev Log",
        date_posted=datetime(2026, 5, 28, 20, 30, 0),
        code_snippet="""/* 核心色彩變數 */
:root {
    --ocean-deep:   #020d1a;
    --biolum:       #00f5d4;
    --moon-silver:  #c8dff5;
}

/* 氣泡動畫：帶漂移的上升效果 */
bubbles.forEach(b => {
    b.y -= b.speed;
    b.x += Math.sin(tick * 0.01 + b.phase) * b.drift;
});"""
    ),
    Post(
        title="🔗 HackMD API 整合 — 定時同步公開筆記到 Blog",
        content="""## 功能目標

在 HackMD 寫好文章後，自動同步到個人網站的 `/hackmd` 頁面，
讓 HackMD 成為 Blog 的寫作後台，網站負責展示。

## 實作架構

```
HackMD API (每小時) → hackmd_sync.py → SQLite → Flask → /hackmd 頁面
```

### 元件說明

| 檔案 | 功能 |
|------|------|
| `hackmd_sync.py` | 同步核心：呼叫 API、Upsert 寫入 DB |
| `models.py` | 新增 `HackMDNote` SQLAlchemy Model |
| `app.py` | 新增路由 + APScheduler 排程 |
| `templates/hackmd.html` | 筆記列表頁（含標籤篩選） |
| `templates/hackmd_note.html` | 單篇筆記閱讀頁 |

## HackMD API 使用

```python
# 取得個人帳號所有筆記
GET https://api.hackmd.io/v1/me/notes
Authorization: Bearer {HACKMD_API_TOKEN}

# 只同步公開筆記（readPermission == "guest"）
public_notes = [n for n in all_notes if n.get("readPermission") == "guest"]
```

## 排程設計（APScheduler）

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(
    func=_scheduled_hackmd_sync,
    trigger=IntervalTrigger(hours=1),
    id='hackmd_hourly_sync'
)
scheduler.start()
```

- Flask 啟動時同時啟動背景排程器
- 每小時自動拉取一次，比對 `lastChangedAt` 決定是否更新
- 支援手動觸發：`POST /api/hackmd/sync`

## 資料庫 Schema

```python
class HackMDNote(db.Model):
    hackmd_id   = db.Column(db.String(64), unique=True)
    title       = db.Column(db.String(300))
    tags        = db.Column(db.String(500))   # JSON array
    content     = db.Column(db.Text)          # Markdown 原文
    publish_link= db.Column(db.String(400))
    hackmd_updated_at = db.Column(db.DateTime)
    synced_at   = db.Column(db.DateTime)
```

## 安全設定更新

- 新增 `.env.example` 範本（含 HACKMD_API_TOKEN 說明）
- 完善 `.gitignore`：`*.db`、`instance/`、`hackmd_cache/` 等
- `python-dotenv` 整合至 Flask app，啟動時自動讀取

## 下一步

- [ ] 增加 `/hackmd` 頁面的搜尋功能
- [ ] 筆記內容支援 Mermaid 圖表渲染
- [ ] 加入同步通知（LINE / Email）
""",
        tag="Dev Log",
        date_posted=datetime(2026, 5, 28, 21, 0, 0),
        code_snippet="""# 手動觸發同步
POST /api/hackmd/sync

# 查詢同步狀態
GET /api/hackmd/status

# 標籤篩選
GET /hackmd?tag=bioinformatics"""
    ),
]

def main():
    with app.app_context():
        db.create_all()
        before = Post.query.count()
        db.session.add_all(LOG_ENTRIES)
        db.session.commit()
        after = Post.query.count()
        print(f"新增 {after - before} 篇開發日誌（共 {after} 篇）")
        for p in LOG_ENTRIES:
            print(f"  ✓ [{p.tag}] {p.title}")

if __name__ == "__main__":
    main()
