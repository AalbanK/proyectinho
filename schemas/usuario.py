from typing import List
from fastapi import Form, Request
from pydantic import BaseModel, constr
from .rol import Rol

class UsuarioIn(BaseModel):
    name: constr(max_length=45)
    id_rol: int
    username: str
    password: str

class UsuarioOut(BaseModel):
    name: str|None
    username: str|None
    id_rol: List[Rol]=[]

class Config:
    orm_mode = True
    allow_population_by_field_name = True

class UsuarioCreate(UsuarioIn):
    pass

class Usuario(UsuarioIn):
    id_uduario: int

class Config:
    orm_mode = True
    allow_population_by_field_name = True

class UsuarioPWOut(UsuarioOut):
    password: str

class Config:
    orm_mode = True
    allow_population_by_field_name = True
