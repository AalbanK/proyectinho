from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import Rol

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/roles",
    tags=["roles"]
)
@router.get("/")
async def read_rol(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("roles/listar.html", {"request": request})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_rol(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("roles/crear.html", {"request": request})

@router.post("/nuevo")
async def create_rol(db: Session = Depends(get_database_session), descri_rol = Form(...)):
    descrol = Rol(descripcion=descri_rol)
    db.add(descrol)
    db.commit()
    db.refresh(descrol)
    response = RedirectResponse('/', status_code=303)
    return response