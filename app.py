from flask import Flask, render_template, request, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mental_health.db'
db = SQLAlchemy(app)

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

COPING_STRATEGIES = [
    {
        "title": "Deep Breathing",
        "description": "Take 5 deep breaths, inhaling for 4 counts and exhaling for 6 counts.",
        "category": "breathing"
    },
    {
        "title": "5-Minute Meditation",
        "description": "Find a quiet place, close your eyes, and focus on your breath.",
        "category": "meditation"
    },
    {
        "title": "Quick Walk",
        "description": "Take a 10-minute walk outside to clear your mind.",
        "category": "exercise"
    },
    {
        "title": "Call a Friend",
        "description": "Reach out to someone you trust and share your feelings.",
        "category": "social"
    },
    {
        "title": "Express Creativity",
        "description": "Spend 15 minutes drawing, writing, or creating something.",
        "category": "creative"
    }
]

@app.route('/')
def index():
    mood_entries = MoodEntry.query.order_by(MoodEntry.timestamp.desc()).all()
    return render_template('index.html', strategies=COPING_STRATEGIES, mood_entries=mood_entries)

@app.route('/api/mood', methods=['POST'])
def add_mood():
    data = request.json
    new_entry = MoodEntry(
        mood=data['mood'],
        note=data['note']
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)