from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.database.db import get_db
from src.schemas import ContactSchema, ContactResponse  # , ContactUpdateSchema
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=10, le=100),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_user),
):
    # db: AsyncSession = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(offset, limit, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


# @router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
# async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
#     contact = await repository_contacts.create_contact(body, db)
#     return contact


# @router.put("/{contact_id}")
@router.put("/")
async def update_contact(
    body: ContactSchema,
    # contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.update_contact(cur_contact.id, body, db)
    if cur_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact


# @router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    # contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.delete_contact(cur_contact.id, db)
    return contact


@router.get("/search/{field_search}", response_model=List[ContactResponse])
async def search_contact(
    field_search: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=10, le=100),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_user),
):
    contacts = await repository_contacts.search_contacts(
        field_search, offset, limit, db
    )
    return contacts


@router.get("/coming-birthday/", response_model=list[ContactResponse])
async def search_coming_birthdays(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=10, le=100),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_user),
):
    contacts = await repository_contacts.search_contacts_coming_birthday(
        offset, limit, db
    )
    return contacts
