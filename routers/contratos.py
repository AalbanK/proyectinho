from schemas import usuario as us
from routers import auth
from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Contrato, Producto, Ciudad, Proveedor, Cliente, Cuenta, Departamento
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
    return templates.TemplateResponse("contratos/listar.html", {"request": request, "data": records, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_contrato(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    produs=db.query(Producto).all()
    cius=db.query(Ciudad).all()
    proves=db.query(Proveedor).all()
    clies=db.query(Cliente).all()
    cues=db.query(Cuenta).all()
    return templates.TemplateResponse("contratos/crear.html", {"request": request, "Productos_lista":produs,"Cius_lista":cius,
                                                                "Proveedores_lista":proves, "Clientes_lista":clies, "Cuentas_lista":cues})

@router.post("/nuevo")
async def create_contrato(db: Session=Depends(get_database_session), nro=Form(...), FechaInicio=Form(...),FechaFin=Form(...),idProducto=Form(...), cantidad=Form(...),
                          precioCompra=Form(...), precioVenta=Form(...), idCiudad=Form(...), idProveedor=Form(...), nroCuentaP=Form(...), ciudad_O=Form(...),
                          idCliente=Form(...), nroCuentaC=Form(...),ciudad_D=Form(...), usuario_actual: us.Usuario=Depends(auth.get_usuario_actual)):
    contrato = Contrato(nro=nro, fecha_inicio=FechaInicio, fecha_fin=FechaFin, idproducto=idProducto, cantidad=cantidad, precio_compra=precioCompra, precio_venta=precioVenta,
                        idproveedor=idProveedor, cuenta_proveedor=nroCuentaP, origen=ciudad_O, idcliente=idCliente, cuenta_cliente=nroCuentaC, destino=ciudad_D)
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/ver")
async def ver_contrato(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("contratos/previsualizacion.html", {"request": request, "datatables": True})
#-----------------------------------------------------------------------------------------------------

# @router.get("/{id}",response_class=HTMLResponse)
# def ver(id:int, response:Response,
#             request:Request,db: Session = Depends(get_database_session)):
#     clie = db.query(Contrato).get(id)
#     depto = db.query(Departamento).get(int(clie.idDepto))
#     return templates.TemplateResponse("contratos/listar.html", {"request": request, "Contrato": clie, "Departamento": depto})

# @router.get("/editar/{id}",response_class=HTMLResponse)
# def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
#     clie= db.query(Contrato).get(id)
#     depto = db.query(Departamento).all()
#     return templates.TemplateResponse("editar_contrato.html", {"request": request, "Contrato": clie, "Departamentos_lista": depto})

# @router.post("/update",response_class=HTMLResponse)
# def editar(db: Session = Depends(get_database_session), idclie = Form(...), color = Form(...), modelo = Form(...), anho = Form(...), idmarca = Form(...)):
#     clie= db.query(Contrato).get(idclie)
#     clie.color=color
#     clie.modelo=modelo
#     clie.anho=anho
#     clie.idmarca=idmarca
#     db.add(clie)
#     db.commit()
#     db.refresh(clie)
#     response = RedirectResponse('/contratos/', status_code=303)
#     return response

# @router.get("/borrar/{id}",response_class=HTMLResponse)
# def eliminar(id : int, db: Session = Depends(get_database_session)):
#     db.query(Contrato).filter(Contrato.idclie == id).delete()
#     db.commit()
#     response = RedirectResponse('/contratos/', status_code=303)
#     return response
