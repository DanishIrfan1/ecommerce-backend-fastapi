"""
Basic API test to check if the server is running and responding.
"""

import requests
import pytest

BASE_URL = "http://localhost:8000"

def test_api_is_running():
    """Test that the API server is running and responding."""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        assert response.status_code in [200, 307, 404]  # 307 for redirect, 404 for not found
        print(f"✅ API server is responding with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"API server is not running or not responding: {e}")

def test_docs_endpoint():
    """Test that the docs endpoint is accessible."""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        assert response.status_code == 200
        print("✅ API documentation is accessible")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Docs endpoint is not accessible: {e}")

def test_openapi_endpoint():
    """Test that the OpenAPI schema endpoint is accessible."""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        assert response.status_code == 200
        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "paths" in openapi_data
        print("✅ OpenAPI schema is accessible")
        
        # Print available endpoints
        print("Available API endpoints:")
        for path, methods in openapi_data.get("paths", {}).items():
            for method in methods.keys():
                print(f"  {method.upper()} {path}")
                
    except requests.exceptions.RequestException as e:
        pytest.fail(f"OpenAPI endpoint is not accessible: {e}")

if __name__ == "__main__":
    test_api_is_running()
    test_docs_endpoint()
    test_openapi_endpoint()
