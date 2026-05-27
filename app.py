import markdown
from flask import Flask, render_template, jsonify, request, session, send_from_directory
from models import db, Post, VisitorStats
import bleach
import os
import json
from datetime import datetime

app = Flask(__name__)
# 設定 SQLite 資料庫
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Load BioRec pre-processed demo datasets
try:
    with open(r"D:\code\drug_repurposing\drug_rec_system\data\processed\demo_data.json", "r", encoding="utf-8") as f:
        biorec_demo_data = json.load(f)
except Exception as e:
    biorec_demo_data = {"genes": [], "drugs": [], "diseases": [], "disease_genes": {}, "ppi_edges": []}

try:
    with open(r"D:\code\drug_repurposing\drug_rec_system\models\validation_metrics.json", "r", encoding="utf-8") as f:
        biorec_validation_metrics = json.load(f)
except Exception as e:
    biorec_validation_metrics = {}

# --- 允許的 HTML 標籤白名單 (Whitelist) ---
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 
    'em', 'i', 'li', 'ol', 'strong', 'ul', 
    'h1', 'h2', 'h3', 'p', 'pre', 'br'
]
ALLOWED_ATTRIBUTES = {'a': ['href', 'title', 'target']}

# --- 啟動區塊 ---
with app.app_context():
    db.create_all()

# --- 訪客追蹤功能 ---
@app.before_request
def track_visitor():
    """在每次請求前追蹤訪客"""
    if request.path.startswith('/static') or request.path.startswith('/api'):
        return
    
    page_path = request.path
    is_new_visitor = session.get('visited') is None
    if is_new_visitor:
        session['visited'] = True
        session.permanent = True
    
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

# --- 輔助函數 (重新命名以避免衝突) ---
def get_aggregate_visitor_stats():
    """獲取訪客統計資料"""
    total_stats = db.session.query(
        db.func.sum(VisitorStats.visit_count).label('total_visits'),
        db.func.sum(VisitorStats.unique_visitors).label('total_unique')
    ).first()
    
    return {
        'total_visits': total_stats.total_visits or 0,
        'total_unique': total_stats.total_unique or 0
    }

# --- 頁面路由 ---
@app.route('/')
def index():
    return render_template('index.html', visitor_stats=get_aggregate_visitor_stats())

@app.route('/blog')
def blog():
    # 從資料庫抓取所有文章
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    # 將 Markdown 轉為 HTML
    for post in posts:
        if post.content:
            post.html_content = markdown.markdown(post.content)
    return render_template('blog.html', posts=posts, visitor_stats=get_aggregate_visitor_stats())

@app.route('/about')
def about():
    return render_template('about.html', visitor_stats=get_aggregate_visitor_stats())

@app.route('/api-tutorial')
def api_doc():
    return render_template('api_doc.html', visitor_stats=get_aggregate_visitor_stats())

@app.route('/projects')
def projects():
    """展示您的所有核心專案"""
    return render_template('projects.html', visitor_stats=get_aggregate_visitor_stats())

@app.route('/biorec')
def biorec_page():
    """生技 GNN 藥物推薦系統 SPA 儀表板"""
    return render_template('biorec.html', visitor_stats=get_aggregate_visitor_stats())

@app.route('/portrait')
def portrait_page():
    """LINE 聊天人物誌分析器對話助理"""
    return render_template('portrait_ui.html', visitor_stats=get_aggregate_visitor_stats())

# --- serve Portrait Wordclouds directly from source ---
@app.route('/visualize/<filename>')
def serve_visualize(filename):
    return send_from_directory(r"D:\code\portrait\visualize", filename)

# ====================================================================
# BioRec 模擬 API 端點
# ====================================================================
@app.route('/api/autocomplete', methods=['GET'])
def api_autocomplete():
    return jsonify({
        "genes": biorec_demo_data.get("genes", []),
        "drugs": biorec_demo_data.get("drugs", []),
        "diseases": biorec_demo_data.get("diseases", [])
    })

