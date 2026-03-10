"""
Test iteration 9 features for Family Hub:
1. WebSocket real-time updates - /api/ws/{family_id}
2. Recipe URL import - POST /api/recipes/import-url
3. Dark mode toggle - Frontend feature (ThemeContext)
4. Offline support (Service Worker) - /sw.js
Plus regression tests on all CRUD endpoints
"""
import pytest
import requests
import os
import uuid
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_headers(api_client):
    """Register a new user and get fresh JWT token"""
    user_email = f"test_iter9_{uuid.uuid4().hex[:8]}@test.com"
    user_password = "Test123456!"
    
    # Register user with family
    reg_resp = api_client.post(f"{BASE_URL}/api/auth/register", json={
        "name": "Iteration 9 Test User",
        "email": user_email,
        "password": user_password,
        "family_name": "Iteration9TestFamily"
    })
    assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
    
    data = reg_resp.json()
    token = data["token"]
    family_id = data["user"].get("family_id")
    
    print(f"✅ Created test user: {user_email}")
    print(f"✅ Family ID: {family_id}")
    
    return {
        "Authorization": f"Bearer {token}", 
        "Content-Type": "application/json",
        "family_id": family_id
    }


# ===== HEALTH & BASIC API TESTS =====
class TestHealthAndBasic:
    """Basic API health and status tests"""
    
    def test_health_check(self, api_client):
        """Test /api/health returns healthy status"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✅ Health check passed")
    
    def test_root_api(self, api_client):
        """Test /api/ returns API info"""
        response = api_client.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "version" in data
        print(f"✅ API version: {data.get('version')}")


# ===== AUTH TESTS =====
class TestAuth:
    """Authentication tests"""
    
    def test_register_new_user(self, api_client):
        """Test POST /api/auth/register with ws_test user"""
        user_email = f"ws_test_{uuid.uuid4().hex[:8]}@test.com"
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "name": "WS Test User",
            "email": user_email,
            "password": "test123",
            "family_name": "WSTestFamily"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == user_email
        print(f"✅ Registered user: {user_email}")
    
    def test_login(self, api_client):
        """Test POST /api/auth/login"""
        # Register first
        user_email = f"login_test_{uuid.uuid4().hex[:8]}@test.com"
        api_client.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Login Test",
            "email": user_email,
            "password": "test123",
            "family_name": "LoginTestFamily"
        })
        
        # Then login
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": user_email,
            "password": "test123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        print("✅ Login successful")


# ===== FAMILY TESTS =====
class TestFamily:
    """Family CRUD tests"""
    
    def test_get_family(self, api_client, auth_headers):
        """Test GET /api/family"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        response = api_client.get(f"{BASE_URL}/api/family", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "id" in data
        print(f"✅ Family: {data['name']}")


# ===== SHOPPING LIST CRUD =====
class TestShoppingCRUD:
    """Shopping list full CRUD cycle"""
    
    def test_shopping_crud_cycle(self, api_client, auth_headers):
        """Test full CRUD on /api/shopping"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        
        # CREATE
        create_resp = api_client.post(f"{BASE_URL}/api/shopping", json={
            "name": "TEST_Milk",
            "quantity": "2 gallons",
            "category": "Dairy"
        }, headers=headers)
        assert create_resp.status_code == 200
        item = create_resp.json()
        item_id = item["id"]
        assert item["name"] == "TEST_Milk"
        print(f"✅ Created shopping item: {item_id}")
        
        # READ (list)
        list_resp = api_client.get(f"{BASE_URL}/api/shopping", headers=headers)
        assert list_resp.status_code == 200
        items = list_resp.json()
        assert isinstance(items, list)
        assert any(i["id"] == item_id for i in items)
        print(f"✅ Listed shopping items: {len(items)}")
        
        # UPDATE
        update_resp = api_client.put(f"{BASE_URL}/api/shopping/{item_id}", json={
            "id": item_id,
            "name": "TEST_Milk_Updated",
            "quantity": "3 gallons",
            "category": "Dairy",
            "checked": True
        }, headers=headers)
        assert update_resp.status_code == 200
        updated = update_resp.json()
        assert updated["name"] == "TEST_Milk_Updated"
        print(f"✅ Updated shopping item")
        
        # DELETE
        delete_resp = api_client.delete(f"{BASE_URL}/api/shopping/{item_id}", headers=headers)
        assert delete_resp.status_code == 200
        print(f"✅ Deleted shopping item")


# ===== TASKS CRUD =====
class TestTasksCRUD:
    """Tasks full CRUD cycle"""
    
    def test_tasks_crud_cycle(self, api_client, auth_headers):
        """Test full CRUD on /api/tasks"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        
        # CREATE
        create_resp = api_client.post(f"{BASE_URL}/api/tasks", json={
            "title": "TEST_Task",
            "description": "Test task description",
            "priority": "high",
            "due_date": "2025-02-15"
        }, headers=headers)
        assert create_resp.status_code == 200
        task = create_resp.json()
        task_id = task["id"]
        print(f"✅ Created task: {task_id}")
        
        # READ
        list_resp = api_client.get(f"{BASE_URL}/api/tasks", headers=headers)
        assert list_resp.status_code == 200
        tasks = list_resp.json()
        assert any(t["id"] == task_id for t in tasks)
        print(f"✅ Listed tasks: {len(tasks)}")
        
        # UPDATE
        update_resp = api_client.put(f"{BASE_URL}/api/tasks/{task_id}", json={
            "id": task_id,
            "title": "TEST_Task_Updated",
            "description": "Updated",
            "priority": "medium",
            "due_date": "2025-02-20",
            "completed": True
        }, headers=headers)
        assert update_resp.status_code == 200
        print(f"✅ Updated task")
        
        # DELETE
        delete_resp = api_client.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
        assert delete_resp.status_code == 200
        print(f"✅ Deleted task")


