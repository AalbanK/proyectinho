from typing import List

from fastapi import APIRouter, Depends, FastAPI, Form, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, load_only
from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import (IVA, Cliente, Contrato, Deposito, Factura_venta_cabecera,
                    Factura_venta_detalle)
from routers import auth
from schemas import usuario as us
from schemas.cabecera_detalle_venta import Venta_cabecera

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/ventas",
    tags=["ventas"]
)

@router.get("/", name="listado_ventas")
async def read_venta(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("ventas/listar.html", {"request": request, "usuario_actual": usuario_actual, "datatables":True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_venta(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    clientes = db.query(Cliente).all()
    contratos = db.query(Contrato).all()
    depositos = db.query(Deposito).all()
    return templates.TemplateResponse("ventas/crear.html", {"request": request, "usuario_actual": usuario_actual, "Clientes": clientes, "Contratos": contratos, "Depositos": depositos})

@router.post("/nuevo")
async def crear_venta(request: Request, cabecera: Venta_cabecera, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    try:
        cabecera_venta = Factura_venta_cabecera(**cabecera.dict(exclude={'detalles'})) # excluye "detalles" porque serán agregados más abajo
        cabecera_venta.alta_usuario = usu.idusuario
        detalles = [detalle.dict() for detalle in cabecera.detalles]
        #print(detalles)
        for detalle in detalles:
            det = Factura_venta_detalle(**detalle)
            det.detalle = cabecera_venta #con esto se hace el FK a la cabecera
        db.add(cabecera_venta)
        db.commit()
    except Exception as e:
        response = JSONResponse(content={"error": str(e)}, status_code=500)
        return response
    else: # sin no hubo errores
        response = JSONResponse(content={"error": 'Ninguno.'}, status_code=200)
        return response
    
# @router.get("/todos")
# async def listar_ventas(request: Request, usuario_actual: us.Usuario = Depends(auth.get_usuario_actual), db: Session = Depends(get_database_session)):
#     vent = db.query(Factura_venta_cabecera.fecha, Factura_venta_cabecera.numero, Contrato.nro.label('nro_contrato'), Cliente.descripcion.label('descripcion_cliente'),
#                        Factura_venta_detalle.descripcion_producto, Factura_venta_detalle.cantidad, Factura_venta_cabecera.total_monto
#                        ).join(Contrato, Factura_venta_cabecera.idcontrato==Contrato.idcontrato).join(Cliente,Factura_venta_cabecera.idcliente==Cliente.idcliente
#                        ).join(Factura_venta_detalle
#                        ).all()
#     respuesta = [dict(r._mapping) for r in vent]
#     return JSONResponse(jsonable_encoder(respuesta))

@router.get("/todos")
async def listar_venta(request: Request, usuario_actual: us.Usuario = Depends(auth.get_usuario_actual), db: Session = Depends(get_database_session)):

    print('hola')
    respuesta = db.query(Factura_venta_cabecera).options(
            joinedload(Factura_venta_cabecera.detalles).load_only(Factura_venta_detalle.descripcion_producto, Factura_venta_detalle.cantidad),
            joinedload(Factura_venta_cabecera.cliente).load_only(Cliente.descripcion),
            joinedload(Factura_venta_cabecera.contrato).load_only(Contrato.nro), load_only(Factura_venta_cabecera.idfactura_venta, Factura_venta_cabecera.fecha, Factura_venta_cabecera.numero, Factura_venta_cabecera.total_monto)
        )
    respuesta = respuesta.all()
    
    print(jsonable_encoder(respuesta))
    #respuesta = [dict(r._mapping) for r in vent]
    return JSONResponse(jsonable_encoder(respuesta))

    """
    vent = db.query(Factura_compra_cabecera.fecha, Factura_compra_cabecera.numero, Contrato.nro.label('nro_contrato'), Proveedor.descripcion.label('descripcion_proveedor'),
                       Factura_compra_detalle.descripcion_producto, Factura_compra_detalle.cantidad, Factura_compra_cabecera.total_monto
                       ).join(Contrato, Factura_compra_cabecera.idcontrato==Contrato.idcontrato).join(Proveedor,Factura_compra_cabecera.idproveedor==Proveedor.idproveedor
                       ).join(Factura_compra_detalle,
                       ).all()
    """