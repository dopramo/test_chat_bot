from flask import Flask, jsonify, request, render_template, session
import csv
import os
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')
CORS(app, supports_credentials=True)

# Heroku manages HTTPS, so don't force secure cookies unless needed
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

def load_menus():
    menus = []
    with open('menus.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['id'] = int(row['id'])
            row['privilege_id'] = int(row['privilege_id'])
            menus.append(row)
    return menus

@app.route("/")
def index():
    return render_template("index.html")

# POST: Receive array of menu IDs, filter, and store in session
@app.route("/suggest", methods=["POST"])
def suggest_post():
    data = request.get_json()
    ids = set(map(int, data.get("ids", [])))
    session['filtered_menu_ids'] = list(ids)
    return jsonify({"filtered_menu_ids": session['filtered_menu_ids']})

# POST: Receive array of privilege IDs and store in session
@app.route("/set_privileges", methods=["POST"])
def set_privileges():
    data = request.get_json()
    privilege_ids = set(map(int, data.get("privilege_ids", [])))
    session['allowed_privilege_ids'] = list(privilege_ids)
    return jsonify({"allowed_privilege_ids": session['allowed_privilege_ids']})

# GET: Search only within filtered entries in session (by menu id or privilege id)
@app.route("/suggest", methods=["GET"])
def suggest_get():
    query = request.args.get("q", "").strip().lower()

    # Prefer privilege-based filtering if present, else fallback to filtered_menu_ids
    if 'allowed_privilege_ids' in session:
        allowed_privs = set(session['allowed_privilege_ids'])
        filtered_menus = [m for m in load_menus() if m['privilege_id'] in allowed_privs]
    elif 'filtered_menu_ids' in session:
        ids = set(session.get('filtered_menu_ids', []))
        filtered_menus = [m for m in load_menus() if m['id'] in ids]
    else:
        return jsonify({"error": "No privilege or menu ids found. Please POST first."}), 400

    menus = []
    exact_match = None
    for row in filtered_menus:
        title = row['title'].strip().lower()
        if query == title:
            exact_match = {
                "title": row['title'],
                "url": row['url'],
                "description": row.get('description', '')
            }
            break

    if exact_match:
        return jsonify([exact_match])

    query_words = [w.strip() for w in query.split() if w.strip()]
    for row in filtered_menus:
        keywords = [k.strip().lower() for k in row['keywords'].split(',')]
        title = row['title'].lower()
        if any(
            k.startswith(qw) or title.startswith(qw)
            for qw in query_words
            for k in keywords
        ):
            menus.append({
                "title": row['title'],
                "url": row['url'],
                "description": row.get('description', '')
            })
    return jsonify(menus)

if __name__ == "__main__":
    app.run()
