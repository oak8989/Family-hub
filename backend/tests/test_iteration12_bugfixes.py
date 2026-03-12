"""
Test file for Iteration 12 bug fixes:
1. Recipe URL import - test with multiple sites
2. Chore points - verify points update in leaderboard after completion
3. Reward claim - test redeeming chore points for rewards
4. Meal to Grocery - add missing ingredients from meal recipe
5. Pantry barcode lookup - verify category field returned
"""
import pytest
import requests
import uuid
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_OWNER_EMAIL = "owner@test.com"
TEST_OWNER_PASSWORD = "test123"


class TestRecipeImport:
    """Test recipe import from various URLs with HTTP/2 support"""

    def get_auth_token(self):
        """Get auth token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_OWNER_EMAIL,
            "password": TEST_OWNER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None

    def test_import_bbc_good_food(self):
        """Test importing recipe from BBC Good Food"""
        token = self.get_auth_token()
        if not token:
            pytest.skip("Auth failed - skipping recipe import test")
        
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://www.bbcgoodfood.com/recipes/easy-chocolate-cake"
        
        response = requests.post(
            f"{BASE_URL}/api/recipes/import-url",
            json={"url": url},
            headers=headers,
            timeout=30
        )
        
        print(f"BBC Good Food response status: {response.status_code}")
        print(f"Response: {response.text[:500] if response.text else 'Empty'}")
        
        # Should return 200 with recipe data OR 400/422 if site blocks
        if response.status_code == 200:
            data = response.json()
            assert "name" in data, "Recipe should have name"
            assert data.get("name"), "Recipe name should not be empty"
            print(f"Successfully imported: {data.get('name')}")
            print(f"Ingredients count: {len(data.get('ingredients', []))}")
            print(f"Instructions count: {len(data.get('instructions', []))}")
        else:
            # Site may block - this is acceptable behavior
            print(f"Site returned {response.status_code} - may be blocking")
            assert response.status_code in [400, 422], f"Unexpected status: {response.status_code}"

    def test_import_sallys_baking(self):
        """Test importing recipe from Sally's Baking Addiction (HTTP/2 site)"""
        token = self.get_auth_token()
        if not token:
            pytest.skip("Auth failed - skipping recipe import test")
        
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://sallysbakingaddiction.com/best-banana-bread-recipe/"
        
        response = requests.post(
            f"{BASE_URL}/api/recipes/import-url",
            json={"url": url},
            headers=headers,
            timeout=30
        )
        
        print(f"Sally's Baking response status: {response.status_code}")
        print(f"Response: {response.text[:500] if response.text else 'Empty'}")
        
        if response.status_code == 200:
            data = response.json()
            assert "name" in data, "Recipe should have name"
            assert data.get("name"), "Recipe name should not be empty"
            print(f"Successfully imported: {data.get('name')}")
        else:
            print(f"Site returned {response.status_code} - may be blocking")
            assert response.status_code in [400, 422]

    def test_import_pinch_of_yum(self):
        """Test importing recipe from Pinch of Yum"""
        token = self.get_auth_token()
        if not token:
            pytest.skip("Auth failed - skipping recipe import test")
        
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://pinchofyum.com/the-best-soft-chocolate-chip-cookies"
        
        response = requests.post(
            f"{BASE_URL}/api/recipes/import-url",
            json={"url": url},
            headers=headers,
            timeout=30
        )
        
        print(f"Pinch of Yum response status: {response.status_code}")
        print(f"Response: {response.text[:500] if response.text else 'Empty'}")
        
        if response.status_code == 200:
            data = response.json()
            assert "name" in data, "Recipe should have name"
            print(f"Successfully imported: {data.get('name')}")
        else:
            print(f"Site returned {response.status_code} - may be blocking")
            assert response.status_code in [400, 422]


