import statistics
from typing import List

from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from starlette import status
from sqlalchemy.orm import Session, joinedload, load_only
from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import (IVA, Cliente, Contrato, Deposito, Factura_venta_cabecera, Factura_venta_detalle)
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

#funcion para verificar si ya existe el número de factura y timbrado en la bd
def buscar_nro(numero:str, timbrado:int, request:Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    fact_venta = db.query(Factura_venta_cabecera).filter_by(numero=numero, timbrado=timbrado).first()
    print(fact_venta)
    return fact_venta

@router.get("/", name="listado_ventas")
async def read_venta(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("ventas/listar.html", {"request": request, "usuario_actual": usuario_actual, "datatables":True, "filtro_fecha":True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_venta(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    clientes = db.query(Cliente).all()
    contratos = db.query(Contrato).all()
    depositos = db.query(Deposito).all()
    return templates.TemplateResponse("ventas/crear.html", {"request": request, "usuario_actual": usuario_actual, "Clientes": clientes, "Contratos": contratos, "Depositos": depositos})

@router.post("/nuevo")
async def crear_venta(request: Request, cabecera: Venta_cabecera, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    print(cabecera)
    usu = us.Usuario.from_orm(usuario_actual)
    try:
        cabecera_venta = Factura_venta_cabecera(**cabecera.dict(exclude={'detalles'})) # excluye "detalles" porque serán agregados más abajo
        if buscar_nro(numero=cabecera_venta.numero, timbrado=cabecera_venta.timbrado, request=request, db=db, usuario_actual=usuario_actual) is None:
            cabecera_venta.alta_usuario = usu.idusuario
            detalles = [detalle.dict() for detalle in cabecera.detalles]
            for detalle in detalles:
                det = Factura_venta_detalle(**detalle)
                det.detalle = cabecera_venta #con esto se hace el FK a la cabecera
                print(cabecera_venta.__dict__)
            db.add(cabecera_venta)
            db.commit()
        else:
            response= JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error":"El número de factura y timbrado ingresado ya se utilizó."})
            return response
    except Exception as e:
        response = JSONResponse(content={"error": str(e)}, status_code=500)
        return response
    else: # sin no hubo errores
        response = JSONResponse(content={"error": 'Ninguno.'}, status_code=200)
        return response

@router.get("/todos")
async def listar_venta(request: Request, usuario_actual: us.Usuario = Depends(auth.get_usuario_actual), db: Session = Depends(get_database_session)):
    respuesta = db.query(Factura_venta_cabecera).options(
            joinedload(Factura_venta_cabecera.detalles).load_only(Factura_venta_detalle.descripcion_producto, Factura_venta_detalle.cantidad),
            joinedload(Factura_venta_cabecera.cliente).load_only(Cliente.descripcion),
            joinedload(Factura_venta_cabecera.contrato).load_only(Contrato.nro), load_only(Factura_venta_cabecera.idfactura_venta, Factura_venta_cabecera.fecha, Factura_venta_cabecera.numero, Factura_venta_cabecera.total_monto, Factura_venta_cabecera.anulado)
        )
    respuesta = respuesta.all()
    
    print(jsonable_encoder(respuesta))
    #respuesta = [dict(r._mapping) for r in vent]
    return JSONResponse(jsonable_encoder(respuesta))

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    venta = db.query(Factura_venta_cabecera).get(id) #obtiene el registro del modelo venta por su id
    if(venta is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(venta)) #en caso de que exista el registro, lo devuelve en formato json
    
@router.get("/anular/{id}",response_class=JSONResponse)
def anular(id : int, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    venta= db.query(Factura_venta_cabecera).filter(Factura_venta_cabecera.idfactura_venta == id)
    print(venta)
    venta=venta.first()
    
    venta.anulado='S'
    venta.modif_usuario = usu.idusuario
    db.add(venta)
    db.commit()
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro anulado correctamente.") #retorna el codigo http 200
    return response