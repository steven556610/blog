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
