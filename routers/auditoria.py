import sqlalchemy as sa
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from schemas import usuario as us

templates = Jinja2Templates(directory="templates")

from db.misc import get_database_session
from models import Auditoria, Usuario
from routers import auth

router = APIRouter(
    prefix="/auditoria",
    tags=["auditoria"],
    dependencies=[Depends(auth.verificar_si_usuario_es_superusuario)],
    responses={404: {"description": "No encontrado"}},
)

@router.get("/")
async def read_auditoria(request: Request, db: Session = Depends(get_database_session), superusuario = Depends(auth.verificar_si_usuario_es_superusuario), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usuarios = db.query(Usuario).all()
    return templates.TemplateResponse("auditorias/listar.html", {"request": request, "usuario_actual": usuario_actual, "datatables": True, "Usuarios_lista": usuarios, "datatables": True})

@router.get("/todos")
async def listar_auditoria(request: Request, db: Session = Depends(get_database_session)):
    auditoria = db.query(Auditoria).all()
    return JSONResponse(jsonable_encoder(auditoria))

@router.post("/filtrar")
async def filtrar_auditoria(request: Request, db: Session = Depends(get_database_session), fechaDesde = Form(), fechaHasta = Form(), accion = Form(default = None), usuarioAltaModif = Form(default = None)):
    print(accion)
    print(fechaDesde)
    print(fechaHasta)
    print(usuarioAltaModif)
    # es como hacer 
    # "select * from auditoria a 
    # where (parametroAccion is null or a.accion = parametroAccion) 
    # and (fechaDesde is null or a.accion_fecha >= fechaDesde) 
    # and (fechaHasta is null or a.accion_fecha <= fechaHasta)"

    # Falta filtrar por idusuario, que se extrae de valor_viejo y valor_nuevo, en las columnas de alta_usuario y modif_usuario
    
    auditoria = db.query(Auditoria).filter(
        sa.or_(Auditoria.accion == accion, accion == None),
        sa.or_(sa.func.date(Auditoria.accion_fecha) >= fechaDesde if fechaDesde else True), # se convierte en true = 1 si fecha_desde es None (else True), o sea, no compara; se parsea como date para que solo tome la fecha, no la hora
        sa.or_(sa.func.date(Auditoria.accion_fecha) <= fechaHasta if fechaHasta else True)).all()
    
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