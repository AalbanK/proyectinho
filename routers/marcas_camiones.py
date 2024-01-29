import statistics
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from models import Marca_camion
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from starlette import status

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/marcas_camiones",
    tags=["marcas_camiones"]
)

@router.get("/") #funcion para leer todos los marcas_camiones
async def read_marca_camion(request: Request, db: Session = Depends(get_database_session)):#.TemplateResponse muestra la interfaz (html)
    return templates.TemplateResponse("marcas_camiones/listar.html", {"request": request, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_marca_camion(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("marcas_camiones/crear.html", {"request": request})#.TemplateResponse muestra la interfaz (html)

@router.post("/nuevo") #el action al cual el form llama en el .html crear
async def create_marca_camion(db: Session = Depends(get_database_session), marca_cami_desc = Form(...)):#al agregar una variable = fomrulario (...) lo vuelve obligatorio
    marcacam = Marca_camion(descripcion=marca_cami_desc)#crea el nuevo objeto en python. La variable es el campo que tengo en mi modelo (models.py) y el valor es lo que viene de mi formulario html (atributo name
    db.add(marcacam)#agrega el objeto marcacam a la base de datos
    db.commit()#confirma los cambios
    db.refresh(marcacam)#actualiza el objeto marcacam
    response = RedirectResponse('/', status_code=303)#redirige al inicio..
    return response

@router.get("/todos") #aca la funcion convierte la lista de marcas en un json que luego se usa en datatable
async def listar_marcascam(request: Request, db: Session = Depends(get_database_session)): 
    marcacam = db.query(Marca_camion).all() #guarda en el objeto 'marcacam' todas las marcas_camiones usando sql alchemy
    return JSONResponse(jsonable_encoder(marcacam)) #devuele el objeto 'marcascam' en formato json

#            al usar {x} se pasa como parametro lo que esta dentro de las llaves (en este caso x)
@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)): 
     marcacam= db.query(Marca_camion).get(id) #obtiene el registro del modelo Marca_camion por su id
     return templates.TemplateResponse("marcas_camiones/editar.html", {"request": request, "Marca_camion": marcacam})  #devuelve el .html de editar

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idmarca_camion = Form(...), descripcion = Form(...)): #los names dentro del .html deben llamarse igual que los parametros de esta funcion
     marcacam= db.query(Marca_camion).get(idmarca_camion) #obtiene el registro del modelo Marca_camion por su id
     marcacam.descripcion=descripcion # cambia el valor actual de descripcion del objeto marcacam por lo que recibe en el parametro 'descripcion'
     db.add(marcacam) #agrega el objeto marcacam a la base de datos
     db.commit() #confirma los cambios
     db.refresh(marcacam) #actualiza el objeto marcacam
     response = RedirectResponse('/marcas_camiones/', status_code=303)
     return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session)): #se definen los parametros para la funcion
    marcacam = db.query(Marca_camion).get(id) #obtiene el registro del modelo Marca_camion por su id
    if(marcacam is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(marcacam)) #en caso de que exista el registro, lo devuelve en formato json
    
@router.get("/borrar/{id}",response_class=JSONResponse) #####dependencies=[Depends(auth.verificar_si_usuario_es_superusuario)'''])
def eliminar(id : int, db: Session = Depends(get_database_session)):#se definen los parametros para la funcion
    db.query(Marca_camion).filter(Marca_camion.idmarca_camion == id).delete() #filtra por id y luego lo elimina
    db.commit()#confirma los cambios
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response