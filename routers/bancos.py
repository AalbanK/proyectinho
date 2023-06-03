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
    prefix="/bancos",
    tags=["bancos"]
)

@router.get("/")
async def read_marca_camion(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("bancos/listar.html", {"request": request})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_banco(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("bancos/crear.html", {"request": request})

@router.post("/nuevo")
async def create_banco(db: Session = Depends(get_database_session), desc_banco = Form(...)):
    banco = Banco(descripcion=desc_banco)
    db.add(banco)
    db.commit()
    db.refresh(banco)
    response = RedirectResponse('/', status_code=303)
    return response
