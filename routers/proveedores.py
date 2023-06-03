from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Proveedor, Departamento
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/proveedores",
    tags=["proveedores"]
)

@router.get("/")
async def read_proveedor(request: Request, db: Session = Depends(get_database_session)):
    records = db.query(Proveedor).all()
    return templates.TemplateResponse("proveedores/listar.html", {"request": request, "data": records})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_proveedor(request: Request, db: Session = Depends(get_database_session)):
    depas=db.query(Departamento).all()
    return templates.TemplateResponse("proveedores/crear.html", {"request": request, "Depas_lista":depas})

@router.post("/nuevo")
async def create_proveedor(db: Session = Depends(get_database_session), descProveedor = Form(...), idDepartamento=Form(...)):
    proveedor = Proveedor(descripcion=descProveedor, id_departamento=idDepartamento)
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    response = RedirectResponse('/', status_code=303)
    return response

#-----------------------------------------------------------------------------------------------------

@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
            request:Request,db: Session = Depends(get_database_session)):
    clie = db.query(Proveedor).get(id)
    depto = db.query(Departamento).get(int(clie.idDepto))
    return templates.TemplateResponse("proveedores/listar.html", {"request": request, "Proveedor": clie, "Departamento": depto})

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
    clie= db.query(Proveedor).get(id)
    depto = db.query(Departamento).all()
    return templates.TemplateResponse("editar_proveedor.html", {"request": request, "Proveedor": clie, "Departamentos_lista": depto})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idclie = Form(...), color = Form(...), modelo = Form(...), anho = Form(...), idmarca = Form(...)):
    clie= db.query(Proveedor).get(idclie)
    clie.color=color
    clie.modelo=modelo
    clie.anho=anho
    clie.idmarca=idmarca
    db.add(clie)
    db.commit()
    db.refresh(clie)
    response = RedirectResponse('/proveedores/', status_code=303)
    return response

@router.get("/borrar/{id}",response_class=HTMLResponse)
def eliminar(id : int, db: Session = Depends(get_database_session)):
    db.query(Proveedor).filter(Proveedor.idclie == id).delete()
    db.commit()
    response = RedirectResponse('/proveedores/', status_code=303)
    return response
