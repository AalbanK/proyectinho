from fastapi import APIRouter
from schemas import usuario as us
from routers import auth
from sqlalchemy.orm import Session, joinedload, load_only
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from models import Deposito, Proveedor, IVA, Contrato, Factura_compra_cabecera, Factura_compra_detalle
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from typing import List

from schemas.cabecera_detalle_compra import Compra_cabecera, Compra_cabecera_Vista

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/compras",
    tags=["compras"]
)

@router.get("/", name="listado_compras")
async def read_compra(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("compras/listar.html", {"request": request, "usuario_actual": usuario_actual, "datatables":True})


@router.get("/nuevo", response_class=HTMLResponse)
async def create_compra(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    proveedores = db.query(Proveedor).all()
    contratos = db.query(Contrato).all()
    depositos = db.query(Deposito).all()
    return templates.TemplateResponse("compras/crear.html", {"request": request, "Proveedores": proveedores, "Contratos": contratos, "Depositos": depositos, "usuario_actual": usuario_actual})

@router.post("/nuevo")
async def crear_compra(request: Request, cabecera: Compra_cabecera, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    print(cabecera)
    usu = us.Usuario.from_orm(usuario_actual)
    try:
        cabecera_compra = Factura_compra_cabecera(**cabecera.dict(exclude = {'detalles'})) # excluye "detalles" porque serán agregados más abajo
        cabecera_compra.alta_usuario = usu.idusuario
        detalles = [detalle.dict() for detalle in cabecera.detalles]
        for detalle in detalles:
            det = Factura_compra_detalle(**detalle)
            det.detalle = cabecera_compra # con esto se hace el FK a la cabecera
        print(cabecera_compra.__dict__)
        db.add(cabecera_compra)
        db.commit()
    except Exception as e:
        response = JSONResponse(content={"error": str(e)}, status_code=500)
        return response
    else: # si no hubo errores
        response = JSONResponse(content={"error": 'Ninguno.'}, status_code=200)
        return response
    

@router.get("/todos")
async def listar_compras(request: Request, usuario_actual: us.Usuario = Depends(auth.get_usuario_actual), db: Session = Depends(get_database_session)):
    """
    vent = db.query(Factura_compra_cabecera.fecha, Factura_compra_cabecera.numero, Contrato.nro.label('nro_contrato'), Proveedor.descripcion.label('descripcion_proveedor'),
                       Factura_compra_detalle.descripcion_producto, Factura_compra_detalle.cantidad, Factura_compra_cabecera.total_monto
                       ).join(Contrato, Factura_compra_cabecera.idcontrato==Contrato.idcontrato).join(Proveedor,Factura_compra_cabecera.idproveedor==Proveedor.idproveedor
                       ).join(Factura_compra_detalle,
                       ).all()
    """
    respuesta = db.query(Factura_compra_cabecera).options(
            joinedload(Factura_compra_cabecera.detalles).load_only(Factura_compra_detalle.descripcion_producto, Factura_compra_detalle.cantidad),
            joinedload(Factura_compra_cabecera.proveedor).load_only(Proveedor.descripcion),
            joinedload(Factura_compra_cabecera.contrato).load_only(Contrato.nro), load_only(Factura_compra_cabecera.idfactura_compra, Factura_compra_cabecera.fecha, Factura_compra_cabecera.numero, Factura_compra_cabecera.total_monto)
        )
    respuesta = respuesta.all()
    
    print(jsonable_encoder(respuesta))
    #respuesta = [dict(r._mapping) for r in vent]
    return JSONResponse(jsonable_encoder(respuesta))

@router.get("/test")
async def listar_compras(request: Request, db: Session = Depends(get_database_session)):
    vent = db.query(Factura_compra_cabecera).all()
    respuesta = [Compra_cabecera_Vista.from_orm(p) for p in vent] # convierte los valores en una lista
    return JSONResponse(jsonable_encoder(respuesta))