@app.route('/api/recommend/disease', methods=['GET'])
def api_recommend_disease():
    disease_name = request.args.get('name', '')
    method = request.args.get('method', 'gnn').lower()
    
    diseases = biorec_demo_data.get("diseases", [])
    disease_genes = biorec_demo_data.get("disease_genes", {})
    
    if disease_name not in diseases:
        return jsonify({"error": f"Disease '{disease_name}' not found"}), 404
        
    assoc_genes = disease_genes.get(disease_name, [])
    
    genes_recs = []
    for i, g in enumerate(assoc_genes[:10]):
        genes_recs.append({
            "gene": g,
            "score": round(0.95 - i*0.02, 4),
            "type": "Known Marker" if i < 6 else "Predicted Marker"
        })
        
    mock_drugs = {
        "Oncology": [
            {"drug": "OncoStop-A", "score": 0.9251, "type": "Approved Indication", "indications": "Oncology"},
            {"drug": "BioMed-101", "score": 0.8142, "type": "Repurposed Candidate", "indications": "General"},
            {"drug": "KinaseOff", "score": 0.7812, "type": "Repurposed Candidate", "indications": "Oncology"},
            {"drug": "DNA-Repairer", "score": 0.7412, "type": "Repurposed Candidate", "indications": "Oncology"},
            {"drug": "TumorSlay", "score": 0.6991, "type": "Repurposed Candidate", "indications": "General"}
        ],
        "Autoimmune": [
            {"drug": "ImmunoCalm", "score": 0.9412, "type": "Approved Indication", "indications": "Autoimmune"},
            {"drug": "TNF-Squelch", "score": 0.8874, "type": "Approved Indication", "indications": "Autoimmune"},
            {"drug": "ArthriFix", "score": 0.8124, "type": "Repurposed Candidate", "indications": "Autoimmune"},
            {"drug": "Steroidol", "score": 0.7512, "type": "Repurposed Candidate", "indications": "Inflammation"}
        ],
        "Metabolic Syndrome": [
            {"drug": "MetaboFix", "score": 0.9324, "type": "Approved Indication", "indications": "Metabolic Syndrome"},
            {"drug": "InsulMax", "score": 0.8921, "type": "Approved Indication", "indications": "Diabetes"},
            {"drug": "Glucagon-1", "score": 0.8251, "type": "Repurposed Candidate", "indications": "Diabetes"},
            {"drug": "LipoBuster", "score": 0.7612, "type": "Repurposed Candidate", "indications": "Obesity"}
        ],
        "Hypertension": [
            {"drug": "CardioGlow", "score": 0.9512, "type": "Approved Indication", "indications": "Hypertension"},
            {"drug": "BetaBlocker-X", "score": 0.8912, "type": "Approved Indication", "indications": "Hypertension"},
            {"drug": "VasoDilate", "score": 0.8321, "type": "Repurposed Candidate", "indications": "Cardiac"},
            {"drug": "AceInhibitor", "score": 0.7912, "type": "Repurposed Candidate", "indications": "Cardiac"}
        ]
    }
    
    drugs_list = mock_drugs.get(disease_name, [
        {"drug": "BioMed-101", "score": 0.75, "type": "Repurposed Candidate", "indications": "General"}
    ])
    
    drugs_recs = []
    for idx, d in enumerate(drugs_list, start=1):
        drugs_recs.append({
            "rank": idx,
            "drug": d["drug"],
            "score": d["score"],
            "type": d["type"],
            "indications": d["indications"]
        })
        
    return jsonify({
        "query": disease_name,
        "method": method.upper(),
        "results": {
            "disease": disease_name,
            "genes": genes_recs,
            "drugs": drugs_recs
        }
    })

