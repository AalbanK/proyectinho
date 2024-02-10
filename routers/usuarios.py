from schemas import usuario as us
from routers import auth
import statistics
from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session, load_only
from fastapi import Depends, FastAPI
from fastapi.templating import Jinja2Templates
from models import Usuario, Rol
from fastapi.staticfiles import StaticFiles
from starlette import status

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

@router.get("/")
async def read_rol(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("usuarios/listar.html", {"request": request, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_usuario(request: Request, db: Session = Depends(get_database_session)):
    rol=db.query(Rol).all()
    return templates.TemplateResponse("usuarios/crear.html", {"request": request, "Roles_lista":rol})

@router.post("/nuevo")
async def create_usuario(db: Session = Depends(get_database_session), nam = Form(...), user = Form(...), pasw = Form(...), idrol = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    usua = Usuario(name=nam, username=user, password=pasw, idrol=idrol, alta_usuario = usu.idusuario)
    db.add(usua)
    db.commit()
    db.refresh(usua)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/todos") #aca la funcion convierte la lista de usuarios en un json que luego se usa en datatable
async def listar_usuarios(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): 
    usuarios = db.query(Usuario).all() #guarda en el objeto 'usuarios' todos los usuarios usando sql alchemy
    usua = db.query(Usuario.idusuario, Usuario.name, Usuario.username, Rol.descripcion.label('descripcion_rol')).join(Rol, Usuario.idrol == Rol.idrol).all()
    respuesta = [dict(r._mapping) for r in usua]
    return JSONResponse(jsonable_encoder(respuesta)) #devuele el objeto 'usuarios' en formato json

#            al usar {x} se pasa como parametro lo que esta dentro de las llaves (en este caso x)
@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): 
    usua= db.query(Usuario).get(id) #obtiene el registro del modelo Usuario por su id
    roles= db.query(Rol).all()
    return templates.TemplateResponse("usuarios/editar.html", {"request": request, "Usuario": usua, "Roles":roles})  #devuelve el .html de editar

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idusuario = Form(...), name = Form(...), username = Form(...), password = Form(...), idrol = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #los names dentro del .html deben llamarse igual que los parametros de esta funcion
    usu = us.Usuario.from_orm(usuario_actual)
    usua= db.query(Usuario).get(idusuario) #obtiene el registro del modelo Usuario por su id
    usua.name = name # cambia el valor actual de name del objeto usu por lo que recibe en el parametro 'name'
    usua.username = username
    usua.password = password
    usua.idrol = idrol
    usua.modif_usuario = usu.idusuario
    db.add(usua) #agrega el objeto usu a la base de datos
    db.commit() #confirma los cambios
    db.refresh(usua) #actualiza el objeto usu
    response = RedirectResponse('/usuarios/', status_code=303)
    return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    usuario = db.query(Usuario).get(id) #obtiene el registro del modelo Usuario por su id
    if(usuario is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(usuario)) #en caso de que exista el registro, lo devuelve en formato json
    
@router.get("/borrar/{id}",response_class=JSONResponse) #####dependencies=[Depends(auth.verificar_si_usuario_es_superusuario)'''])
def eliminar(id : int, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):#se definen los parametros para la funcion
    db.query(Usuario).filter(Usuario.idusuario == id).delete() #filtra por id y luego lo elimina
    db.commit()#confirma los cambios
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response