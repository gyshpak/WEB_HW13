from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.database.db import get_db
from src.database.models import Contact
from src.schemas import ContactSchema

from validate_email import validate_email

from datetime import datetime, timedelta


async def get_contacts(offset: int, limit: int, db: AsyncSession):
    """
    The get_contacts function returns a list of contacts from the database.
    
    :param offset: int: Specify the offset of the first row to return
    :param limit: int: Limit the number of contacts returned
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    """
    The get_contact function returns a contact object from the database.
    
    :param contact_id: int: Specify the contact_id of the contact you want to get
    :param db: AsyncSession: Pass in the database session
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession):
    """
    The update_contact function updates a contact in the database.
    
    :param contact_id: int: Identify the contact we want to update
    :param body: ContactSchema: Pass in the data from the request body
    :param db: AsyncSession: Pass the database session to the function
    :return: The updated contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    """
    The delete_contact function deletes a contact from the database.
    
    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: AsyncSession: Pass the database session into the function
    :return: The contact object that was deleted
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(field_search, offset: int, limit: int, db: AsyncSession):
    """
    The search_contacts function searches for contacts in the database.
        It takes three arguments: field_search, offset and limit.
        The field_search argument is a string that can be either an email or a name/phone number.
        The offset argument is an integer that specifies where to start returning results from (useful for pagination).
        The limit argument is an integer that specifies how many results to return (useful for pagination).
    
    :param field_search: Search for a contact by name or phone number
    :param offset: int: Determine where to start the search
    :param limit: int: Limit the number of contacts returned
    :param db: AsyncSession: Pass the database connection to the function
    :return: A list of objects
    :doc-author: Trelent
    """
    if validate_email(field_search):
        stmt = select(Contact).filter_by(email=field_search)
        contacts = await db.execute(stmt)

    else:
        stmt = (
            select(Contact)
            .where(
                or_(
                    Contact.name.like(f"%{field_search}%"),
                    (Contact.phone.like(f"%{field_search}%")),
                )
            )
            .offset(offset)
            .limit(limit)
        )
        contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def search_contacts_coming_birthday(offset: int, limit: int, db: AsyncSession):
    """
    The search_contacts_coming_birthday function searches for contacts whose birthday is coming in the next 7 days.
    
    :param offset: int: Specify the number of records to skip
    :param limit: int: Limit the number of results returned by the query
    :param db: AsyncSession: Pass the database connection to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    today = datetime.now().date()
    end_date = today + timedelta(days=7)
    stmt = (
        select(Contact)
        .filter(Contact.birthday.between(today, end_date))
        .offset(offset)
        .limit(limit)
    )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_contact_by_email function returns a contact object from the database based on the email address provided.
        Args:
            email (str): The email address of the contact to be retrieved.
            db (AsyncSession): An async session for interacting with an SQLAlchemy database.
        Returns:
            Contact: A single Contact object matching the provided email address, or None if no match is found.
    
    :param email: str: Pass the email of the contact to be retrieved
    :param db: AsyncSession: Pass in the database session to the function
    :return: A contact object or none if the email is not found
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(email=email)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    return contact


async def update_token(contact: Contact, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a given contact.
    
    :param contact: Contact: Get the contact object that is being updated
    :param token: str | None: Update the refresh token of a contact
    :param db: AsyncSession: Commit the changes to the database
    :return: The contact object
    :doc-author: Trelent
    """
    contact.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function marks a contact as confirmed.
    
    :param email: str: Pass in the email address of the contact to be updated
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    contact = await get_contact_by_email(email, db)
    contact.confirmed = True
    await db.commit()


async def update_avatar(email: str, url: str, db: AsyncSession):
    """
    The update_avatar function updates the avatar of a contact.
    
    Args:
        email (str): The email address of the contact to update.
        url (str): The URL for the new avatar image.
        db (AsyncSession): An async database session object, used to commit changes and refresh objects in memory after committing them to the database.
    
    :param email: str: Get the contact from the database
    :param url: str: Pass the url of the avatar to be updated
    :param db: AsyncSession: Pass the database session to the function
    :return: The contact object
    :doc-author: Trelent
    """
    contact = await get_contact_by_email(email, db)
    contact.avatar = url
    await db.commit()
    await db.refresh(contact)
    return contact
