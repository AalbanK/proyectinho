from schemas import usuario as us
from routers import auth
import statistics
from fastapi.encoders import jsonable_encoder
from models import Producto, IVA
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, FastAPI
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette import status
from schemas import producto

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/productos",
    tags=["productos"]
)

@router.get("/")
async def read_producto(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("productos/listar.html", {"request": request, "usuario_actual": usuario_actual, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_producto(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    ivas=db.query(IVA).all()
    return templates.TemplateResponse("productos/crear.html", {"request": request, "usuario_actual": usuario_actual, "Ivas_lista":ivas})

@router.post("/nuevo")
async def create_producto(db: Session = Depends(get_database_session), descProducto = Form(...), idIVA=Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    producto = Producto(descripcion=descProducto, idIVA=idIVA, alta_usuario = usu.idusuario)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/todos") #aca la funcion convierte la lista de usuarios en un json que luego se usa en datatable
async def listar_productos(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): 
    productos=db.query(Producto.idproducto, Producto.descripcion, IVA.porcentaje.label('porcentaje_iva')).join(IVA, Producto.idIVA == IVA.idIVA).all() #guarda en el objeto 'usuarios' todos los usuarios usando sql alchemy
    respuesta = [producto.ProductoBase.from_orm(prod) for prod in productos] # convierte los valores en una lista
    return JSONResponse(jsonable_encoder(respuesta)) #devuele el objeto 'usuarios' en formato json

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    produ= db.query(Producto).get(id)
    iv = db.query(IVA).all()
    return templates.TemplateResponse("productos/editar.html", {"request": request, "usuario_actual": usuario_actual, "Producto": produ, "Ivas_lista": iv})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idproducto = Form(...), descripcion = Form(...), iva = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    produ= db.query(Producto).get(idproducto)
    produ.descripcion=descripcion
    produ.idIVA=iva
    produ.modif_usuario = usu.idusuario
    db.add(produ)
    db.commit()
    db.refresh(produ)
    response = RedirectResponse('/productos/', status_code=303)
    return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    producto = db.query(Producto).get(id) #obtiene el registro del modelo Producto por su id
    if(producto is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(producto)) #en caso de que exista el registro, lo devuelve en formato json
    
@router.get("/borrar/{id}",response_class=JSONResponse) #####dependencies=[Depends(auth.verificar_si_usuario_es_superusuario)'''])
def eliminar(id : int, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):#se definen los parametros para la funcion
    db.query(Producto).filter(Producto.idproducto == id).delete() #filtra por id y luego lo elimina
    db.commit()#confirma los cambios
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response

