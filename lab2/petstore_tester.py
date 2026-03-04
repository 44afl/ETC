from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

PETSTORE_URL = "https://petstore.swagger.io/v2/pet/1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Petstore HTTP Method Tester</title>
</head>
<body>
    <h1>Test HTTP Methods on Petstore</h1>
    <form method="post">
        <label for="method">Choose HTTP method:</label>
        <select name="method" id="method">
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
            <option value="PATCH">PATCH</option>
            <option value="HEAD">HEAD</option>
            <option value="OPTIONS">OPTIONS</option>
        </select>
        <button type="submit">Send Request</button>
    </form>
    {% if result %}
        <h2>Result</h2>
        <pre>{{ result }}</pre>
    {% endif %}
</body>
</html>
'''

import random as rand
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        method = request.form['method']
        try:
            if method == 'GET':
                resp = requests.get(PETSTORE_URL, json={"id": rand.randint(1, 10)})
            elif method == 'POST':
                resp = requests.post(PETSTORE_URL, json={"id": 1, "name": "doggie", "status": "available"})
            elif method == 'PUT':
                resp = requests.put(PETSTORE_URL, json={"id": 1, "name": "doggie", "status": "sold"})
            elif method == 'DELETE':
                resp = requests.delete(PETSTORE_URL, json={"id": 2})
            elif method == 'PATCH':
                resp = requests.patch(PETSTORE_URL, json={"id": 4, "status": "pending"})
            elif method == 'HEAD':
                resp = requests.head(PETSTORE_URL)
            elif method == 'OPTIONS':
                resp = requests.options(PETSTORE_URL)
            else:
                result = "Unsupported method"
                resp = None
            if resp is not None:
                result = f"Status: {resp.status_code}\nHeaders: {resp.headers}\nBody: {resp.text if method != 'HEAD' else ''}"
        except Exception as e:
            result = f"Error: {e}"
    return render_template_string(HTML, result=result)

if __name__ == '__main__':
    app.run(debug=True)
