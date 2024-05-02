import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactSchema, ContactResponse, TokenSchema, RequestEmail
from src.repository.contacts import (
    get_contact,
    get_contacts,
    get_contact_by_email,
    create_contact,
    delete_contact,
    update_contact,
    update_avatar,
    update_token,
)

class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # self.contact = Contact(id=1, name="Test Name", email="testemail@ukr.net", phone="0674444444", birthday=date(1975, 12, 12), password="123qweasdzxc")
        self.contact = Contact(id=1, email="testemail@ukr.net")
        self.session = AsyncMock(spec=AsyncSession)
        print("Start Test")


    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contact
        result = await get_contacts(offset=0, limit=10, db=self.session)
        self.assertEqual(result, contacts)


    async def test_get_contact(self):
        contact = Contact()
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id=self.id, db=self.session)
        self.assertEqual(result, contact)


    async def test_get_contact_by_email(self):
        contact = Contact()
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact_by_email(email=self.contact.email, db=self.session)
        self.assertEqual(result, contact)


    async def test_create_contact(self):
        body = ContactSchema(
            name="test_name",
            email="testemail@ukr.net",
            phone="0674444444",
            birthday=date(1975, 12, 12),
            password="123qweas",
        )
        result = await create_contact(body, self.session)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.email, body.email)

    async def tearDown(self):
        print("End Test")

if __name__ == "__main__":
    unittest.main()
