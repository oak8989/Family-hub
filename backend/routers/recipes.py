from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.schemas import Recipe
from auth import get_current_user
from database import db

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("", response_model=List[Recipe])
async def get_recipes(user: dict = Depends(get_current_user)):
    recipes = await db.recipes.find({"family_id": user["family_id"]}, {"_id": 0}).to_list(1000)
    for r in recipes:
        r.pop("family_id", None)
    return recipes


@router.post("", response_model=Recipe)
async def create_recipe(recipe: Recipe, user: dict = Depends(get_current_user)):
    recipe_doc = recipe.model_dump()
    recipe_doc["family_id"] = user["family_id"]
    recipe_doc["created_by"] = user["user_id"]
    await db.recipes.insert_one(recipe_doc)
    del recipe_doc["_id"]
    del recipe_doc["family_id"]
    return recipe_doc


@router.get("/{recipe_id}")
async def get_recipe(recipe_id: str, user: dict = Depends(get_current_user)):
    recipe = await db.recipes.find_one({"id": recipe_id, "family_id": user["family_id"]}, {"_id": 0})
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put("/{recipe_id}")
async def update_recipe(recipe_id: str, recipe: Recipe, user: dict = Depends(get_current_user)):
    recipe_doc = recipe.model_dump()
    await db.recipes.update_one({"id": recipe_id, "family_id": user["family_id"]}, {"$set": recipe_doc})
    return recipe_doc


@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id: str, user: dict = Depends(get_current_user)):
    await db.recipes.delete_one({"id": recipe_id, "family_id": user["family_id"]})
    return {"message": "Recipe deleted"}
