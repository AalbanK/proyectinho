from fastapi import APIRouter, Depends, FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import IVA
from routers import auth
from schemas import usuario as us

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/ivas",
    tags=["ivas"]
)

@router.get("/")
async def read_marca_camion(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("ivas/listar.html", {"request": request, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_iva(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("ivas/crear.html", {"request": request})

@router.post("/nuevo")
async def create_iva(db: Session = Depends(get_database_session), iva_porc = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    iva = IVA(porcentaje=iva_porc)
    db.add(iva)
    db.commit()
    db.refresh(iva)
    response = RedirectResponse('/', status_code=303)
    return response
