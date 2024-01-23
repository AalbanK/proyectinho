from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session, load_only
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Proveedor, Departamento, Ciudad
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
    #records = db.query(Proveedor).all()
    ciud = db.query(Proveedor.idproveedor, Proveedor.descripcion, Proveedor.ruc,Ciudad.descripcion.label('descripcion_ciudad'),Proveedor.direccion, Proveedor.mail, Proveedor.telefono).join(Ciudad, Proveedor.idciudad == Ciudad.idciudad).all()
    return templates.TemplateResponse("proveedores/listar.html", {"request": request, "proveedores": ciud})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_proveedor(request: Request, db: Session = Depends(get_database_session)):
    depas=db.query(Departamento).all()
    return templates.TemplateResponse("proveedores/crear.html", {"request": request, "Depas_lista":depas})

@router.post("/nuevo")
async def create_proveedor(db: Session = Depends(get_database_session), descripcion = Form(...), idDepartamento=Form(...), idCiudad=Form(...), ruc = Form(...), mail = Form(...), direccion = Form(...), telefono = Form(...)):
    proveedor = Proveedor(descripcion=descripcion, idciudad = idCiudad, ruc=ruc, mail=mail, direccion=direccion, telefono=telefono)
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    response = RedirectResponse('/', status_code=303)
    return response

@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
            request:Request,db: Session = Depends(get_database_session)):
    prove = db.query(Proveedor).get(id)
    depto = db.query(Departamento).get(int(prove.idDepto))
    return templates.TemplateResponse("proveedores/listar.html", {"request": request, "Proveedor": prove, "Departamento": depto})

@router.get("/editar/{id}",response_class=HTMLResponse)
def editar_view(id:int,response:Response,request:Request,db: Session = Depends(get_database_session)):
    prove= db.query(Proveedor).get(id)
    depto = db.query(Departamento).all()
    refdepto = db.query(Ciudad).options(load_only(Ciudad.iddepartamento)).get(int(prove.idciudad))
    return templates.TemplateResponse("proveedores/editar.html", {"request": request, "Proveedor": prove, "Departamentos_lista": depto, "ref_depto":refdepto})

@router.post("/update",response_class=HTMLResponse)
def editar(db: Session = Depends(get_database_session), idproveedor = Form(...), descripcion = Form(...), ruc = Form(...), idciudad = Form(...), direccion = Form(...), mail = Form(), telefono = Form()):
        prove= db.query(Proveedor).get(idproveedor)
        prove.descripcion=descripcion
        prove.ruc=ruc
        prove.idciudad=idciudad
        prove.direccion=direccion
        prove.mail=mail
        prove.telefono=telefono
        db.add(prove)
        db.commit()
        db.refresh(prove)
        response = RedirectResponse('/proveedores/', status_code=303)
        return response

@router.get("/borrar/{id}",response_class=HTMLResponse)
def eliminar(id : int, db: Session = Depends(get_database_session)):
    db.query(Proveedor).filter(Proveedor.idproveedor == id).delete()
    db.commit()
    response = RedirectResponse('/proveedores/', status_code=303)
    return response
