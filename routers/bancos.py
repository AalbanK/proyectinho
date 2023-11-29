import statistics
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Banco
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, Response
from starlette import status

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/bancos",
    tags=["bancos"]
)

@router.get("/")
async def read_bancos(request: Request, db: Session = Depends(get_database_session)): #funcion para leer todos los bancos
    return templates.TemplateResponse("bancos/listar.html", {"request": request, "datatables": True}) #.TemplateResponse muestra la interfaz (html)

@router.get("/nuevo", response_class=HTMLResponse)
async def create_banco(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("bancos/crear.html", {"request": request}) #.TemplateResponse muestra la interfaz (html)

@router.post("/nuevo") #el action al cual el form llama en el .html crear
async def create_banco(db: Session = Depends(get_database_session), descripcion = Form(...)): #al agregar una variable = fomrulario (...) lo vuelve obligatorio
    banco = Banco(descripcion=descripcion) #crea el nuevo objeto en python. La variable es el campo que tengo en mi modelo (models.py) y el valor es lo que viene de mi formulario html (atributo name)
    db.add(banco) #agrega el objeto banco a la base de datos
    db.commit() #confirma los cambios
    db.refresh(banco) #actualiza el objeto banco
    response = RedirectResponse('/', status_code=303) #redirige al inicio...
    return response

@router.get("/todos") #aca la funcion convierte la lista de bancos en un json que luego se usa en datatable
async def listar_bancos(request: Request, db: Session = Depends(get_database_session)): 
    bancos = db.query(Banco).all() #guarda en el objeto 'bancos' todos los bancos usando sql alchemy
    return JSONResponse(jsonable_encoder(bancos)) #devuele el objeto 'bancos' en formato json

#            al usar {x} se pasa como parametro lo que esta dentro de las llaves (en este caso x)
@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)): 
     banc= db.query(Banco).get(id) #obtiene el registro del modelo Banco por su id
     return templates.TemplateResponse("bancos/editar.html", {"request": request, "Banco": banc})  #devuelve el .html de editar

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idbanco = Form(...), descripcion = Form(...)): #los names dentro del .html deben llamarse igual que los parametros de esta funcion
     banc= db.query(Banco).get(idbanco) #obtiene el registro del modelo Banco por su id
     banc.descripcion=descripcion # cambia el valor actual de descripcion del objeto banc por lo que recibe en el parametro 'descripcion'
     db.add(banc) #agrega el objeto banc a la base de datos
     db.commit() #confirma los cambios
     db.refresh(banc) #actualiza el objeto banc
     response = RedirectResponse('/bancos/', status_code=303)
     return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session)): #se definen los parametros para la funcion
    banco = db.query(Banco).get(id) #obtiene el registro del modelo Banco por su id
    if(banco is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(banco)) #en caso de que exista el registro, lo devuelve en formato json
    
@router.get("/borrar/{id}",response_class=JSONResponse) #####dependencies=[Depends(auth.verificar_si_usuario_es_superusuario)'''])
def eliminar(id : int, db: Session = Depends(get_database_session)):#se definen los parametros para la funcion
    db.query(Banco).filter(Banco.idbanco == id).delete() #filtra por id y luego lo elimina
    db.commit()#confirma los cambios
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response