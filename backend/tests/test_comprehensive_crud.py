"""
Family Hub Comprehensive CRUD Tests
Tests ALL CRUD operations for ALL modules:
- Calendar, Shopping, Tasks, Chores, Rewards, Notes, Budget, Meals, Recipes, Grocery, Contacts, Pantry
- Also tests: Meal Suggestions, Barcode Lookup, Member Management
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_PASSWORD = "test123"


class TestSetup:
    """Setup test family with owner for CRUD testing"""
    
    @pytest.fixture(scope="class")
    def auth_setup(self):
        """Create owner with family for testing"""
        owner_email = f"crud_owner_{uuid.uuid4().hex[:8]}@test.com"
        
        # Register with family name to become owner
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "CRUD Test Owner",
            "email": owner_email,
            "password": TEST_PASSWORD,
            "family_name": "CRUD Test Family"
        })
        assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
        reg_data = reg_resp.json()
        
        token = reg_data["token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = reg_data["user"]["id"]
        family_pin = reg_data.get("family_pin")
        
        print(f"✓ Owner created with family - Family PIN: {family_pin}")
        
        return {
            "token": token,
            "headers": headers,
            "user_id": user_id,
            "email": owner_email,
            "family_pin": family_pin
        }


# ============== CALENDAR CRUD TESTS ==============
class TestCalendarCRUD(TestSetup):
    """Calendar module CRUD tests"""
    
    def test_create_event(self, auth_setup):
        """Test creating calendar event"""
        headers = auth_setup["headers"]
        event_data = {
            "title": "TEST_Family Meeting",
            "description": "Weekly family meeting",
            "date": "2025-02-15",
            "time": "18:00",
            "color": "#E07A5F"
        }
        response = requests.post(f"{BASE_URL}/api/calendar", json=event_data, headers=headers)
        assert response.status_code == 200, f"Create event failed: {response.text}"
        data = response.json()
        assert data["title"] == "TEST_Family Meeting"
        assert "id" in data
        print(f"✓ Calendar event created: {data['id']}")
        return data["id"]
    
    def test_get_all_events(self, auth_setup):
        """Test getting all calendar events"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/calendar", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Calendar events retrieved: {len(data)} events")
    
    def test_update_event(self, auth_setup):
        """Test updating calendar event"""
        headers = auth_setup["headers"]
        # Create event first
        create_resp = requests.post(f"{BASE_URL}/api/calendar", json={
            "title": "TEST_Update Event",
            "date": "2025-02-20"
        }, headers=headers)
        event_id = create_resp.json()["id"]
        
        # Update event
        update_resp = requests.put(f"{BASE_URL}/api/calendar/{event_id}", json={
            "id": event_id,
            "title": "TEST_Updated Event Title",
            "date": "2025-02-21"
        }, headers=headers)
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["title"] == "TEST_Updated Event Title"
        print("✓ Calendar event updated")
    
    def test_delete_event(self, auth_setup):
        """Test deleting calendar event"""
        headers = auth_setup["headers"]
        # Create event first
        create_resp = requests.post(f"{BASE_URL}/api/calendar", json={
            "title": "TEST_Delete Event",
            "date": "2025-02-25"
        }, headers=headers)
        event_id = create_resp.json()["id"]
        
        # Delete event
        delete_resp = requests.delete(f"{BASE_URL}/api/calendar/{event_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Calendar event deleted")


