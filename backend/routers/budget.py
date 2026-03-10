from fastapi import APIRouter, Depends
from typing import List
from models.schemas import BudgetEntry
from auth import get_current_user
from database import db

router = APIRouter(prefix="/api/budget", tags=["budget"])


@router.get("", response_model=List[BudgetEntry])
async def get_budget_entries(user: dict = Depends(get_current_user)):
    entries = await db.budget_entries.find({"family_id": user["family_id"]}, {"_id": 0}).to_list(1000)
    for e in entries:
        e.pop("family_id", None)
    return entries


@router.post("", response_model=BudgetEntry)
async def create_budget_entry(entry: BudgetEntry, user: dict = Depends(get_current_user)):
    entry_doc = entry.model_dump()
    entry_doc["family_id"] = user["family_id"]
    entry_doc["created_by"] = user["user_id"]
    await db.budget_entries.insert_one(entry_doc)
    del entry_doc["_id"]
    del entry_doc["family_id"]
    return entry_doc


@router.put("/{entry_id}")
async def update_budget_entry(entry_id: str, entry: BudgetEntry, user: dict = Depends(get_current_user)):
    entry_doc = entry.model_dump()
    await db.budget_entries.update_one({"id": entry_id, "family_id": user["family_id"]}, {"$set": entry_doc})
    return entry_doc


@router.delete("/{entry_id}")
async def delete_budget_entry(entry_id: str, user: dict = Depends(get_current_user)):
    await db.budget_entries.delete_one({"id": entry_id, "family_id": user["family_id"]})
    return {"message": "Entry deleted"}


@router.get("/summary")
async def get_budget_summary(user: dict = Depends(get_current_user)):
    entries = await db.budget_entries.find({"family_id": user["family_id"]}, {"_id": 0}).to_list(1000)
    total_income = sum(e["amount"] for e in entries if e["type"] == "income")
    total_expenses = sum(e["amount"] for e in entries if e["type"] == "expense")
    categories = {}
    monthly = {}
    for e in entries:
        cat = e.get("category", "Other")
        if cat not in categories:
            categories[cat] = {"income": 0, "expense": 0}
        categories[cat][e["type"]] += e["amount"]
        month = e.get("date", "")[:7]
        if month:
            if month not in monthly:
                monthly[month] = {"income": 0, "expense": 0}
            monthly[month][e["type"]] += e["amount"]
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": total_income - total_expenses,
        "by_category": categories,
        "by_month": monthly
    }
