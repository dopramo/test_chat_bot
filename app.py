from flask import Flask, jsonify, request, render_template, session
import csv
import json
from flask_cors import CORS  # Add this import

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for using session
CORS(app, supports_credentials=True)  # Add this line

# Heroku manages HTTPS, so don't force secure cookies unless needed
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

def load_menus():
    menus = []
    with open('menus.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Ensure ID is an integer for comparison
            row['id'] = int(row['privilege_id'])
            menus.append(row)
    return menus

@app.route("/")
def index():
    return render_template("index.html")


# POST: Receive array of IDs, filter, and store in session
@app.route("/suggest", methods=["POST"])
def suggest_post():
    data = request.get_json()
    ids = set(map(int, data.get("ids", [])))
    session['filtered_menu_ids'] = list(ids)
    # print(f"Filtered IDs stored in session: {session['filtered_menu_ids']}")  # Debugging line
    return jsonify({"filtered_menu_ids": session['filtered_menu_ids']})

# GET: Search only within filtered entries in session
@app.route("/suggest", methods=["GET"])
def suggest_get():
    query = request.args.get("q", "").strip().lower()
    # Check if filtered_menus exists in session
    print('filtered',session.get('filtered_menu_ids', []))  # Debugging line
    if 'filtered_menu_ids' not in session:
        return jsonify({"error": "No filtered menu ids found. Please POST first."}), 400

    ids = set(session.get('filtered_menu_ids', []))    
    filtered_menus = [m for m in load_menus() if m['id'] in ids]

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
            break  # Stop at the first exact match

    if exact_match:
        return jsonify([exact_match])

    # Fallback to partial match if no exact match
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