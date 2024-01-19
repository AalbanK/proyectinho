from fastapi import Depends, FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

from models import *

from db.database import SessionLocal, engine
import models
from routers import (auth,bancos,camiones,carretas,choferes,ciudades,clientes,contratos,departamentos,ivas,marcas_camiones,marcas_carretas,productos,proveedores,roles,usuarios,cuentas#,remisiones,
)

app = FastAPI() 

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/",response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse("index.html", {"request":request})

models.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.include_router(auth.router)
app.include_router(ciudades.router)
app.include_router(choferes.router)
app.include_router(departamentos.router)
app.include_router(clientes.router)
app.include_router(proveedores.router)
app.include_router(marcas_carretas.router)
app.include_router(marcas_camiones.router)
app.include_router(ivas.router)
app.include_router(productos.router)
app.include_router(bancos.router)
app.include_router(camiones.router)
app.include_router(carretas.router)
app.include_router(roles.router)
app.include_router(contratos.router)
app.include_router(usuarios.router)
app.include_router(cuentas.router)