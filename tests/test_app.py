from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path.endswith("/static/index.html")

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data) > 0

def test_signup_flow():
    # Setup
    activity_name = "Chess Club"
    email = "test_user@mergington.edu"
    
    # Ensure user is not already in participants (cleanup from previous runs if any)
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)
    
    # 1. Sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    
    # Verify added
    assert email in activities[activity_name]["participants"]
    
    # 2. Try to sign up again (should fail)
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

    # 3. Unregister
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    
    # Verify removed
    assert email not in activities[activity_name]["participants"]

def test_signup_invalid_activity():
    response = client.post("/activities/NonExistentActivity/signup?email=test@example.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_invalid_activity():
    response = client.delete("/activities/NonExistentActivity/participants?email=test@example.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_not_signed_up():
    activity_name = "Chess Club"
    email = "not_signed_up@mergington.edu"
    
    # Ensure not in list
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)
        
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not found in this activity"
