from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import sqlalchemy as sa
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from models import Departamento, Moneda, Cliente, Proveedor, Banco, Cuenta
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/cuentas",
    tags=["cuentas"]
)

@router.get("/")
async def read_cuenta(request: Request, db: Session = Depends(get_database_session)):
    records = db.query(Cuenta).all()
    return templates.TemplateResponse("cuentas/listar.html", {"request": request, "data": records, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_cuenta(request: Request, db: Session = Depends(get_database_session)):
    bancos = db.query(Banco).all()
    monedas = db.query(Moneda).all()
    clientes = db.query(Cliente).all()
    proveedores = db.query(Proveedor).all()
    return templates.TemplateResponse("cuentas/crear.html", {"request": request, "Proveedores_lista": proveedores, "Clientes_lista": clientes, "Bancos_lista": bancos})

@router.post("/nuevo")
async def create_cuenta(db: Session = Depends(get_database_session), nroCuenta = Form(...), idCliente=Form(), idProveedor = Form(), idBanco = Form(...)):
    
    campos_a_agregar = {
        "nro": nroCuenta, 
        "idbanco": idBanco
    }
    
    # Ya que debe ser o cliente o proveedor
    
    if idCliente is not None and idCliente != '0':
        campos_a_agregar["idcliente"] = idCliente
    
    if idProveedor is not None and idProveedor != '0':
        campos_a_agregar["idproveedor"] = idProveedor

    cuenta = Cuenta(**campos_a_agregar)

    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    response = RedirectResponse('/', status_code=303)
    return response

#-----------------------------------------------------------------------------------------------------

@router.get("/cliente/{id_cliente}",response_class=JSONResponse)
def ver(id_cliente:int, response:Response,
            request:Request, db: Session = Depends(get_database_session)):
    cuentas = db.query(Cuenta).filter(
                     Cuenta.id_cliente == id_cliente
                 ).all()
    return JSONResponse(jsonable_encoder(cuentas, exclude={'id_proveedor'}))

"""
@router.get("/cliente/{id_cliente}/{id_moneda}",response_class=JSONResponse)
def ver(id_cliente:int, id_moneda: int, response:Response,
            request:Request, db: Session = Depends(get_database_session)):
    cuentas = db.query(Cuenta).filter(
                     sa.or_(
                         Cuenta.id_moneda == id_moneda,
                         Cuenta.is_(None)
                     ),
                     Cuenta.id_cliente == id_cliente
                 ).all()
    return JSONResponse(jsonable_encoder(cuentas, exclude={'id_proveedor'}))
"""

@router.get("/proveedor/{id_proveedor}",response_class=JSONResponse)
def ver_proveedor(id_proveedor:int, response:Response,
            request:Request, db: Session = Depends(get_database_session)):
    cuentas = db.query(Cuenta).filter(
                     Cuenta.id_proveedor == id_proveedor
                 ).all()
    return JSONResponse(jsonable_encoder(cuentas, exclude={'id_cliente'}))

"""
@router.get("/proveedor/{id_proveedor}/{id_moneda}",response_class=JSONResponse)
def ver_proveedor(id_proveedor:int, id_moneda: int, response:Response,
            request:Request, db: Session = Depends(get_database_session)):
    cuentas = db.query(Cuenta).filter(
                     sa.or_(
                         Cuenta.id_moneda == id_moneda,
                         Cuenta.is_(None)
                     ),
                     Cuenta.id_proveedor == id_proveedor
                 ).all()
    return JSONResponse(jsonable_encoder(cuentas, exclude={'id_cliente'}))
"""

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
    clie= db.query(cuenta).get(id)
    depto = db.query(Departamento).all()
    return templates.TemplateResponse("editar_cuenta.html", {"request": request, "cuenta": clie, "Departamentos_lista": depto})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idclie = Form(...), color = Form(...), modelo = Form(...), anho = Form(...), idmarca = Form(...)):
    clie= db.query(cuenta).get(idclie)
    clie.color=color
    clie.modelo=modelo
    clie.anho=anho
    clie.idmarca=idmarca
    db.add(clie)
    db.commit()
    db.refresh(clie)
    response = RedirectResponse('/cuentas/', status_code=303)
    return response

@router.get("/borrar/{id}",response_class=HTMLResponse)
def eliminar(id : int, db: Session = Depends(get_database_session)):
    db.query(cuenta).filter(cuenta.idclie == id).delete()
    db.commit()
    response = RedirectResponse('/cuentas/', status_code=303)
    return response 
