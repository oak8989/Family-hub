from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from models.schemas import PushSubscription
from auth import get_current_user
from database import db
from datetime import datetime, timezone
import os
import io
import json
import qrcode
import base64

router = APIRouter(prefix="/api", tags=["utilities"])


# QR Code
@router.get("/qr-code")
async def generate_qr_code(url: str = Query(..., description="Server URL to encode")):
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/qr-code/base64")
async def get_qr_code_base64(url: str = Query(..., description="Server URL to encode")):
    try:
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        base64_str = base64.b64encode(buffer.getvalue()).decode()
        return {"qr_code": f"data:image/png;base64,{base64_str}", "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Push Notifications
@router.post("/notifications/subscribe")
async def subscribe_push(subscription: PushSubscription, user: dict = Depends(get_current_user)):
    await db.push_subscriptions.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "user_id": user["user_id"],
            "family_id": user["family_id"],
            "subscription": subscription.model_dump(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    return {"message": "Subscribed to notifications"}


@router.delete("/notifications/unsubscribe")
async def unsubscribe_push(user: dict = Depends(get_current_user)):
    await db.push_subscriptions.delete_one({"user_id": user["user_id"]})
    return {"message": "Unsubscribed from notifications"}


@router.get("/notifications/vapid-key")
async def get_vapid_public_key():
    vapid_public = os.environ.get('VAPID_PUBLIC_KEY', 'BPbmrjjC3bH1P0vCGGjQnKfb_hAHQFLFgzVn-1IwQQWvLqHUDZJ6L3wqJ-3HzL9hH6xJxP7JQ3qRFmR9J_T8K2k')
    return {"public_key": vapid_public}


# Data Export/Backup
@router.get("/export/data")
async def export_family_data(user: dict = Depends(get_current_user)):
    family_id = user["family_id"]
    data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "exported_by": user["user_id"],
        "family": await db.families.find_one({"id": family_id}, {"_id": 0}),
        "members": await db.users.find({"family_id": family_id}, {"_id": 0, "password": 0}).to_list(100),
        "calendar_events": await db.calendar_events.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "shopping_items": await db.shopping_items.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "tasks": await db.tasks.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "chores": await db.chores.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "rewards": await db.rewards.find({"family_id": family_id}, {"_id": 0}).to_list(100),
        "notes": await db.notes.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "budget_entries": await db.budget_entries.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "meal_plans": await db.meal_plans.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "recipes": await db.recipes.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "grocery_items": await db.grocery_items.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "contacts": await db.contacts.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "pantry_items": await db.pantry_items.find({"family_id": family_id}, {"_id": 0}).to_list(1000),
        "settings": await db.settings.find_one({"family_id": family_id}, {"_id": 0}),
    }
    json_str = json.dumps(data, indent=2, default=str)
    return StreamingResponse(
        io.BytesIO(json_str.encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=family-hub-backup-{datetime.now().strftime('%Y%m%d')}.json"}
    )


@router.get("/export/csv/{module}")
async def export_module_csv(module: str, user: dict = Depends(get_current_user)):
    family_id = user["family_id"]
    collections = {
        "calendar": ("calendar_events", ["id", "title", "description", "date", "time", "color"]),
        "shopping": ("shopping_items", ["id", "name", "quantity", "category", "checked"]),
        "tasks": ("tasks", ["id", "title", "description", "priority", "assigned_to", "due_date", "completed"]),
        "chores": ("chores", ["id", "title", "description", "difficulty", "points", "assigned_to", "completed"]),
        "budget": ("budget_entries", ["id", "description", "amount", "type", "category", "date"]),
        "contacts": ("contacts", ["id", "name", "email", "phone", "address"]),
        "pantry": ("pantry_items", ["id", "name", "quantity", "unit", "category", "expiry_date"]),
    }
    if module not in collections:
        raise HTTPException(status_code=400, detail=f"Invalid module. Choose from: {', '.join(collections.keys())}")

    collection_name, fields = collections[module]
    items = await db[collection_name].find({"family_id": family_id}, {"_id": 0}).to_list(1000)
    output = io.StringIO()
    output.write(",".join(fields) + "\n")
    for item in items:
        row = [str(item.get(f, "")).replace(",", ";").replace("\n", " ") for f in fields]
        output.write(",".join(row) + "\n")
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={module}-export-{datetime.now().strftime('%Y%m%d')}.csv"}
    )
