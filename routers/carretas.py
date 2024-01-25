from models import Carreta, Marca_carreta
from fastapi import APIRouter, Depends, Request, Form, Response, FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse



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
    records=db.query(Carreta).join(Marca_carreta).all()
    return templates.TemplateResponse("carretas/listar.html", {"request":request, "datatables": True})

@router.get("/nuevo",response_class=HTMLResponse)
async def create_carreta(request:Request,db:Session=Depends(get_database_session)):
    marcas=db.query(Marca_carreta).all()
    return templates.TemplateResponse("carretas/crear.html",{"request":request, "Marcas_lista":marcas})

@router.post("/nuevo")
async def create_carreta(db:Session=Depends(get_database_session),chapaCarreta=Form(...), idmarca_carreta = Form(...)):
    carreta=Carreta(carreta_chapa = chapaCarreta, idmarca_carreta = idmarca_carreta)
    db.add(carreta)
    db.commit()
    db.refresh(carreta)
    response=RedirectResponse('/',status_code=303)
    return response