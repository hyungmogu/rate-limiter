import time
import httpx
from flask import Flask, request, jsonify, Response
from functools import wraps

app = Flask(__name__)

# In-memory storage to track requests per ID
request_counts = {}

# Rate limit configuration
MAX_REQUESTS_PER_DAY = 1000
SECONDS_IN_DAY = 24 * 60 * 60

def rate_limiter():
    current_time = int(time.time())

    # Extract the ID from the request
    id = request.headers.get('X-Request-ID', None)
    if id is None:
        return jsonify({"error": "Missing X-Request-ID header"}), 400

    # Initialize request count if ID is not present
    if id not in request_counts:
        request_counts[id] = {
            "count": 0,
            "reset_time": current_time + SECONDS_IN_DAY
        }

    # Check if request count exceeds the limit
    if request_counts[id]["count"] >= MAX_REQUESTS_PER_DAY:
        return jsonify({"error": "Rate limit exceeded"}), 429

    # Check if rate limit reset time has passed
    if current_time > request_counts[id]["reset_time"]:
        request_counts[id]["count"] = 0
        request_counts[id]["reset_time"] = current_time + SECONDS_IN_DAY

    request_counts[id]["count"] += 1

app.before_request(rate_limiter)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    url = f'http://php-service:80/{path}'
    headers = {k: v for k, v in request.headers if k != 'Host'}

    try:
        response = httpx.request(
            request.method,
            url,
            headers=headers,
            params=request.args,
            data=request.data,
            timeout=30.0
        )
        return Response(response.content, response.status_code, response.headers.items())
    except httpx.RequestError as e:
        return jsonify({"error": f"An error occurred while forwarding the request: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)