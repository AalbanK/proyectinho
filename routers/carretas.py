import statistics

from fastapi import (APIRouter, Depends, FastAPI, Form, HTTPException, Request,
                     Response)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import Carreta, Marca_carreta
from routers import auth
from schemas import usuario as us

app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates= Jinja2Templates(directory="templates")

router=APIRouter(
    prefix="/carretas",
    tags=["carretas"]
)

@router.get("/")
async def read_ccarreta(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    carre = db.query(Carreta.idcarreta, Carreta.carreta_chapa, Marca_carreta.descripcion.label('descripcion_marca')).join(Marca_carreta, Carreta.idcarreta == Marca_carreta.idmarca_carreta).all()
    return templates.TemplateResponse("carretas/listar.html", {"request": request, "carretas": carre, "usuario_actual": usuario_actual, "datatables": True})

@router.get("/nuevo",response_class=HTMLResponse)
async def create_carreta(request:Request,db:Session=Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    marcas=db.query(Marca_carreta).all()
    return templates.TemplateResponse("carretas/crear.html",{"request":request, "Marcas_lista":marcas, "usuario_actual": usuario_actual})

@router.post("/nuevo")
async def create_carreta(db:Session=Depends(get_database_session),chapaCarreta=Form(...), idmarca_carreta = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    carreta=Carreta(carreta_chapa = chapaCarreta, idmarca_carreta = idmarca_carreta, alta_usuario = usu.idusuario)
    db.add(carreta)
    db.commit()
    db.refresh(carreta)
    response=RedirectResponse('/',status_code=303)
    return response

@router.get("/todos") #aca la funcion convierte la lista de usuarios en un json que luego se usa en datatable
async def listar_carretas(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): 
    carre = db.query(Carreta.idcarreta, Carreta.carreta_chapa, Marca_carreta.descripcion.label('descripcion_marca_carreta')).join(Marca_carreta, Carreta.idmarca_carreta == Marca_carreta.idmarca_carreta).all()
    respuesta = [dict(r._mapping) for r in carre]
    return JSONResponse(jsonable_encoder(respuesta)) #devuele el objeto 'usuarios' en formato json

#            al usar {x} se pasa como parametro lo que esta dentro de las llaves (en este caso x)
@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): 
    carre= db.query(Carreta).get(id) #obtiene el registro del modelo Usuario por su id
    marcas= db.query(Marca_carreta).all()
    return templates.TemplateResponse("carretas/editar.html", {"request": request, "Carreta": carre, "Marcas_lista":marcas, "usuario_actual": usuario_actual})  #devuelve el .html de editar

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idcarreta = Form(...), carreta_chapa = Form(...), idmarca_carreta= Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #los names dentro del .html deben llamarse igual que los parametros de esta funcion
    usu = us.Usuario.from_orm(usuario_actual)
    carre= db.query(Carreta).get(idcarreta) #obtiene el registro del modelo Carreta por su id
    carre.carreta_chapa = carreta_chapa # cambia el valor actual de name del objeto usu por lo que recibe en el parametro 'name'
    carre.idmarca_carreta = idmarca_carreta
    carre.modif_usuario = usu.idusuario
    db.add(carre) #agrega el objeto usu a la base de datos
    db.commit() #confirma los cambios
    db.refresh(carre) #actualiza el objeto usu
    response = RedirectResponse('/carretas/', status_code=303)
    return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    carreta = db.query(Carreta).get(id) #obtiene el registro del modelo Usuario por su id
    if(carreta is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(carreta)) #en caso de que exista el registro, lo devuelve en formato json

@router.get("/borrar/{id}",response_class=JSONResponse) #####dependencies=[Depends(auth.verificar_si_usuario_es_superusuario)'''])
def eliminar(id : int, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):#se definen los parametros para la funcion
    db.query(Carreta).filter(Carreta.idcarreta == id).delete() #filtra por id y luego lo elimina
    db.commit()#confirma los cambios
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response