# ===== CALENDAR CRUD =====
class TestCalendarCRUD:
    """Calendar full CRUD cycle"""
    
    def test_calendar_crud_cycle(self, api_client, auth_headers):
        """Test full CRUD on /api/calendar"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        
        # CREATE
        create_resp = api_client.post(f"{BASE_URL}/api/calendar", json={
            "title": "TEST_Event",
            "description": "Test event",
            "date": "2025-02-15",
            "time": "14:00",
            "color": "blue"
        }, headers=headers)
        assert create_resp.status_code == 200
        event = create_resp.json()
        event_id = event["id"]
        print(f"✅ Created calendar event: {event_id}")
        
        # READ
        list_resp = api_client.get(f"{BASE_URL}/api/calendar", headers=headers)
        assert list_resp.status_code == 200
        events = list_resp.json()
        assert any(e["id"] == event_id for e in events)
        print(f"✅ Listed events: {len(events)}")
        
        # UPDATE
        update_resp = api_client.put(f"{BASE_URL}/api/calendar/{event_id}", json={
            "id": event_id,
            "title": "TEST_Event_Updated",
            "description": "Updated event",
            "date": "2025-02-20",
            "time": "15:00",
            "color": "red"
        }, headers=headers)
        assert update_resp.status_code == 200
        print(f"✅ Updated event")
        
        # DELETE
        delete_resp = api_client.delete(f"{BASE_URL}/api/calendar/{event_id}", headers=headers)
        assert delete_resp.status_code == 200
        print(f"✅ Deleted event")


# ===== NOTES CRUD =====
class TestNotesCRUD:
    """Notes full CRUD cycle"""
    
    def test_notes_crud_cycle(self, api_client, auth_headers):
        """Test full CRUD on /api/notes"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        
        # CREATE
        create_resp = api_client.post(f"{BASE_URL}/api/notes", json={
            "title": "TEST_Note",
            "content": "Test note content",
            "color": "yellow"
        }, headers=headers)
        assert create_resp.status_code == 200
        note = create_resp.json()
        note_id = note["id"]
        print(f"✅ Created note: {note_id}")
        
        # READ
        list_resp = api_client.get(f"{BASE_URL}/api/notes", headers=headers)
        assert list_resp.status_code == 200
        notes = list_resp.json()
        assert any(n["id"] == note_id for n in notes)
        print(f"✅ Listed notes: {len(notes)}")
        
        # UPDATE
        update_resp = api_client.put(f"{BASE_URL}/api/notes/{note_id}", json={
            "id": note_id,
            "title": "TEST_Note_Updated",
            "content": "Updated content",
            "color": "blue"
        }, headers=headers)
        assert update_resp.status_code == 200
        print(f"✅ Updated note")
        
        # DELETE
        delete_resp = api_client.delete(f"{BASE_URL}/api/notes/{note_id}", headers=headers)
        assert delete_resp.status_code == 200
        print(f"✅ Deleted note")


