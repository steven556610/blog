from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False) # 網誌內容
    code_snippet = db.Column(db.Text, nullable=True) # 分享的程式碼
    tag = db.Column(db.String(50), nullable=True) # 文章標籤/分類
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class KaggleCompetition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)        # 比賽名稱
    url = db.Column(db.String(300), nullable=False)         # 比賽連結
    description = db.Column(db.Text, nullable=True)         # 比賽筆記 (Markdown)
    api_command = db.Column(db.String(300), nullable=True)  # API 指令
    rank_info = db.Column(db.String(100), nullable=True)    # 你的排名或狀態
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"KaggleCompetition('{self.name}', '{self.date_added}')"

class VisitorStats(db.Model):
    """訪客統計模型"""
    id = db.Column(db.Integer, primary_key=True)
    page_path = db.Column(db.String(200), nullable=False)   # 頁面路徑
    visit_count = db.Column(db.Integer, default=0)          # 訪問次數
    unique_visitors = db.Column(db.Integer, default=0)      # 獨立訪客數
    last_visit = db.Column(db.DateTime, default=datetime.utcnow)  # 最後訪問時間

    def __repr__(self):
        return f"VisitorStats('{self.page_path}', visits={self.visit_count})"


class HackMDNote(db.Model):
    """HackMD 同步筆記模型 — 儲存從 HackMD API 拉取的公開筆記"""
    __tablename__ = 'hackmd_note'

    id          = db.Column(db.Integer, primary_key=True)
    hackmd_id   = db.Column(db.String(64), unique=True, nullable=False)  # HackMD note ID
    short_id    = db.Column(db.String(32), nullable=True)                # HackMD short ID
    title       = db.Column(db.String(300), nullable=False, default='Untitled')
    tags        = db.Column(db.String(500), nullable=True)               # JSON array string
    content     = db.Column(db.Text, nullable=True)                      # Markdown 原文
    permalink   = db.Column(db.String(200), nullable=True)               # 自訂永久連結
    publish_link= db.Column(db.String(400), nullable=True)               # 完整公開 URL
    read_permission  = db.Column(db.String(20), default='guest')        # guest / signed_in / owner
    write_permission = db.Column(db.String(20), default='owner')
    hackmd_created_at = db.Column(db.DateTime, nullable=True)            # HackMD 建立時間
    hackmd_updated_at = db.Column(db.DateTime, nullable=True)            # HackMD 最後修改時間
    synced_at   = db.Column(db.DateTime, default=datetime.utcnow)        # 最後同步時間

    def __repr__(self):
        return f"HackMDNote('{self.title}', synced={self.synced_at})"

    def tags_list(self):
        """回傳標籤列表"""
        import json
        if not self.tags:
            return []
        try:
            return json.loads(self.tags)
        except Exception:
            return []
