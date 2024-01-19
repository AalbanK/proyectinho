from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI
from fastapi.templating import Jinja2Templates
from models import Usuario, Rol
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

@router.get("/")
async def read_rol(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("usuarios/listar.html", {"request": request})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_usuario(request: Request, db: Session = Depends(get_database_session)):
    rol=db.query(Rol).all()
    return templates.TemplateResponse("usuarios/crear.html", {"request": request, "Roles_lista":rol})

@router.post("/nuevo")
async def create_usuario(db: Session = Depends(get_database_session), nam = Form(...), user = Form(...), pasw = Form(...), idrol = Form(...)):
    usuario = Usuario(name=nam, username=user, password=pasw, idrol=idrol)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    response = RedirectResponse('/', status_code=303)
    return response

# @router.post("/crear")
# async def register_user(username: str, password: str, db: Session = Depends(get_database_session)):
#     existing_user = db.query(Usuario).filter(Usuario.username == username).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
    
#     new_user = Usuario(username=username, password=password)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return {"message": "User registered successfully", "user_id": new_user.idusuario}

