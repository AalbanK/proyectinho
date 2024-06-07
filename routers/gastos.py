from typing import List
import statistics

from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, load_only
from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import (IVA, Contrato, Factura_gasto_cabecera, Factura_gasto_detalle, Proveedor)
from routers import auth
from schemas import usuario as us
from schemas.cabecera_detalle_gasto import (Gasto_cabecera, Gasto_cabecera_Vista)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/gastos",
    tags=["gastos"]
)

#funcion para verificar si ya existe el número de factura y timbrado en la bd
def buscar_nro(numero:str, timbrado:int, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    fact_gasto = db.query(Factura_gasto_cabecera).filter_by(numero=numero, timbrado=timbrado).first()
    return fact_gasto

@router.get("/", name="listado_gastos")
async def read_gasto(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("gastos/listar.html", {"request": request, "usuario_actual": usuario_actual, "datatables":True, "filtro_fecha":True})


@router.get("/nuevo", response_class=HTMLResponse)
async def create_gasto(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    proveedores = db.query(Proveedor).all()
    contratos = db.query(Contrato).all()
    return templates.TemplateResponse("gastos/crear.html", {"request": request, "Proveedores": proveedores, "Contratos": contratos, "usuario_actual": usuario_actual})

@router.post("/nuevo")
async def crear_gasto(request: Request, cabecera: Gasto_cabecera, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    print(cabecera)
    usu = us.Usuario.from_orm(usuario_actual)
    try:
        cabecera_gasto = Factura_gasto_cabecera(**cabecera.dict(exclude = {'detalles'})) # excluye "detalles" porque serán agregados más abajo
        if buscar_nro(numero=cabecera_gasto.numero, timbrado=cabecera_gasto.timbrado, request=request, db=db, usuario_actual=usuario_actual) is None: #si es "None" significa que no existe
            cabecera_gasto.alta_usuario = usu.idusuario
            detalles = [detalle.dict() for detalle in cabecera.detalles]
            for detalle in detalles:
                det = Factura_gasto_detalle(**detalle)
                det.detalle = cabecera_gasto # con esto se hace el FK a la cabecera
            print(cabecera_gasto.__dict__)
            db.add(cabecera_gasto)
            db.commit()
        else:
            response= JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error":"El número de factura y timbrado ingresados ya existen."})
            return response
    except Exception as e:
        response = JSONResponse(content={"error": str(e)}, status_code=500)
        return response
    else: # si no hubo errores
        response = JSONResponse(content={"error": 'Ninguno.'}, status_code=200)
        return response
    

@router.get("/todos")
async def listar_gastos(request: Request, usuario_actual: us.Usuario = Depends(auth.get_usuario_actual), db: Session = Depends(get_database_session)):
    respuesta = db.query(Factura_gasto_cabecera).options(
            joinedload(Factura_gasto_cabecera.detalles).load_only(Factura_gasto_detalle.descripcion_producto, Factura_gasto_detalle.cantidad),
            joinedload(Factura_gasto_cabecera.proveedor).load_only(Proveedor.descripcion),
            joinedload(Factura_gasto_cabecera.contrato).load_only(Contrato.nro), load_only(Factura_gasto_cabecera.idfactura_gasto, Factura_gasto_cabecera.fecha, Factura_gasto_cabecera.numero, Factura_gasto_cabecera.total_monto, Factura_gasto_cabecera.anulado)
        )
    respuesta = respuesta.all()
    
    print(jsonable_encoder(respuesta))
    #respuesta = [dict(r._mapping) for r in vent]
    return JSONResponse(jsonable_encoder(respuesta))

@router.get("/test")
async def listar_gastos(request: Request, db: Session = Depends(get_database_session)):
    vent = db.query(Factura_gasto_cabecera).all()
    respuesta = [Gasto_cabecera_Vista.from_orm(p) for p in vent] # convierte los valores en una lista
    return JSONResponse(jsonable_encoder(respuesta))

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    compra = db.query(Factura_gasto_cabecera).get(id) #obtiene el registro del modelo Compra por su id
    if(compra is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(compra)) #en caso de que exista el registro, lo devuelve en formato json
    
@router.get("/anular/{id}",response_class=JSONResponse)
def anular(id : int, db: Session = Depends(get_database_session)):
    gasto= db.query(Factura_gasto_cabecera).filter(Factura_gasto_cabecera.idfactura_gasto == id).first()
    gasto.anulado='S'
    db.add(gasto)
    db.commit()
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro anulado correctamente.") #retorna el codigo http 200
    return response