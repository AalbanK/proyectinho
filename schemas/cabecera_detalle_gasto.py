from typing import List, Optional
from datetime import date
from pydantic import BaseModel

class Gasto_detalle(BaseModel):
    idfactura_gasto: Optional[int] = None
    idproducto: int
    descripcion_producto: str
    cantidad: int
    precio: int
    porcentaje_iva: int
    subtotal_iva: int
    subtotal: int

class Gasto_cabecera(BaseModel):
    idfactura_gasto: Optional[int] = None
    numero: str
    timbrado: str
    fecha: str
    idproveedor: int
    #iddeposito: int
    total_monto: int
    idcontrato: Optional[int] = None
    detalles: List[Gasto_detalle]

class Gasto_detalle_Vista(BaseModel):
    idfactura_gasto: int
    idproducto: int
    descripcion_producto: str
    cantidad: int
    precio: int
    porcentaje_iva: int
    subtotal_iva: int
    subtotal: int

    class Config:
        orm_mode = True

class Gasto_cabecera_Vista(BaseModel):
    idfactura_gasto: int
    numero: str
    fecha: date
    idproveedor: int
    #iddeposito: int
    total_monto: int
    idcontrato: Optional[int] = None
    detalles: List[Gasto_detalle_Vista]
    class Config:
        orm_mode = True