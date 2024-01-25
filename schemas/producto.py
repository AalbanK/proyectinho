from pydantic import BaseModel

class ProductoBase(BaseModel):
    idproducto: int
    descripcion: str
    porcentaje_iva: int

    class Config:
        orm_mode = True