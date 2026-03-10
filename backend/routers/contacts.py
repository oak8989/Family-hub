from fastapi import APIRouter, Depends
from typing import List
from models.schemas import Contact
from auth import get_current_user
from database import db

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.get("", response_model=List[Contact])
async def get_contacts(user: dict = Depends(get_current_user)):
    contacts = await db.contacts.find({"family_id": user["family_id"]}, {"_id": 0}).to_list(1000)
    for c in contacts:
        c.pop("family_id", None)
    return contacts


@router.post("", response_model=Contact)
async def create_contact(contact: Contact, user: dict = Depends(get_current_user)):
    contact_doc = contact.model_dump()
    contact_doc["family_id"] = user["family_id"]
    await db.contacts.insert_one(contact_doc)
    del contact_doc["_id"]
    del contact_doc["family_id"]
    return contact_doc


@router.put("/{contact_id}")
async def update_contact(contact_id: str, contact: Contact, user: dict = Depends(get_current_user)):
    contact_doc = contact.model_dump()
    await db.contacts.update_one({"id": contact_id, "family_id": user["family_id"]}, {"$set": contact_doc})
    return contact_doc


@router.delete("/{contact_id}")
async def delete_contact(contact_id: str, user: dict = Depends(get_current_user)):
    await db.contacts.delete_one({"id": contact_id, "family_id": user["family_id"]})
    return {"message": "Contact deleted"}
