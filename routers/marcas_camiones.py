from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Marca_camion
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/marcas_camiones",
    tags=["marcas_camiones"]
)

@router.get("/")
async def read_marca_camion(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("marcas_camiones/listar.html", {"request": request})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_marca_camion(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("marcas_camiones/crear.html", {"request": request})

@router.post("/nuevo")
async def create_marca_camion(db: Session = Depends(get_database_session), marca_cami_desc = Form(...)):
    marca_camion = Marca_camion(descripcion=marca_cami_desc)
    db.add(marca_camion)
    db.commit()
    db.refresh(marca_camion)
    response = RedirectResponse('/', status_code=303)
    return response
