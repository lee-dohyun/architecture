from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import json
from datetime import datetime

app = Flask(__name__)

SUPPORTED_LANGS = ['ko', 'en', 'ja', 'zh']

def load_lang_data(lang):
    if lang not in SUPPORTED_LANGS:
        lang = 'ko'
    filepath = os.path.join(app.root_path, 'data', f'{lang}.json')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {lang}.json: {e}")
        return {}

@app.route('/')
def index_ko():
    data = load_lang_data('ko')
    return render_template('index.html', t=data, lang='ko')

@app.route('/<lang>/')
def index_lang(lang):
    if lang not in SUPPORTED_LANGS:
        return redirect(url_for('index_ko'))
    data = load_lang_data(lang)
    return render_template('index.html', t=data, lang=lang)

@app.route('/api/architecture')
def api_architecture():
    lang = request.args.get('lang', 'ko')
    data = load_lang_data(lang)
    return jsonify(data.get('data', {}))

@app.route('/api/status')
def api_status():
    data = load_lang_data('ko').get('data', {})
    personal_line = data.get("current", {}).get("services", {}).get("personal_line", [])
    shop_line = data.get("current", {}).get("services", {}).get("shop_line", [])
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "personal_services": len(personal_line),
        "shop_services": len(shop_line)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
