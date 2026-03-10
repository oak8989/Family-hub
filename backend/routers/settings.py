from fastapi import APIRouter, HTTPException, Depends
from models.schemas import FamilySettings
from auth import get_current_user, get_user_role, DEFAULT_FAMILY_SETTINGS, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_FROM, GOOGLE_CLIENT_ID
from database import db

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
async def get_settings(user: dict = Depends(get_current_user)):
    family = await db.families.find_one({"id": user["family_id"]}, {"_id": 0})
    if not family:
        return DEFAULT_FAMILY_SETTINGS
    return family.get("settings", DEFAULT_FAMILY_SETTINGS)


@router.put("")
async def update_settings(settings: FamilySettings, user: dict = Depends(get_current_user)):
    if not user.get("family_id"):
        raise HTTPException(status_code=400, detail="No family associated with user")
    user_role = await get_user_role(user)
    if user_role not in ["owner", "parent"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = {}
    if settings.modules:
        update_data["settings.modules"] = settings.modules
    if settings.permissions:
        update_data["settings.permissions"] = settings.permissions
    if settings.theme:
        update_data["settings.theme"] = settings.theme
    if settings.chore_rewards:
        update_data["settings.chore_rewards"] = settings.chore_rewards

    if update_data:
        await db.families.update_one({"id": user["family_id"]}, {"$set": update_data})
    family = await db.families.find_one({"id": user["family_id"]}, {"_id": 0})
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    return family.get("settings", DEFAULT_FAMILY_SETTINGS)


@router.get("/server")
async def get_server_settings(user: dict = Depends(get_current_user)):
    user_role = await get_user_role(user)
    if user_role != "owner":
        raise HTTPException(status_code=403, detail="Only owner can view server settings")
    return {
        "smtp_configured": bool(SMTP_HOST),
        "google_configured": bool(GOOGLE_CLIENT_ID),
        "smtp_host": SMTP_HOST,
        "smtp_port": SMTP_PORT,
        "smtp_user": SMTP_USER,
        "smtp_from": SMTP_FROM,
    }
