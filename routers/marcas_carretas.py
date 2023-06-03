from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Marca_carreta
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/marcas_carretas",
    tags=["marcas_carretas"]
)

@router.get("/")
async def read_marca_carreta(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("marcas_carretas/listar.html", {"request": request})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_marca_carreta(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("marcas_carretas/crear.html", {"request": request})

@router.post("/nuevo")
async def create_marca_carreta(db: Session = Depends(get_database_session), marca_carre_desc = Form(...)):
    marca_carreta = Marca_carreta(descripcion=marca_carre_desc)
    db.add(marca_carreta)
    db.commit()
    db.refresh(marca_carreta)
    response = RedirectResponse('/', status_code=303)
    return response
