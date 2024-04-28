from typing import List

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Depends,
    UploadFile,
    status,
    Path,
    Query,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.database.db import get_db
from src.schemas import ContactSchema, ContactResponse  # , ContactUpdateSchema
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

import cloudinary
import cloudinary.uploader

from my_limiter import limiter

from conf.config import config

router = APIRouter(prefix="/contacts", tags=["contacts"])

cloudinary.config(
    cloud_name=config.CLOUD_NAME,
    api_key=config.CLOUD_API_KEY,
    api_secret=config.CLOUD_API_SECRET,
)


@router.get("/", response_model=List[ContactResponse])
@limiter.limit("5/minute")
async def get_contacts(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=10, le=100),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_contact),
):
    contacts = await repository_contacts.get_contacts(offset, limit, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_contact),
):
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put("/")
async def update_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_contact),
):
    contact = await repository_contacts.update_contact(cur_contact.id, body, db)
    if cur_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_contact),
):
    contact = await repository_contacts.delete_contact(cur_contact.id, db)
    return contact


@router.get("/search/{field_search}", response_model=List[ContactResponse])
async def search_contact(
    field_search: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=10, le=100),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_contact),
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
    cur_contact: Contact = Depends(auth_service.get_current_contact),
):
    contacts = await repository_contacts.search_contacts_coming_birthday(
        offset, limit, db
    )
    return contacts


@router.patch("/avatar", response_model=ContactResponse)
async def update_avatar_contact(
    file: UploadFile = File(),
    current_contact: Contact = Depends(auth_service.get_current_contact),
    db: AsyncSession = Depends(get_db),
):

    r = cloudinary.uploader.upload(
        file.file, public_id=f"NotesApp/{current_contact.name}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f"NotesApp/{current_contact.name}").build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    contact = await repository_contacts.update_avatar(
        current_contact.email, src_url, db
    )
    return contact
