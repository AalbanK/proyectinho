import statistics
from schemas import usuario as us
from routers import auth
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, aliased
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from models import Contrato, Producto, Proveedor, Cliente, Cuenta, Departamento, Ciudad
from fastapi.staticfiles import StaticFiles
from starlette import status

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
                          precioCompra=Form(...), precioVenta=Form(...), idProveedor=Form(...),idcuentaC=Form(None), nroCuentaP=Form(None), ciudad_O=Form(...),
                          idCliente=Form(...),idcuentaP=Form(None), nroCuentaC=Form(None),ciudad_D=Form(...), usuario_actual: us.Usuario=Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    campos_a_agregar = {
        "nro": nro,
        "fecha_inicio": FechaInicio,
        "fecha_fin": FechaFin,
        "idproducto": idProducto,
        "cantidad": cantidad,
        "precio_compra": precioCompra,
        "precio_venta": precioVenta,
        "idproveedor": idProveedor,
        "origen": ciudad_O,
        "idcliente": idCliente,
        "destino": ciudad_D
    }
    if idCliente is not None and idCliente != '0':
        campos_a_agregar["cuenta_cliente"] = nroCuentaC
        campos_a_agregar["idcuentaC"] = idcuentaC
    
    if idProveedor is not None and idProveedor != '0':
        campos_a_agregar["cuenta_proveedor"] = nroCuentaP
        campos_a_agregar["idcuentaP"] = idcuentaP
        
    contrato = Contrato(**campos_a_agregar)
    contrato.alta_usuario=usu.idusuario
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/detalles/{idc}", response_class=JSONResponse)
async def ver_detalle_contrato(idc: int, request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    
    depto_O=aliased(Departamento)
    depto_D=aliased(Departamento)
    ciu_O=aliased(Ciudad)
    ciu_D=aliased(Ciudad)
    consulta=db.query(Contrato.idcontrato, Contrato.nro,Contrato.idcliente, Cliente.descripcion.label("desc_cliente"),Contrato.idproveedor, Proveedor.descripcion.label("desc_proveedor"),
                      Contrato.idproducto, Producto.descripcion.label("desc_producto"),Contrato.cantidad, Contrato.origen,ciu_O.descripcion.label("desc_ciudad_origen"),
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
                      ).first()
    return JSONResponse(jsonable_encoder(consulta._asdict()))

@router.get("/ver/{idcontrato}")
async def ver_contrato(idcontrato:int,request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    depto_O=aliased(Departamento)
    depto_D=aliased(Departamento)
    ciu_O=aliased(Ciudad)
    ciu_D=aliased(Ciudad)
    contra = db.query(Contrato.idcontrato, Contrato.nro, Contrato.fecha_inicio, Contrato.fecha_fin, Proveedor.descripcion.label("desc_provee"), Proveedor.ruc.label("ruc_provee"),
                      Cliente.descripcion.label("desc_clie"), Cliente.ruc.label("ruc_clie"), Contrato.idproducto, Producto.descripcion.label("desc_producto"), Contrato.cantidad,
                      Contrato.precio_compra, Contrato.precio_venta, Contrato.cuenta_proveedor, Contrato.cuenta_proveedor,
                      Contrato.origen,ciu_O.descripcion.label("desc_ciudad_origen"), depto_O.descripcion.label("desc_depto_origen"),
                      Contrato.destino,ciu_D.descripcion.label("desc_ciudad_destino"), depto_D.descripcion.label("desc_depto_destino")
                      ).join(Cliente, Cliente.idcliente==Contrato.idcliente
                      ).join(ciu_D,ciu_D.idciudad==Contrato.destino
                      ).join(depto_D,ciu_D.iddepartamento==depto_D.iddepartamento
                      ).join(Proveedor, Proveedor.idproveedor==Contrato.idproveedor
                      ).join(ciu_O,ciu_O.idciudad==Contrato.origen
                      ).join(depto_O,ciu_O.iddepartamento==depto_O.iddepartamento
                      ).join(Producto, Producto.idproducto==Contrato.idproducto
                      ).filter(Contrato.idcontrato == idcontrato
                      ).first()
    return templates.TemplateResponse("contratos/previsualizacion.html", {"request": request, "datatables": True, "usuario_actual": usuario_actual, "Contrato":contra})



@router.get("/todos")
async def listar_contratos(request: Request, usuario_actual: us.Usuario = Depends(auth.get_usuario_actual), db: Session = Depends(get_database_session)):
    ciu_O=aliased(Ciudad)
    ciu_D=aliased(Ciudad)
    contr = db.query(Contrato.idcontrato,Contrato.nro, Contrato.fecha_inicio, Contrato.fecha_fin, Contrato.idproducto, Proveedor.descripcion.label('descripcion_proveedor'),
                     Cliente.descripcion.label('descripcion_cliente'), ciu_O.descripcion.label('ciudad_o'), ciu_D.descripcion.label('ciudad_d'), Producto.descripcion.label('descripcion_producto'),
                     Contrato.cantidad, Contrato.precio_compra, Contrato.precio_venta
                     ).join(Proveedor, Contrato.idproveedor==Proveedor.idproveedor).join(Cliente, Contrato.idcliente==Cliente.idcliente).join(ciu_O, Contrato.origen==ciu_O.idciudad
                     ).join(ciu_D, Contrato.destino==ciu_D.idciudad).join(Producto, Contrato.idproducto==Producto.idproducto
                     ).all()
    respuesta = [dict(r._mapping) for r in contr]
    return JSONResponse(jsonable_encoder(respuesta))