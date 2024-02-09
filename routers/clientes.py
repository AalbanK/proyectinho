from schemas import usuario as us
from routers import auth
import statistics
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session, load_only
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from models import Cliente, Departamento, Ciudad
from fastapi.staticfiles import StaticFiles
from starlette import status

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/clientes",
    tags=["clientes"]
)

@router.get("/")
async def read_cliente(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    #records = db.query(Cliente).all()
    cli = db.query(Cliente.idcliente, Cliente.descripcion, Cliente.ruc,Ciudad.descripcion.label('descripcion_ciudad'),Cliente.direccion, Cliente.mail, Cliente.telefono).join(Ciudad, Cliente.idciudad == Ciudad.idciudad).all()
    return templates.TemplateResponse("clientes/listar.html", {"request": request, "clientes": cli, "datatables": True, "usuario_actual": usuario_actual})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_cliente(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("clientes/crear.html", {"request": request, "usuario_actual": usuario_actual})

@router.post("/nuevo")
async def create_cliente(db: Session = Depends(get_database_session), descripcion = Form(...), ruc = Form(...), idCiudad=Form(...), direccion = Form(...), mail = Form(...), telefono = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    cliente = Cliente(descripcion=descripcion, ruc=ruc, idciudad = idCiudad, direccion=direccion, mail=mail, telefono=telefono, alta_usuario = usu.idusuario)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
            request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    clie = db.query(Cliente).get(id)
    depto = db.query(Departamento).get(int(clie.idDepto))
    return templates.TemplateResponse("clientes/listar.html", {"request": request, "Cliente": clie, "Departamento": depto, "usuario_actual": usuario_actual})

@router.get("/{id}/iddepto",response_class=HTMLResponse)
def obtener_iddepto_cliente(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    clie= db.query(Cliente).get(id)
    refdepto = db.query(Ciudad).options(load_only(Ciudad.iddepartamento)).get(int(clie.idciudad))
    refdepto = refdepto.__dict__.get('iddepartamento')
    respuesta = {'iddepto': refdepto}
    return JSONResponse(content=jsonable_encoder(respuesta))

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    clie= db.query(Cliente).get(id)
    depto = db.query(Departamento).all()
    refdepto = db.query(Ciudad).options(load_only(Ciudad.iddepartamento)).get(int(clie.idciudad))
    return templates.TemplateResponse("clientes/editar.html", {"request": request, "Cliente": clie, "Departamentos_lista": depto, "ref_depto":refdepto, "usuario_actual": usuario_actual})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idcliente = Form(...), descripcion = Form(...), ruc = Form(...), idciudad = Form(...), direccion = Form(...), mail = Form(), telefono = Form(), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    clie= db.query(Cliente).get(idcliente)
    clie.descripcion=descripcion
    clie.ruc=ruc
    clie.idciudad=idciudad
    clie.direccion=direccion
    clie.mail=mail
    clie.telefono=telefono
    clie.modif_usuario = usu.idusuario
    db.add(clie)
    db.commit()
    db.refresh(clie)
    response = RedirectResponse('/clientes/', status_code=303)
    return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    cliente = db.query(Cliente).get(id) #obtiene el registro del modelo Cliente por su id
    if(cliente is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(cliente)) #en caso de que exista el registro, lo devuelve en formato json
    
@router.get("/borrar/{id}",response_class=JSONResponse)
def eliminar(id : int, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    db.query(Cliente).filter(Cliente.idcliente == id).delete()
    db.commit()
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response