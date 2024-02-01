from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy.orm import Session
import sqlalchemy as sa
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette import status

templates = Jinja2Templates(directory="templates")

from ..db.sesion import get_database_session
from ..models.models import Auditoria, Usuario
from ..routers import auth, usuarios
from ..schemas import usuario

router = APIRouter(
    prefix="/auditoria",
    tags=["auditoria"],
    dependencies=[Depends(auth.verificar_si_usuario_es_superusuario)],
    responses={404: {"description": "No encontrado"}},
)

@router.get("/")
async def read_auditoria(request: Request, db: Session = Depends(get_database_session), superusuario = Depends(auth.verificar_si_usuario_es_superusuario)):
    usuarios = db.query(Usuario).all()
    return templates.TemplateResponse("auditorias/listar.html", {"request": request, "datatables": True, "Usuarios_lista": usuarios, "datatables": True})

@router.get("/todos")
async def listar_auditoria(request: Request, db: Session = Depends(get_database_session)):
    auditoria = db.query(Auditoria).all()
    return JSONResponse(jsonable_encoder(auditoria))

@router.post("/filtrar")
async def filtrar_auditoria(request: Request, db: Session = Depends(get_database_session), fechaDesde = Form(), fechaHasta = Form(), accion = Form(default = None), usuarioAltaModif = Form(default = None)):
    
    # es como hacer 
    # "select * from auditoria a 
    # where (parametroAccion is null or a.accion = parametroAccion) 
    # and (fechaDesde is null or a.accion_fecha >= fechaDesde) 
    # and (fechaHasta is null or a.accion_fecha <= fechaHasta)"

    # Falta filtrar por idusuario, que se extrae de valor_viejo y valor_nuevo, en las columnas de alta_usuario y modif_usuario
    
    auditoria = db.query(Auditoria).filter(
        sa.or_(Auditoria.accion == accion, accion == None), 
        sa.or_(Auditoria.accion_fecha >= fechaDesde, fechaDesde == None),
        sa.or_(Auditoria.accion_fecha <= fechaHasta, fechaHasta == None)).all()
    return JSONResponse(jsonable_encoder(auditoria))

#-----------------------------------------------------------------------------------------------------

@router.get("/{id}",response_class=HTMLResponse)
def ver(id:int, response:Response,
            request:Request,db: Session = Depends(get_database_session)):
    auditoria = db.query(Auditoria).get(id)
    return templates.TemplateResponse("auditoria/listar.html", {"request": request, "Auditoria": auditoria})

@router.get("/ver/{id}",response_class=JSONResponse)
def ver(id:int, response:Response,
            request:Request,db: Session = Depends(get_database_session)):
    auditoria = db.query(Auditoria).get(id)
    if(auditoria is None):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Registro no encontrado.")
    else:
        return JSONResponse(jsonable_encoder(auditoria))