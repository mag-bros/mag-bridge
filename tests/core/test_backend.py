import os
from pathlib import Path
import tempfile
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def app_env():
    """Sets up the environment for the FastAPI app."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.environ["APP_DATA_DIR"] = tmp_dir
        # Import app inside the fixture to ensure environment variable is set
        from backend import app
        yield app, Path(tmp_dir)

def test_upload_sdf_file(app_env):
    app, app_data_dir = app_env
    client = TestClient(app)
    
    with tempfile.TemporaryDirectory() as src_dir:
        # 1. Create a dummy SDF file
        sdf_path = Path(src_dir) / "test.sdf"
        sdf_path.write_text("dummy sdf content")
        
        # 2. Prepare request data
        data = {
            "input_type": "sdf",
            "path": str(sdf_path),
            "selections": ["AC", "DC"]
        }
        
        # 3. Call the endpoint
        response = client.post("/calculations/submit", json=data)
        
        # 4. Assertions
        assert response.status_code == 200
        assert response.json()["filename"] == "test.sdf"
        
        # 5. Check if file actually got copied to SDF_DIR
        dest_path = app_data_dir / "sdf" / "test.sdf"
        assert dest_path.exists()
        assert dest_path.read_text() == "dummy sdf content"

def test_upload_non_existent_file(app_env):
    app, _ = app_env
    client = TestClient(app)
    
    response = client.post("/calculations/submit", json={"input_type": "sdf", "path": "/non/existent/path.sdf"})
    assert response.status_code == 400
    assert response.json()["detail"] == "File does not exist"

def test_upload_smiles(app_env):
    app, _ = app_env
    client = TestClient(app)
    
    data = {
        "input_type": "smiles_formula",
        "smiles_formula": "C1=CC=CC=C1"
    }
    response = client.post("/calculations/submit", json=data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["input"] == "C1=CC=CC=C1"

def test_upload_invalid_extension(app_env):
    app, _ = app_env
    client = TestClient(app)
    
    with tempfile.TemporaryDirectory() as src_dir:
        txt_path = Path(src_dir) / "test.txt"
        txt_path.write_text("dummy content")
        
        response = client.post("/calculations/submit", json={"input_type": "sdf", "path": str(txt_path)})
        assert response.status_code == 400
        assert response.json()["detail"] == "Only SDF files are allowed"
