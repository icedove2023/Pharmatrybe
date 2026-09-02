#!/usr/bin/env python3
import os
import sys

os.chdir(r"c:\Users\Adetokunbo\Desktop\Pharmatrybe_project\Pharmatrybe\apps\api")
sys.path.insert(0, r"c:\Users\Adetokunbo\Desktop\Pharmatrybe_project\Pharmatrybe\apps\api")

# Load environment
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Adetokunbo\Desktop\Pharmatrybe_project\Pharmatrybe\.env")

print("Testing JWT verification setup...")
print(f"ISSUER: {os.getenv('SUPABASE_JWT_ISSUER')}")
print(f"AUDIENCE: {os.getenv('SUPABASE_JWT_AUDIENCE')}")
print(f"JWKS_URL: {os.getenv('SUPABASE_JWKS_URL')}")

try:
    # Try to get JWKS
    from jwt import PyJWKClient
    jwks_url = os.getenv('SUPABASE_JWKS_URL')
    print(f"\nTesting JWKS access...")
    client = PyJWKClient(jwks_url, timeout=10)
    print("  - Created PyJWKClient")
    keys = client.fetch_data()
    print(f"✓ JWKS accessible, keys count: {len(keys.get('keys', []))}")
except Exception as e:
    print(f"✗ JWKS Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
