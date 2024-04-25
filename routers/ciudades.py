from fastapi import APIRouter, Depends, FastAPI, Form, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from db.misc import get_database_session
from models import Ciudad, Departamento
from routers import auth
from schemas import usuario as us

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/ciudades",
    tags=["ciudades"]
)



@router.get("/")
async def read_ciudad(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    #records = db.query(Ciudad).all()
    records=db.query(Ciudad, Departamento).join(Departamento).all()
    return templates.TemplateResponse("ciudades/listar.html", {"request": request, "data": records, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_ciudad(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    depas=db.query(Departamento).all()
    return templates.TemplateResponse("ciudades/crear.html", {"request": request, "Depas_lista":depas})

@router.post("/nuevo")
async def create_ciudad(db: Session = Depends(get_database_session), descCiudad = Form(...), idDepartamento=Form(...), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    ciudad = Ciudad(descripcion=descCiudad, iddepartamento=idDepartamento)
    db.add(ciudad)
    db.commit()
    db.refresh(ciudad)
    response = RedirectResponse('/', status_code=303)
    return response


@router.get("/todos")
async def listar_ciudades(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    ciudades = db.query(Ciudad).all()
    return JSONResponse(jsonable_encoder(ciudades))




#-----------------------------------------------------------------------------------------------------

"""@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
            request:Request,db: Session = Depends(get_database_session)):
    city = db.query(Ciudad).get(id)
    depto = db.query(Departamento).get(int(city.idDepto))
    return templates.TemplateResponse("ciudades/listar.html", {"request": request, "Ciudad": city, "Departamento": depto})

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
    city= db.query(Ciudad).get(id)
    depto = db.query(Departamento).all()
    return templates.TemplateResponse("editar_ciudad.html", {"request": request, "Ciudad": city, "Departamentos_lista": depto})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idcity = Form(...), color = Form(...), modelo = Form(...), anho = Form(...), idmarca = Form(...)):
    city= db.query(Ciudad).get(idcity)
    city.color=color
    city.modelo=modelo
    city.anho=anho
    city.idmarca=idmarca
    db.add(city)
    db.commit()
    db.refresh(city)
    response = RedirectResponse('/ciudades/', status_code=303)
    return response

@router.get("/borrar/{id}",response_class=HTMLResponse)
def eliminar(id : int, db: Session = Depends(get_database_session)):
    db.query(Ciudad).filter(Ciudad.idcity == id).delete()
    db.commit()
    response = RedirectResponse('/ciudades/', status_code=303)
    return response
"""
