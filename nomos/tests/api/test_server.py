# tests/api/test_server.py
import pytest
from fastapi.testclient import TestClient
from frontierqu.api.server import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_search_endpoint():
    response = client.get("/search?q=mercy&k=5")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) <= 5

def test_verse_endpoint():
    response = client.get("/verse/1/1")
    assert response.status_code == 200
    data = response.json()
    assert data["surah"] == 1
    assert data["verse"] == 1
    assert "arabic" in data
    assert "morphology" in data

def test_ruling_endpoint():
    response = client.get("/ruling?verse_surah=2&verse_ayah=43&subject=salah")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("WAJIB", "HARAM", "MANDUB", "MAKRUH", "MUBAH")

def test_thematic_endpoint():
    response = client.get("/thematic/tawhid")
    assert response.status_code == 200
    data = response.json()
    assert "theme" in data
    assert "verses" in data
    assert len(data["verses"]) > 0

def test_analyze_endpoint():
    response = client.post("/analyze", json={"arabic": "الْحَمْدُ لِلَّهِ"})
    assert response.status_code == 200
    data = response.json()
    assert "words" in data
    assert "rhetorical_density" in data
