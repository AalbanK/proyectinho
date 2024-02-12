from schemas import usuario as us
from routers import auth
from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Remision, Contrato, Chofer, Camion, Carreta, Producto
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/remisiones",
    tags=["remisiones"]
)

@router.get("/")
async def read_remision(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    records=db.query(Remision, Contrato).join(Contrato).all()
    return templates.TemplateResponse("remisiones/listar.html", {"request": request, "usuario_actual": usuario_actual, "data": records, "datatables": True})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_remision(request: Request, db: Session = Depends(get_database_session), usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    contras=db.query(Contrato).all()
    chofes=db.query(Chofer).all()
    camis=db.query(Camion).all()
    carres=db.query(Carreta).all()
    return templates.TemplateResponse("remisiones/crear.html", {"request": request, "usuario_actual": usuario_actual, "Contratos_lista":contras, "Choferes_lista":chofes, "Camiones_lista":camis,"Carretas_lista":carres})

@router.post("/nuevo")
async def create_remision(db: Session=Depends(get_database_session), fechacarga=Form(...), fechadescarga=Form(), bruto=Form(...), tara=Form(...),neto=Form(...),
                          idchofer=Form(...), idcontrato=Form(...), idcamion=Form(...), idcarreta=Form(...),usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    usu = us.Usuario.from_orm(usuario_actual)
    remi = Remision(idcontrato=idcontrato,fecha_carga=fechacarga, fecha_descarga=fechadescarga, bruto_carga=bruto, tara_carga=tara, neto_carga=neto, idchofer=idchofer, alta_usuario = usu.idusuario)
    db.add(remi)
    db.commit()
    db.refresh(remi)
    response = RedirectResponse('/', status_code=303)
    return response