from pydantic import BaseModel
from datetime import datetime

class ReporteStockBase(BaseModel):
    tipo_movimiento: str = None
    idproducto: str = None
    descripcion: str = None
    fecha: datetime = None
    cantidad: int = None

    class Config:
        orm_mode = True

class ReporteVentasBase(BaseModel):
    idcliente: str = None
    descripcion_cliente: str = None
    idproducto: str = None
    producto: str = None
    descripcion_producto: str = None
    numero: str = None
    subtotal: str = None
    fecha: datetime = None
    cantidad: int = None

    class Config:
        orm_mode = True

class ReporteComprasBase(BaseModel):
    idproveedor: str = None
    descripcion_proveedor: str = None
    idproducto: str = None
    producto: str = None
    descripcion_producto: str = None
    numero: str = None
    subtotal: str = None
    fecha: datetime = None
    cantidad: int = None

    class Config:
        orm_mode = True