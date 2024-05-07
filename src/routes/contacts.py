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
from src.schemas import UpdateSchema, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

import cloudinary
import cloudinary.uploader

# from my_limiter import limiter

from conf.config import config
from conf import messages

router = APIRouter(prefix="/contacts", tags=["contacts"])

cloudinary.config(
    cloud_name=config.CLOUD_NAME,
    api_key=config.CLOUD_API_KEY,
    api_secret=config.CLOUD_API_SECRET,
)


@router.get("/", response_model=List[ContactResponse])
# @limiter.limit("5/minute")
async def get_contacts(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=10, le=100),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_contact),
):
    """
    The get_contacts function returns a list of contacts.
    
    :param request: Request: Get the request object
    :param offset: int: Specify the offset of the contacts to be returned
    :param ge: Set a minimum value for the parameter
    :param limit: int: Limit the number of contacts returned
    :param ge: Specify a minimum value for the parameter
    :param le: Limit the number of contacts returned
    :param db: AsyncSession: Get the database session
    :param cur_contact: Contact: Get the current contact from the database
    :param : Get the current contact
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(offset, limit, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_contact),
):
    """
    The get_contact function is used to retrieve a contact from the database.
    
    :param contact_id: int: Get the contact_id from the url
    :param db: AsyncSession: Pass the database session to the function
    :param cur_contact: Contact: Get the current contact object
    :param : Get the contact id from the url path
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.put("/")
async def update_contact(
    body: UpdateSchema,
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_contact),
):
    """
    The update_contact function updates a contact in the database.
        The function takes an id, body and db as parameters.
        It returns a contact object.
    
    :param body: ContactSchema: Validate the data sent in the request body
    :param db: AsyncSession: Pass the database session to the repository layer
    :param cur_contact: Contact: Get the current contact information
    :param : Get the current contact
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(cur_contact.id, body, db)
    if cur_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.CONTACT_NOT_FOUND,
        )
    return contact


@router.delete("/")#, status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    db: AsyncSession = Depends(get_db),
    cur_contact: Contact = Depends(auth_service.get_current_contact),
):
    """
    The delete_contact function deletes a contact from the database.
        The function takes in an id of the contact to be deleted and returns a JSON object containing information about the deleted contact.
    
    :param db: AsyncSession: Pass the database session to the repository
    :param cur_contact: Contact: Get the current contact
    :param : Get the current contact
    :return: The deleted contact
    :doc-author: Trelent
    """
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
    """
    The search_contact function searches for contacts in the database.
        The search is performed on the first_name, last_name and email fields of a contact.
        The function returns a list of contacts that match the search criteria.
    
    :param field_search: str: Search a contact by name or email
    :param offset: int: Specify the number of records to skip before returning results
    :param ge: Specify that the value must be greater than or equal to a given number
    :param limit: int: Limit the number of contacts returned
    :param ge: Set the minimum value of a parameter
    :param le: Limit the number of results returned
    :param db: AsyncSession: Get the database session
    :param cur_contact: Contact: Get the current contact
    :param : Get the current contact
    :return: A list of contacts
    :doc-author: Trelent
    """
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
    """
    The search_coming_birthdays function searches for contacts with birthdays coming up.
    
    :param offset: int: Determine the offset of the query
    :param ge: Set a minimum value for the offset parameter
    :param limit: int: Limit the number of results returned
    :param ge: Set the minimum value for the offset parameter
    :param le: Limit the number of contacts returned
    :param db: AsyncSession: Pass the database connection to the function
    :param cur_contact: Contact: Get the current contact from the database
    :param : Get the current contact
    :return: A list of contacts
    :doc-author: Trelent
    """
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

    """
    The update_avatar_contact function updates the avatar of a contact.
        Args:
            file (UploadFile): The uploaded image file.
            current_contact (Contact): The currently logged in user's contact object.
            db (AsyncSession): An async session for database accesses.
    
    :param file: UploadFile: Get the file from the request body
    :param current_contact: Contact: Get the current user's contact details
    :param db: AsyncSession: Get the database session
    :param : Get the current user's email address from the database
    :return: The updated contact object
    :doc-author: Trelent
    """
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