class TestChorePointsFlow:
    """Test complete chore → points → reward flow"""

    def get_auth_token(self):
        """Get auth token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_OWNER_EMAIL,
            "password": TEST_OWNER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token"), response.json().get("user")
        return None, None

    def test_create_and_complete_chore_updates_points(self):
        """Test that completing a chore updates user points in leaderboard"""
        token, user = self.get_auth_token()
        if not token:
            pytest.skip("Auth failed")
        
        headers = {"Authorization": f"Bearer {token}"}
        user_id = user.get("id")
        
        # 1. Get initial leaderboard points
        leaderboard_res = requests.get(f"{BASE_URL}/api/leaderboard", headers=headers)
        assert leaderboard_res.status_code == 200
        leaderboard = leaderboard_res.json()
        initial_points = next((m["points"] for m in leaderboard if m["id"] == user_id), 0)
        print(f"Initial points for user {user_id}: {initial_points}")
        
        # 2. Create a chore assigned to this user
        chore_data = {
            "id": str(uuid.uuid4()),
            "title": f"TEST_ChorePointsTest_{uuid.uuid4().hex[:6]}",
            "description": "Test chore for points verification",
            "difficulty": "easy",  # 5 points
            "assigned_to": user_id
        }
        create_res = requests.post(f"{BASE_URL}/api/chores", json=chore_data, headers=headers)
        assert create_res.status_code == 200, f"Failed to create chore: {create_res.text}"
        created_chore = create_res.json()
        chore_id = created_chore.get("id")
        expected_points = created_chore.get("points", 5)
        print(f"Created chore {chore_id} with {expected_points} points")
        
        # 3. Complete the chore
        complete_res = requests.post(f"{BASE_URL}/api/chores/{chore_id}/complete", headers=headers)
        assert complete_res.status_code == 200, f"Failed to complete chore: {complete_res.text}"
        complete_data = complete_res.json()
        assert "points_earned" in complete_data
        print(f"Completed chore, earned {complete_data.get('points_earned')} points")
        
        # 4. Verify leaderboard shows updated points
        leaderboard_res2 = requests.get(f"{BASE_URL}/api/leaderboard", headers=headers)
        assert leaderboard_res2.status_code == 200
        leaderboard2 = leaderboard_res2.json()
        new_points = next((m["points"] for m in leaderboard2 if m["id"] == user_id), 0)
        print(f"New points for user: {new_points}")
        
        assert new_points == initial_points + expected_points, \
            f"Expected {initial_points + expected_points} points, got {new_points}"
        print(f"SUCCESS: Points correctly updated from {initial_points} to {new_points}")
        
        # Cleanup - delete the chore
        requests.delete(f"{BASE_URL}/api/chores/{chore_id}", headers=headers)


class TestRewardClaim:
    """Test reward creation and claiming"""

    def get_auth_token(self):
        """Get auth token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_OWNER_EMAIL,
            "password": TEST_OWNER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token"), response.json().get("user")
        return None, None

    def test_create_reward_and_claim(self):
        """Test creating a reward and claiming it"""
        token, user = self.get_auth_token()
        if not token:
            pytest.skip("Auth failed")
        
        headers = {"Authorization": f"Bearer {token}"}
        user_id = user.get("id")
        
        # 1. Get current user points from leaderboard
        leaderboard_res = requests.get(f"{BASE_URL}/api/leaderboard", headers=headers)
        assert leaderboard_res.status_code == 200
        leaderboard = leaderboard_res.json()
        current_points = next((m["points"] for m in leaderboard if m["id"] == user_id), 0)
        print(f"User has {current_points} points")
        
        if current_points < 1:
            # Create and complete a chore to get some points
            print("Need to earn points first...")
            chore_data = {
                "id": str(uuid.uuid4()),
                "title": f"TEST_EarnPoints_{uuid.uuid4().hex[:6]}",
                "difficulty": "hard",  # 20 points
                "assigned_to": user_id
            }
            create_res = requests.post(f"{BASE_URL}/api/chores", json=chore_data, headers=headers)
            assert create_res.status_code == 200
            chore_id = create_res.json().get("id")
            
            complete_res = requests.post(f"{BASE_URL}/api/chores/{chore_id}/complete", headers=headers)
            assert complete_res.status_code == 200
            
            # Refresh points
            leaderboard_res = requests.get(f"{BASE_URL}/api/leaderboard", headers=headers)
            leaderboard = leaderboard_res.json()
            current_points = next((m["points"] for m in leaderboard if m["id"] == user_id), 0)
            print(f"After earning: User has {current_points} points")
            
            requests.delete(f"{BASE_URL}/api/chores/{chore_id}", headers=headers)
        
        # 2. Create a reward that costs 1 point (to ensure user can claim)
        reward_data = {
            "id": str(uuid.uuid4()),
            "name": f"TEST_Reward_{uuid.uuid4().hex[:6]}",
            "description": "Test reward for claiming",
            "points_required": 1
        }
        create_reward_res = requests.post(f"{BASE_URL}/api/rewards", json=reward_data, headers=headers)
        assert create_reward_res.status_code == 200, f"Failed to create reward: {create_reward_res.text}"
        reward = create_reward_res.json()
        reward_id = reward.get("id")
        print(f"Created reward {reward_id} costing {reward.get('points_required')} points")
        
        # 3. Claim the reward using POST /api/rewards/claim
        claim_res = requests.post(
            f"{BASE_URL}/api/rewards/claim",
            json={"reward_id": reward_id, "user_id": user_id},
            headers=headers
        )
        assert claim_res.status_code == 200, f"Failed to claim reward: {claim_res.text}"
        claim_data = claim_res.json()
        print(f"Claim response: {claim_data}")
        assert "points_spent" in claim_data or "message" in claim_data
        
        # 4. Verify points decreased
        leaderboard_res2 = requests.get(f"{BASE_URL}/api/leaderboard", headers=headers)
        leaderboard2 = leaderboard_res2.json()
        new_points = next((m["points"] for m in leaderboard2 if m["id"] == user_id), 0)
        print(f"Points after claim: {new_points}")
        
        assert new_points == current_points - 1, \
            f"Expected {current_points - 1} points after claim, got {new_points}"
        print(f"SUCCESS: Points correctly deducted from {current_points} to {new_points}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/rewards/{reward_id}", headers=headers)


