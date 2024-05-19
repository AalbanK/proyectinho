import statistics

from fastapi import (APIRouter, Depends, FastAPI, Form, HTTPException, Request,
                     Response)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload, load_only
from starlette import status
from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import Deposito, Deposito_y_producto, Producto
from routers import auth
from schemas import usuario as us

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/depositos",
    tags=["depositos"]
)

@router.get("/")
async def read_depositos(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #funcion para leer todos los depositos
    return templates.TemplateResponse("depositos/listar.html", {"request": request, "usuario_actual": usuario_actual, "datatables": True}) #.TemplateResponse muestra la interfaz (html)

@router.get("/nuevo", response_class=HTMLResponse)
async def create_deposito(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("depositos/crear.html", {"request": request, "usuario_actual": usuario_actual}) #.TemplateResponse muestra la interfaz (html)

@router.post("/nuevo") #el action al cual el form llama en el .html crear
async def create_deposito(db: Session = Depends(get_database_session), descripcion = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #al agregar una variable = fomrulario (...) lo vuelve obligatorio
    usu = us.Usuario.from_orm(usuario_actual)
    deposito = Deposito(descripcion=descripcion, alta_usuario = usu.idusuario) #crea el nuevo objeto en python. La variable es el campo que tengo en mi modelo (models.py) y el valor es lo que viene de mi formulario html (atributo name)
    db.add(deposito) #agrega el objeto deposito a la base de datos
    db.commit() #confirma los cambios
    db.refresh(deposito) #actualiza el objeto deposito
    response = RedirectResponse('/', status_code=303) #redirige al inicio...
    return response

@router.get("/todos") #aca la funcion convierte la lista de depositos en un json que luego se usa en datatable
async def listar_depositos(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): 
    #depositos = db.query(Deposito).all() #guarda en el objeto 'depositos' todos los depositos usando sql alchemy
    depositos = db.query(Deposito).options(
            joinedload(Deposito.deposito_y_producto).load_only(Deposito_y_producto.idproducto, Deposito_y_producto.cantidad),
            #joinedload(Deposito_y_producto.producto).load_only(Producto.descripcion)
        ).join(Producto, Producto.idproducto==Deposito_y_producto.idproducto)
    
    depositos = depositos.all()
    return JSONResponse(jsonable_encoder(depositos)) #devuele el objeto 'depositos' en formato json

#            al usar {x} se pasa como parametro lo que esta dentro de las llaves (en este caso x)
@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): 
    dep= db.query(Deposito).get(id) #obtiene el registro del modelo Deposito por su id
    return templates.TemplateResponse("depositos/editar.html", {"request": request, "Deposito": dep, "usuario_actual": usuario_actual})  #devuelve el .html de editar

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), iddeposito = Form(...), descripcion = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #los names dentro del .html deben llamarse igual que los parametros de esta funcion
    usu = us.Usuario.from_orm(usuario_actual)
    dep= db.query(Deposito).get(iddeposito) #obtiene el registro del modelo Deposito por su id
    dep.descripcion=descripcion # cambia el valor actual de descripcion del objeto dep por lo que recibe en el parametro 'descripcion'
    dep.modif_usuario=usu.idusuario
    db.add(dep) #agrega el objeto dep a la base de datos
    db.commit() #confirma los cambios
    db.refresh(dep) #actualiza el objeto dep
    response = RedirectResponse('/depositos/', status_code=303)
    return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    deposito = db.query(Deposito).get(id) #obtiene el registro del modelo Deposito por su id
    if(deposito is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(deposito)) #en caso de que exista el registro, lo devuelve en formato json
    
@router.get("/borrar/{id}",response_class=JSONResponse) #####dependencies=[Depends(auth.verificar_si_usuario_es_superusuario)'''])
def eliminar(id : int, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):#se definen los parametros para la funcion
    db.query(Deposito).filter(Deposito.iddeposito == id).delete() #filtra por id y luego lo elimina
    db.commit()#confirma los cambios
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response