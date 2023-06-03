from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import IVA
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/ivas",
    tags=["ivas"]
)

@router.get("/")
async def read_marca_camion(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("ivas/listar.html", {"request": request})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_iva(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("ivas/crear.html", {"request": request})

@router.post("/nuevo")
async def create_iva(db: Session = Depends(get_database_session), iva_porc = Form(...)):
    iva = IVA(porcentaje=iva_porc)
    db.add(iva)
    db.commit()
    db.refresh(iva)
    response = RedirectResponse('/', status_code=303)
    return response
