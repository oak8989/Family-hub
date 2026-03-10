from fastapi import APIRouter, Depends
from typing import List
from models.schemas import MealPlan
from auth import get_current_user
from database import db

router = APIRouter(prefix="/api/meals", tags=["meals"])


@router.get("", response_model=List[MealPlan])
async def get_meal_plans(user: dict = Depends(get_current_user)):
    plans = await db.meal_plans.find({"family_id": user["family_id"]}, {"_id": 0}).to_list(1000)
    for p in plans:
        p.pop("family_id", None)
    return plans


@router.post("", response_model=MealPlan)
async def create_meal_plan(plan: MealPlan, user: dict = Depends(get_current_user)):
    plan_doc = plan.model_dump()
    plan_doc["family_id"] = user["family_id"]
    await db.meal_plans.insert_one(plan_doc)
    del plan_doc["_id"]
    del plan_doc["family_id"]
    return plan_doc


@router.put("/{plan_id}")
async def update_meal_plan(plan_id: str, plan: MealPlan, user: dict = Depends(get_current_user)):
    plan_doc = plan.model_dump()
    await db.meal_plans.update_one({"id": plan_id, "family_id": user["family_id"]}, {"$set": plan_doc})
    return plan_doc


@router.delete("/{plan_id}")
async def delete_meal_plan(plan_id: str, user: dict = Depends(get_current_user)):
    await db.meal_plans.delete_one({"id": plan_id, "family_id": user["family_id"]})
    return {"message": "Plan deleted"}
