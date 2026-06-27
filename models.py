from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicks = db.relationship('Click', backref='link', lazy=True)

class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    referrer = db.Column(db.String(512))
    user_agent = db.Column(db.String(512))
    ip_address = db.Column(db.String(64))

@property
def click_count(self):
    return len(self.clicks)