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
    subtotaliva : int
    subtotal: int

class Venta_cabecera(BaseModel):
    idfactura_venta: Optional[int] = None
    numero : str
    timbrado : str
    fecha : str
    idproveedor: int
    iddeposito: int
    #total_monto: int
    idcontrato: Optional[int] = None
    #detalles: List[Compra_Detalle]