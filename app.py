from flask import Flask, render_template_string, request, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

# Single-file HTML layout for the proxy browser interface
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Proxy Browser</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f4f4f9; }
        .bar { background: #222; padding: 12px; display: flex; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .bar form { display: flex; width: 100%; gap: 10px; }
        .bar input { flex: 1; padding: 10px; border: 1px solid #444; border-radius: 4px; background: #333; color: #fff; font-size: 14px; }
        .bar button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .bar button:hover { background: #0056b3; }
        iframe { width: 100%; height: calc(100vh - 65px); border: none; background: white; }
    </style>
</head>
<body>
    <div class="bar">
        <form action="/view" method="GET">
            <input type="text" name="url" placeholder="Enter full URL here (e.g., https://example.com)" required>
            <button type="submit">Go</button>
        </form>
    </div>
    {% if target %}
        <iframe src="/proxy?url={{ target }}"></iframe>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

@app.route('/view')
def view():
    url = request.args.get('url', '')
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return render_template_string(HTML_LAYOUT, target=url)

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Missing URL parameter", 400

    try:
        # Request headers to look like a standard desktop browser
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers, timeout=10)
        
        # Parse HTML and fix broken relative links for images/styles
        soup = BeautifulSoup(res.text, 'html.parser')
        for tag in soup.find_all(['a', 'link', 'script', 'img']):
            attr = 'href' if tag.name in ['a', 'link'] else 'src'
            if tag.has_attr(attr):
                # Convert relative links into absolute working URLs
                abs_url = urljoin(url, tag[attr])
                if tag.name == 'a':
                    tag[attr] = f"/view?url={abs_url}"
                else:
                    tag[attr] = abs_url

        return Response(str(soup), mimetype=res.headers.get('content-type', 'text/html'))
    except Exception as err:
        return f"Error loading page: {str(err)}", 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
