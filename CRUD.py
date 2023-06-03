from fastapi import Depends, FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Form


from models import *

import schemas
from db.database import SessionLocal, engine
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.post("/departamento/")
async def create_departamento(db: Session = Depends(get_database_session), descDepartamento = Form(...)):
    departamento = Departamento(descripcion=descDepartamento)
    db.add(departamento)
    db.commit()
    db.refresh(departamento)
    response = RedirectResponse('/', status_code=303)
    return response


'''@app.post("/ciudad/")
async def create_ciudad(db: Session = Depends(get_database_session), descCiudad = Form(...)):
    ciudad = Ciudad(descCiudad=descCiudad)
    db.add(ciudad)
    db.commit()
    db.refresh(ciudad)
    response = RedirectResponse('/', status_code=303)
    return response'''


'''@app.post("/productos/")
async def create_articulo(db: Session = Depends(get_database_session),
producto_desc: schemas.productos.producto_desc = Form(...),
producto_stock: schemas.productos.producto_stock = Form(...),
):
    pais = Pais(NombrePais=nombrePais, nroHabitantes=nroHabitantes)
    db.add(pais)
    db.commit()
    db.refresh(pais)
    response = RedirectResponse('/', status_code=303)
    return response
'''
