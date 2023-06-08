from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, Request, Form, Response, FastAPI
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models import Remision, IVA
from fastapi.staticfiles import StaticFiles

from  db.misc import get_database_session

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/productos",
    tags=["productos"]
)



@router.get("/")
async def read_producto(request: Request, db: Session = Depends(get_database_session)):
    records=db.query(Producto, IVA).join(IVA).all()
    return templates.TemplateResponse("productos/listar.html", {"request": request, "data": records})

@router.get("/nuevo", response_class=HTMLResponse)
async def create_producto(request: Request, db: Session = Depends(get_database_session)):
    ivas=db.query(IVA).all()
    return templates.TemplateResponse("productos/crear.html", {"request": request, "Ivas_lista":ivas})

@router.post("/nuevo")
async def create_producto(db: Session = Depends(get_database_session), descProducto = Form(...), idIVA=Form(...), stkProducto = Form(...)):
    producto = Producto(descripcion=descProducto, idIVA=idIVA, stock=stkProducto)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    response = RedirectResponse('/', status_code=303)
    return response