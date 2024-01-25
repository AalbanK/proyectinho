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

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/productos",
    tags=["productos"]
)

@router.get("/")
async def read_producto(request: Request, db: Session = Depends(get_database_session)):
    records=db.query(Producto).join(IVA).all()
    return templates.TemplateResponse("productos/listar.html", {"request": request, "productos": records, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_producto(request: Request, db: Session = Depends(get_database_session)):
    ivas=db.query(IVA).all()
    return templates.TemplateResponse("productos/crear.html", {"request": request, "Ivas_lista":ivas})

@router.post("/nuevo")
async def create_producto(db: Session = Depends(get_database_session), descProducto = Form(...), idIVA=Form(...)):
    producto = Producto(descripcion=descProducto, idIVA=idIVA)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/todos") #aca la funcion convierte la lista de usuarios en un json que luego se usa en datatable
async def listar_usuarios(request: Request, db: Session = Depends(get_database_session)): 
    usuarios = db.query(Producto).all() #guarda en el objeto 'usuarios' todos los usuarios usando sql alchemy
    return JSONResponse(jsonable_encoder(usuarios)) #devuele el objeto 'usuarios' en formato json

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
    produ= db.query(Producto).get(id)
    iv = db.query(IVA).all()
    return templates.TemplateResponse("productos/editar.html", {"request": request, "Producto": produ, "Ivas_lista": iv})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idproducto = Form(...), descripcion = Form(...), iva = Form(...)):
     produ= db.query(Producto).get(idproducto)
     produ.descripcion=descripcion
     produ.idIVA=iva
     db.add(produ)
     db.commit()
     db.refresh(produ)
     response = RedirectResponse('/productos/', status_code=303)
     return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session)): #se definen los parametros para la funcion
    usuario = db.query(Producto).get(id) #obtiene el registro del modelo Usuario por su id
    if(usuario is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(usuario)) #en caso de que exista el registro, lo devuelve en formato json
    
# @router.get("/{id}",response_class=HTMLResponse)
# def ver(id:int, response:Response,
#             request:Request,db: Session = Depends(get_database_session)):
#     produ = db.query(Producto).get(id)
#     iv = db.query(IVA).get(int(produ.idIVA))
#     return templates.TemplateResponse("productos/listar.html", {"request": request, "Producto": produ, "Iva": iv})


@router.get("/borrar/{id}",response_class=JSONResponse) #####dependencies=[Depends(auth.verificar_si_usuario_es_superusuario)'''])
def eliminar(id : int, db: Session = Depends(get_database_session)):#se definen los parametros para la funcion
    db.query(Producto).filter(Producto.idproducto == id).delete() #filtra por id y luego lo elimina
    db.commit()#confirma los cambios
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response

# @router.get("/borrar/{id}",response_class=HTMLResponse)
# def eliminar(id : int, db: Session = Depends(get_database_session)):
#      db.query(Producto).filter(Producto.idprodu == id).delete()
#      db.commit()
#      response = RedirectResponse('/productos/', status_code=303)
#      return response

