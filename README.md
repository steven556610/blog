# Steven's Matrix Hub

A Flask-based web application with a Matrix hacker aesthetic for tracking Kaggle competitions, blog posts, and API documentation. This project demonstrates full-stack web development with Python, featuring database management, Markdown rendering, and a cyberpunk-inspired UI.

## Features

- 🏆 **Kaggle Competition Tracker**: Track competitions with status, API commands, and analysis notes
- 📝 **Blog System**: Create and display blog posts with code snippets and tags
- 🔌 **RESTful API**: Example API endpoints for educational purposes
- 💾 **SQLite Database**: Lightweight database with automatic initialization
- 🎨 **Matrix Theme**: Cyberpunk aesthetic with falling Matrix rain effect
- 📚 **API Documentation**: Built-in API tutorial page
- 📊 **Markdown Support**: Rich text formatting for competition analysis

## Tech Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML templates (Jinja2), Vanilla CSS, JavaScript
- **Markdown**: Python-Markdown for rich text rendering
- **Theme**: Matrix-inspired cyberpunk design

## Project Structure

```
make_a_blog/
├── app.py                  # Main application with routes and initialization
├── models.py               # Database models (Post, KaggleCompetition)
├── config.py               # Configuration settings
├── add_sample_data.py      # Helper script to add sample blog posts
├── requirements.txt        # Python dependencies
├── database.db             # SQLite database file (auto-created)
├── static/
│   ├── css/
│   │   └── style.css       # Matrix theme styling
│   └── js/
├── templates/
│   ├── base.html           # Base template with Matrix rain effect
│   ├── index.html          # Homepage
│   ├── blog.html           # Blog listing page
│   ├── kaggle.html         # Kaggle competition tracker
│   └── api_doc.html        # API documentation page
└── instance/               # Instance-specific files
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/steven556610/blog.git
   cd blog
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy markdown
   ```

## Usage

1. **Run the application**
   ```bash
   python app.py
   ```
   
   The application will automatically:
   - Create the database tables
   - Initialize sample data for Kaggle competitions and blog posts
   - Start the development server on http://localhost:5000

2. **Access the application**
   - **Homepage**: http://localhost:5000/
   - **Blog**: http://localhost:5000/blog
   - **Kaggle Tracker**: http://localhost:5000/kaggle
   - **API Documentation**: http://localhost:5000/api-tutorial

3. **Add sample blog data** (optional)
   ```bash
   python add_sample_data.py
   ```

## Database Schema

### Post Model

| Field        | Type     | Description                    |
|--------------|----------|--------------------------------|
| id           | Integer  | Primary key                    |
| title        | String   | Post title (max 100 chars)     |
| content      | Text     | Blog post content              |
| code_snippet | Text     | Optional code snippet          |
| tag          | String   | Post category/tag (max 50)     |
| date_posted  | DateTime | Post creation timestamp (UTC)  |

### KaggleCompetition Model

| Field        | Type     | Description                       |
|--------------|----------|-----------------------------------|
| id           | Integer  | Primary key                       |
| name         | String   | Competition name (max 200 chars)  |
| url          | String   | Competition URL (max 300 chars)   |
| description  | Text     | Analysis notes (Markdown format)  |
| api_command  | String   | Kaggle API download command       |
| rank_info    | String   | Current rank/status (max 100)     |
| date_added   | DateTime | Entry creation timestamp (UTC)    |

## API Endpoints

### GET /api/v1/get-code

Returns a sample code snippet in JSON format for educational purposes.

**Example Request:**
```bash
curl http://localhost:5000/api/v1/get-code
```

**Example Response:**
```json
{
  "author": "Steven",
  "language": "Python",
  "tool": "Pandas",
  "snippet": "import pandas as pd\ndf = pd.read_csv('data.csv')"
}
```

## Development

### Database Management

The application automatically creates and initializes the database on first run. To interact with the database manually:

**Using Flask Shell:**
```bash
python -m flask shell
```

**Add a new blog post:**
```python
from models import Post, db
post = Post(
    title="My First Post",
    content="Hello World!",
    tag="Python",
    code_snippet="print('Hello World')"
)
db.session.add(post)
db.session.commit()
```

**Add a new Kaggle competition:**
```python
from models import KaggleCompetition, db
comp = KaggleCompetition(
    name="Competition Name",
    url="https://www.kaggle.com/competitions/...",
    rank_info="Top 10%",
    api_command="kaggle competitions download -c competition-name",
    description="### Analysis\nMy notes here..."
)
db.session.add(comp)
db.session.commit()
```

### Design Philosophy

The application features a **Matrix-inspired cyberpunk aesthetic**:
- Green monospace text on black background
- Animated falling Matrix rain effect (Canvas)
- Hover effects with green glow
- Terminal-style API command boxes
- Responsive design for mobile devices

## Features in Detail

### 🏆 Kaggle Competition Tracker
- Track multiple competitions in one place
- Store competition URLs and API download commands
- Write analysis notes in Markdown format
- Monitor rank/status for each competition
- Terminal-style command display

### 📝 Blog System
- Create posts with titles, content, and code snippets
- Categorize posts with tags (Python, API, Bioinformatics, etc.)
- Automatic timestamp tracking
- Sample data script included

### 🎨 Matrix Theme
- Animated background with falling characters
- Cyberpunk green (#0F0) color scheme
- Monospace fonts for authentic terminal feel
- Responsive design with mobile support

## Contributing

Feel free to fork this project and submit pull requests for any improvements!

## License

This project is open source and available for educational purposes.

## Author

Steven - NYCU Researcher  
[GitHub](https://github.com/steven556610)

---

> System Status: Online | © 2025 NYCU Researcher
