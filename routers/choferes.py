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
from models import Chofer, Departamento, Ciudad
from fastapi.staticfiles import StaticFiles
from starlette import status

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/choferes",
    tags=["choferes"]
)

@router.get("/")
async def read_chofer(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    #records = db.query(Chofer).all()
    ciud = db.query(Chofer.idchofer, Chofer.ci, Chofer.nombre, Chofer.apellido, Ciudad.descripcion.label('descripcion_ciudad'), Chofer.telefono).join(Ciudad, Chofer.idciudad == Ciudad.idciudad).all()
    return templates.TemplateResponse("choferes/listar.html", {"request": request, "choferes": ciud, "datatables": True, "usuario_actual": usuario_actual})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_chofer(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    city=db.query(Ciudad).all()
    depas=db.query(Departamento).all()
    return templates.TemplateResponse("choferes/crear.html", {"request": request, "Depas_lista":depas, "Citys_lista":city, "usuario_actual": usuario_actual})

@router.post("/nuevo")
async def create_chofer(db: Session = Depends(get_database_session), chofe_ci = Form(...), chofe_nom=Form(...), chofe_ape=Form(...), idCiudad=Form(...), chofe_tel=Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    chofer = Chofer(ci=chofe_ci, nombre=chofe_nom, apellido=chofe_ape, idciudad=idCiudad, telefono=chofe_tel, alta_usuario = usu.idusuario)
    db.add(chofer)
    db.commit()
    db.refresh(chofer)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
            request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    chofe = db.query(Chofer).get(id)
    depto = db.query(Departamento).get(int(chofe.idDepto))
    return templates.TemplateResponse("clientes/listar.html", {"request": request, "Chofer": chofe, "Departamento": depto, "usuario_actual": usuario_actual})

@router.get("/{id}/iddepto",response_class=JSONResponse)
def obtener_iddepto_chofer(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    chofe= db.query(Chofer).get(id)
    refdepto = db.query(Ciudad).options(load_only(Ciudad.iddepartamento)).get(int(chofe.idciudad))
    refdepto = refdepto.__dict__.get('iddepartamento')
    respuesta = {'iddepto': refdepto}
    return JSONResponse(content=jsonable_encoder(respuesta))

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    chofe= db.query(Chofer).get(id)
    depto = db.query(Departamento).all()
    refdepto = db.query(Ciudad).options(load_only(Ciudad.iddepartamento)).get(int(chofe.idciudad))
    return templates.TemplateResponse("choferes/editar.html", {"request": request, "Chofer": chofe, "Departamentos_lista": depto, "ref_depto":refdepto, "usuario_actual": usuario_actual})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idchofer = Form(...), ci = Form(...), nombre = Form(...), apellido = Form(...), idciudad = Form(...), telefono = Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    chof= db.query(Chofer).get(idchofer)
    chof.idchofer=idchofer
    chof.ci=ci
    chof.nombre=nombre
    chof.apellido=apellido
    chof.idciudad=idciudad
    chof.telefono=telefono
    chof.modif_usuario = usu.idusuario
    db.add(chof)
    db.commit()
    db.refresh(chof)
    response = RedirectResponse('/choferes/', status_code=303)
    return response

@router.get("/ver/{id}",response_class=JSONResponse) #esta ruta es para la funcion que se utiliza en el Datatable para verificar si el registro a ser eliminado realmente existe en la base de datos
def ver(id:int, response:Response, request:Request,db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)): #se definen los parametros para la funcion
    chofer = db.query(Chofer).get(id) #obtiene el registro del modelo Cliente por su id
    if(chofer is None): #en caso de que no exista el registro correpondiente al id recibido como parametro devuelve el siguiente error
        return HTTPException(status_code=statistics.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(chofer)) #en caso de que exista el registro, lo devuelve en formato json

@router.get("/borrar/{id}",response_class=JSONResponse)
def eliminar(id : int, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    db.query(Chofer).filter(Chofer.idchofer == id).delete()
    db.commit()
    response = HTTPException(status_code=status.HTTP_200_OK, detail="Registro eliminado correctamente.") #retorna el codigo http 200
    return response
