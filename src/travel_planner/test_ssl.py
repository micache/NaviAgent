import certifi
import ssl
import httpx

print("Testing SSL configuration...")
print(f"Certifi location: {certifi.where()}")

# Test SSL context
ssl_context = ssl.create_default_context(cafile=certifi.where())
print(f"SSL context created successfully")

# Test HTTPS connection
try:
    http_client = httpx.Client(verify=ssl_context, timeout=10.0)
    response = http_client.get("https://api.openai.com/v1/models")
    print(f"✓ SSL connection successful! Status: {response.status_code}")
    http_client.close()
except Exception as e:
    print(f"✗ SSL connection failed: {e}")
