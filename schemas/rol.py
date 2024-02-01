from pydantic import BaseModel, constr


class Rol(BaseModel):
    descripcion: constr(max_length=45)
    idrol: int

    class Config:
        orm_mode = True