# ============== SHOPPING LIST CRUD TESTS ==============
class TestShoppingCRUD(TestSetup):
    """Shopping list module CRUD tests"""
    
    def test_create_shopping_item(self, auth_setup):
        """Test creating shopping item with category"""
        headers = auth_setup["headers"]
        item_data = {
            "name": "TEST_Milk",
            "quantity": "2",
            "category": "Dairy"
        }
        response = requests.post(f"{BASE_URL}/api/shopping", json=item_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Milk"
        assert data["category"] == "Dairy"
        print(f"✓ Shopping item created: {data['id']}")
    
    def test_get_all_shopping_items(self, auth_setup):
        """Test getting all shopping items"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/shopping", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Shopping items retrieved: {len(data)} items")
    
    def test_update_shopping_item_check(self, auth_setup):
        """Test checking/unchecking shopping item"""
        headers = auth_setup["headers"]
        # Create item
        create_resp = requests.post(f"{BASE_URL}/api/shopping", json={
            "name": "TEST_Bread",
            "quantity": "1"
        }, headers=headers)
        item_id = create_resp.json()["id"]
        
        # Check item
        update_resp = requests.put(f"{BASE_URL}/api/shopping/{item_id}", json={
            "id": item_id,
            "name": "TEST_Bread",
            "quantity": "1",
            "checked": True
        }, headers=headers)
        assert update_resp.status_code == 200
        assert update_resp.json()["checked"] == True
        print("✓ Shopping item checked")
    
    def test_delete_shopping_item(self, auth_setup):
        """Test deleting shopping item"""
        headers = auth_setup["headers"]
        # Create item
        create_resp = requests.post(f"{BASE_URL}/api/shopping", json={
            "name": "TEST_Delete Item"
        }, headers=headers)
        item_id = create_resp.json()["id"]
        
        # Delete item
        delete_resp = requests.delete(f"{BASE_URL}/api/shopping/{item_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Shopping item deleted")
    
    def test_clear_checked_items(self, auth_setup):
        """Test clearing checked items"""
        headers = auth_setup["headers"]
        # Create and check item
        create_resp = requests.post(f"{BASE_URL}/api/shopping", json={
            "name": "TEST_Clear Item"
        }, headers=headers)
        item_id = create_resp.json()["id"]
        
        requests.put(f"{BASE_URL}/api/shopping/{item_id}", json={
            "id": item_id,
            "name": "TEST_Clear Item",
            "checked": True
        }, headers=headers)
        
        # Clear checked
        clear_resp = requests.delete(f"{BASE_URL}/api/shopping", headers=headers)
        assert clear_resp.status_code == 200
        print("✓ Checked shopping items cleared")


# ============== TASKS CRUD TESTS ==============
class TestTasksCRUD(TestSetup):
    """Tasks module CRUD tests"""
    
    def test_create_task_with_assignment(self, auth_setup):
        """Test creating task with assignment"""
        headers = auth_setup["headers"]
        task_data = {
            "title": "TEST_Complete Report",
            "description": "Finish the quarterly report",
            "assigned_to": auth_setup["user_id"],
            "due_date": "2025-02-28",
            "priority": "high"
        }
        response = requests.post(f"{BASE_URL}/api/tasks", json=task_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Complete Report"
        assert data["assigned_to"] == auth_setup["user_id"]
        assert data["priority"] == "high"
        print(f"✓ Task created with assignment: {data['id']}")
    
    def test_get_all_tasks(self, auth_setup):
        """Test getting all tasks"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Tasks retrieved: {len(data)} tasks")
    
    def test_update_task(self, auth_setup):
        """Test updating task"""
        headers = auth_setup["headers"]
        # Create task
        create_resp = requests.post(f"{BASE_URL}/api/tasks", json={
            "title": "TEST_Update Task",
            "priority": "low"
        }, headers=headers)
        task_id = create_resp.json()["id"]
        
        # Update task
        update_resp = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json={
            "id": task_id,
            "title": "TEST_Updated Task",
            "priority": "high",
            "completed": True
        }, headers=headers)
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["title"] == "TEST_Updated Task"
        assert data["completed"] == True
        print("✓ Task updated")
    
    def test_delete_task(self, auth_setup):
        """Test deleting task"""
        headers = auth_setup["headers"]
        # Create task
        create_resp = requests.post(f"{BASE_URL}/api/tasks", json={
            "title": "TEST_Delete Task"
        }, headers=headers)
        task_id = create_resp.json()["id"]
        
        # Delete task
        delete_resp = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Task deleted")


