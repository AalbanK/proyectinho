from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Banco
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, Response

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
async def create_banco(db: Session = Depends(get_database_session), descripcion = Form(...)):
    banco = Banco(descripcion=descripcion)
    db.add(banco)
    db.commit()
    db.refresh(banco)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/todos")
async def listar_bancos(request: Request, db: Session = Depends(get_database_session)):
    bancos = db.query(Banco).all()
    return JSONResponse(jsonable_encoder(bancos))

@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
             request:Request,db: Session = Depends(get_database_session)):
     banc = db.query(Banco).get(id)
     return templates.TemplateResponse("bancos/listar.html", {"request": request, "Banco": banc})

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
     banc= db.query(Banco).get(id)
     return templates.TemplateResponse("bancos/editar.html", {"request": request, "Banco": banc})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idbanco = Form(...), descripcion = Form(...)):
     banc= db.query(Banco).get(idbanco)
     banc.descripcion=descripcion
     db.add(banc)
     db.commit()
     db.refresh(banc)
     response = RedirectResponse('/bancos/', status_code=303)
     return response

@router.get("/borrar/{id}",response_class=HTMLResponse)
def eliminar(id : int, db: Session = Depends(get_database_session)):
     db.query(Banco).filter(Banco.idbanco == id).delete()
     db.commit()
     response = RedirectResponse('/bancos/', status_code=303)
     return response