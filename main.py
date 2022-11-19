import os
from typing import Union

import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from starlette import status
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "some-random-string"))

oauth = OAuth()
issuer = os.getenv('ISSUER', 'http://localhost:8080/auth/realms/fast-api-oauth-lib')
client_id = os.getenv('CLIENT_ID', 'fast-api-oauth-lib')
client_secret = os.getenv('CLIENT_SECRET', 'UB8uxVJFRoa30HFukKA1PePXhcBM8Dpt')
oidc_discovery_url = f'{issuer}/.well-known/openid-configuration'
callback_url = 'http://localhost:8000/auth'
end_session_endpoint = f'{issuer}/protocol/openid-connect/logout'

oauth.register(
    name='keycloak',
    client_id=client_id,
    client_secret=client_secret,
    server_metadata_url=oidc_discovery_url,
    client_kwargs={
        'scope': 'openid email profile',
        'code_challenge_method': 'S256'  # enable PKCE
    },
)


async def get_current_user_session(request: Request):
    user = request.session.get("user")
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized...",
            headers={"WWW-Authenticate": "Session"},
        )
    else:
        return user


@app.get("/")
async def root(request: Request, cmd: Union[str, None] = None):
    if request.session.get("user") is not None:
        return {
            "action": "Successfully logged in..." if cmd == "0" else None,
            "success": True,
            "message": "There is a list of things you can do...",
            "list": [
                {
                    "id": 0,
                    "action_point": "Visit protected route '/jobs'"
                },
                {
                    "id": 1,
                    "action_point": "Log out from system '/logout'"
                }
            ],
            "user_object": request.session.get("user")
        }
    else:
        return {
            "action": "Successfully logged out..." if cmd == "1" else None,
            "success": True,
            "message": "There is a list of things you can do...",
            "user_object": None,
            "list": [
                {
                    "id": 0,
                    "action_point": "Authorize to access protected route '/jobs', (visit route '/login')"
                },
                {
                    "id": 1,
                    "action_point": "View this endpoint"
                }
            ]
        }


@app.get("/login")
async def user_login(request: Request):
    return await oauth.keycloak.authorize_redirect(request, callback_url)


@app.get("/auth")
async def oauth_callback(request: Request):
    token = await oauth.keycloak.authorize_access_token(request)
    user = token['userinfo']
    request.session["user"] = user
    request.session["refresh_token"] = token["refresh_token"]
    return RedirectResponse('/?cmd=0', status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout")
async def user_logout(request: Request):
    refresh_token = request.session.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token was not found...",
            headers={"Client-Error": "Refresh Token State"},
        )
    else:
        client = httpx.AsyncClient(http2=True)
        data = {"client_id": client_id, "client_secret": client_secret, "refresh_token": str(refresh_token)}
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        result = await client.post(url=end_session_endpoint, data=data, headers=headers)
        if result.status_code == 204:
            request.session["refresh_token"] = ''
            request.session["user"] = None
            return RedirectResponse('/?cmd=1', status_code=status.HTTP_303_SEE_OTHER)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Not successful...",
                headers={"Keycloak-Error": "Logout State"},
            )


@app.get("/jobs")
async def job_list(user=Depends(get_current_user_session)):
    jobs = [{"id": 1, "name": "Name one", "is_active": True}, {"id": 2, "name": "Name two", "is_active": False},
            {"id": 3, "name": "Name three", "is_active": True}, {"id": 4, "name": "Name four", "is_active": True}]
    return {
        "success": True,
        "jobs": jobs,
        "current_user": user
    }


@app.on_event("startup")
async def connect_db():
    print("Init")


@app.on_event("shutdown")
async def connect_db():
    print("Power off")
