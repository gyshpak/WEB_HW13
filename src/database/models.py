from datetime import date
from sqlalchemy import Column, Integer, String, DateTime, func

# from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    phone: Mapped[str] = mapped_column(String(13), unique=True)
    birthday: Mapped[date] = mapped_column("birthday")
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(default=False)


# class Contact(Base):
#     __tablename__ = "contacts"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(40), nullable=False)
#     email = Column(String(50), unique=True)
#     phone = Column(String(13), unique=True)
#     birthday = Column(Date)
