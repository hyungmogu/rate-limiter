import os
import httpx
import hashlib
from flask import Flask, request, jsonify, Response
from redis import Redis

app = Flask(__name__)
redis = Redis(
    host=os.environ['CACHE_REDIS_HOST'],
    port=os.environ['CACHE_REDIS_PORT'],
    password=os.environ['CACHE_REDIS_PASSWORD']
)
redis.ping()

# Rate limit configuration
MAX_REQUESTS_PER_DAY = int(os.environ['API_MAX_REQUESTS_PER_DAY'])

@app.before_request
def rate_limiter():
    hash_object = hashlib.sha256(str.encode(request.remote_addr))
    hashed_ipv6 = hash_object.hexdigest()
    redis_result = redis.get(hashed_ipv6)
    count = 0

    if redis_result:
        count = int(redis_result.decode())

    # ================ DEBUG ==================
    app.logger.info('Redis Result: {}'.format(redis_result))
    app.logger.info('Count: {}'.format(count))
    app.logger.info('Hashed IPv6: {}'.format(hashed_ipv6))
    app.logger.info('Redis Count: {}'.format(count))
    app.logger.info('API_MAX_REQUESTS_PER_DAY: {}'.format(MAX_REQUESTS_PER_DAY))
    # =========================================

    # Check if request count exceeds the limit
    if count >= MAX_REQUESTS_PER_DAY:
        return jsonify({"error": "Rate limit exceeded"}), 429

    redis.set(hashed_ipv6, str.encode('{}'.format(count + 1)))

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    url = f'http://img-converter:80/{path}'
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
    app.run(host='0.0.0.0', port=8089)