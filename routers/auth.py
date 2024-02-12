# https://www.fastapitutorial.com/blog/permissions-in-fastapi/

from datetime import datetime
from typing import List, Union, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body, status, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
import sqlalchemy
from starlette.responses import RedirectResponse

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordRequestForm

from db.utils import OAuth2PasswordBearerWithCookie

from db.misc import get_database_session
from models import Usuario, Rol
from schemas import usuario
from schemas.token import TokenPayload, TokenSchema

from db.misc import (
    get_password_hasheado,
    crear_access_token,
    crear_refresh_token,
    verificar_password,
    ALGORITHM,
    JWT_SECRET_KEY
)

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "No encontrado"}},
)

def autenticar_usuario(username: str, password: str, db: Session= Depends(get_database_session)):
    user = db.query(Usuario).filter(Usuario.username == username).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos."
        )

    hashed_pass = get_password_hasheado(user.password)
    if not verificar_password(password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos."
        )

    '''

    if not user:
        return False
    if not verificar_password(password, user.password):
        return False

    '''
    
    return user

@router.post('/token', response_model=TokenSchema)
async def login_para_token_de_acceso(response: Response, db: Session=Depends(get_database_session), form_data: OAuth2PasswordRequestForm = Depends()):
    datos = form_data._dict
    print(datos)
    user = autenticar_usuario(datos['username'], datos['password'], db)

    '''
    user = db.query(Usuario).filter(Usuario.username == datos['username']).first()
    print(user.__dict__)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos."
        )

    hashed_pass = user.password
    if not verificar_password(datos['password'], hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos."
        )
    '''
    access_token = crear_access_token(user.username)
    refresh_token = crear_refresh_token(user.username)

    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

reuseable_oauth = OAuth2PasswordBearerWithCookie(
    tokenUrl="/auth/token",
    scheme_name="JWT"
)

# Dependencia a utilizar
async def get_usuario_actual(token: str = Depends(reuseable_oauth), db: Session=Depends(get_database_session)) -> usuario.Usuario:
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El signature expiró. Debe reiniciar su sesión.",
            headers={"WWW-Authenticate": "Bearer"},
        )        
    except(jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se ha podido revalidar las credenciales.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(Usuario).filter(Usuario.username == token_data.sub).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el usuario.",
        )
    return usuario.Usuario(**user.__dict__)


# verificar si el usuario es superusuario (id = 1)
async def verificar_si_usuario_es_superusuario(usuario_actual: usuario.Usuario = Depends(get_usuario_actual)) -> usuario.Usuario:
    if not usuario_actual.idrol == 2:
        raise HTTPException(status_code=401, detail="No tiene privilegios suficientes para realizar esta acción.")
    return usuario_actual


@router.get("/login", response_class=HTMLResponse)
async def mostrar_login(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def iniciar_sesion(request: Request, db: Session = Depends(get_database_session)):
    form = await request.form()
    response = RedirectResponse('/', status_code=303)
    log = await login_para_token_de_acceso(response=response, form_data=form, db=db)
    return response

@router.get("/logout", response_class=HTMLResponse)
def cerrar_sesion():
    response = RedirectResponse("/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response