from typing import List, Optional
from datetime import date
from pydantic import BaseModel

class Compra_detalle(BaseModel):
    idcabecera_compra: Optional[int] = None
    idproducto: int
    descripcion_producto: str
    cantidad: int
    precio: int
    porcentaje_iva: int
    subtotal_iva: int
    subtotal: int

class Compra_cabecera(BaseModel):
    idfactura_compra: Optional[int] = None
    numero: str
    # timbrado: str
    fecha: str
    idproveedor: int
    iddeposito: int
    total_monto: int
    idcontrato: Optional[int] = None
    detalles: List[Compra_detalle]

class Compra_detalle_Vista(BaseModel):
    idcabecera_compra: int
    idproducto: int
    descripcion_producto: str
    cantidad: int
    precio: int
    porcentaje_iva: int
    subtotal_iva: int
    subtotal: int

    class Config:
        orm_mode = True

class Compra_cabecera_Vista(BaseModel):
    idfactura_compra: int
    numero: str
    fecha: date
    idproveedor: int
    iddeposito: int
    total_monto: int
    idcontrato: Optional[int] = None
    detalles: List[Compra_detalle_Vista]
    class Config:
        orm_mode = True