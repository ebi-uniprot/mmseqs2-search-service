from fastapi.testclient import TestClient


# def test_submit_valid_fasta(client: TestClient):
#     """Test /submit endpoint with a valid FASTA string."""
#     fasta_data = ">seq1\nMKTAYIAKQRQISFVKSHFSRQDILDLWIYHTQGYFPQ\n"
#     response = client.post("/submit", json={"fasta": fasta_data})
#     assert response.status_code == 200
#     data = response.json()
#     assert "job_id" in data or "uuid" in data