@app.route('/api/recommend/gene', methods=['GET'])
def api_recommend_gene():
    gene_name = request.args.get('name', '')
    method = request.args.get('method', 'gnn').lower()
    
    genes = biorec_demo_data.get("genes", [])
    if gene_name not in genes:
        return jsonify({"error": f"Gene '{gene_name}' not found"}), 404
        
    standard_drugs = [
        {"drug": "OncoStop-A", "indications": "Oncology", "targets": ["EGFR", "TP53", "BRCA1", "BRCA2"]},
        {"drug": "BioMed-101", "indications": "General", "targets": ["AKT1", "MTOR", "KRAS"]},
        {"drug": "KinaseOff", "indications": "Oncology", "targets": ["EGFR", "KIT", "PDGFRA"]},
        {"drug": "MetaboFix", "indications": "Metabolic Syndrome", "targets": ["AMPK1", "HMGCR", "PPARG"]},
        {"drug": "CardioGlow", "indications": "Hypertension", "targets": ["ACE", "AGT", "AGTR1"]},
        {"drug": "BetaBlocker-X", "indications": "Hypertension", "targets": ["ADRB1", "ADRB2", "CACNA1C"]},
        {"drug": "ImmunoCalm", "indications": "Autoimmune", "targets": ["TNF", "IL6", "IL1B"]},
        {"drug": "TNF-Squelch", "indications": "Autoimmune", "targets": ["TNF", "IL2", "CTLA4"]},
        {"drug": "VasoDilate", "indications": "Cardiac", "targets": ["EDN1", "NOS3", "SCN5A"]},
        {"drug": "TumorSlay", "indications": "General", "targets": ["MYC", "MET", "SRC"]}
    ]
    
    results = []
    for i, d in enumerate(standard_drugs):
        is_direct = gene_name in d["targets"]
        score = round(0.92 - i*0.04 + (0.05 if is_direct else 0.0), 4)
        results.append({
            "rank": i + 1,
            "drug": d["drug"],
            "score": min(score, 1.0),
            "type": "Direct Target" if is_direct else "Repurposed (Indirect)",
            "indications": d["indications"]
        })
        
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    for i, r in enumerate(results, start=1):
        r["rank"] = i
        
    return jsonify({
        "query": gene_name,
        "method": method.upper(),
        "results": results[:10]
    })

@app.route('/api/recommend/multi', methods=['GET'])
def api_recommend_multi():
    gene_name = request.args.get('name', '')
    genes = biorec_demo_data.get("genes", [])
    if gene_name not in genes:
        return jsonify({"error": f"Gene '{gene_name}' not found"}), 404
        
    standard_drugs = [
        {"drug": "OncoStop-A", "indications": "Oncology", "targets": ["EGFR", "TP53", "BRCA1", "BRCA2"]},
        {"drug": "BioMed-101", "indications": "General", "targets": ["AKT1", "MTOR", "KRAS"]},
        {"drug": "KinaseOff", "indications": "Oncology", "targets": ["EGFR", "KIT", "PDGFRA"]},
        {"drug": "MetaboFix", "indications": "Metabolic Syndrome", "targets": ["AMPK1", "HMGCR", "PPARG"]},
        {"drug": "CardioGlow", "indications": "Hypertension", "targets": ["ACE", "AGT", "AGTR1"]},
        {"drug": "BetaBlocker-X", "indications": "Hypertension", "targets": ["ADRB1", "ADRB2", "CACNA1C"]},
        {"drug": "ImmunoCalm", "indications": "Autoimmune", "targets": ["TNF", "IL6", "IL1B"]},
        {"drug": "TNF-Squelch", "indications": "Autoimmune", "targets": ["TNF", "IL2", "CTLA4"]},
        {"drug": "VasoDilate", "indications": "Cardiac", "targets": ["EDN1", "NOS3", "SCN5A"]},
        {"drug": "TumorSlay", "indications": "General", "targets": ["MYC", "MET", "SRC"]}
    ]
    
    results = []
    for i, d in enumerate(standard_drugs):
        is_direct = gene_name in d["targets"]
        consensus_score = round(0.94 - i*0.03, 4)
        methods_agreed = 7 if is_direct else (6 if i < 3 else 4)
        
        results.append({
            "rank": i + 1,
            "drug": d["drug"],
            "consensus_score": consensus_score,
            "methods_agreed": methods_agreed,
            "type": "Direct Target" if is_direct else "Repurposed (Indirect)",
            "indications": d["indications"],
            "scores": {
                "SVD": round(consensus_score + 0.02, 4),
                "GNN": round(consensus_score - 0.01, 4),
                "Node2Vec": round(consensus_score - 0.03, 4),
                "NetProp": round(consensus_score + 0.04, 4),
                "TransE": round(consensus_score - 0.05, 4),
                "Fingerprint": round(consensus_score + 0.01, 4),
                "Traversal": round(consensus_score + 0.02, 4)
            }
        })
        
    return jsonify({
        "query": gene_name,
        "method": "CONSENSUS",
        "results": results
    })

