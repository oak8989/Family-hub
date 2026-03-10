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
