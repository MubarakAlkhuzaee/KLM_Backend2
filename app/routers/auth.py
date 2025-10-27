from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from ..schemas import RegisterIn, TokenOut, GoogleAuthStartOut
from ..models import User, Team
from ..security import hash_password, verify_password, create_access_token
from ..config import settings
from ..db import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Email/password ---
@router.post("/register", response_model=TokenOut)
async def register(data: RegisterIn, db: AsyncSession = Depends(get_session)):
    # team_code optional on register; can be set later
    exists = await db.execute(select(User).where(User.email == data.email))
    if exists.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    team_id = None
    if data.team_code:
        t = await db.execute(select(Team).where(Team.code == data.team_code))
        team = t.scalar_one_or_none()
        if not team:
            raise HTTPException(400, "Invalid team code")
        team_id = team.id

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        display_name=data.display_name,
        team_id=team_id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(str(user.id))
    return TokenOut(access_token=token)

@router.post("/login", response_model=TokenOut)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    q = await db.execute(select(User).where(User.email == form.username))
    user = q.scalar_one_or_none()
    if not user or not user.hashed_password or not verify_password(form.password, user.hashed_password):
        raise HTTPException(400, "Incorrect email or password")
    token = create_access_token(str(user.id))
    return TokenOut(access_token=token)

# --- Google OAuth ---
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@router.get("/google/start", response_model=GoogleAuthStartOut)
async def google_start(request: Request):
    redirect_uri = settings.OAUTH_REDIRECT_URI
    # We return the URL for Godot to open in a webview or external browser
    conf = await oauth.google.load_server_metadata()
    client = oauth.create_client("google")
    uri, _state = client.create_authorization_url(conf["authorization_endpoint"], redirect_uri=redirect_uri)
    return GoogleAuthStartOut(authorization_url=uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_session)):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if not userinfo:
        # fallback: fetch
        userinfo = await oauth.google.parse_id_token(request, token)

    email = userinfo["email"]
    sub = userinfo["sub"]
    display_name = userinfo.get("name")

    q = await db.execute(select(User).where(User.google_sub == sub))
    user = q.scalar_one_or_none()
    if user is None:
        # If email exists, link it. Else create a new oauth-only user.
        by_email = await db.execute(select(User).where(User.email == email))
        user = by_email.scalar_one_or_none()
        if user:
            user.google_sub = sub
            if not user.display_name:
                user.display_name = display_name
        else:
            user = User(email=email, hashed_password=None, google_sub=sub, display_name=display_name)
            db.add(user)
        await db.commit()
        await db.refresh(user)

    jwt_token = create_access_token(str(user.id))
    # You can redirect back to your game custom URL scheme, or show a small page that prints the token.
    # For simplicity, return as a 302 to a URL that your Godot client can capture:
    # e.g. mygame://auth?token=...  (register a handler) OR return a simple HTML.
    return RedirectResponse(url=f"mygame://auth?token={jwt_token}")
