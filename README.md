# Blog Application

A simple Flask-based blog application with API tutorial features. This project demonstrates how to build a web application with blog functionality and RESTful API endpoints.

## Features

- 📝 **Blog Posts**: Create and display blog posts with code snippets
- 🔌 **RESTful API**: Example API endpoints for educational purposes
- 💾 **SQLite Database**: Lightweight database for storing blog posts
- 📚 **API Documentation**: Built-in API tutorial page

## Tech Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML templates (Jinja2)

## Project Structure

```
make_a_blog/
├── app.py              # Main application file with routes
├── models.py           # Database models (Post)
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── database.db         # SQLite database file
├── static/             # Static files (CSS, JS, images)
├── templates/          # HTML templates
│   ├── index.html      # Homepage
│   ├── blog.html       # Blog listing page
│   └── api_doc.html    # API documentation page
└── instance/           # Instance-specific files
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
   pip install flask flask-sqlalchemy
   ```

## Usage

1. **Run the application**
   ```bash
   python app.py
   ```

2. **Access the application**
   - Homepage: http://localhost:5000/
   - Blog: http://localhost:5000/blog
   - API Tutorial: http://localhost:5000/api-tutorial

## API Endpoints

### GET /api/v1/get-code

Returns a sample code snippet in JSON format.

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

## Database Schema

### Post Model

| Field        | Type     | Description                    |
|--------------|----------|--------------------------------|
| id           | Integer  | Primary key                    |
| title        | String   | Post title (max 100 chars)     |
| content      | Text     | Blog post content              |
| code_snippet | Text     | Optional code snippet          |
| date_posted  | DateTime | Post creation timestamp (UTC)  |

## Development

The application runs in debug mode by default. The database is automatically created on first run.

### Adding New Posts

Posts are stored in the SQLite database. You can interact with the database using the Flask shell:

```bash
flask shell
>>> from models import Post, db
>>> post = Post(title="My First Post", content="Hello World!")
>>> db.session.add(post)
>>> db.session.commit()
```

## Contributing

Feel free to fork this project and submit pull requests for any improvements!

## License

This project is open source and available for educational purposes.

## Author

Steven - [GitHub](https://github.com/steven556610)
