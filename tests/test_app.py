import pytest


class TestGetActivities:
    """Test suite for retrieving activities"""
    
    def test_get_all_activities_returns_success(self, client, reset_activities):
        """Should return all available activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", 
                              "Basketball Team", "Tennis Club", "Art Studio", 
                              "Music Band", "Science Club", "Debate Team"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity in expected_activities:
            assert activity in data
        assert len(data) == 9
    
    def test_get_activities_returns_participant_count(self, client, reset_activities):
        """Should return participant information in activities"""
        # Arrange
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "Chess Club" in data
        assert "participants" in data["Chess Club"]
        assert isinstance(data["Chess Club"]["participants"], list)
        assert len(data["Chess Club"]["participants"]) == 2


class TestSignupForActivity:
    """Test suite for student signup"""
    
    def test_signup_new_participant_succeeds(self, client, reset_activities):
        """Should successfully register a new student"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Should prevent duplicate registrations"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Should return 404 for non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_reflects_in_activity_data(self, client, reset_activities):
        """Should update activity participant list after signup"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = 2
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_multiple_different_participants(self, client, reset_activities):
        """Should allow multiple different students to register"""
        # Arrange
        activity_name = "Tennis Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        
        # Act
        for email in emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for email in emails:
            assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 3  # 1 original + 2 new


class TestUnregisterFromActivity:
    """Test suite for student unregistration"""
    
    def test_unregister_existing_participant_succeeds(self, client, reset_activities):
        """Should successfully unregister an enrolled student"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Should return 404 for non-registered student"""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_removes_from_activity_data(self, client, reset_activities):
        """Should update activity participant list after unregistration"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = 2
        
        # Act
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_from_nonexistent_activity_fails(self, client, reset_activities):
        """Should return 404 when unregistering from non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister workflows"""
    
    def test_signup_then_unregister_flow(self, client, reset_activities):
        """Should allow signup and then unregister in sequence"""
        # Arrange
        activity_name = "Art Studio"
        email = "artist@mergington.edu"
        initial_count = 2
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        get_response_after_signup = client.get("/activities")
        activities_after_signup = get_response_after_signup.json()
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        get_response_after_unregister = client.get("/activities")
        activities_after_unregister = get_response_after_unregister.json()
        
        # Assert - Signup worked
        assert signup_response.status_code == 200
        assert email in activities_after_signup[activity_name]["participants"]
        assert len(activities_after_signup[activity_name]["participants"]) == initial_count + 1
        
        # Assert - Unregister worked
        assert unregister_response.status_code == 200
        assert email not in activities_after_unregister[activity_name]["participants"]
        assert len(activities_after_unregister[activity_name]["participants"]) == initial_count
