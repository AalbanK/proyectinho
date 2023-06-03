from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Camion, Carreta, Chofer
from fastapi.staticfiles import StaticFiles

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
    #records = db.query(Camion).all()
    records=db.query(Camion, Carreta, Chofer).join(Carreta, Chofer).all()
    return templates.TemplateResponse("camiones/listar.html", {"request": request, "data": records})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_camion(request: Request, db: Session = Depends(get_database_session)):
    carre=db.query(Carreta, Chofer).all()
    return templates.TemplateResponse("camiones/crear.html", {"request": request, "Carre_lista":carre})

@router.post("/nuevo")
async def create_camion(db: Session = Depends(get_database_session), descCamion = Form(...), idCarreta=Form(...), idChofer=Form(...)):
    camion = Camion(descripcion=descCamion, id_carreta=idCarreta, id_chofer=idChofer)
    db.add(camion)
    db.commit()
    db.refresh(camion)
    response = RedirectResponse('/', status_code=303)
    return response