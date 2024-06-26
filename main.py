from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import (HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED,
                              HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND)

import models
from db.database import SessionLocal, engine
from models import *
from routers import (auditoria, auth, bancos, camiones,
                     carretas, choferes, ciudades, clientes, compras,
                     contratos, cuentas, departamentos, depositos, ivas,
                     marcas_camiones, marcas_carretas, productos, proveedores,
                     remisiones, reportes, roles, usuarios, ventas, gastos)
from schemas import usuario as us

app = FastAPI()
from fastapi.templating import Jinja2Templates


@app.exception_handler(404)
async def custom_404_handler(request, __):
    return templates.TemplateResponse("404.html", {"request": request})

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == HTTP_403_FORBIDDEN or exc.status_code == HTTP_401_UNAUTHORIZED or exc.status_code == HTTP_400_BAD_REQUEST:
        return templates.TemplateResponse("login.html", {"request": request, "error": exc.detail})
        # Si el error no es 401 o 403 o 400, relanzarlo
    raise exc

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/",response_class=HTMLResponse)
async def home(request:Request, usuario_actual: us.Usuario = Depends(auth.get_usuario_actual)):
    return templates.TemplateResponse("index.html", {"request":request, "usuario_actual": usuario_actual})

models.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.include_router(auth.router)
app.include_router(auditoria.router)
app.include_router(depositos.router)
app.include_router(ciudades.router)
app.include_router(choferes.router)
app.include_router(departamentos.router)
app.include_router(clientes.router)
app.include_router(proveedores.router)
app.include_router(marcas_carretas.router)
app.include_router(marcas_camiones.router)
app.include_router(ivas.router)
app.include_router(compras.router)
app.include_router(productos.router)
app.include_router(bancos.router)
app.include_router(camiones.router)
app.include_router(carretas.router)
app.include_router(remisiones.router)
app.include_router(reportes.router)
app.include_router(roles.router)
app.include_router(contratos.router)
app.include_router(usuarios.router)
app.include_router(ventas.router)
app.include_router(cuentas.router)
app.include_router(gastos.router)