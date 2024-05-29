import statistics

from fastapi import (APIRouter, Depends, FastAPI, Form, HTTPException, Request,
                     Response)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import (Camion, Carreta, Chofer, Contrato, Producto, Proveedor, Deposito, Remision)
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
    records = db.query(Remision.idremision, Remision.numero, Remision.fecha_carga, Contrato.nro.label('nro_contrato'), Remision.idchofer, Camion.camion_chapa.label('chapacamion'), Remision.idcarreta, Remision.neto
                ).join(Contrato,Remision.idcontrato==Contrato.idcontrato
                ).join(Camion, Remision.idcamion==Camion.idcamion
                ).join(Deposito,Remision.iddeposito==Deposito.iddeposito
                ).all()
    return templates.TemplateResponse("remisiones/listar.html", {"request": request, "usuario_actual": usuario_actual, "data": records, "datatables": True})

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

@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
            request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    remi = db.query(Remision).get(id)
    return templates.TemplateResponse("remisiones/listar.html", {"request": request, "Remision": remi, "usuario_actual": usuario_actual})

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    remision = db.query(Remision).get(id) #obtiene el registro del modelo Remision por su id
    if(Remision is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(remision)) #en caso de que exista el registro, lo devuelve en formato json
    
# @router.get("/todos")
# async def listar_remisiones(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):

#     return cue

# Remision.idcuenta, Banco.descripcion.label('desc_banco'),
#                     case((and_(Remision.idcliente.is_(None), Remision.idproveedor.is_not(None)),Proveedor.descripcion.label('desc_RazonSocial')),
#                           (and_(Remision.idcliente.is_not(None), Remision.idproveedor.is_(None)),Remision.descripcion.label('desc_RazonSocial')),
#                            else_= literal('Otros').label('desc_RazonSocial')).label('desc_RazonSocial'), Remision.nro
#                     ).join(Banco, Remision.idbanco==Banco.idbanco
#                     ).join(Remision, Remision.idcliente == Remision.idcliente, isouter = True).join(Proveedor, Remision.idproveedor == Proveedor.idproveedor, isouter = True


@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    remi= db.query(Remision).get(id)
    return templates.TemplateResponse("remisiones/editar.html", {"request": request, "Remision": remi, "usuario_actual": usuario_actual})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idremision = Form(...), numero = Form(...), fecha_carga  = Form(...), fecha_descarga = Form(...), idcontrato = Form(...), 
           idchofer = Form(), idcamion = Form(), idcarreta = Form(), tara = Form(), bruto = Form(), neto = Form(), neto_descarga = Form(), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    remi= db.query(Remision).get(idremision)
    remi.numero
    remi.fecha_carga
    remi.fecha_descarga
    remi.idcontrato
    remi.idchofer
    remi.idcamion
    remi.idcarreta
    remi.tara
    remi.bruto
    remi.neto
    remi.neto_descarga
    remi.modif_usuario = usu.idusuario
    db.add(remi)
    db.commit()
    db.refresh(remi)
    response = RedirectResponse('/clientes/', status_code=303)
    return response