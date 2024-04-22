from typing import List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Depends,
    Request,
    status,
    Path,
    Query,
    Security,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import (
    ContactSchema,
    ContactResponse,
    TokenSchema,
    RequestEmail,
)
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.services.email import send_email

from fastapi.security import (
    HTTPBearer,
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
)

router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post(
    "/signup", response_model=ContactResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: ContactSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    exist_user = await repository_contacts.get_contact_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_contacts.create_contact(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.name, request.base_url
    )
    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation.",
    }


# @router.post(
#     "/signup", response_model=ContactResponse, status_code=status.HTTP_201_CREATED
# )
# async def signup(body: ContactSchema, db: AsyncSession = Depends(get_db)):
#     exist_user = await repository_contacts.get_contact_by_email(body.email, db)
#     if exist_user:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
#         )
#     body.password = auth_service.get_password_hash(body.password)
#     new_user = await repository_contacts.create_contact(body, db)
#     return new_user


@router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await repository_contacts.get_contact_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_contacts.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# @router.post("/login", response_model=TokenSchema)
# async def login(
#     body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
# ):
#     user = await repository_contacts.get_contact_by_email(body.username, db)
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
#         )
#     if not auth_service.verify_password(body.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
#         )
#     # Generate JWT
#     access_token = await auth_service.create_access_token(data={"sub": user.email})
#     refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
#     await repository_contacts.update_token(user, refresh_token, db)
#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#     }


router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await repository_contacts.get_contact_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.name, request.base_url
        )
    return {"message": "Check your email for confirmation."}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_contacts.get_contact_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_contacts.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    contact = await repository_contacts.get_contact_by_email(email, db)
    if contact.refresh_token != token:
        await repository_contacts.update_token(contact, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_contacts.update_token(contact, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
