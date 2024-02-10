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
from models import Proveedor, Departamento, Ciudad
from fastapi.staticfiles import StaticFiles
from starlette import status

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/proveedores",
    tags=["proveedores"]
)

@router.get("/")
async def read_proveedor(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    #records = db.query(Proveedor).all()
    ciud = db.query(Proveedor.idproveedor, Proveedor.descripcion, Proveedor.ruc, Ciudad.descripcion.label('descripcion_ciudad'),Proveedor.direccion, Proveedor.mail, Proveedor.telefono).join(Ciudad, Proveedor.idciudad == Ciudad.idciudad).all()
    return templates.TemplateResponse("proveedores/listar.html", {"request": request, "usuario_actual": usuario_actual, "proveedores": ciud, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_proveedor(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("proveedores/crear.html", {"request": request})

@router.post("/nuevo")
async def create_proveedor(db: Session = Depends(get_database_session), descripcion = Form(...), ruc = Form(...), idCiudad=Form(...), direccion = Form(...), mail = Form(...), telefono = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    proveedor = Proveedor(descripcion=descripcion, idciudad = idCiudad, ruc=ruc, mail=mail, direccion=direccion, telefono=telefono, alta_usuario = usu.idusuario)
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
            request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    prove = db.query(Proveedor).get(id)
    depto = db.query(Departamento).get(int(prove.idDepto))
    return templates.TemplateResponse("proveedores/listar.html", {"request": request, "usuario_actual": usuario_actual, "Proveedor": prove, "Departamento": depto})

@router.get("/{id}/iddepto",response_class=HTMLResponse)
def obtener_iddepto_proveedor(id:int, response:Response, request:Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    prove= db.query(Proveedor).get(id)
    refdepto = db.query(Ciudad).options(load_only(Ciudad.iddepartamento)).get(int(prove.idciudad))
    refdepto = refdepto.__dict__.get('iddepartamento')
    respuesta = {'iddepto': refdepto}
    return JSONResponse(content=jsonable_encoder(respuesta))

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    prove= db.query(Proveedor).get(id)
    depto = db.query(Departamento).all()
    refdepto = db.query(Ciudad).options(load_only(Ciudad.iddepartamento)).get(int(prove.idciudad))
    return templates.TemplateResponse("proveedores/editar.html", {"request": request, "usuario_actual": usuario_actual, "Proveedor": prove, "Departamentos_lista": depto, "ref_depto":refdepto})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idproveedor = Form(...), descripcion = Form(...), ruc = Form(...), idciudad = Form(...), direccion = Form(...), mail = Form(), telefono = Form(), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
        usu = us.Usuario.from_orm(usuario_actual)
        prove= db.query(Proveedor).get(idproveedor)
        prove.descripcion=descripcion
        prove.ruc=ruc
        prove.idciudad=idciudad
        prove.direccion=direccion
        prove.mail=mail
        prove.telefono=telefono
        prove.modif_usuario = usu.idusuario
        db.add(prove)
        db.commit()
        db.refresh(prove)
        response = RedirectResponse('/proveedores/', status_code=303)
        return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    proveedor = db.query(Proveedor).get(id) #obtiene el registro del modelo Cliente por su id
    if(proveedor is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(proveedor)) #en caso de que exista el registro, lo devuelve en formato json

@router.get("/borrar/{id}",response_class=JSONResponse)
def eliminar(id : int, db: Session = Depends(get_database_session)):
    db.query(Proveedor).filter(Proveedor.idproveedor == id).delete()
    db.commit()
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response