# ============== CHORES & REWARDS CRUD TESTS ==============
class TestChoresCRUD(TestSetup):
    """Chores module CRUD tests"""
    
    def test_create_chore_with_difficulty(self, auth_setup):
        """Test creating chore with difficulty-based points"""
        headers = auth_setup["headers"]
        chore_data = {
            "title": "TEST_Clean Kitchen",
            "description": "Deep clean the kitchen",
            "difficulty": "hard",
            "assigned_to": auth_setup["user_id"]
        }
        response = requests.post(f"{BASE_URL}/api/chores", json=chore_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Clean Kitchen"
        assert data["difficulty"] == "hard"
        assert data["points"] == 20  # Hard = 20 points
        print(f"✓ Chore created with {data['points']} points")
    
    def test_get_all_chores(self, auth_setup):
        """Test getting all chores"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/chores", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Chores retrieved: {len(data)} chores")
    
    def test_complete_chore_awards_points(self, auth_setup):
        """Test completing chore awards points"""
        headers = auth_setup["headers"]
        # Create chore
        create_resp = requests.post(f"{BASE_URL}/api/chores", json={
            "title": "TEST_Complete Chore",
            "difficulty": "easy",
            "assigned_to": auth_setup["user_id"]
        }, headers=headers)
        chore_id = create_resp.json()["id"]
        
        # Complete chore
        complete_resp = requests.post(f"{BASE_URL}/api/chores/{chore_id}/complete", headers=headers)
        assert complete_resp.status_code == 200
        data = complete_resp.json()
        assert "points_earned" in data
        assert data["points_earned"] == 5  # Easy = 5 points
        print(f"✓ Chore completed, earned {data['points_earned']} points")
    
    def test_delete_chore(self, auth_setup):
        """Test deleting chore"""
        headers = auth_setup["headers"]
        # Create chore
        create_resp = requests.post(f"{BASE_URL}/api/chores", json={
            "title": "TEST_Delete Chore",
            "difficulty": "medium"
        }, headers=headers)
        chore_id = create_resp.json()["id"]
        
        # Delete chore
        delete_resp = requests.delete(f"{BASE_URL}/api/chores/{chore_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Chore deleted")


class TestRewardsCRUD(TestSetup):
    """Rewards module CRUD tests"""
    
    def test_create_reward(self, auth_setup):
        """Test creating reward (owner/parent only)"""
        headers = auth_setup["headers"]
        reward_data = {
            "name": "TEST_Extra Screen Time",
            "description": "30 minutes extra screen time",
            "points_required": 50
        }
        response = requests.post(f"{BASE_URL}/api/rewards", json=reward_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Extra Screen Time"
        assert data["points_required"] == 50
        print(f"✓ Reward created: {data['id']}")
    
    def test_get_rewards(self, auth_setup):
        """Test getting all rewards"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/rewards", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Rewards retrieved: {len(data)} rewards")
    
    def test_get_leaderboard(self, auth_setup):
        """Test getting family leaderboard"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/leaderboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Leaderboard retrieved: {len(data)} members")
    
    def test_delete_reward(self, auth_setup):
        """Test deleting reward (owner/parent only)"""
        headers = auth_setup["headers"]
        # Create reward
        create_resp = requests.post(f"{BASE_URL}/api/rewards", json={
            "name": "TEST_Delete Reward",
            "points_required": 10
        }, headers=headers)
        reward_id = create_resp.json()["id"]
        
        # Delete reward
        delete_resp = requests.delete(f"{BASE_URL}/api/rewards/{reward_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Reward deleted")


# ============== NOTES CRUD TESTS ==============
class TestNotesCRUD(TestSetup):
    """Notes module CRUD tests"""
    
    def test_create_note_with_color(self, auth_setup):
        """Test creating note with color"""
        headers = auth_setup["headers"]
        note_data = {
            "title": "TEST_Shopping List",
            "content": "Remember to buy groceries",
            "color": "#F2CC8F"
        }
        response = requests.post(f"{BASE_URL}/api/notes", json=note_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Shopping List"
        assert data["color"] == "#F2CC8F"
        print(f"✓ Note created: {data['id']}")
    
    def test_get_all_notes(self, auth_setup):
        """Test getting all notes"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/notes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Notes retrieved: {len(data)} notes")
    
    def test_update_note(self, auth_setup):
        """Test updating note"""
        headers = auth_setup["headers"]
        # Create note
        create_resp = requests.post(f"{BASE_URL}/api/notes", json={
            "title": "TEST_Update Note",
            "content": "Original content"
        }, headers=headers)
        note_id = create_resp.json()["id"]
        
        # Update note
        update_resp = requests.put(f"{BASE_URL}/api/notes/{note_id}", json={
            "id": note_id,
            "title": "TEST_Updated Note",
            "content": "Updated content",
            "color": "#81B29A"
        }, headers=headers)
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["title"] == "TEST_Updated Note"
        print("✓ Note updated")
    
    def test_delete_note(self, auth_setup):
        """Test deleting note"""
        headers = auth_setup["headers"]
        # Create note
        create_resp = requests.post(f"{BASE_URL}/api/notes", json={
            "title": "TEST_Delete Note",
            "content": "To be deleted"
        }, headers=headers)
        note_id = create_resp.json()["id"]
        
        # Delete note
        delete_resp = requests.delete(f"{BASE_URL}/api/notes/{note_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Note deleted")


