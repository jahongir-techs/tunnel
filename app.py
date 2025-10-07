from flask import Flask, request, jsonify, redirect
import requests
from threading import Lock

app = Flask(__name__)

SECRET_TOKEN = "aerhnszlgjderfhuil"
current_colab_url = None
lock = Lock()

@app.route('/register_colab', methods=['POST'])
def register_colab():
    """Colab tomonidan yuborilgan ngrok manzilni qabul qiladi"""
    global current_colab_url
    data = request.get_json(force=True)
    if not data or data.get('token') != SECRET_TOKEN:
        return jsonify({"error": "Access denied"}), 403
    
    new_url = data.get('url')
    if not new_url:
        return jsonify({"error": "URL not provided"}), 400
    
    with lock:
        current_colab_url = new_url.rstrip('/')
    
    print(f"✅ New Colab URL registered: {current_colab_url}")
    return jsonify({"message": "Colab URL updated", "url": current_colab_url})
@app.route('/')
def asfhj():
    return redirect("/asosiy")
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    """Foydalanuvchidan kelgan so‘rovni Colab’ga uzatadi"""
    global current_colab_url
    if not current_colab_url:
        return jsonify({"error": "Colab server not connected"}), 503
    
    target_url = f"{current_colab_url}/{path}"
    try:
        if request.method == 'POST':
            resp = requests.post(target_url, data=request.form, files=request.files)
        else:
            resp = requests.get(target_url, params=request.args)
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({"error": f"Proxy error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
