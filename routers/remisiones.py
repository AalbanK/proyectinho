import statistics

from fastapi import (APIRouter, Depends, FastAPI, Form, HTTPException, Request,
                     Response)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, aliased
from starlette import status

from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import (Camion, Marca_camion, Carreta, Marca_carreta, Chofer, Contrato, Producto, Deposito, Remision, Cliente,Factura_venta_cabecera, Ciudad, Departamento)
from routers import auth
from schemas import usuario as us

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/remisiones",
    tags=["remisiones"]
)

@router.get("/")
async def read_remision(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    records = db.query(Remision.idremision, Remision.numero, Remision.fecha_carga, Remision.fecha_descarga, Contrato.nro.label('nro_contrato'), Remision.idchofer
                    , Camion.camion_chapa.label('chapacamion'), Carreta.carreta_chapa.label('chapacarreta'), Producto.descripcion.label('producto'), Remision.neto, Remision.netod, Remision.anulado,
                    ).join(Contrato,Remision.idcontrato==Contrato.idcontrato
                    ).join(Camion, Remision.idcamion==Camion.idcamion
                    ).join(Carreta, Remision.idcarreta==Carreta.idcarreta
                    ).join(Producto,Contrato.idproducto==Producto.idproducto
                    ).join(Deposito,Remision.iddeposito==Deposito.iddeposito, isouter = True #es un left join
                    ).group_by(Remision.idremision, Remision.numero, Remision.fecha_carga, Contrato.nro, Remision.idchofer, Camion.camion_chapa,
                    Carreta.carreta_chapa, Remision.neto, Remision.anulado).all()
    return templates.TemplateResponse("remisiones/listar.html", {"request": request, "usuario_actual": usuario_actual, "data": records, "datatables": True, "filtro_fecha":True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_remision(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    contras=db.query(Contrato).all()
    chofes=db.query(Chofer).all()
    camis=db.query(Camion).all()
    carres=db.query(Carreta).all()
    depos=db.query(Deposito).all()
    return templates.TemplateResponse("remisiones/crear.html", {"request": request, "usuario_actual": usuario_actual, "Contratos_lista":contras, "Choferes_lista":chofes, "Camiones_lista":camis,"Carretas_lista":carres, "Depositos_lista":depos})

@router.post("/nuevo")
async def create_remision(db: Session=Depends(get_database_session),usuario_actual: us.Usuario = Depends(auth.get_usuario_actual),numero=Form(...),fechacarga=Form(...),
                          idcontrato=Form(...), idchofer=Form(...), idcamion=Form(...), idcarreta=Form(...),bruto=Form(...), tara=Form(...),neto=Form(...), iddeposito=Form(...)):

    usu = us.Usuario.from_orm(usuario_actual)
    remi = Remision(numero=numero, fecha_carga=fechacarga, idcontrato=idcontrato, idchofer = idchofer,idcamion=idcamion, idcarreta=idcarreta, iddeposito=iddeposito,
                    bruto=bruto, tara=tara,neto=neto, alta_usuario = usu.idusuario)
    db.add(remi)
    db.commit()
    db.refresh(remi)
    response = RedirectResponse('/', status_code=303)
    return response


@router.get("/ver/{id}")
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    depto_d=aliased(Departamento)
    depto_o=aliased(Departamento)
    ciudad_d=aliased(Ciudad)
    ciudad_o=aliased(Ciudad)
    
    remi = db.query(Remision.idcontrato, Remision.numero, Remision.fecha_carga, Remision.fecha_descarga, Cliente.descripcion.label('desc_cliente'), Cliente.ruc.label('ruc_cliente')
                    , Cliente.direccion.label('dir_cliente'), Factura_venta_cabecera.numero.label('numero_factura')
                    , ciudad_o.descripcion.label('ciudadorigen'), depto_o.descripcion.label('departamentoorigen')
                    , ciudad_d.descripcion.label('ciudaddestino'), depto_d.descripcion.label('departamentodestino')
                    , Remision.idcamion, Marca_camion.descripcion.label('marcacamion'), Camion.camion_chapa, Marca_carreta.descripcion.label('marcacarreta'), Carreta.carreta_chapa
                    , Chofer.nombre, Chofer.apellido, Chofer.ci, Remision.bruto, Remision.tara, Remision.neto, Remision.brutod, Remision.tarad, Remision.netod, Producto.descripcion.label('desc_producto')
                    ).join(Contrato, Remision.idcontrato==Contrato.idcontrato
                    ).join(Cliente, Contrato.idcliente==Cliente.idcliente, isouter=True
                    ).join(Factura_venta_cabecera, Remision.idcontrato==Factura_venta_cabecera.idcontrato, isouter=True
                    ).join(ciudad_o, Contrato.origen==ciudad_o.idciudad
                    ).join(depto_o, ciudad_o.iddepartamento==depto_o.iddepartamento
                    ).join(ciudad_d, Contrato.destino==ciudad_d.idciudad
                    ).join(depto_d, ciudad_d.iddepartamento==depto_d.iddepartamento
                    ).join(Camion, Remision.idcamion==Camion.idcamion
                    ).join(Marca_camion, Camion.idmarca_camion==Marca_camion.idmarca_camion
                    ).join(Carreta, Remision.idcarreta==Carreta.idcarreta
                    ).join(Marca_carreta, Carreta.idmarca_carreta==Marca_carreta.idmarca_carreta
                    ).join(Chofer,Remision.idchofer==Chofer.idchofer
                    ).join(Producto, Contrato.idproducto==Producto.idproducto
                    ).filter(Remision.idremision==id).first()
    print(remi)
    return templates.TemplateResponse("remisiones/ver.html", {"request": request, "usuario_actual": usuario_actual, "Remision":remi})


@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    remi= db.query(Remision).get(id)
    contras=db.query(Contrato).all()
    chofes=db.query(Chofer).all()
    camis=db.query(Camion).all()
    carres=db.query(Carreta).all()
    depos=db.query(Deposito).all()
    return templates.TemplateResponse("remisiones/editar.html", {"request": request, "Remision": remi, "usuario_actual": usuario_actual, "Contratos_lista":contras, "Choferes_lista":chofes, "Camiones_lista":camis,"Carretas_lista":carres, "Depositos_lista":depos})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idremi = Form(...), fechadescarga = Form(...), tarad = Form(), brutod = Form(), netod= Form(), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    remi= db.query(Remision).get(idremi)
    remi.fecha_descarga=fechadescarga
    remi.tarad=tarad
    remi.brutod=brutod
    remi.netod=netod
    remi.modif_usuario = usu.idusuario
    db.add(remi)
    db.commit()
    db.refresh(remi)
    response = RedirectResponse('/remisiones/', status_code=303)
    return response

@router.get("/verificar/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    remision = db.query(Remision).get(id) #obtiene el registro del modelo Remision por su id
    if(remision is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(remision)) #en caso de que exista el registro, lo devuelve en formato json

@router.get("/anular/{id}",response_class=JSONResponse)
def anular(id : int, db: Session = Depends(get_database_session)):
    remi= db.query(Remision).filter(Remision.idremision == id).first()
    remi.anulado='S'
    db.add(remi)
    db.commit()
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro anulado correctamente.") #retorna el codigo http 200
    return response

@router.get("/listar", name="listado_remisiones") # se le da un name para que pueda ser accedido fácilmente desde otros routers
async def listado_remisiones(request: Request, db: Session = Depends(get_database_session)):
    remisiones = db.query(Remision.idremision, Remision.numero, Remision.fecha_carga, Remision.fecha_descarga, Remision.idcontrato,
        Remision.idchofer, Remision.idcamion, Remision.idcarreta, Remision.tara, Remision.bruto, Remision.neto, Remision.iddeposito,
        Remision.brutod, Remision.tarad, Remision.netod, Remision.anulado
        ).order_by(Remision.numero).all()
    return remisiones