# ============== BUDGET CRUD TESTS ==============
class TestBudgetCRUD(TestSetup):
    """Budget module CRUD tests"""
    
    def test_create_income_entry(self, auth_setup):
        """Test creating income entry"""
        headers = auth_setup["headers"]
        entry_data = {
            "description": "TEST_Salary",
            "amount": 5000.00,
            "category": "Salary",
            "type": "income",
            "date": "2025-02-01"
        }
        response = requests.post(f"{BASE_URL}/api/budget", json=entry_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "TEST_Salary"
        assert data["type"] == "income"
        assert data["amount"] == 5000.00
        print(f"✓ Income entry created: {data['id']}")
    
    def test_create_expense_entry(self, auth_setup):
        """Test creating expense entry"""
        headers = auth_setup["headers"]
        entry_data = {
            "description": "TEST_Groceries",
            "amount": 150.50,
            "category": "Groceries",
            "type": "expense",
            "date": "2025-02-05"
        }
        response = requests.post(f"{BASE_URL}/api/budget", json=entry_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "expense"
        print(f"✓ Expense entry created: {data['id']}")
    
    def test_get_all_budget_entries(self, auth_setup):
        """Test getting all budget entries"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/budget", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Budget entries retrieved: {len(data)} entries")
    
    def test_get_budget_summary(self, auth_setup):
        """Test getting budget summary with totals"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/budget/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expenses" in data
        assert "balance" in data
        assert "by_category" in data
        assert "by_month" in data
        print(f"✓ Budget summary: Income=${data['total_income']}, Expenses=${data['total_expenses']}, Balance=${data['balance']}")
    
    def test_update_budget_entry(self, auth_setup):
        """Test updating budget entry"""
        headers = auth_setup["headers"]
        # Create entry
        create_resp = requests.post(f"{BASE_URL}/api/budget", json={
            "description": "TEST_Update Entry",
            "amount": 100,
            "category": "Other",
            "type": "expense",
            "date": "2025-02-10"
        }, headers=headers)
        entry_id = create_resp.json()["id"]
        
        # Update entry
        update_resp = requests.put(f"{BASE_URL}/api/budget/{entry_id}", json={
            "id": entry_id,
            "description": "TEST_Updated Entry",
            "amount": 200,
            "category": "Shopping",
            "type": "expense",
            "date": "2025-02-11"
        }, headers=headers)
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["amount"] == 200
        print("✓ Budget entry updated")
    
    def test_delete_budget_entry(self, auth_setup):
        """Test deleting budget entry"""
        headers = auth_setup["headers"]
        # Create entry
        create_resp = requests.post(f"{BASE_URL}/api/budget", json={
            "description": "TEST_Delete Entry",
            "amount": 50,
            "category": "Other",
            "type": "expense",
            "date": "2025-02-15"
        }, headers=headers)
        entry_id = create_resp.json()["id"]
        
        # Delete entry
        delete_resp = requests.delete(f"{BASE_URL}/api/budget/{entry_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Budget entry deleted")


# ============== MEAL PLANNER CRUD TESTS ==============
class TestMealPlannerCRUD(TestSetup):
    """Meal planner module CRUD tests"""
    
    def test_create_meal_plan(self, auth_setup):
        """Test creating meal plan"""
        headers = auth_setup["headers"]
        meal_data = {
            "date": "2025-02-15",
            "meal_type": "dinner",
            "recipe_name": "TEST_Spaghetti Bolognese",
            "notes": "Family favorite"
        }
        response = requests.post(f"{BASE_URL}/api/meals", json=meal_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["recipe_name"] == "TEST_Spaghetti Bolognese"
        assert data["meal_type"] == "dinner"
        print(f"✓ Meal plan created: {data['id']}")
    
    def test_get_all_meal_plans(self, auth_setup):
        """Test getting all meal plans"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/meals", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Meal plans retrieved: {len(data)} plans")
    
    def test_update_meal_plan(self, auth_setup):
        """Test updating meal plan"""
        headers = auth_setup["headers"]
        # Create meal plan
        create_resp = requests.post(f"{BASE_URL}/api/meals", json={
            "date": "2025-02-16",
            "meal_type": "lunch",
            "recipe_name": "TEST_Update Meal"
        }, headers=headers)
        plan_id = create_resp.json()["id"]
        
        # Update meal plan
        update_resp = requests.put(f"{BASE_URL}/api/meals/{plan_id}", json={
            "id": plan_id,
            "date": "2025-02-17",
            "meal_type": "breakfast",
            "recipe_name": "TEST_Updated Meal"
        }, headers=headers)
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["meal_type"] == "breakfast"
        print("✓ Meal plan updated")
    
    def test_delete_meal_plan(self, auth_setup):
        """Test deleting meal plan"""
        headers = auth_setup["headers"]
        # Create meal plan
        create_resp = requests.post(f"{BASE_URL}/api/meals", json={
            "date": "2025-02-18",
            "meal_type": "dinner",
            "recipe_name": "TEST_Delete Meal"
        }, headers=headers)
        plan_id = create_resp.json()["id"]
        
        # Delete meal plan
        delete_resp = requests.delete(f"{BASE_URL}/api/meals/{plan_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Meal plan deleted")


# ============== RECIPES CRUD TESTS ==============
class TestRecipesCRUD(TestSetup):
    """Recipes module CRUD tests"""
    
    def test_create_recipe_with_ingredients(self, auth_setup):
        """Test creating recipe with ingredients and instructions"""
        headers = auth_setup["headers"]
        recipe_data = {
            "name": "TEST_Chocolate Cake",
            "description": "Delicious chocolate cake",
            "ingredients": ["2 cups flour", "1 cup sugar", "1/2 cup cocoa", "2 eggs"],
            "instructions": ["Mix dry ingredients", "Add eggs", "Bake at 350F for 30 min"],
            "prep_time": "15 min",
            "cook_time": "30 min",
            "servings": 8,
            "category": "Dessert"
        }
        response = requests.post(f"{BASE_URL}/api/recipes", json=recipe_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Chocolate Cake"
        assert len(data["ingredients"]) == 4
        assert len(data["instructions"]) == 3
        print(f"✓ Recipe created: {data['id']}")
        return data["id"]
    
    def test_get_all_recipes(self, auth_setup):
        """Test getting all recipes"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/recipes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Recipes retrieved: {len(data)} recipes")
    
    def test_get_single_recipe(self, auth_setup):
        """Test getting single recipe by ID"""
        headers = auth_setup["headers"]
        # Create recipe first
        create_resp = requests.post(f"{BASE_URL}/api/recipes", json={
            "name": "TEST_Single Recipe",
            "ingredients": ["ingredient1"],
            "instructions": ["step1"]
        }, headers=headers)
        recipe_id = create_resp.json()["id"]
        
        # Get single recipe
        get_resp = requests.get(f"{BASE_URL}/api/recipes/{recipe_id}", headers=headers)
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["name"] == "TEST_Single Recipe"
        print("✓ Single recipe retrieved")
    
    def test_update_recipe(self, auth_setup):
        """Test updating recipe"""
        headers = auth_setup["headers"]
        # Create recipe
        create_resp = requests.post(f"{BASE_URL}/api/recipes", json={
            "name": "TEST_Update Recipe",
            "ingredients": ["old ingredient"],
            "instructions": ["old step"]
        }, headers=headers)
        recipe_id = create_resp.json()["id"]
        
        # Update recipe
        update_resp = requests.put(f"{BASE_URL}/api/recipes/{recipe_id}", json={
            "id": recipe_id,
            "name": "TEST_Updated Recipe",
            "ingredients": ["new ingredient 1", "new ingredient 2"],
            "instructions": ["new step 1", "new step 2"]
        }, headers=headers)
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["name"] == "TEST_Updated Recipe"
        assert len(data["ingredients"]) == 2
        print("✓ Recipe updated")
    
    def test_delete_recipe(self, auth_setup):
        """Test deleting recipe"""
        headers = auth_setup["headers"]
        # Create recipe
        create_resp = requests.post(f"{BASE_URL}/api/recipes", json={
            "name": "TEST_Delete Recipe",
            "ingredients": ["ingredient"],
            "instructions": ["step"]
        }, headers=headers)
        recipe_id = create_resp.json()["id"]
        
        # Delete recipe
        delete_resp = requests.delete(f"{BASE_URL}/api/recipes/{recipe_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Recipe deleted")


# ============== GROCERY LIST CRUD TESTS ==============
class TestGroceryCRUD(TestSetup):
    """Grocery list module CRUD tests"""
    
    def test_create_grocery_item(self, auth_setup):
        """Test creating grocery item"""
        headers = auth_setup["headers"]
        item_data = {
            "name": "TEST_Apples",
            "quantity": "6"
        }
        response = requests.post(f"{BASE_URL}/api/grocery", json=item_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Apples"
        print(f"✓ Grocery item created: {data['id']}")
    
    def test_get_all_grocery_items(self, auth_setup):
        """Test getting all grocery items"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/grocery", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Grocery items retrieved: {len(data)} items")
    
    def test_update_grocery_item(self, auth_setup):
        """Test updating grocery item"""
        headers = auth_setup["headers"]
        # Create item
        create_resp = requests.post(f"{BASE_URL}/api/grocery", json={
            "name": "TEST_Update Grocery"
        }, headers=headers)
        item_id = create_resp.json()["id"]
        
        # Update item
        update_resp = requests.put(f"{BASE_URL}/api/grocery/{item_id}", json={
            "id": item_id,
            "name": "TEST_Updated Grocery",
            "quantity": "10",
            "checked": True
        }, headers=headers)
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["checked"] == True
        print("✓ Grocery item updated")
    
    def test_delete_grocery_item(self, auth_setup):
        """Test deleting grocery item"""
        headers = auth_setup["headers"]
        # Create item
        create_resp = requests.post(f"{BASE_URL}/api/grocery", json={
            "name": "TEST_Delete Grocery"
        }, headers=headers)
        item_id = create_resp.json()["id"]
        
        # Delete item
        delete_resp = requests.delete(f"{BASE_URL}/api/grocery/{item_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Grocery item deleted")
    
    def test_clear_checked_grocery_items(self, auth_setup):
        """Test clearing checked grocery items"""
        headers = auth_setup["headers"]
        # Create and check item
        create_resp = requests.post(f"{BASE_URL}/api/grocery", json={
            "name": "TEST_Clear Grocery"
        }, headers=headers)
        item_id = create_resp.json()["id"]
        
        requests.put(f"{BASE_URL}/api/grocery/{item_id}", json={
            "id": item_id,
            "name": "TEST_Clear Grocery",
            "checked": True
        }, headers=headers)
        
        # Clear checked
        clear_resp = requests.delete(f"{BASE_URL}/api/grocery", headers=headers)
        assert clear_resp.status_code == 200
        print("✓ Checked grocery items cleared")


# ============== CONTACTS CRUD TESTS ==============
class TestContactsCRUD(TestSetup):
    """Contacts module CRUD tests"""
    
    def test_create_contact(self, auth_setup):
        """Test creating contact"""
        headers = auth_setup["headers"]
        contact_data = {
            "name": "TEST_Dr. Smith",
            "relationship": "Family Doctor",
            "phone": "555-1234",
            "email": "dr.smith@example.com",
            "address": "123 Medical Center",
            "notes": "Pediatrician"
        }
        response = requests.post(f"{BASE_URL}/api/contacts", json=contact_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Dr. Smith"
        assert data["relationship"] == "Family Doctor"
        print(f"✓ Contact created: {data['id']}")
    
    def test_get_all_contacts(self, auth_setup):
        """Test getting all contacts"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/contacts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Contacts retrieved: {len(data)} contacts")
    
    def test_update_contact(self, auth_setup):
        """Test updating contact"""
        headers = auth_setup["headers"]
        # Create contact
        create_resp = requests.post(f"{BASE_URL}/api/contacts", json={
            "name": "TEST_Update Contact",
            "phone": "555-0000"
        }, headers=headers)
        contact_id = create_resp.json()["id"]
        
        # Update contact
        update_resp = requests.put(f"{BASE_URL}/api/contacts/{contact_id}", json={
            "id": contact_id,
            "name": "TEST_Updated Contact",
            "phone": "555-9999",
            "email": "updated@example.com"
        }, headers=headers)
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["phone"] == "555-9999"
        print("✓ Contact updated")
    
    def test_delete_contact(self, auth_setup):
        """Test deleting contact"""
        headers = auth_setup["headers"]
        # Create contact
        create_resp = requests.post(f"{BASE_URL}/api/contacts", json={
            "name": "TEST_Delete Contact"
        }, headers=headers)
        contact_id = create_resp.json()["id"]
        
        # Delete contact
        delete_resp = requests.delete(f"{BASE_URL}/api/contacts/{contact_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Contact deleted")


# ============== PANTRY CRUD TESTS ==============
class TestPantryCRUD(TestSetup):
    """Pantry module CRUD tests"""
    
    def test_create_pantry_item(self, auth_setup):
        """Test creating pantry item"""
        headers = auth_setup["headers"]
        item_data = {
            "name": "TEST_Rice",
            "quantity": 2,
            "unit": "kg",
            "category": "Grains",
            "expiry_date": "2025-12-31"
        }
        response = requests.post(f"{BASE_URL}/api/pantry", json=item_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Rice"
        assert data["category"] == "Grains"
        print(f"✓ Pantry item created: {data['id']}")
    
    def test_get_all_pantry_items(self, auth_setup):
        """Test getting all pantry items"""
        headers = auth_setup["headers"]
        response = requests.get(f"{BASE_URL}/api/pantry", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Pantry items retrieved: {len(data)} items")
    
    def test_update_pantry_item(self, auth_setup):
        """Test updating pantry item"""
        headers = auth_setup["headers"]
        # Create item
        create_resp = requests.post(f"{BASE_URL}/api/pantry", json={
            "name": "TEST_Update Pantry",
            "quantity": 1
        }, headers=headers)
        item_id = create_resp.json()["id"]
        
        # Update item
        update_resp = requests.put(f"{BASE_URL}/api/pantry/{item_id}", json={
            "id": item_id,
            "name": "TEST_Updated Pantry",
            "quantity": 5,
            "unit": "pcs"
        }, headers=headers)
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["quantity"] == 5
        print("✓ Pantry item updated")
    
    def test_delete_pantry_item(self, auth_setup):
        """Test deleting pantry item"""
        headers = auth_setup["headers"]
        # Create item
        create_resp = requests.post(f"{BASE_URL}/api/pantry", json={
            "name": "TEST_Delete Pantry",
            "quantity": 1
        }, headers=headers)
        item_id = create_resp.json()["id"]
        
        # Delete item
        delete_resp = requests.delete(f"{BASE_URL}/api/pantry/{item_id}", headers=headers)
        assert delete_resp.status_code == 200
        print("✓ Pantry item deleted")
    
    def test_barcode_lookup(self, auth_setup):
        """Test barcode lookup API"""
        headers = auth_setup["headers"]
        # Test with a known barcode (Coca-Cola)
        response = requests.get(f"{BASE_URL}/api/pantry/barcode/5449000000996", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "found" in data
        print(f"✓ Barcode lookup: found={data['found']}")


# ============== MEAL SUGGESTIONS TESTS ==============
class TestMealSuggestions(TestSetup):
    """Meal suggestions based on pantry"""
    
    def test_get_meal_suggestions(self, auth_setup):
        """Test getting meal suggestions based on pantry items"""
        headers = auth_setup["headers"]
        
        # Add some pantry items
        requests.post(f"{BASE_URL}/api/pantry", json={
            "name": "TEST_Pasta",
            "quantity": 1
        }, headers=headers)
        
        # Add a recipe with matching ingredient
        requests.post(f"{BASE_URL}/api/recipes", json={
            "name": "TEST_Pasta Dish",
            "ingredients": ["pasta", "tomato sauce"],
            "instructions": ["Cook pasta", "Add sauce"]
        }, headers=headers)
        
        # Get suggestions
        response = requests.get(f"{BASE_URL}/api/suggestions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Meal suggestions retrieved: {len(data)} suggestions")


# ============== MEMBER MANAGEMENT TESTS ==============
class TestMemberManagement(TestSetup):
    """Family member management tests"""
    
    def test_change_member_role(self, auth_setup):
        """Test changing member role (owner/parent only)"""
        headers = auth_setup["headers"]
        
        # Add a member
        add_resp = requests.post(f"{BASE_URL}/api/family/add-member", json={
            "name": "TEST_Role Change Member",
            "role": "child"
        }, headers=headers)
        member_id = add_resp.json()["user_id"]
        
        # Change role to member
        change_resp = requests.put(f"{BASE_URL}/api/family/members/{member_id}/role", json={
            "role": "member"
        }, headers=headers)
        assert change_resp.status_code == 200
        print("✓ Member role changed")
    
    def test_cannot_change_owner_role(self, auth_setup):
        """Test that owner role cannot be changed"""
        headers = auth_setup["headers"]
        owner_id = auth_setup["user_id"]
        
        # Try to change owner role
        change_resp = requests.put(f"{BASE_URL}/api/family/members/{owner_id}/role", json={
            "role": "member"
        }, headers=headers)
        # Should fail - can't change owner role
        assert change_resp.status_code in [403, 400], f"Should not be able to change owner role: {change_resp.text}"
        print("✓ Owner role cannot be changed")
    
    def test_remove_member(self, auth_setup):
        """Test removing family member"""
        headers = auth_setup["headers"]
        
        # Add a member
        add_resp = requests.post(f"{BASE_URL}/api/family/add-member", json={
            "name": "TEST_Remove Member",
            "role": "child"
        }, headers=headers)
        member_id = add_resp.json()["user_id"]
        
        # Remove member
        remove_resp = requests.delete(f"{BASE_URL}/api/family/members/{member_id}", headers=headers)
        assert remove_resp.status_code == 200
        print("✓ Member removed")
    
    def test_cannot_remove_owner(self, auth_setup):
        """Test that owner cannot be removed"""
        headers = auth_setup["headers"]
        owner_id = auth_setup["user_id"]
        
        # Try to remove owner
        remove_resp = requests.delete(f"{BASE_URL}/api/family/members/{owner_id}", headers=headers)
        assert remove_resp.status_code == 403, f"Should not be able to remove owner: {remove_resp.text}"
        print("✓ Owner cannot be removed")
    
    def test_regenerate_user_pin(self, auth_setup):
        """Test regenerating user PIN"""
        headers = auth_setup["headers"]
        
        # Add a member
        add_resp = requests.post(f"{BASE_URL}/api/family/add-member", json={
            "name": "TEST_Regen PIN Member",
            "role": "child"
        }, headers=headers)
        member_id = add_resp.json()["user_id"]
        old_pin = add_resp.json()["user_pin"]
        
        # Regenerate PIN
        regen_resp = requests.post(f"{BASE_URL}/api/family/members/{member_id}/regenerate-pin", headers=headers)
        assert regen_resp.status_code == 200
        new_pin = regen_resp.json()["pin"]
        assert new_pin != old_pin
        assert len(new_pin) == 4
        print(f"✓ User PIN regenerated: {old_pin} -> {new_pin}")


# ============== REGISTRATION WITH FAMILY TESTS ==============
class TestRegistrationWithFamily:
    """Test registration flow that creates family"""
    
    def test_register_with_family_name_creates_owner(self):
        """Test that registering with family_name creates family and makes user owner"""
        user_email = f"reg_family_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "New Family Owner",
            "email": user_email,
            "password": TEST_PASSWORD,
            "family_name": "New Test Family"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Should have user, token, user_pin, and family_pin
        assert "user" in data
        assert "token" in data
        assert "user_pin" in data
        assert "family_pin" in data
        
        # User should be owner
        assert data["user"]["role"] == "owner"
        
        # Family PIN should be 6 digits
        assert len(data["family_pin"]) == 6
        
        # User PIN should be 4 digits
        assert len(data["user_pin"]) == 4
        
        print(f"✓ Registration with family creates owner - Family PIN: {data['family_pin']}, User PIN: {data['user_pin']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
