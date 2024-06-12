from datetime import datetime

from fastapi import APIRouter, Body, Depends, FastAPI, Form, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, cast, func, label, literal, or_, union_all
from sqlalchemy.orm import Session, aliased
from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import (IVA, Camion, Carreta, Chofer, Ciudad, Cliente, Contrato, Departamento, Factura_compra_cabecera,
                    Factura_compra_detalle, Factura_venta_cabecera,
                    Factura_venta_detalle, Marca_camion, Marca_carreta, Producto, Proveedor, Remision, Deposito)
from routers import auth
from schemas import reporte
from schemas import usuario as us

from . import clientes as routerclientes
from . import productos as routerproductos
from . import proveedores as routerproveedores
from . import depositos as routerdepositos
from . import remisiones as routerremisiones

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/reportes",
    tags=["reportes"]
)

@router.get("/")
async def mostrar_interfaz_reportes(request: Request, db: Session = Depends(get_database_session), superusuario = Depends(auth.verificar_si_usuario_es_superusuario), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("reportes.html", {"request": request, "usuario_actual": usuario_actual})

@router.get("/stock")
async def mostrar_parametros_stock(request: Request, db: Session = Depends(get_database_session), superusuario = Depends(auth.verificar_si_usuario_es_superusuario), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    productos = await routerproductos.listado_productos(request=request, db=db)
    return templates.TemplateResponse("/reportes/stock.html", {"request": request, "Productos": productos, "datatables": True, "usuario_actual": usuario_actual})

@router.post("/stock")
def mostrar_stock(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual), fecha_desde = Body(), fecha_hasta = Body(), producto = Body(), tipo_movimiento = Body()):

    query_compras = db.query(
        Producto.descripcion.label('descripcion'),
        literal('Compra').label('tipo_movimiento'),
        Factura_compra_detalle.idproducto.label('idproducto'),
        func.sum(Factura_compra_detalle.cantidad).label('cantidad'),
        Factura_compra_cabecera.fecha.label('fecha')
    ).join(Factura_compra_cabecera, Factura_compra_detalle.idcabecera_compra == Factura_compra_cabecera.idfactura_compra
    ).join(Producto, Factura_compra_detalle.idproducto == Producto.idproducto
    ).group_by(Factura_compra_detalle.idproducto, Factura_compra_cabecera.fecha)

    query_ventas = db.query(
        Producto.descripcion.label('descripcion'),
        literal('Venta').label('tipo_movimiento'),
        Factura_venta_detalle.idproducto.label('idproducto'),
        -(func.sum(Factura_venta_detalle.cantidad)).label('cantidad'),
        Factura_venta_cabecera.fecha.label('fecha')
    ).join(Factura_venta_cabecera, Factura_venta_detalle.idcabecera_venta == Factura_venta_cabecera.idfactura_venta
    ).join(Producto, Factura_venta_detalle.idproducto == Producto.idproducto
    ).group_by(Factura_venta_detalle.idproducto, Factura_venta_cabecera.fecha)

    
    # query_remisiones = db.query(
    #     literal('Remision').label('tipo_movimiento'),
    #     Remision.idproducto,
    #     func.sum(Remision.cantidad).label('cantidad'),
    #     Remision.fecha.label('fecha')
    # ).group_by(Remision.idproducto, Remision.fecha)
    

    fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d') if fecha_desde else None
    fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d') if fecha_hasta else None

    # combinar las consultas con union all
    subconsulta = union_all(query_compras, query_ventas).alias('subconsulta')

    # filtrar según parámetros
    consulta_final = db.query(
        subconsulta.c.descripcion,
        subconsulta.c.tipo_movimiento,
        subconsulta.c.idproducto,
        subconsulta.c.cantidad,
        subconsulta.c.fecha
    ).filter(
        and_(
            or_(func.date(subconsulta.c.fecha) >= fecha_desde if fecha_desde else True), # se convierte en true = 1 si fecha_desde es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
            or_(func.date(subconsulta.c.fecha) <= fecha_hasta if fecha_hasta else True), # se convierte en true = 1 si fecha_hasta es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
            or_(subconsulta.c.idproducto == producto if producto else True),
            or_(
                not tipo_movimiento, # para que devuelva "True" en caso de que tipo_movimiento sea nulo
                tipo_movimiento == 'C' and subconsulta.c.tipo_movimiento == 'Compra',
                tipo_movimiento == 'V' and subconsulta.c.tipo_movimiento == 'Venta',
                tipo_movimiento == 'R' and subconsulta.c.tipo_movimiento == 'Remisión',
            )
        )
    )

    # Ejecutar la consulta combinada
    resultado = consulta_final.all()
    respuesta = [reporte.ReporteStockBase.from_orm(fila) for fila in resultado] # convierte los valores en una lista
    #print(jsonable_encoder(respuesta))
    return JSONResponse(jsonable_encoder(respuesta))

@router.get("/ventas")
async def mostrar_parametros_ventas(request: Request, db: Session = Depends(get_database_session), superusuario = Depends(auth.verificar_si_usuario_es_superusuario), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    clientes = await routerclientes.listado_clientes(request=request, db=db)
    productos = await routerproductos.listado_productos(request=request, db=db)
    return templates.TemplateResponse("/reportes/ventas.html", {"request": request, "Clientes": clientes, "Productos": productos, "datatables": True, "usuario_actual": usuario_actual})

@router.post("/ventas")
def mostrar_ventas(request: Request, db: Session = Depends(get_database_session), fecha_desde = Body(), fecha_hasta = Body(), producto = Body(), cliente = Body()):
    
    # select c.idcliente, c.fecha, c.numero, cli.descripcion as descripcion_cliente, 
    # d.idproducto, d.descripcion_producto, d.subtotal 
    # from factura_venta_detalle d 
    # join factura_venta_cabecera c on d.idcabecera_venta = c.idfactura_venta 
    # join cliente cli on c.idcliente = cli.idcliente 
    # group by c.idcliente, c.fecha, c.numero;
    
    consulta = db.query(
        Factura_venta_cabecera.idcliente.label('idcliente'),
        Factura_venta_cabecera.fecha.label('fecha'),
        Factura_venta_cabecera.numero.label('numero'),
        Cliente.descripcion.label('descripcion_cliente'),
        Factura_venta_detalle.idproducto.label('idproducto'),
        Factura_venta_detalle.descripcion_producto.label('descripcion_producto'),
        Factura_venta_detalle.cantidad.label('cantidad'),
        Factura_venta_detalle.subtotal.label('subtotal'),
    ).join(Factura_venta_cabecera, Factura_venta_detalle.idcabecera_venta == Factura_venta_cabecera.idfactura_venta
    ).join(Cliente, Factura_venta_cabecera.idcliente == Cliente.idcliente
    ).group_by(Factura_venta_cabecera.idcliente, Factura_venta_cabecera.fecha, Factura_venta_cabecera.numero
    ).order_by(Factura_venta_cabecera.idcliente, Factura_venta_cabecera.fecha.desc(), Factura_venta_cabecera.numero)
    
    consulta_filtrada = consulta.filter(
        and_(
            or_(func.date(Factura_venta_cabecera.fecha) >= fecha_desde if fecha_desde else True), # se convierte en true = 1 si fecha_desde es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
            or_(func.date(Factura_venta_cabecera.fecha) <= fecha_hasta if fecha_hasta else True), # se convierte en true = 1 si fecha_hasta es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
            or_(Factura_venta_detalle.idproducto == producto if producto else True),
            or_(Factura_venta_cabecera.idcliente == cliente if cliente else True),
        )
    )

    resultado = consulta_filtrada.all()

    respuesta = [reporte.ReporteVentasBase.from_orm(fila) for fila in resultado] # convierte los valores en una lista
    return JSONResponse(jsonable_encoder(respuesta))
    return {}

@router.get("/compras")
async def mostrar_parametros_compras(request: Request, db: Session = Depends(get_database_session), superusuario = Depends(auth.verificar_si_usuario_es_superusuario), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    proveedores = await routerproveedores.listado_proveedores(request=request, db=db)
    productos = await routerproductos.listado_productos(request=request, db=db)
    return templates.TemplateResponse("/reportes/compras.html", {"request": request, "Proveedores": proveedores, "Productos": productos, "datatables": True, "usuario_actual": usuario_actual})

@router.post("/compras")
def mostrar_compras(request: Request, db: Session = Depends(get_database_session), fecha_desde = Body(), fecha_hasta = Body(), producto = Body(), proveedor = Body()):
    
    # select c.idcliente, c.fecha, c.numero, cli.descripcion as descripcion_cliente, 
    # d.idproducto, d.descripcion_producto, d.subtotal 
    # from factura_venta_detalle d 
    # join factura_venta_cabecera c on d.idcabecera_venta = c.idfactura_venta 
    # join cliente cli on c.idcliente = cli.idcliente 
    # group by c.idcliente, c.fecha, c.numero;
    
    consulta = db.query(
        Factura_compra_cabecera.idproveedor.label('idproveedor'),
        Factura_compra_cabecera.fecha.label('fecha'),
        Factura_compra_cabecera.numero.label('numero'),
        Proveedor.descripcion.label('descripcion_proveedor'),
        Factura_compra_detalle.idproducto.label('idproducto'),
        Factura_compra_detalle.descripcion_producto.label('descripcion_producto'),
        Factura_compra_detalle.cantidad.label('cantidad'),
        Factura_compra_detalle.subtotal.label('subtotal'),
    ).join(Factura_compra_cabecera, Factura_compra_detalle.idcabecera_compra == Factura_compra_cabecera.idfactura_compra
    ).join(Proveedor, Factura_compra_cabecera.idproveedor == Proveedor.idproveedor
    ).group_by(Factura_compra_cabecera.idproveedor, Factura_compra_cabecera.fecha, Factura_compra_cabecera.numero
    ).order_by(Factura_compra_cabecera.idproveedor, Factura_compra_cabecera.fecha.desc(), Factura_compra_cabecera.numero)
    
    consulta_filtrada = consulta.filter(
        and_(
            or_(func.date(Factura_compra_cabecera.fecha) >= fecha_desde if fecha_desde else True), # se convierte en true = 1 si fecha_desde es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
            or_(func.date(Factura_compra_cabecera.fecha) <= fecha_hasta if fecha_hasta else True), # se convierte en true = 1 si fecha_hasta es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
            or_(Factura_compra_detalle.idproducto == producto if producto else True),
            or_(Factura_compra_cabecera.idproveedor == proveedor if proveedor else True),
        )
    )

    resultado = consulta_filtrada.all()

    respuesta = [reporte.ReporteComprasBase.from_orm(fila) for fila in resultado] # convierte los valores en una lista
    return JSONResponse(jsonable_encoder(respuesta))

@router.get("/remisiones")
async def mostrar_parametros_remisiones(request: Request, db: Session = Depends(get_database_session), superusuario = Depends(auth.verificar_si_usuario_es_superusuario), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    remisiones = await routerremisiones.listado_remisiones(request=request, db=db)
    productos = await routerproductos.listado_productos(request=request, db=db)
    return templates.TemplateResponse("/reportes/remisiones.html", {"request": request, "Remisiones": remisiones, "Productos": productos, "datatables": True, "usuario_actual": usuario_actual})

@router.post("/remisiones")
def mostrar_remisiones(request: Request, db: Session = Depends(get_database_session), fecha_desde = Body(), fecha_hasta = Body(), producto=Body()):#, producto = Body(), remision = Body()):
    depto_d=aliased(Departamento)
    depto_o=aliased(Departamento)
    ciudad_d=aliased(Ciudad)
    ciudad_o=aliased(Ciudad)

    consulta = db.query(Remision.idremision, Remision.numero, Remision.fecha_carga, Remision.fecha_descarga,  Contrato.nro.label('nro_contrato'), Cliente.descripcion.label('desc_cliente')
                        , ciudad_d.descripcion.label('ciudaddestino'), Camion.camion_chapa.label('chapacamion'), Carreta.carreta_chapa.label('chapacarreta'), Chofer.nombre, Chofer.apellido
                        , Producto.descripcion.label('producto'), Remision.neto, Remision.netod
                        ).join(Contrato, Remision.idcontrato==Contrato.idcontrato
                        ).join(Cliente, Contrato.idcliente==Cliente.idcliente, isouter=True
                        ).join(ciudad_d, Contrato.destino==ciudad_d.idciudad
                        ).join(Camion, Remision.idcamion==Camion.idcamion
                        ).join(Carreta, Remision.idcarreta==Carreta.idcarreta
                        ).join(Chofer,Remision.idchofer==Chofer.idchofer
                        ).join(Producto,Contrato.idproducto==Producto.idproducto
                        ).group_by(Remision.idremision, Remision.fecha_carga,
                        ).order_by(Remision.idremision, Remision.fecha_carga,)
    
    consulta_filtrada = consulta.filter(
        and_(
            or_(func.date(Remision.fecha_carga) >= fecha_desde if fecha_desde else True), # se convierte en true = 1 si fecha_desde es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
            or_(func.date(Remision.fecha_carga) <= fecha_hasta if fecha_hasta else True), # se convierte en true = 1 si fecha_hasta es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
            or_(Contrato.idproducto == producto if producto else True),
        )
    )
    respuesta = [dict(r._asdict()) for r in consulta_filtrada]
    return JSONResponse(jsonable_encoder(respuesta))

@router.get("/depositos")
async def mostrar_parametros_depositos(request: Request, db: Session = Depends(get_database_session), superusuario = Depends(auth.verificar_si_usuario_es_superusuario), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    depositos= await routerdepositos.listado_depositos(request=request, db=db)
    productos = await routerproductos.listado_productos(request=request, db=db)
    proveedores = await routerproveedores.listado_proveedores(request=request, db=db)
    clientes = await routerclientes.listado_clientes(request=request, db=db)
    return templates.TemplateResponse("/reportes/depositos.html", {"request": request, "Depositos":depositos, "Productos": productos, "Proveedores": proveedores, "Clientes": clientes, "datatables": True, "usuario_actual": usuario_actual})

@router.post("/depositos")
def mostrar_depositos(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual), fecha_desde = Body(), fecha_hasta = Body(), deposito = Body(), producto = Body(), tipo_movimiento = Body()):    

    deposito_o=aliased(Deposito)
    deposito_d=aliased(Deposito)

    query_compras = db.query(
        Producto.descripcion.label('descripcion'),
        literal('Compra').label('tipo_movimiento'),
        Factura_compra_cabecera.numero.label('numero_doc'),
        Factura_compra_detalle.idproducto.label('idproducto'),
        func.sum(Factura_compra_detalle.cantidad).label('cantidad'),
        Factura_compra_cabecera.fecha.label('fecha'),
        literal('').label('deposito_origen'),
        deposito_d.descripcion.label('deposito_destino'),
    ).join(Factura_compra_cabecera, Factura_compra_detalle.idcabecera_compra == Factura_compra_cabecera.idfactura_compra
    ).join(Producto, Factura_compra_detalle.idproducto == Producto.idproducto
    ).join(deposito_d, Factura_compra_cabecera.iddeposito == deposito_d.iddeposito
    ).group_by(Factura_compra_cabecera.iddeposito, Factura_compra_detalle.idproducto, Factura_compra_cabecera.fecha
    ).order_by(Factura_compra_cabecera.iddeposito, Factura_compra_detalle.idproducto, Factura_compra_cabecera.fecha)

    query_ventas = db.query(
        Producto.descripcion.label('descripcion'),
        literal('Venta').label('tipo_movimiento'),
        Factura_venta_cabecera.numero.label('numero_doc'),
        Factura_venta_detalle.idproducto.label('idproducto'),
        (func.sum(Factura_venta_detalle.cantidad)).label('cantidad'),
        Factura_venta_cabecera.fecha.label('fecha'),
        deposito_o.descripcion.label('deposito_origen'),
        deposito_d.descripcion.label('deposito_destino'),
    ).join(Factura_venta_cabecera, Factura_venta_detalle.idcabecera_venta == Factura_venta_cabecera.idfactura_venta
    ).join(Producto, Factura_venta_detalle.idproducto == Producto.idproducto
    ).join(deposito_o, Factura_venta_cabecera.iddeposito == deposito_o.iddeposito
    ).join(Factura_compra_cabecera, Factura_venta_cabecera.idcontrato == Factura_compra_cabecera.idcontrato
    ).join(deposito_d, Factura_venta_cabecera.iddeposito == deposito_d.iddeposito
    ).group_by(Factura_venta_cabecera.iddeposito, Factura_venta_detalle.idproducto, Factura_venta_cabecera.fecha
    ).order_by(Factura_venta_cabecera.iddeposito, Factura_venta_detalle.idproducto, Factura_venta_cabecera.fecha)

    
    query_remisiones = db.query(
        Producto.descripcion.label('descripcion'),
        literal('Remisión').label('tipo_movimiento'),
        Remision.numero.label('numero_doc'),
        Contrato.idproducto.label('idproducto'),
        Remision.neto.label('cantidad'),
        Remision.fecha_carga.label('fecha'),
        deposito_o.descripcion.label('deposito_origen'),
        literal('').label('deposito_destino')
    ).join(Contrato, Remision.idcontrato==Contrato.idcontrato
    ).join(Producto, Contrato.idproducto==Producto.idproducto
    ).join(deposito_o, Remision.iddeposito == deposito_o.iddeposito
    ).filter(Remision.anulado != 'S'
    ).order_by(Remision.iddeposito, Contrato.idproducto, Remision.fecha_carga)
    

    print(query_remisiones)
    fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d') if fecha_desde else None
    fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d') if fecha_hasta else None

    # combinar las consultas con union all
    subconsulta = union_all(query_compras , query_ventas, query_remisiones).alias('subconsulta')

    # filtrar según parámetros
    consulta_final = db.query(
        subconsulta.c.descripcion,
        subconsulta.c.tipo_movimiento,
        subconsulta.c.numero_doc,
        subconsulta.c.idproducto,
        subconsulta.c.cantidad,
        subconsulta.c.fecha,
        subconsulta.c.deposito_origen,
        subconsulta.c.deposito_destino,
    ).filter(
        and_(
            or_(func.date(subconsulta.c.fecha) >= fecha_desde if fecha_desde else True), # se convierte en true = 1 si fecha_desde es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
            or_(func.date(subconsulta.c.fecha) <= fecha_hasta if fecha_hasta else True), # se convierte en true = 1 si fecha_hasta es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
            or_(subconsulta.c.deposito == deposito if deposito else True),
            or_(subconsulta.c.idproducto == producto if producto else True),
            or_(
                not tipo_movimiento, # para que devuelva "True" en caso de que tipo_movimiento sea nulo
                tipo_movimiento == 'C' and subconsulta.c.tipo_movimiento == 'Compra',
                tipo_movimiento == 'V' and subconsulta.c.tipo_movimiento == 'Venta',
                tipo_movimiento == 'R' and subconsulta.c.tipo_movimiento == 'Remisión',
            )
        )
    )

    # Ejecutar la consulta combinada
    resultado = consulta_final.all()
    respuesta = [reporte.ReporteStockBase.from_orm(fila) for fila in resultado] # convierte los valores en una lista
    #print(jsonable_encoder(respuesta))
    return JSONResponse(jsonable_encoder(respuesta))

