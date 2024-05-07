from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Depends,
    Request,
    status,
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

# from my_limiter import limiter

from conf import messages

router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute")
async def signup(
    body: ContactSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The signup function creates a new user in the database.
    
    :param body: ContactSchema: Validate the request body
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base url of the request
    :param db: AsyncSession: Get the database connection
    :param : Send an email to the user who has just signed up
    :return: The new user
    :doc-author: Trelent
    """
    exist_user = await repository_contacts.get_contact_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_contacts.create_contact(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.name, str(request.base_url)
    )
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    The login function is used to authenticate a user.
    
    :param body: OAuth2PasswordRequestForm: Validate the request body
    :param db: AsyncSession: Get the database session
    :return: A dict with the access_token, refresh_token and token type
    :doc-author: Trelent
    """
    user = await repository_contacts.get_contact_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
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


router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The request_email function is used to send an email to the user with a link
    to confirm their email address. The function takes in the body of the request,
    the background tasks object, and a database session. It then uses these objects
    to get information about the user from our database and sends them an email using 
    our send_email function.
    
    :param body: RequestEmail: Validate the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks
    :param request: Request: Get the base_url of the api
    :param db: AsyncSession: Get the database session
    :param : Get the email address from the user
    :return: A dictionary with a message key
    :doc-author: Trelent
    """
    user = await repository_contacts.get_contact_by_email(body.email, db)

    if user.confirmed:
        return {"message": messages.EMAIL_ALREADY_CONFIRMED}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.name, request.base_url
        )
    return {"message": messages.CHECK_EMAIL}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it checks if that email exists in our database, and if so, confirms their account.
    
    :param token: str: Get the token from the url
    :param db: AsyncSession: Get the database connection
    :return: A dict with a message
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_contacts.get_contact_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=messages.VERIFICATION_ERROR
        )
    if user.confirmed:
        return {"message": messages.EMAIL_ALREADY_CONFIRMED}
    await repository_contacts.confirmed_email(email, db)
    return {"message": messages.EMAIL_CONFIRMED}


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token,
        a new refresh_token, and the type of token (bearer).
    
    :param credentials: HTTPAuthorizationCredentials: Get the refresh token from the authorization header
    :param db: AsyncSession: Get the database session
    :param : Get the refresh token from the request header
    :return: A dict with the access_token, refresh_token and token_type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    contact = await repository_contacts.get_contact_by_email(email, db)
    if contact.refresh_token != token:
        await repository_contacts.update_token(contact, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_contacts.update_token(contact, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
