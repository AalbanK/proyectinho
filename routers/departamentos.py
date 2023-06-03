from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from models import Departamento
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/departamentos",
    tags=["departamentos"])


@app.post("/departamentos/")
async def create_departamento(db: Session = Depends(get_database_session), descDepartamento = Form(...)):
    departamento = Departamento(descripcion=descDepartamento)
    db.add(departamento)
    db.commit()
    db.refresh(departamento)
    response = RedirectResponse('/', status_code=303)
    return response

@app.get("/departamentos/nuevo/", response_class=HTMLResponse)
async def create_departamentos(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("departamentos/crear.html", {"request": request})

@app.get("/departamentos/")
async def read_departamento(request: Request, db: Session = Depends(get_database_session)):
    records = db.query(Departamento).all()
    return templates.TemplateResponse("departamentos/listar.html", {"request": request, "data": records})

@router.get("/todos")
async def listar_departamentos(request: Request, db: Session = Depends(get_database_session)):
    departamentos = db.query(Departamento).all()
    return JSONResponse(jsonable_encoder(departamentos))