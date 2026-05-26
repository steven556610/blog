# Steven's Matrix Hub 🧬💻

A Flask-based web application with a Matrix hacker aesthetic, acting as a personal portfolio, research log feed, and interactive AI project dashboard. This platform is highly optimized to run on a **zero-dependency simulated backend** for premium, lag-free client-side experiences and **100% compatibility with free hosting accounts like PythonAnywhere**.

---

## 🏆 Core Projects Showcase

The mainframe serves as an interactive deployment gate for three state-of-the-art computational biology and AI systems:

### 1. 🧬 BioRec: Drug Recommendation Suite
An advanced biological recommendation and repurposing framework inspired by **Ceddia et al. (2020) (PMID: 32365039)**.
*   **Methodology**: Integrates **STRING Protein-Protein Interaction (PPI)** networks and **DrugBank target mappings** to construct **Shortest-Path Proximity Matrices (SPPM)**.
*   **Algorithms**: Compares Matrix Singular Value Decomposition (SVD) and a custom **PyTorch Graph Convolutional Network (GCN)**, combined with 5 other external methods (Node2Vec, NetProp RWR, TransE KG, Fingerprint, Traversal) via a standard normalized **Consensus Engine**.
*   **Interactive SPA**: Serves top drug rankings, dynamic ROC & Precision-Recall evaluation curves (via Chart.js), and an **HTML5 D3-inspired canvas force-directed local association network visualization**.

### 2. 💬 Portrait: LINE Chat Persona Analyzer
A privacy-first, local LINE chat log aggregator and personal profile summarizer.
*   **Methodology**: Uses **LangChain** and **Ollama** (preconfigured for `qwen2.5:7b` GGUF) to extract chat histories across eight key dimensions: personality, goals, likes, dislikes, history, relationships, assets, and hobbies.
*   **Memory Vault**: Indexes embeddings inside a local **ChromaDB vector store** to enable a highly precise RAG conversation assistant.
*   **Interactive Assistant**: Select a persona (e.g. `何珮瑄` or `蘇威霖 Steven`), view their **Wordcloud** keyword canvas and expandable persona reports, check the custom **Risk Alert and Fraud Detection panel**, and query the assistant via an **interactive cited RAG chat panel**.

### 3. 📅 Notion Logs Summarizer
An automated daily log organizer, weekly/monthly aggregator, and thematic reporter.
*   **Methodology**: Regularly queries the **Notion API** to fetch daily standup diaries (`Date_daily`), aggregates them using local GGUF models via **llama-cpp-python** in CPU environments, and pushes summaries back to Notion.
*   **Interactive Dashboard**: Provides date selectors for generating Weekly/Monthly reports, custom theme textboxes for topic-specific summarization, and an interactive **History Vault table** connected to a local SQLite tracker.

---

## 🛠️ Tech Stack & Architecture

*   **Backend**: Flask (Python Web Frame)
*   **Database**: SQLite with SQLAlchemy ORM (History trackers & Blog storage)
*   **Frontend**: HTML5 Templates (Jinja2), Vanilla CSS, JavaScript
*   **Visual Elements**: Animated Matrix Falling Rain (Canvas), Chart.js (ROC Curves), Lucide Icons
*   **Integrations**: Streamlit dark-theme replica, Notion API pipelines, Ollama geolocal prompts

---

## 🗂 Project Structure

```
make_a_blog/
├── app.py                  # Flask Core server, API router and simulated databases
├── models.py               # ORM Models (Post, VisitorStats)
├── config.py               # Application settings
├── requirements.txt        # Python dependencies
├── instance/
│   └── database.db         # Local SQLite database (visitor logs & posts)
├── static/
│   ├── css/
│   │   ├── style.css       # Matrix main blog theme
│   │   ├── biorec_style.css # Glassmorphic Biotech dashboard styling
│   │   └── portrait_style.css # Streamlit dashboard replica styling
│   ├── js/
│   │   ├── biorec_script.js # Canvas network drawer & tab switches
│   │   └── notion_script.js # Progressive delay spinners & markdown rendering
│   │   └── portrait_script.js # Dynamic reports and cited RAG chats
├── templates/
│   ├── base.html           # Main navigation and Matrix canvas
│   ├── index.html          # Homepage
│   ├── blog.html           # System Log Blog feed (with Markdown support)
│   ├── projects.html       # Unified 3-Card Projects Directory
│   ├── biorec.html         # GNN Biotech SPA Dashboard
│   ├── portrait_ui.html    # LINE Persona Streamlit Dashboard
│   └── notion_integrator_ui.html # Notion Summarizer Dashboard
```

---

## 🚀 Installation & Local Launch

1. **Clone the repository**
   ```bash
   git clone https://github.com/steven556610/blog.git
   cd blog
   ```

2. **Create virtual environment & Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install flask flask-sqlalchemy markdown
   ```

3. **Launch the application**
   ```bash
   python app.py
   ```
   *   The server will boot on **http://localhost:5000**.
   *   Click `[ Projects ]` to access the main portfolio.

---

## 🌐 Deploying to PythonAnywhere (Free Account)

Since PythonAnywhere free accounts have limited RAM and disk quotas, attempting to run heavy PyTorch GCN models, ChromaDB, or background LLM services will cause immediate out-of-memory crashes.

Steven's Matrix Hub **resolves this perfectly** by packaging lightweight client-side simulators. All visual networks, curves, and LLM thematic summaries parse directly on the browser using pre-compiled datasets (`demo_data.json` and `validation_metrics.json`) and responsive regex keyword indexing.

### How to deploy in 2 minutes:
1. **Pull changes on PythonAnywhere**:
   ```bash
   cd ~/my_blog
   git pull origin main
   ```
2. **Reload Web App**: Open PythonAnywhere **Web** tab and click **Reload**.
3. **Enjoy zero-lag execution**! Your portfolios, canvases, and Q&A chat panels will run at lightning speed.

---

## ⚡ Git-to-Blog Auto-Publisher

To update the system log feed with technical updates from `drug_rec_system`, simply run the automated publisher in your host terminal:

```powershell
python "D:\code\drug_repurposing\drug_rec_system\code\blog_publisher.py"
```

This will automatically extract git commits, format a beautiful weekly report, commit it to `database.db`, and push everything to GitHub.

---
> System Status: Operational | © 2026 NYCU Researcher
