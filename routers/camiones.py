from models import Camion, Marca_camion
from schemas import usuario as us
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, FastAPI
import statistics
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette import status
from routers import auth


from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/camiones",
    tags=["camiones"]
)

@router.get("/")
async def read_camion(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    cami = db.query(Camion.idcamion, Camion.camion_chapa, Marca_camion.descripcion.label('descripcion_marca')).join(Marca_camion, Camion.idcamion == Marca_camion.idmarca_camion).all()
    return templates.TemplateResponse("camiones/listar.html", {"request": request, "choferes": cami, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_camion(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    marcas=db.query(Marca_camion).all()
    return templates.TemplateResponse("camiones/crear.html", {"request": request, "Marcas_lista":marcas})

@router.post("/nuevo")
async def create_camion(db: Session = Depends(get_database_session), chapaCamion = Form(...), idmarca_camion = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    camion = Camion(camion_chapa = chapaCamion, idmarca_camion = idmarca_camion, alta_usuario = usu.idusuario)
    db.add(camion)
    db.commit()
    db.refresh(camion)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/todos") #aca la funcion convierte la lista de usuarios en un json que luego se usa en datatable
async def listar_camiones(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    cami = db.query(Camion.idcamion, Camion.camion_chapa, Marca_camion.descripcion.label('descripcion_marca_camion')).join(Marca_camion, Camion.idmarca_camion == Marca_camion.idmarca_camion).all()
    respuesta = [dict(r._mapping) for r in cami]
    return JSONResponse(jsonable_encoder(respuesta)) #devuele el objeto 'usuarios' en formato json

#            al usar {x} se pasa como parametro lo que esta dentro de las llaves (en este caso x)
@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): 
    cami= db.query(Camion).get(id) #obtiene el registro del modelo Usuario por su id
    marcas= db.query(Marca_camion).all()
    return templates.TemplateResponse("camiones/editar.html", {"request": request, "Camion": cami, "Marcas_lista":marcas})  #devuelve el .html de editar

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idcamion = Form(...), camion_chapa = Form(...), idmarca_camion= Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #los names dentro del .html deben llamarse igual que los parametros de esta funcion
    usu = us.Usuario.from_orm(usuario_actual)
    cami= db.query(Camion).get(idcamion) #obtiene el registro del modelo Camion por su id
    cami.camion_chapa = camion_chapa # cambia el valor actual de name del objeto usu por lo que recibe en el parametro 'name'
    cami.idmarca_camion = idmarca_camion
    cami.alta_usuario =  alta_usuario = usu.idusuario
    db.add(cami) #agrega el objeto usu a la base de datos
    db.commit() #confirma los cambios
    db.refresh(cami) #actualiza el objeto usu
    response = RedirectResponse('/camiones/', status_code=303)
    return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    camion = db.query(Camion).get(id) #obtiene el registro del modelo Usuario por su id
    if(camion is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(camion)) #en caso de que exista el registro, lo devuelve en formato json

@router.get("/borrar/{id}",response_class=JSONResponse) #####dependencies=[Depends(auth.verificar_si_usuario_es_superusuario)'''])
def eliminar(id : int, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):#se definen los parametros para la funcion
    db.query(Camion).filter(Camion.idcamion == id).delete() #filtra por id y luego lo elimina
    db.commit()#confirma los cambios
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response