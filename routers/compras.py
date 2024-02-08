from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from models import Deposito, Proveedor, IVA, Contrato, Factura_compra_cabecera, Factura_compra_detalle, Factura_venta_cabecera, Factura_venta_detalle
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from typing import List

from schemas.cabecera_detalle_compra import Compra_cabecera, Compra_detalle

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/compras",
    tags=["compras"]
)

@router.get("/", name="listado_compras")
async def read_compra(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("compras/listar.html", {"request": request, "datatables":True})

# @router.get("/todos")
# async def listar_compras(request: Request, db: Session = Depends(get_database_session)):
#     compras = db.query(Compra).all()
#     return JSONResponse(jsonable_encoder(compras))

@router.get("/nuevo", response_class=HTMLResponse)
async def create_compra(request: Request, db: Session = Depends(get_database_session)):
    proveedores = db.query(Proveedor).all()
    contratos = db.query(Contrato).all()
    depositos = db.query(Deposito).all()
    return templates.TemplateResponse("compras/crear.html", {"request": request, "Proveedores": proveedores, "Contratos": contratos, "Depositos": depositos})

@router.post("/nuevo")
async def crear_compra(request: Request, cabecera: Compra_cabecera, db: Session = Depends(get_database_session)):
    try:
        cabecera_compra = Factura_compra_cabecera(**cabecera.dict(exclude = {'detalles'})) # excluye "detalles" porque serán agregados más abajo
        detalles = [detalle.dict() for detalle in cabecera.detalles]
        #print(detalles)
        for detalle in detalles:
            det = Factura_compra_detalle(**detalle)
            det.detalle = cabecera_compra # con esto se hace el FK a la cabecera
        db.add(cabecera_compra)
        db.commit()
    except Exception as e:
        response = JSONResponse(content={"error": str(e)}, status_code=500)
        return response
    else: # si no hubo errores
        response = JSONResponse(content={"error": 'Ninguno.'}, status_code=200)
        return response
