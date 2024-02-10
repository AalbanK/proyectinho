from fastapi.encoders import jsonable_encoder
from schemas import usuario as us
from routers import auth
from fastapi import APIRouter
from sqlalchemy.orm import Session, aliased
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from models import Contrato, Producto, Proveedor, Cliente, Cuenta, Departamento, Ciudad
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
async def read_contrato(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    records = db.query(Contrato).all()
    return templates.TemplateResponse("contratos/listar.html", {"request": request, "usuario_actual": usuario_actual, "data": records, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_contrato(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    produs=db.query(Producto).all()
    cius=db.query(Ciudad).all()
    proves=db.query(Proveedor).all()
    clies=db.query(Cliente).all()
    cues=db.query(Cuenta).all()
    return templates.TemplateResponse("contratos/crear.html", {"request": request, "Productos_lista":produs,"Cius_lista":cius,
                                                                "Proveedores_lista":proves, "Clientes_lista":clies, "Cuentas_lista":cues, "usuario_actual": usuario_actual})

@router.post("/nuevo")
async def create_contrato(db: Session=Depends(get_database_session), nro=Form(...), FechaInicio=Form(...),FechaFin=Form(...),idProducto=Form(...), cantidad=Form(...),
                          precioCompra=Form(...), precioVenta=Form(...), idProveedor=Form(...), nroCuentaP=Form(...), ciudad_O=Form(...),
                          idCliente=Form(...), nroCuentaC=Form(...),ciudad_D=Form(...), usuario_actual: us.Usuario=Depends(auth.get_usuario_actual)):
    contrato = Contrato(nro=nro, fecha_inicio=FechaInicio, fecha_fin=FechaFin, idproducto=idProducto, cantidad=cantidad, precio_compra=precioCompra, precio_venta=precioVenta,
                        idproveedor=idProveedor, cuenta_proveedor=nroCuentaP, origen=ciudad_O, idcliente=idCliente, cuenta_cliente=nroCuentaC, destino=ciudad_D)
    campos_a_agregar = {
        "nro": nro,
        "fecha_inicio": FechaInicio,
        "fecha_fin": FechaFin,
        "idproducto": idProducto,
        "cantidad": cantidad,
        "precio_compra": precioCompra,
        "precio_venta": precioVenta,
        "idproveedor": idProveedor,
        "cuenta_proveedor": nroCuentaP,
        "origen": ciudad_O,
        "idcliente": idCliente,
        "cuenta_cliente": nroCuentaC,
        "destino": ciudad_D
    }
    usu = us.Usuario.from_orm(usuario_actual)
    contrato = Contrato(**campos_a_agregar, alta_usuario = usu.idusuario)
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/detalles/{idc}", response_class=JSONResponse)
async def ver_detalle_contrato(idc: int, request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    
    print(idc)
    
    depto_O=aliased(Departamento)
    depto_D=aliased(Departamento)
    ciu_O=aliased(Ciudad)
    ciu_D=aliased(Ciudad)
    consulta=db.query(Contrato.idcliente, Cliente.descripcion.label("desc_cliente"),Contrato.idproveedor, Proveedor.descripcion.label("desc_proveedor"),
                      Contrato.idproducto, Producto.descripcion.label("desc_producto"),Contrato.origen,ciu_O.descripcion.label("desc_ciudad_origen"),
                      depto_O.descripcion.label("desc_depto_origen"), Contrato.destino,ciu_D.descripcion.label("desc_ciudad_destino"),
                      depto_D.descripcion.label("desc_depto_destino")
                      ).join(Cliente, Cliente.idcliente==Contrato.idcliente
                      ).join(ciu_D,ciu_D.idciudad==Contrato.destino
                      ).join(depto_D,ciu_D.iddepartamento==depto_D.iddepartamento
                      ).join(Proveedor, Proveedor.idproveedor==Contrato.idproveedor
                      ).join(ciu_O,ciu_O.idciudad==Contrato.origen
                      ).join(depto_O,ciu_O.iddepartamento==depto_O.iddepartamento
                      ).join(Producto, Producto.idproducto==Contrato.idproducto
                      ).filter(Contrato.idcontrato == idc
                      ).all()

    respuesta = [dict(r._mapping) for r in consulta]
    return JSONResponse(jsonable_encoder(respuesta))

@router.get("/ver")
async def ver_contrato(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("contratos/previsualizacion.html", {"request": request, "datatables": True, "usuario_actual": usuario_actual})