import markdown
from flask import Flask, render_template, jsonify, request, session
from models import db, Post, KaggleCompetition, VisitorStats
import bleach
import os
from datetime import datetime

app = Flask(__name__)
# 設定 SQLite 資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

db.init_app(app)

# --- 允許的 HTML 標籤白名單 (Whitelist) ---
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 
    'em', 'i', 'li', 'ol', 'strong', 'ul', 
    'h1', 'h2', 'h3', 'p', 'pre', 'br'
]
ALLOWED_ATTRIBUTES = {'a': ['href', 'title', 'target']}

# --- 修改 init_data 函式 ---
def init_data():
    # 1. 初始化 Kaggle 資料
    if not KaggleCompetition.query.first():
        sample_comp = KaggleCompetition(
            name="Playground Series - Season 5, Episode 12",
            url="https://www.kaggle.com/competitions/playground-series-s5e12/rules",
            rank_info="Participating",
            api_command="kaggle competitions download -c playground-series-s5e12",
            description="### Init Data\nData loaded successfully."
        )
        db.session.add(sample_comp)
        
    # 2. 初始化 Blog 資料 (這就是你缺少的！)
    if not Post.query.first():
        sample_post = Post(
            title="System Reboot: Hello World",
            content="資料庫重置完成。這是第一篇自動生成的網誌文章。系統運作正常。",
            code_snippet="print('Hello World')",
            # date_posted 會自動生成
        )
        db.session.add(sample_post)
    
    # 提交所有變更
    db.session.commit()
    print(">> System Database: All Systems Operational.")

# --- 啟動區塊 ---
with app.app_context():
    db.create_all()
    #init_data() # 呼叫這個新的函式

# --- 訪客追蹤功能 ---
@app.before_request
def track_visitor():
    """在每次請求前追蹤訪客"""
    # 排除靜態資源和 API 請求
    if request.path.startswith('/static') or request.path.startswith('/api'):
        return
    
    page_path = request.path
    
    # 檢查是否為新訪客（使用 session）
    is_new_visitor = session.get('visited') is None
    if is_new_visitor:
        session['visited'] = True
        session.permanent = True
    
    # 更新或創建訪客統計
    stats = VisitorStats.query.filter_by(page_path=page_path).first()
    
    if stats:
        stats.visit_count += 1
        if is_new_visitor:
            stats.unique_visitors += 1
        stats.last_visit = datetime.utcnow()
    else:
        stats = VisitorStats(
            page_path=page_path,
            visit_count=1,
            unique_visitors=1 if is_new_visitor else 0
        )
        db.session.add(stats)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()

# --- 輔助函數 ---
def get_visitor_stats():
    """獲取訪客統計資料"""
    total_stats = db.session.query(
        db.func.sum(VisitorStats.visit_count).label('total_visits'),
        db.func.sum(VisitorStats.unique_visitors).label('total_unique')
    ).first()
    
    return {
        'total_visits': total_stats.total_visits or 0,
        'total_unique': total_stats.total_unique or 0
    }

# --- 新增路由 ---
@app.route('/kaggle')
def kaggle_page():
    comps = KaggleCompetition.query.order_by(KaggleCompetition.date_added.desc()).all()
    
    # 將 Markdown 轉為 HTML
    for comp in comps:
        if comp.description:
            comp.description = markdown.markdown(comp.description)
            
    return render_template('kaggle.html', comps=comps, visitor_stats=get_visitor_stats())

# --- 頁面路由 ---
@app.route('/')
def index():
    return render_template('index.html', visitor_stats=get_visitor_stats())

@app.route('/blog')
def blog():
    # 從資料庫抓取所有文章
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('blog.html', posts=posts, visitor_stats=get_visitor_stats())

@app.route('/about')
def about():
    return render_template('about.html', visitor_stats=get_visitor_stats())

@app.route('/api-tutorial')
def api_doc():
    return render_template('api_doc.html', visitor_stats=get_visitor_stats())

# --- 你的教學 API 範例 ---
# 這就是你可以教大家怎麼 call 的 API
@app.route('/api/v1/get-code', methods=['GET'])
def get_code_example():
    """
    這是一個範例 API，回傳一段 JSON 格式的程式碼。
    """
    sample_data = {
        "author": "Steven",
        "language": "Python",
        "tool": "Pandas",
        "snippet": "import pandas as pd\ndf = pd.read_csv('data.csv')"
    }
    return jsonify(sample_data)

@app.route('/api/v1/visitor-stats', methods=['GET'])
def get_visitor_stats():
    """
    取得訪客統計資料 API
    """
    # 獲取所有頁面的統計
    all_stats = VisitorStats.query.all()
    
    stats_data = {
        'total_visits': sum(s.visit_count for s in all_stats),
        'total_unique_visitors': sum(s.unique_visitors for s in all_stats),
        'pages': [
            {
                'path': s.page_path,
                'visits': s.visit_count,
                'unique_visitors': s.unique_visitors,
                'last_visit': s.last_visit.strftime('%Y-%m-%d %H:%M:%S')
            }
            for s in all_stats
        ]
    }
    
    return jsonify(stats_data)

if __name__ == '__main__':
    is_debug = os.environ.get('FLASK_DEBUG') == '1'
    app.run(debug=is_debug)