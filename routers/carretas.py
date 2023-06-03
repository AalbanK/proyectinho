from fastapi import APIRouter, Depends, Request, Form, Response, FastAPI
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import Carreta

from db.misc import get_database_session

app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates= Jinja2Templates(directory="templates")

router=APIRouter(
    prefix="/carretas",
    tags=["carretas"]
)

@router.get("/")
async def read_carreta(request:Request,db:Session=Depends(get_database_session)):
    return templates.TemplateResponse("carretas/listar.html", {"request":request})

@router.get("/nuevo",response_class=HTMLResponse)
async def create_carreta(request:Request,db:Session=Depends(get_database_session)):
    return templates.TemplateResponse("carretas/crear.html",{"request":request})

@router.post("nuevo")
async def create_carreta(db:Session=Depends(get_database_session),chapa_carre=Form(...)):
    carreta=Carreta(chapa=chapa_carre)
    db.add(carreta)
    db.commit()
    db.refresh(carreta)
    response=RedirectResponse("/",status_code=300)
    return response