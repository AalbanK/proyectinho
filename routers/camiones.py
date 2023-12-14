from models import Camion, Marca_camion
from fastapi import APIRouter, Depends, Request, Form, Response, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse


from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/camiones",
    tags=["camiones"]
)

@router.get("/")
async def read_camion(request: Request, db: Session = Depends(get_database_session)):
    records=db.query(Camion).join(Marca_camion).all()
    return templates.TemplateResponse("camiones/listar.html", {"request": request, "data": records})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_camion(request: Request, db: Session = Depends(get_database_session)):
    marcas=db.query(Marca_camion).all()
    return templates.TemplateResponse("camiones/crear.html", {"request": request, "Marcas_lista":marcas})

@router.post("/nuevo")
async def create_camion(db: Session = Depends(get_database_session), chapaCamion = Form(...), idmarca_camion = Form(...)):
    camion = Camion(camion_chapa = chapaCamion, idmarca_camion = idmarca_camion)
    db.add(camion)
    db.commit()
    db.refresh(camion)
    response = RedirectResponse('/', status_code=303)
    return response