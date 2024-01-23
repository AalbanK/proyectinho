import statistics
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session, load_only
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from models import Cliente, Departamento, Ciudad
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
    #records = db.query(Cliente).all()
    ciud = db.query(Cliente.idcliente, Cliente.descripcion, Cliente.ruc,Ciudad.descripcion.label('descripcion_ciudad'),Cliente.direccion, Cliente.mail, Cliente.telefono).join(Ciudad, Cliente.idciudad == Ciudad.idciudad).all()
    print(ciud)
    return templates.TemplateResponse("clientes/listar.html", {"request": request, "clientes": ciud, "datatables": True})

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

# @router.get("/{id}/iddepto",response_class=HTMLResponse)
# def obtener_iddepto_cliente(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
#     clie= db.query(Cliente).get(id)
#     refdepto = db.query(Ciudad).options(load_only(Ciudad.iddepartamento)).get(int(clie.idciudad))
#     refdepto = refdepto.__dict__.get('iddepartamento')
#     respuesta = {'iddepto': refdepto}
#     return JSONResponse(content=jsonable_encoder(respuesta))

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
    clie= db.query(Cliente).get(id)
    depto = db.query(Departamento).all()
    refdepto = db.query(Ciudad).options(load_only(Ciudad.iddepartamento)).get(int(clie.idciudad))
    return templates.TemplateResponse("clientes/editar.html", {"request": request, "Cliente": clie, "Departamentos_lista": depto, "ref_depto":refdepto})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idcliente = Form(...), descripcion = Form(...), ruc = Form(...), idciudad = Form(...), direccion = Form(...), mail = Form(), telefono = Form()):
     clie= db.query(Cliente).get(idcliente)
     clie.descripcion=descripcion
     clie.ruc=ruc
     clie.idciudad=idciudad
     clie.direccion=direccion
     clie.mail=mail
     clie.telefono=telefono
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