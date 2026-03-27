# check_backend.py
import requests

BASE = "http://localhost:8000"   # use http://backend:8000 only inside docker network

def show(resp, name):
    print(f"\n--- {name} ---")
    print("status:", resp.status_code)
    print("text:", resp.text[:1000])

# 1) health
r = requests.get(f"{BASE}/health", timeout=10)
show(r, "health")

# 2) register
payload = {"email": "test123@example.com", "password": "TestPassword123!@#"}
r = requests.post(f"{BASE}/auth/register", json=payload, timeout=10)
show(r, "register")

# 3) login
r = requests.post(
    f"{BASE}/auth/login",
    data={"username": payload["email"], "password": payload["password"]},
    timeout=10,
)
show(r, "login")

if r.status_code == 200:
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4) predict
    abstract = (
        "This study evaluates the effect of aspirin on cardiovascular outcomes. "
        "Participants received aspirin or placebo for 24 months. "
        "Results showed a reduction in major cardiovascular events."
    )
    r = requests.post(f"{BASE}/predict", json={"abstract": abstract}, headers=headers, timeout=30)
    show(r, "predict")