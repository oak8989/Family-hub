from fastapi import APIRouter, Depends
from typing import List
from models.schemas import GroceryItem
from auth import get_current_user
from database import db

router = APIRouter(prefix="/api/grocery", tags=["grocery"])


@router.get("", response_model=List[GroceryItem])
async def get_grocery_items(user: dict = Depends(get_current_user)):
    items = await db.grocery_items.find({"family_id": user["family_id"]}, {"_id": 0}).to_list(1000)
    for i in items:
        i.pop("family_id", None)
    return items


@router.post("", response_model=GroceryItem)
async def create_grocery_item(item: GroceryItem, user: dict = Depends(get_current_user)):
    item_doc = item.model_dump()
    item_doc["family_id"] = user["family_id"]
    await db.grocery_items.insert_one(item_doc)
    del item_doc["_id"]
    del item_doc["family_id"]
    return item_doc


@router.put("/{item_id}")
async def update_grocery_item(item_id: str, item: GroceryItem, user: dict = Depends(get_current_user)):
    item_doc = item.model_dump()
    await db.grocery_items.update_one({"id": item_id, "family_id": user["family_id"]}, {"$set": item_doc})
    return item_doc


@router.delete("/{item_id}")
async def delete_grocery_item(item_id: str, user: dict = Depends(get_current_user)):
    await db.grocery_items.delete_one({"id": item_id, "family_id": user["family_id"]})
    return {"message": "Item deleted"}


@router.delete("")
async def clear_grocery_list(user: dict = Depends(get_current_user)):
    await db.grocery_items.delete_many({"family_id": user["family_id"], "checked": True})
    return {"message": "Checked items cleared"}


@router.post("/add-from-meal/{plan_id}")
async def add_meal_ingredients_to_grocery(plan_id: str, user: dict = Depends(get_current_user)):
    """Add missing meal ingredients to grocery list (checks pantry first)."""
    import uuid as _uuid
    meal = await db.meal_plans.find_one({"id": plan_id, "family_id": user["family_id"]}, {"_id": 0})
    if not meal:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Meal plan not found")

    recipe = None
    if meal.get("recipe_id"):
        recipe = await db.recipes.find_one({"id": meal["recipe_id"]}, {"_id": 0})
    if not recipe:
        recipe = await db.recipes.find_one({"name": meal.get("recipe_name"), "family_id": user["family_id"]}, {"_id": 0})
    if not recipe or not recipe.get("ingredients"):
        return {"added": 0, "message": "No recipe ingredients found for this meal"}

    pantry_items = await db.pantry_items.find({"family_id": user["family_id"]}, {"_id": 0, "name": 1}).to_list(1000)
    pantry_names = {p["name"].lower().strip() for p in pantry_items}

    existing_grocery = await db.grocery_items.find({"family_id": user["family_id"]}, {"_id": 0, "name": 1}).to_list(1000)
    grocery_names = {g["name"].lower().strip() for g in existing_grocery}

    added = 0
    for ingredient in recipe["ingredients"]:
        ingredient_lower = ingredient.lower().strip()
        in_pantry = any(pn in ingredient_lower or ingredient_lower in pn for pn in pantry_names)
        in_grocery = any(gn in ingredient_lower or ingredient_lower in gn for gn in grocery_names)

        if not in_pantry and not in_grocery:
            item = {"id": str(_uuid.uuid4()), "name": ingredient, "quantity": "1", "checked": False, "family_id": user["family_id"]}
            await db.grocery_items.insert_one(item)
            added += 1

    return {"added": added, "message": f"Added {added} items to grocery list"}
