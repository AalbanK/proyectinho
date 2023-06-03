from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Banco
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
async def read_marca_camion(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("usuarios/listar.html", {"request": request})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_usuario(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("usuarios/crear.html", {"request": request})

@router.post("/nuevo")
async def create_usuario(db: Session = Depends(get_database_session), desc_usuario = Form(...)):
    usuario = Banco(descripcion=desc_usuario)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    response = RedirectResponse('/', status_code=303)
    return response