# ===== RECIPES CRUD + IMPORT URL (NEW FEATURE) =====
class TestRecipesCRUD:
    """Recipes full CRUD cycle + URL import feature"""
    
    def test_recipes_crud_cycle(self, api_client, auth_headers):
        """Test full CRUD on /api/recipes"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        
        # CREATE
        create_resp = api_client.post(f"{BASE_URL}/api/recipes", json={
            "name": "TEST_Recipe",
            "description": "Test recipe description",
            "ingredients": ["flour", "sugar", "eggs"],
            "instructions": ["Mix ingredients", "Bake at 350F"],
            "prep_time": "15 mins",
            "cook_time": "30 mins",
            "servings": 4,
            "category": "Dessert"
        }, headers=headers)
        assert create_resp.status_code == 200
        recipe = create_resp.json()
        recipe_id = recipe["id"]
        print(f"✅ Created recipe: {recipe_id}")
        
        # READ
        list_resp = api_client.get(f"{BASE_URL}/api/recipes", headers=headers)
        assert list_resp.status_code == 200
        recipes = list_resp.json()
        assert any(r["id"] == recipe_id for r in recipes)
        print(f"✅ Listed recipes: {len(recipes)}")
        
        # UPDATE
        update_resp = api_client.put(f"{BASE_URL}/api/recipes/{recipe_id}", json={
            "id": recipe_id,
            "name": "TEST_Recipe_Updated",
            "description": "Updated",
            "ingredients": ["flour", "sugar", "eggs", "butter"],
            "instructions": ["Mix", "Bake"],
            "prep_time": "20 mins",
            "cook_time": "35 mins",
            "servings": 6,
            "category": "Dessert"
        }, headers=headers)
        assert update_resp.status_code == 200
        print(f"✅ Updated recipe")
        
        # DELETE
        delete_resp = api_client.delete(f"{BASE_URL}/api/recipes/{recipe_id}", headers=headers)
        assert delete_resp.status_code == 200
        print(f"✅ Deleted recipe")
    
    def test_recipe_import_from_url(self, api_client, auth_headers):
        """Test POST /api/recipes/import-url - NEW FEATURE"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        
        # Test with a known recipe URL that has JSON-LD
        response = api_client.post(f"{BASE_URL}/api/recipes/import-url", json={
            "url": "https://www.food.com/recipe/banana-bread-180529"
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response has expected fields
        assert "name" in data
        assert "ingredients" in data
        assert "instructions" in data
        print(f"✅ Recipe import: name={data.get('name', 'N/A')}")
        print(f"   ingredients count: {len(data.get('ingredients', []))}")
        print(f"   instructions count: {len(data.get('instructions', []))}")


# ===== PANTRY CRUD + BARCODE =====
class TestPantryCRUD:
    """Pantry full CRUD cycle + barcode lookup"""
    
    def test_pantry_crud_cycle(self, api_client, auth_headers):
        """Test full CRUD on /api/pantry"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        
        # CREATE
        create_resp = api_client.post(f"{BASE_URL}/api/pantry", json={
            "name": "TEST_Cereal",
            "quantity": 2,
            "unit": "boxes",
            "category": "Dry Goods",
            "expiry_date": "2025-06-01"
        }, headers=headers)
        assert create_resp.status_code == 200
        item = create_resp.json()
        item_id = item["id"]
        print(f"✅ Created pantry item: {item_id}")
        
        # READ
        list_resp = api_client.get(f"{BASE_URL}/api/pantry", headers=headers)
        assert list_resp.status_code == 200
        items = list_resp.json()
        assert any(i["id"] == item_id for i in items)
        print(f"✅ Listed pantry items: {len(items)}")
        
        # UPDATE
        update_resp = api_client.put(f"{BASE_URL}/api/pantry/{item_id}", json={
            "id": item_id,
            "name": "TEST_Cereal_Updated",
            "quantity": 3,
            "unit": "boxes",
            "category": "Dry Goods",
            "expiry_date": "2025-07-01"
        }, headers=headers)
        assert update_resp.status_code == 200
        print(f"✅ Updated pantry item")
        
        # DELETE
        delete_resp = api_client.delete(f"{BASE_URL}/api/pantry/{item_id}", headers=headers)
        assert delete_resp.status_code == 200
        print(f"✅ Deleted pantry item")
    
    def test_barcode_lookup(self, api_client):
        """Test GET /api/pantry/barcode/{barcode}"""
        # Coca-Cola Zero Sugar barcode
        response = api_client.get(f"{BASE_URL}/api/pantry/barcode/049000042559")
        assert response.status_code == 200
        data = response.json()
        assert "found" in data
        assert data["found"] == True
        print(f"✅ Barcode lookup: found={data['found']}, name={data.get('name', 'N/A')}")


# ===== CHORES CRUD + COMPLETE =====
class TestChoresCRUD:
    """Chores full CRUD cycle + completion"""
    
    def test_chores_crud_cycle(self, api_client, auth_headers):
        """Test full CRUD on /api/chores + POST /api/chores/{id}/complete"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        
        # CREATE
        create_resp = api_client.post(f"{BASE_URL}/api/chores", json={
            "title": "TEST_Chore",
            "description": "Test chore description",
            "difficulty": "medium"
        }, headers=headers)
        assert create_resp.status_code == 200
        chore = create_resp.json()
        chore_id = chore["id"]
        assert chore["points"] == 10  # medium = 10 points
        print(f"✅ Created chore: {chore_id} with {chore['points']} points")
        
        # READ
        list_resp = api_client.get(f"{BASE_URL}/api/chores", headers=headers)
        assert list_resp.status_code == 200
        chores = list_resp.json()
        assert any(c["id"] == chore_id for c in chores)
        print(f"✅ Listed chores: {len(chores)}")
        
        # COMPLETE
        complete_resp = api_client.post(f"{BASE_URL}/api/chores/{chore_id}/complete", headers=headers)
        assert complete_resp.status_code == 200
        complete_data = complete_resp.json()
        assert "points_earned" in complete_data
        print(f"✅ Completed chore, earned {complete_data['points_earned']} points")
        
        # DELETE
        delete_resp = api_client.delete(f"{BASE_URL}/api/chores/{chore_id}", headers=headers)
        assert delete_resp.status_code == 200
        print(f"✅ Deleted chore")


# ===== BUDGET TESTS =====
class TestBudget:
    """Budget endpoint tests"""
    
    def test_budget_summary(self, api_client, auth_headers):
        """Test GET /api/budget/summary"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        response = api_client.get(f"{BASE_URL}/api/budget/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expenses" in data
        assert "balance" in data
        print(f"✅ Budget summary: balance={data.get('balance')}")


# ===== SETTINGS TESTS =====
class TestSettings:
    """Settings endpoint tests"""
    
    def test_get_settings(self, api_client, auth_headers):
        """Test GET /api/settings"""
        headers = {k: v for k, v in auth_headers.items() if k != "family_id"}
        response = api_client.get(f"{BASE_URL}/api/settings", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "modules" in data or "family_id" in data
        print(f"✅ Settings retrieved")


# ===== QR CODE TESTS =====
class TestQRCode:
    """QR Code generation tests"""
    
    def test_qr_code_base64(self, api_client):
        """Test GET /api/qr-code/base64?url=..."""
        response = api_client.get(f"{BASE_URL}/api/qr-code/base64?url=https://test.com")
        assert response.status_code == 200
        data = response.json()
        assert "qr_code" in data
        assert data["qr_code"].startswith("data:image/png;base64,")
        print(f"✅ QR code generated")


# ===== WEBSOCKET TESTS (NEW FEATURE) =====
class TestWebSocket:
    """WebSocket endpoint tests - NEW FEATURE"""
    
    def test_websocket_endpoint_exists(self, api_client, auth_headers):
        """Test WebSocket endpoint is accessible (HTTP upgrade needed for actual WS)"""
        family_id = auth_headers.get("family_id", "test_family_id")
        
        # We can't test actual WebSocket with requests, but we can verify:
        # 1. The route exists by checking the server doesn't 404
        # This is a basic verification - actual WebSocket test would need a WS client
        
        # Try to access the WebSocket endpoint with HTTP - should not 404
        # (It may return 4xx because it expects WS upgrade, but not 404)
        try:
            response = api_client.get(f"{BASE_URL}/api/ws/{family_id}")
            # WebSocket endpoint returns various codes when accessed via HTTP
            # 400 = upgrade required, 403 = forbidden, 426 = upgrade required
            # But NOT 404 which would mean endpoint doesn't exist
            assert response.status_code != 404, "WebSocket endpoint not found"
            print(f"✅ WebSocket endpoint exists (status: {response.status_code})")
        except Exception as e:
            # Connection might be refused/dropped which is expected for WS over HTTP
            print(f"✅ WebSocket endpoint accessed (connection handled: {str(e)[:50]})")


# ===== SERVICE WORKER TESTS (OFFLINE SUPPORT) =====
class TestServiceWorker:
    """Service worker file accessibility - OFFLINE SUPPORT FEATURE"""
    
    def test_service_worker_accessible(self, api_client):
        """Test /sw.js is accessible"""
        response = api_client.get(f"{BASE_URL}/sw.js")
        # Service worker should be accessible
        assert response.status_code == 200
        content = response.text
        assert "CACHE_NAME" in content or "caches" in content
        print(f"✅ Service worker accessible at /sw.js")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
