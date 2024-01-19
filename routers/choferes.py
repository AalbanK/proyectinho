from fastapi import APIRouter
from sqlalchemy.orm import Session, load_only
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Chofer, Departamento, Ciudad
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/choferes",
    tags=["choferes"]
)

# @router.get("/")
# async def read_chofer(request: Request, db: Session = Depends(get_database_session)):
#     records = db.query(Chofer, Departamento, Ciudad).join(Ciudad, Departamento).all()
#     return templates.TemplateResponse("choferes/listar.html", {"request": request, "data": records})

@router.get("/")
async def read_chofer(request: Request, db: Session = Depends(get_database_session)):
    #records = db.query(Chofer).all()
    ciud = db.query(Chofer.idchofer, Chofer.ci, Chofer.nombre,Ciudad.descripcion.label('descripcion_ciudad'),Chofer.telefono).join(Ciudad, Chofer.idciudad == Ciudad.idciudad).all()
    print(ciud)
    return templates.TemplateResponse("choferes/listar.html", {"request": request, "choferes": ciud})


@router.get("/nuevo", response_class=HTMLResponse)
async def create_chofer(request: Request, db: Session = Depends(get_database_session)):
    city=db.query(Ciudad).all()
    depas=db.query(Departamento).all()
    return templates.TemplateResponse("choferes/crear.html", {"request": request, "Depas_lista":depas, "Citys_lista":city})

@router.post("/nuevo")
async def create_chofer(db: Session = Depends(get_database_session), chofe_ci = Form(...), chofe_nom=Form(...), chofe_ape=Form(...), idCiudad=Form(...), chofe_tel=Form(...)):
    chofer = Chofer(ci=chofe_ci, nombre=chofe_nom, apellido=chofe_ape, idciudad=idCiudad, telefono=chofe_tel)
    db.add(chofer)
    db.commit()
    db.refresh(chofer)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
            request:Request,db: Session = Depends(get_database_session)):
    clie = db.query(Chofer).get(id)
    city = db.query(Ciudad).get(int(clie.idDepto))
    return templates.TemplateResponse("clientes/listar.html", {"request": request, "Chofer": clie, "Ciudad": city})

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
    chof= db.query(Chofer).get(id)
    depto = db.query(Departamento).all()
    refdepto = db.query(Ciudad).options(load_only(Ciudad.iddepartamento)).get(int(chof.idciudad))
    return templates.TemplateResponse("choferes/editar.html", {"request": request, "Chofer": chof, "Departamentos_lista": depto, "ref_depto":refdepto})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idclie = Form(...), color = Form(...), modelo = Form(...), anho = Form(...), idmarca = Form(...)):
    clie= db.query(Chofer).get(idclie)
    clie.color=color
    clie.modelo=modelo
    clie.anho=anho
    clie.idmarca=idmarca
    db.add(clie)
    db.commit()
    db.refresh(clie)
    response = RedirectResponse('/clientes/', status_code=303)
    return response

@router.get("/borrar/{id}",response_class=HTMLResponse)
def eliminar(id : int, db: Session = Depends(get_database_session)):
    db.query(Chofer).filter(Chofer.idclie == id).delete()
    db.commit()
    response = RedirectResponse('/clientes/', status_code=303)
    return response
