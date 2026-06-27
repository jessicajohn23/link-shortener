from flask import Flask, redirect, render_template, request, jsonify, abort
from models import db, Link, Click
from datetime import datetime, timedelta
import random, string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///links.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if not Link.query.filter_by(short_code=code).first():
            return code

# Home Page 
@app.route('/')
def index():
    links = Link.query.order_by(Link.created_at.desc()).limit(10).all()
    return render_template('index.html', links=links)

# Shorten URL
@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form.get('url')
    if not original_url:
        return "No URL provided", 400
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url

    code = generate_code()
    link = Link(original_url=original_url, short_code=code)
    db.session.add(link)
    db.session.commit()
    return render_template('index.html',
        links=Link.query.order_by(Link.created_at.desc()).limit(10).all(),
        new_link=request.host_url + code
    )

# Redirect short URL
@app.route('/<code>')
def redirect_link(code):
    link = Link.query.filter_by(short_code=code).first_or_404()
    
    # Log click
    click = Click(
        link_id=link.id,
        referrer=request.referrer,
        user_agent=request.headers.get('User-Agent'),
        ip_address=request.remote_addr
    )
    db.session.add(click)
    db.session.commit()
    
    return redirect(link.original_url)

# Analytics Dashboard
@app.route('/dashboard/<code>')
def dashboard(code):
    link = Link.query.filter_by(short_code=code).first_or_404()
    return render_template('dashboard.html', link=link)

# API click analytics (7 days)
@app.route('/api/analytics/<code>')
def analytics_data(code):
    link = Link.query.filter_by(short_code=code).first_or_404()
    
    # Clicks per day for last 7 days
    days = []
    counts = []
    for i in range(6, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        count = Click.query.filter(
            Click.link_id == link.id,
            db.func.date(Click.timestamp) == day
        ).count()
        days.append(day.strftime('%b %d'))
        counts.append(count)

    # Top referrers
    referrers = db.session.query(
        Click.referrer,
        db.func.count(Click.id).label('count')
    ).filter(Click.link_id == link.id)\
     .group_by(Click.referrer)\
     .order_by(db.desc('count'))\
     .limit(5).all()

    return jsonify({
        'total_clicks': len(link.clicks),
        'days': days,
        'counts': counts,
        'referrers': [{'source': r[0] or 'Direct', 'count': r[1]} for r in referrers]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   
    app.run(debug=True)