@app.route('/api/recommend/drug', methods=['GET'])
def api_recommend_drug():
    drug_name = request.args.get('name', '')
    method = request.args.get('method', 'gnn').lower()
    
    drugs = biorec_demo_data.get("drugs", [])
    if drug_name not in drugs:
        return jsonify({"error": f"Drug '{drug_name}' not found"}), 404
        
    standard_drugs = [
        {"drug": "OncoStop-A", "indications": "Oncology"},
        {"drug": "BioMed-101", "indications": "General"},
        {"drug": "KinaseOff", "indications": "Oncology"},
        {"drug": "MetaboFix", "indications": "Metabolic Syndrome"},
        {"drug": "CardioGlow", "indications": "Hypertension"},
        {"drug": "BetaBlocker-X", "indications": "Hypertension"},
        {"drug": "ImmunoCalm", "indications": "Autoimmune"},
        {"drug": "TNF-Squelch", "indications": "Autoimmune"},
        {"drug": "VasoDilate", "indications": "Cardiac"},
        {"drug": "TumorSlay", "indications": "General"}
    ]
    
    results = []
    rank = 1
    for d in standard_drugs:
        if d["drug"] == drug_name:
            continue
        results.append({
            "rank": rank,
            "drug": d["drug"],
            "score": round(0.88 - rank*0.03, 4),
            "indications": d["indications"]
        })
        rank += 1
        
    return jsonify({
        "query": drug_name,
        "method": method.upper(),
        "results": results[:10]
    })

@app.route('/api/network', methods=['GET'])
def api_network():
    query = request.args.get('query', '')
    method = request.args.get('method', 'gnn').lower()
    
    genes = biorec_demo_data.get("genes", [])
    drugs = biorec_demo_data.get("drugs", [])
    diseases = biorec_demo_data.get("diseases", [])
    disease_genes = biorec_demo_data.get("disease_genes", {})
    ppi_edges = biorec_demo_data.get("ppi_edges", [])
    
    nodes = []
    links = []
    added_nodes = set()
    
    def add_node(nid, label, ntype):
        if nid not in added_nodes:
            nodes.append({"id": nid, "label": label, "type": ntype})
            added_nodes.add(nid)
            
    if query in genes:
        add_node(query, query, "gene")
        
        direct_drugs = []
        standard_drugs = [
            {"drug": "OncoStop-A", "targets": ["EGFR", "TP53", "BRCA1", "BRCA2"]},
            {"drug": "BioMed-101", "targets": ["AKT1", "MTOR", "KRAS"]},
            {"drug": "KinaseOff", "targets": ["EGFR", "KIT", "PDGFRA"]},
            {"drug": "MetaboFix", "targets": ["AMPK1", "HMGCR", "PPARG"]}
        ]
        for d in standard_drugs:
            if query in d["targets"]:
                direct_drugs.append(d["drug"])
                
        for d in direct_drugs[:4]:
            add_node(d, d, "drug")
            links.append({"source": d, "target": query, "value": 1.5, "type": "direct"})
            
        rec_drugs = ["TumorSlay", "BioMed-101", "KinaseOff"] if query in ["EGFR", "TP53", "BRCA1", "BRCA2", "AKT1", "MTOR"] else ["ImmunoCalm", "TNF-Squelch"]
        for d in rec_drugs:
            if d not in added_nodes:
                add_node(d, d, "drug")
                links.append({"source": d, "target": query, "value": 0.85, "type": "repurposed"})
                
        nbr_count = 0
        for edge in ppi_edges:
            if edge[0] == query:
                nbr = edge[1]
            elif edge[1] == query:
                nbr = edge[0]
            else:
                continue
            if nbr_count < 4:
                add_node(nbr, nbr, "gene")
                links.append({"source": query, "target": nbr, "value": 0.8, "type": "ppi"})
                nbr_count += 1
                
    elif query in drugs:
        add_node(query, query, "drug")
        
        standard_drugs = {
            "OncoStop-A": {"targets": ["EGFR", "TP53", "BRCA1"], "ind": "Oncology"},
            "BioMed-101": {"targets": ["AKT1", "MTOR", "KRAS"], "ind": "General"},
            "KinaseOff": {"targets": ["EGFR", "KIT", "PDGFRA"], "ind": "Oncology"},
            "MetaboFix": {"targets": ["AMPK1", "HMGCR", "PPARG"], "ind": "Metabolic Syndrome"},
            "CardioGlow": {"targets": ["ACE", "AGT", "AGTR1"], "ind": "Hypertension"},
            "BetaBlocker-X": {"targets": ["ADRB1", "ADRB2"], "ind": "Hypertension"},
            "ImmunoCalm": {"targets": ["TNF", "IL6", "IL1B"], "ind": "Autoimmune"}
        }
        
        d_info = standard_drugs.get(query, {"targets": [], "ind": "General"})
        for t in d_info["targets"][:4]:
            add_node(t, t, "gene")
            links.append({"source": query, "target": t, "value": 1.5, "type": "direct"})
            
        other_drugs = [d for d in drugs if d != query]
        for od in other_drugs[:3]:
            add_node(od, od, "drug")
            links.append({"source": query, "target": od, "value": 0.75, "type": "similar_drug"})
            
        add_node(d_info["ind"], d_info["ind"], "disease")
        links.append({"source": query, "target": d_info["ind"], "value": 2.0, "type": "indication"})
        
    elif query in diseases:
        add_node(query, query, "disease")
        
        assoc_genes = disease_genes.get(query, [])
        for g in assoc_genes[:6]:
            add_node(g, g, "gene")
            links.append({"source": query, "target": g, "value": 1.2, "type": "disease_gene"})
            
        mock_disease_drugs = {
            "Oncology": ["OncoStop-A", "KinaseOff", "TumorSlay"],
            "Autoimmune": ["ImmunoCalm", "TNF-Squelch"],
            "Metabolic Syndrome": ["MetaboFix", "InsulMax"],
            "Hypertension": ["CardioGlow", "BetaBlocker-X"]
        }
        for d in mock_disease_drugs.get(query, ["BioMed-101"]):
            add_node(d, d, "drug")
            links.append({"source": query, "target": d, "value": 1.4, "type": "disease_drug"})
    else:
        return jsonify({"error": f"Node '{query}' not found"}), 404
        
    return jsonify({"nodes": nodes, "links": links})

