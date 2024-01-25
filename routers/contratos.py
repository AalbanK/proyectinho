from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Contrato, Producto, Ciudad, Proveedor, Cliente
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/contratos",
    tags=["contratos"]
)

@router.get("/")
async def read_contrato(request: Request, db: Session = Depends(get_database_session)):
    records = db.query(Contrato).all()
    return templates.TemplateResponse("contratos/listar.html", {"request": request, "data": records, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_contrato(request: Request, db: Session = Depends(get_database_session)):
    produs=db.query(Producto).all()
    cius=db.query(Ciudad).all()
    proves=db.query(Proveedor).all()
    clies=db.query(Cliente).all()
    return templates.TemplateResponse("contratos/crear.html", {"request": request, "Produs_lista":produs,"Cius_lista":cius,
                                                                "Proves_lista":proves, "Clies_lista":clies})

@router.post("/nuevo")
async def create_contrato(db: Session = Depends(get_database_session), descContrato = Form(...), idProducto=Form(...), idCiudad=Form(...),
                          idProveedor=Form(...), cuenta_Proveedor = Form(...), idCliente=Form(...), cuenta_Cliente = Form(...)):
    contrato = Contrato(descripcion=descContrato, idproducto=idProducto, idciudad=idCiudad, idProveedor=idProveedor, idCliente=idCliente)
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    response = RedirectResponse('/', status_code=303)
    return response

#-----------------------------------------------------------------------------------------------------

# @router.get("/{id}",response_class=HTMLResponse)
# def ver(id:int, response:Response,
#             request:Request,db: Session = Depends(get_database_session)):
#     clie = db.query(Contrato).get(id)
#     depto = db.query(Departamento).get(int(clie.idDepto))
#     return templates.TemplateResponse("contratos/listar.html", {"request": request, "Contrato": clie, "Departamento": depto})

# @router.get("/editar/{id}",response_class=HTMLResponse)
# def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
#     clie= db.query(Contrato).get(id)
#     depto = db.query(Departamento).all()
#     return templates.TemplateResponse("editar_contrato.html", {"request": request, "Contrato": clie, "Departamentos_lista": depto})

# @router.post("/update",response_class=HTMLResponse)
# def editar(db: Session = Depends(get_database_session), idclie = Form(...), color = Form(...), modelo = Form(...), anho = Form(...), idmarca = Form(...)):
#     clie= db.query(Contrato).get(idclie)
#     clie.color=color
#     clie.modelo=modelo
#     clie.anho=anho
#     clie.idmarca=idmarca
#     db.add(clie)
#     db.commit()
#     db.refresh(clie)
#     response = RedirectResponse('/contratos/', status_code=303)
#     return response

# @router.get("/borrar/{id}",response_class=HTMLResponse)
# def eliminar(id : int, db: Session = Depends(get_database_session)):
#     db.query(Contrato).filter(Contrato.idclie == id).delete()
#     db.commit()
#     response = RedirectResponse('/contratos/', status_code=303)
#     return response
