"""
Integration tests for battle plan gallery endpoint
"""
import pytest
from fastapi.testclient import TestClient


class TestBattlePlanGallery:
    """Test battle plan gallery endpoint"""

    def test_gallery_returns_all_aos_plans(self, test_client: TestClient):
        """Test that gallery returns all 12 AoS battle plans"""
        response = test_client.get("/api/squire/battle-plans/gallery?system=age_of_sigmar")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Gallery should return a list"
        assert len(data) == 12, f"Expected 12 AoS battle plans, got {len(data)}"
        
        # Verify all plans have required fields
        required_fields = ["name", "deployment_description", "primary_objective", 
                          "secondary_objectives", "victory_conditions", "deployment_map_url"]
        
        for plan in data:
            for field in required_fields:
                assert field in plan, f"Plan missing field: {field}"
            
            # Verify deployment_map_url is present and points to static assets
            assert plan["deployment_map_url"] is not None, f"Plan {plan['name']} missing deployment_map_url"
            assert "/static/battle-plans/" in plan["deployment_map_url"], \
                f"Plan {plan['name']} has invalid deployment_map_url: {plan['deployment_map_url']}"
    
    def test_gallery_plan_names(self, test_client: TestClient):
        """Test that all expected AoS battle plan names are present"""
        expected_names = {
            "Passing Seasons", "Paths of the Fey", "Roiling Roots", "Cyclic Shifts",
            "Surge of Slaughter", "Linked Ley Lines", "Noxious Nexus", "The Liferoots",
            "Bountiful Equinox", "Lifecycle", "Creeping Corruption", "Grasp of Thorns"
        }
        
        response = test_client.get("/api/squire/battle-plans/gallery?system=age_of_sigmar")
        assert response.status_code == 200
        
        data = response.json()
        actual_names = {plan["name"] for plan in data}
        
        assert actual_names == expected_names, \
            f"Plan names mismatch. Missing: {expected_names - actual_names}, Extra: {actual_names - expected_names}"
    
    def test_gallery_invalid_system(self, test_client: TestClient):
        """Test that invalid game system returns error"""
        response = test_client.get("/api/squire/battle-plans/gallery?system=invalid_system")
        assert response.status_code == 400
    
    def test_gallery_40k_not_implemented(self, test_client: TestClient):
        """Test that 40k gallery returns 404 (not implemented)"""
        response = test_client.get("/api/squire/battle-plans/gallery?system=warhammer_40k")
        assert response.status_code == 404
        data = response.json()
        # Check that response contains error message about gallery not being available
        assert "message" in data
        assert "not available" in data["message"].lower()