@app.route('/api/validation', methods=['GET'])
def api_validation():
    return jsonify(biorec_validation_metrics)

# ====================================================================
# Portrait 模擬 API 端點
# ====================================================================
@app.route('/api/portrait/personas', methods=['GET'])
def api_portrait_personas():
    reports_dir = r"D:\code\portrait\data\reports"
    if not os.path.exists(reports_dir):
        return jsonify([])
    personas = []
    for f in os.listdir(reports_dir):
        if f.endswith('.md'):
            personas.append(f[:-3])
    return jsonify(sorted(personas))

@app.route('/api/portrait/query', methods=['POST'])
def api_portrait_query():
    data = request.json or {}
    persona = data.get('persona', '')
    question = data.get('question', '')
    
    if not persona or not question:
        return jsonify({"error": "Missing persona or question"}), 400
        
    # Read and parse md file
    file_path = os.path.join(r"D:\code\portrait\data\reports", f"{persona}.md")
    if not os.path.exists(file_path):
        return jsonify({"answer": "找不到該人物的分析報告。", "sources": []})
        
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    keyword_map = {
        "性格": "核心性格與價值觀",
        "特質": "核心性格與價值觀",
        "價值": "核心性格與價值觀",
        "目標": "近期目標與煩惱",
        "煩惱": "近期目標與煩惱",
        "焦慮": "近期目標與煩惱",
        "飲食": "飲食與一般喜好",
        "喜歡": "飲食與一般喜好",
        "喜好": "飲食與一般喜好",
        "不喜歡": "飲食與一般喜好",
        "討厭": "飲食與一般喜好",
        "興趣": "興趣與嗜好",
        "嗜好": "興趣與嗜好",
        "休閒": "興趣與嗜好",
        "娛樂": "興趣與嗜好",
        "經歷": "經歷與過往",
        "過往": "經歷與過往",
        "背景": "經歷與過往",
        "歷史": "經歷與過往",
        "學校": "經歷與過往",
        "工作": "經歷與過往",
        "人際": "人際網絡",
        "關係": "人際網絡",
        "朋友": "人際網絡",
        "父母": "人際網絡",
        "家人": "人際網絡",
        "資產": "擁有資產與標誌性物品",
        "物品": "擁有資產與標誌性物品",
        "寵物": "擁有資產與標誌性物品",
        "東西": "擁有資產與標誌性物品"
    }
    
    target_title_part = "核心性格與價值觀" # default
    for k, v in keyword_map.items():
        if k in question:
            target_title_part = v
            break
            
    capturing = False
    section_lines = []
    for line in lines:
        if line.startswith("## "):
            if target_title_part in line:
                capturing = True
                continue
            else:
                capturing = False
        if capturing:
            if line.strip():
                # Clean up bullet characters
                cleaned = line.strip().lstrip('-*').strip()
                if cleaned:
                    section_lines.append(cleaned)
                    
    if section_lines:
        formatted_bullets = "\n".join([f"* {b}" for b in section_lines])
        answer_text = f"根據 LINE 聊天對話紀錄的人物誌長期記憶提取，關於「**{persona}**」的**{target_title_part}**如下：\n\n{formatted_bullets}"
        sources = [f"【長期記憶庫片段 - {target_title_part}】: {b}" for b in section_lines]
        return jsonify({
            "answer": answer_text,
            "sources": sources
        })
        
    return jsonify({
        "answer": f"根據目前關於「{persona}」的長期記憶庫資料，無法直接定位到相關細節。您可以嘗試點擊上面的**✨ 建議問題**，或詢問關於其性格特質、近期目標、飲食喜好、興趣嗜好、經歷過往、人際網絡或擁有物品等核心維度！",
        "sources": []
    })

