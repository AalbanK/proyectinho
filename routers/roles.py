from fastapi import APIRouter, Depends, FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import Rol
from routers import auth
from schemas import usuario as us

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)
@router.get("/")
async def read_rol(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("roles/listar.html", {"request": request, "usuario_actual": usuario_actual, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_rol(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("roles/crear.html", {"request": request, "usuario_actual": usuario_actual})

@router.post("/nuevo")
async def create_rol(db: Session = Depends(get_database_session), descri_rol = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    descrol = Rol(descripcion=descri_rol, alta_usuario = usu.idusuario )
    db.add(descrol)
    db.commit()
    db.refresh(descrol)
    response = RedirectResponse('/', status_code=303)
    return response