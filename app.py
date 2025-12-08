from flask import Flask, render_template, jsonify, request
from models import db, Post

app = Flask(__name__)
# 設定 SQLite 資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 初始化資料庫 (第一次執行時開啟)
with app.app_context():
    db.create_all()

# --- 頁面路由 ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blog')
def blog():
    # 從資料庫抓取所有文章
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/api-tutorial')
def api_doc():
    return render_template('api_doc.html')

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

if __name__ == '__main__':
    app.run(debug=True)