@app.route('/api/portrait/report', methods=['GET'])
def api_portrait_report():
    persona = request.args.get('persona', '')
    if not persona:
        return jsonify({"error": "Missing persona"}), 400
        
    file_path = os.path.join(r"D:\code\portrait\data\reports", f"{persona}.md")
    if not os.path.exists(file_path):
        return jsonify({"error": "Report not found"}), 404
        
    with open(file_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content)
    return jsonify({"html": html_content})

# ====================================================================
# Notion Integrator 模擬 API 端點
# ====================================================================
@app.route('/notion-integrator')
def notion_integrator_page():
    """Notion 日誌整合器與 LLM 摘要 Web UI 儀表板"""
    return render_template('notion_integrator_ui.html', visitor_stats=get_aggregate_visitor_stats())

@app.route('/literature-integrator')
def literature_integrator_page():
    """智慧文獻整合平台 — arXiv / bioRxiv / medRxiv AI 深度分析儀表板"""
    return render_template('literature_integrator_ui.html', visitor_stats=get_aggregate_visitor_stats())

# In-memory session store for newly generated reports to make the dashboard fully dynamic!
NOTION_REPORTS_CACHE = [
    {
        "id": 1,
        "task_type": "Weekly",
        "theme": "N/A",
        "start_date": "2026-05-10",
        "end_date": "2026-05-17",
        "created_at": "2026-05-17 18:30:12",
        "notion_url": "https://www.notion.so/steven/20260517_weekly"
    },
    {
        "id": 2,
        "task_type": "Monthly",
        "theme": "N/A",
        "start_date": "2026-04-01",
        "end_date": "2026-05-01",
        "created_at": "2026-05-01 20:15:45",
        "notion_url": "https://www.notion.so/steven/20260501_monthly"
    },
    {
        "id": 3,
        "task_type": "Custom",
        "theme": "Cancer Vaccine Research Progress",
        "start_date": "2026-05-18",
        "end_date": "2026-05-24",
        "created_at": "2026-05-24 14:02:11",
        "notion_url": "https://www.notion.so/steven/20260524_theme_cancer"
    }
]

@app.route('/api/notion/history', methods=['GET'])
def api_notion_history():
    return jsonify(NOTION_REPORTS_CACHE)

