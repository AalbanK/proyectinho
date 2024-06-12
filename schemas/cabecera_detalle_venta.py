from typing import List, Optional
from datetime import date
from pydantic import BaseModel

class Venta_detalle(BaseModel):
    idcabecera_venta : Optional[int] = None
    idproducto : int
    descripcion_producto : str
    cantidad : int
    precio : int
    porcentaje_iva : int
    subtotal_iva : int
    subtotal: int

class Venta_cabecera(BaseModel):
    idfactura_venta: Optional[int] = None
    numero : str
    timbrado: str
    fecha : str
    idcliente: int
    iddeposito: int
    total_monto: int
    idcontrato: Optional[int] = None
    detalles: List[Venta_detalle]

class Venta_detalle_Vista(BaseModel):
    idcabecera_venta: int
    idproducto: int
    descripcion_producto: str
    cantidad: int
    precio: int
    porcentaje_iva: int
    subtotal_iva: int
    subtotal: int

    class Config:
        orm_mode = True

class Venta_cabecera_Vista(BaseModel):
    idfactura_venta: int
    numero: str
    fecha: date
    idproveedor: int
    iddeposito: int
    total_monto: int
    idcontrato: Optional[int] = None
    detalles: List[Venta_detalle_Vista]
    class Config:
        orm_mode = True