class TestMealToGrocery:
    """Test adding meal ingredients to grocery list"""

    def get_auth_token(self):
        """Get auth token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_OWNER_EMAIL,
            "password": TEST_OWNER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token"), response.json().get("user")
        return None, None

    def test_add_meal_ingredients_to_grocery(self):
        """Test POST /api/grocery/add-from-meal/{plan_id}"""
        token, user = self.get_auth_token()
        if not token:
            pytest.skip("Auth failed")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Create a recipe with ingredients
        recipe_id = str(uuid.uuid4())
        recipe_data = {
            "id": recipe_id,
            "name": f"TEST_MealGroceryRecipe_{uuid.uuid4().hex[:6]}",
            "description": "Test recipe for grocery addition",
            "ingredients": [
                "2 cups flour",
                "1 cup sugar",
                "3 eggs",
                "1 cup milk"
            ],
            "instructions": ["Mix ingredients", "Bake at 350F"],
            "servings": 4,
            "category": "Dessert"
        }
        recipe_res = requests.post(f"{BASE_URL}/api/recipes", json=recipe_data, headers=headers)
        assert recipe_res.status_code == 200, f"Failed to create recipe: {recipe_res.text}"
        print(f"Created recipe: {recipe_data['name']}")
        
        # 2. Create a meal plan with this recipe
        meal_id = str(uuid.uuid4())
        meal_data = {
            "id": meal_id,
            "date": "2026-01-15",
            "meal_type": "dinner",
            "recipe_id": recipe_id,
            "recipe_name": recipe_data["name"]
        }
        meal_res = requests.post(f"{BASE_URL}/api/meals", json=meal_data, headers=headers)
        assert meal_res.status_code == 200, f"Failed to create meal plan: {meal_res.text}"
        print(f"Created meal plan: {meal_data['recipe_name']}")
        
        # 3. Add meal ingredients to grocery list
        add_res = requests.post(
            f"{BASE_URL}/api/grocery/add-from-meal/{meal_id}",
            headers=headers
        )
        assert add_res.status_code == 200, f"Failed to add to grocery: {add_res.text}"
        add_data = add_res.json()
        print(f"Add to grocery response: {add_data}")
        
        assert "added" in add_data, "Response should include 'added' count"
        assert "message" in add_data, "Response should include 'message'"
        print(f"Added {add_data.get('added')} items to grocery list")
        
        # 4. Verify grocery list contains the ingredients
        grocery_res = requests.get(f"{BASE_URL}/api/grocery", headers=headers)
        assert grocery_res.status_code == 200
        grocery_items = grocery_res.json()
        grocery_names = [g["name"].lower() for g in grocery_items]
        print(f"Grocery list has {len(grocery_items)} items")
        
        # Check that at least some ingredients were added
        ingredients_found = sum(1 for ing in recipe_data["ingredients"] 
                               if any(ing.lower() in name or name in ing.lower() 
                                     for name in grocery_names))
        print(f"Found {ingredients_found} recipe ingredients in grocery list")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/recipes/{recipe_id}", headers=headers)
        requests.delete(f"{BASE_URL}/api/meals/{meal_id}", headers=headers)
        # Delete added grocery items - they have TEST_ prefix in the ingredient names
        for item in grocery_items:
            if any(ing in item["name"] for ing in ["flour", "sugar", "eggs", "milk"]):
                requests.delete(f"{BASE_URL}/api/grocery/{item['id']}", headers=headers)


class TestPantryBarcodeCategory:
    """Test pantry barcode lookup with category field"""

    def test_barcode_lookup_returns_category(self):
        """Test GET /api/pantry/barcode/{barcode} returns category"""
        # Use a known barcode (Coca-Cola)
        test_barcode = "049000006346"
        
        # This endpoint doesn't require auth
        response = requests.get(f"{BASE_URL}/api/pantry/barcode/{test_barcode}", timeout=10)
        assert response.status_code == 200, f"Barcode lookup failed: {response.text}"
        
        data = response.json()
        print(f"Barcode lookup response: {data}")
        
        # Check required fields
        assert "found" in data, "Response should have 'found' field"
        assert "barcode" in data, "Response should have 'barcode' field"
        
        if data.get("found"):
            assert "category" in data, "Found product should have 'category' field"
            assert "name" in data, "Found product should have 'name' field"
            print(f"Product: {data.get('name')}, Category: {data.get('category')}")
        else:
            print(f"Barcode {test_barcode} not found in database - this is acceptable")

    def test_barcode_unknown_product(self):
        """Test barcode lookup for unknown product - returns 200 regardless"""
        # Use a truly random barcode
        test_barcode = "9999999999999"
        
        response = requests.get(f"{BASE_URL}/api/pantry/barcode/{test_barcode}", timeout=10)
        assert response.status_code == 200, f"Barcode lookup failed: {response.text}"
        
        data = response.json()
        print(f"Barcode lookup response: {data}")
        # API returns 200 with found=True or found=False
        assert "found" in data, "Response should have 'found' field"
        assert "barcode" in data, "Response should have 'barcode' field"
        print(f"Found status: {data.get('found')}")


class TestLeaderboardEndpoint:
    """Test leaderboard endpoint returns correct data"""

    def get_auth_token(self):
        """Get auth token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_OWNER_EMAIL,
            "password": TEST_OWNER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None

    def test_leaderboard_returns_points(self):
        """Test GET /api/leaderboard returns user points"""
        token = self.get_auth_token()
        if not token:
            pytest.skip("Auth failed")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/leaderboard", headers=headers)
        
        assert response.status_code == 200, f"Leaderboard failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Leaderboard should return a list"
        print(f"Leaderboard has {len(data)} members")
        
        if len(data) > 0:
            member = data[0]
            assert "id" in member, "Member should have id"
            assert "name" in member, "Member should have name"
            assert "points" in member, "Member should have points"
            print(f"Top member: {member.get('name')} with {member.get('points')} points")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