@app.route('/api/notion/generate', methods=['POST'])
def api_notion_generate():
    data = request.json or {}
    start_date = data.get('start_date', '')
    end_date = data.get('end_date', '')
    report_type = data.get('report_type', 'Weekly')
    theme = data.get('theme', '')
    model = data.get('model', 'Qwen2.5-7B-Instruct')
    
    if not start_date or not end_date:
        return jsonify({"error": "Missing dates"}), 400
        
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title_date = end_date.replace('-', '')
    
    if report_type == "Custom" and theme:
        # Thematic Report
        summary = f"""# 📅 Notion 主題分析報告：{theme}
*   **分析區間**：{start_date} ~ {end_date}
*   **摘要模型**：{model} (本地地端 CPU 推理)
*   **報告生成時間**：{date_str}

## 🎯 主題回顧引言
本報告針對您所設定的主題「**{theme}**」進行了歷時日誌的語意檢索與精準提煉。在該期間內，您的 Notion 每日日誌呈現出高度專注與系統化的研究軌跡。

## 🧬 核心回顧總結

### 1. 癌症疫苗 (Cancer Vaccine) 演算法與 HLA 靶點研究
*   **多重 binding affinity 預測**：深入調試了 HLA 呈遞評分矩陣 (Presentation Model)，針對特異性抗原結合效率進行建模，解決了少見 HLA 等位基因預測置信度不足的 Edge Case。
*   **數據流工程**：優化了與 Acer 臨床試驗對接的 HLA binding affinity 特徵流處理腳本，將日誌解析速度提升了 40%。

### 2. Side Project 技術演進：BioRec GNN 專案
*   **API 模組化與 CORS 校驗**：完成了對 `drug_rec_system` API 層的全面重構，引入 Pydantic 實現強型別契約，配置了跨網域安全性政策 (CORS Middleware)。
*   **MLflow 本地日誌伺服器**：成功移除了對 wandb 雲端服務的依賴，將實驗追蹤完全收攏至本機 MLflow，實現 100% 隱私去中心化。
*   **一鍵 Docker 容器化**：完成了持久化磁碟卷 (Host Volume) 的掛載測試，確保 `biorec.db` 及模型權重不會因容器重建而丟失。

## 🔮 未來執行規劃與展望
*   **模型精煉**：下一週計劃擴展 RAG 與 ChromaDB 在多文本情境下的精確對話上下文拼接。
*   **實驗驗證**：在 CAFA-6 蛋白集上對 BioRec 的 consensus 融合算法進行全面 Cross-Validation。
"""
        notion_url = f"https://www.notion.so/steven/{title_date}_theme_{theme[:10]}"
    else:
        # Time-Based Report (Weekly or Monthly)
        summary = f"""# 📅 Notion {report_type} 工作與專案整合報告
*   **分析區間**：{start_date} ~ {end_date}
*   **摘要模型**：{model} (CPU GGUF 本地推理)
*   **報告生成時間**：{date_str}

## 📢 本週/本月核心工作回顧

### 👨‍💻 1. 工作日常 (Acer 癌症疫苗研發 / 生物資訊工程)
*   **HLA 呈遞評分優化**：針對腫瘤特異性抗原的 binding affinity 與呈遞預測管道 (Presentation Model) 進行迭代，調整了特徵加權參數。
*   **臨床數據管線維護**：完成了大規模 HLA binding 實驗結果的 stream-parsing，成功建立與本地資料庫的可靠連接，並修復了空值填充異常。

### 🛠️ 2. 個人 Side Project (BioRec 與地端 AI 實驗)
*   **BioRec 藥物推薦平台**：
    *   **FastAPI 多端點架構**：完成 modular FastAPI 路由重構，支援 Autocomplete、多重 consensus 共識評估以及 local GNN graph 拓撲生成。
    *   **Docker-compose 配備**：建置完成輕量化實體鏡像，並將 SQLite、特徵向量權重及 MLflow 日誌透過本地卷實現永久持久化。
*   **Portrait 人物誌對話系統**：
    *   完成本地 LangChain + ChromaDB 的初步測試，能針對 LINE 對話記錄成功提取八個性格特徵維度，並產出高質感的對話文字雲。

## 📈 心態、學習與健康狀況
*   **情緒與心態**：本階段整體效率極佳，對 Side Project 的進展與地端隱私 LLM 的成果感到振奮。
*   **健康狀況**：維持規律運動與作息，身體機能良好，大腦思考速度與專注力處於高點。
"""
        notion_url = f"https://www.notion.so/steven/{title_date}_{report_type.lower()}"
        
    new_report = {
        "id": len(NOTION_REPORTS_CACHE) + 1,
        "task_type": report_type,
        "theme": theme if theme else "N/A",
        "start_date": start_date,
        "end_date": end_date,
        "created_at": date_str,
        "notion_url": notion_url
    }
    NOTION_REPORTS_CACHE.append(new_report)
    
    return jsonify({
        "status": "success",
        "notion_url": notion_url,
        "summary": summary,
        "report": new_report
    })


@app.route('/api/v1/visitor-stats', methods=['GET'])
def visitor_stats_api():
    """取得訪客統計資料 API (解決名稱衝突 Bug)"""
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

@app.route('/api/v1/get-code', methods=['GET'])
def get_code_example():
    sample_data = {
        "author": "Steven",
        "language": "Python",
        "tool": "Pandas",
        "snippet": "import pandas as pd\ndf = pd.read_csv('data.csv')"
    }
    return jsonify(sample_data)

if __name__ == '__main__':
    is_debug = os.environ.get('FLASK_DEBUG') == '1'
    app.run(debug=is_debug)