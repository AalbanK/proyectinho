import statistics
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from models import Banco, Cliente, Departamento, Ciudad
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/clientes",
    tags=["clientes"]
)

@router.get("/")
async def read_cliente(request: Request, db: Session = Depends(get_database_session)):
    records = db.query(Cliente).all()
    return templates.TemplateResponse("clientes/listar.html", {"request": request, "clientes": records})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_cliente(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("clientes/crear.html", {"request": request})

@router.post("/nuevo")
async def create_cliente(db: Session = Depends(get_database_session), descripcion = Form(...), idDepartamento=Form(...), idCiudad=Form(...), ruc = Form(...), mail = Form(...), direccion = Form(...), telefono = Form(...)):
    cliente = Cliente(descripcion=descripcion, idciudad = idCiudad, ruc=ruc, mail=mail, direccion=direccion, telefono=telefono)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
             request:Request,db: Session = Depends(get_database_session)):
     clie = db.query(Cliente).get(id)
     depto = db.query(Departamento).get(int(clie.idDepto))
     return templates.TemplateResponse("clientes/listar.html", {"request": request, "Cliente": clie, "Departamento": depto})

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
     clie= db.query(Cliente).get(id)
     depto = db.query(Departamento).all()
     return templates.TemplateResponse("editar_cliente.html", {"request": request, "Cliente": clie, "Departamentos_lista": depto})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idclie = Form(...), color = Form(...), modelo = Form(...), anho = Form(...), idmarca = Form(...)):
     clie= db.query(Cliente).get(idclie)
     clie.color=color
     clie.modelo=modelo
     clie.anho=anho
     clie.idmarca=idmarca
     db.add(clie)
     db.commit()
     db.refresh(clie)
     response = RedirectResponse('/clientes/', status_code=303)
     return response

@router.get("/borrar/{id}",response_class=HTMLResponse)
def eliminar(id : int, db: Session = Depends(get_database_session)):
     db.query(Cliente).filter(Cliente.idclie == id).delete()
     db.commit()
     response = RedirectResponse('/clientes/', status_code=303)
     return response

