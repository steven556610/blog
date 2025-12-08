"""
Sample data script for the blog application.
Run this to add sample blog posts with tags.
"""

from app import app
from models import db, Post

def add_sample_posts():
    """Add sample blog posts to the database."""
    
    with app.app_context():
        # Check if posts already exist
        existing_count = Post.query.count()
        print(f"> Current posts in database: {existing_count}")
        
        # Sample posts
        sample_posts = [
            Post(
                title="Getting Started with Pandas",
                content="Pandas is a powerful data manipulation library for Python. It provides data structures like DataFrame and Series that make working with structured data easy and intuitive. Whether you're cleaning data, performing analysis, or preparing datasets for machine learning, Pandas is an essential tool in any data scientist's toolkit.",
                tag="Python",
                code_snippet="import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())"
            ),
            Post(
                title="Building REST APIs with Flask",
                content="Flask makes it easy to build RESTful APIs. With just a few lines of code, you can create endpoints that return JSON data. This tutorial covers routing, request handling, and best practices for API development.",
                tag="API",
                code_snippet="from flask import Flask, jsonify\n\napp = Flask(__name__)\n\n@app.route('/api/data')\ndef get_data():\n    return jsonify({'status': 'success'})"
            ),
            Post(
                title="Mutect2 Analysis Pipeline",
                content="Mutect2 is a variant caller from GATK that identifies somatic mutations in tumor samples. This tutorial covers the complete pipeline from BAM to VCF, including preprocessing, variant calling, and filtering steps.",
                tag="Bioinformatics"
            ),
            Post(
                title="Matrix Effect with JavaScript",
                content="Learn how to create the iconic Matrix falling characters effect using HTML5 Canvas and JavaScript. This tutorial breaks down the animation loop, character selection, and rendering techniques.",
                tag="JavaScript",
                code_snippet="const canvas = document.getElementById('matrix');\nconst ctx = canvas.getContext('2d');\n// Matrix rain effect code here"
            ),
            Post(
                title="SQLAlchemy ORM Basics",
                content="SQLAlchemy is a powerful ORM for Python that makes database operations intuitive and Pythonic. Learn about models, queries, relationships, and migrations in this comprehensive guide.",
                tag="Python"
            ),
        ]
        
        # Add posts to database
        db.session.add_all(sample_posts)
        db.session.commit()
        
        new_count = Post.query.count()
        print(f"> Successfully added {len(sample_posts)} sample posts!")
        print(f"> Total posts in database: {new_count}")
        print("> System Status: [OK]")
        
        # Display added posts
        print("\n> Added posts:")
        for post in sample_posts:
            print(f"  - {post.title} [{post.tag}]")

if __name__ == "__main__":
    print("> Initializing sample data insertion...")
    add_sample_posts()
    print("> Complete. Visit http://localhost:5000/blog to view the posts.")
