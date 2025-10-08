from flask import Flask, request, jsonify, redirect, Response
import requests
from threading import Lock

app = Flask(__name__)

SECRET_TOKEN = "aerhnszlgjderfhuil"
current_colab_url = None
lock = Lock()

@app.route('/register_colab', methods=['POST'])
def register_colab():
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
def home():
    return redirect("/asosiy")

@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    global current_colab_url
    if not current_colab_url:
        return jsonify({"error": "Colab server not connected"}), 503

    target_url = f"{current_colab_url}/{path}"

    try:
        # Cookie’larni uzatish
        cookies = request.cookies

        # So‘rov yuborish
        if request.method == 'POST':
            resp = requests.post(
                target_url,
                data=request.form,
                files=request.files,
                cookies=cookies,
                allow_redirects=False
            )
        else:
            resp = requests.get(
                target_url,
                params=request.args,
                cookies=cookies,
                allow_redirects=False
            )

        # Foydalanuvchiga cookie va status bilan qaytarish
        response = Response(resp.content, resp.status_code)
        for key, value in resp.headers.items():
            if key.lower() == 'set-cookie':
                response.headers.add('Set-Cookie', value)
            elif key.lower() not in ['content-length', 'transfer-encoding', 'content-encoding']:
                response.headers[key] = value

        return response

    except Exception as e:
        return jsonify({"error": f"Proxy error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
