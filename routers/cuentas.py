from models import Cuenta, Banco, Cliente, Proveedor
from schemas import usuario as us
from fastapi import APIRouter, Depends, Request, Form, Response, FastAPI
import statistics
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import and_, case, literal
from starlette.responses import RedirectResponse
from starlette import status
from routers import auth

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/cuentas",
    tags=["cuentas"]
)

@router.get("/")
async def read_cuenta(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    
    return templates.TemplateResponse("cuentas/listar.html", {"request": request, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_cuenta(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    bancos = db.query(Banco).all()
    clientes = db.query(Cliente).all()
    proveedores = db.query(Proveedor).all()
    return templates.TemplateResponse("cuentas/crear.html", {"request": request, "Proveedores_lista": proveedores, "Clientes_lista": clientes, "Bancos_lista": bancos})

@router.post("/nuevo")
async def create_cuenta(db: Session = Depends(get_database_session), nroCuenta = Form(...), idCliente=Form(), idProveedor = Form(), idBanco = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    
    campos_a_agregar = {
        "nro": nroCuenta, 
        "idbanco": idBanco
    }
    
    # Ya que debe ser o cliente o proveedor
    if idCliente is not None and idCliente != '0':
        campos_a_agregar["idcliente"] = idCliente

    if idProveedor is not None and idProveedor != '0':
        campos_a_agregar["idproveedor"] = idProveedor

    usu = us.Usuario.from_orm(usuario_actual)
    cue = Cuenta(**campos_a_agregar, alta_usuario = usu.idusuario)
    db.add(cue)
    db.commit()
    db.refresh(cue)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/cliente/{id_cliente}",response_class=JSONResponse)
def ver(id_cliente:int, response:Response,request:Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    cuentas = db.query(Cuenta).filter(
                     Cuenta.id_cliente == id_cliente
                 ).all()
    return JSONResponse(jsonable_encoder(cuentas, exclude={'id_proveedor'}))

@router.get("/proveedor/{id_proveedor}",response_class=JSONResponse)
def ver_proveedor(id_proveedor:int, response:Response, request:Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    cuentas = db.query(Cuenta).filter(
                     Cuenta.id_proveedor == id_proveedor
                 ).all()
    return JSONResponse(jsonable_encoder(cuentas, exclude={'id_cliente'}))

@router.get("/todos")
async def listar_cuentas(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    cue = db.query(Cuenta.idcuenta, Banco.descripcion.label('desc_banco'),
                    case((and_(Cuenta.idcliente.is_(None), Cuenta.idproveedor.is_not(None)),Proveedor.descripcion.label('desc_RazonSocial')),
                          (and_(Cuenta.idcliente.is_not(None), Cuenta.idproveedor.is_(None)),Cliente.descripcion.label('desc_RazonSocial')),
                           else_= literal('Otros').label('desc_RazonSocial')).label('desc_RazonSocial'), Cuenta.nro
                    ).join(Banco, Cuenta.idbanco==Banco.idbanco
                    ).join(Cliente, Cuenta.idcliente == Cliente.idcliente, isouter = True).join(Proveedor, Cuenta.idproveedor == Proveedor.idproveedor, isouter = True
                    ).all()
    respuesta = [dict(r._mapping) for r in cue]
    return JSONResponse(jsonable_encoder(respuesta))

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    cue= db.query(Cuenta).get(id)
    depto = db.query(Departamento).all()
    return templates.TemplateResponse("editar_cuenta.html", {"request": request, "cuenta": cue, "Departamentos_lista": depto})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idCuenta = Form(...), idBanco = Form(...), idCliente = Form(...), idProveedor = Form(...), nro = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    cue= db.query(Cuenta).get(idCuenta)
    cue.idbanco=idBanco
    cue.idcliente=idCliente
    cue.idproveedor=idProveedor
    cue.nro=nro
    db.add(cue)
    db.commit()
    db.refresh(cue)
    response = RedirectResponse('/cuentas/', status_code=303)
    return response

@router.get("/borrar/{id}",response_class=HTMLResponse)
def eliminar(id : int, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    db.query(Cuenta).filter(Cuenta.idclie == id).delete()
    db.commit()
    response = RedirectResponse('/cuentas/', status_code=303)
    return response