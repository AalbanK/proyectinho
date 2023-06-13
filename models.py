from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Double, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base



class Auditoria(Base):
    __tablename__ = "auditoria" #Nombre de la tabla en la Base de Datos
    idauditoria = Column(Integer, primary_key=True, index=True)
    accion = Column(String(45))
    accionfecha = Column(DateTime(timezone=True), server_default=func.now())
    valorviejo = Column(String(4000))
    valornuevo = Column(String(4000))
    columnas    = Column(String(4000))


class Banco(Base):
    __tablename__ = "banco" #Nombre de la tabla en la Base de Datos
    idbanco = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    # altausuario = Column(Integer)
    # altafecha = Column(DateTime(), server_default=func.now(), default=func.now())


class Cliente(Base):
    __tablename__ = "cliente" #Nombre de la tabla en la Base de Datos
    idcliente = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    ruc = Column(String(15), unique=True)
    idciudad = Column(Integer, ForeignKey("ciudad.id_ciudad"))
    direccion = Column(String(45))
    mail = Column(String(45))
    telefono = Column(String(45))


class Departamento(Base):
    __tablename__ = "departamento"
    iddepartamento = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45))
    # Para incluir todas las ciudades de un departamento...
    # campo Hijo = relationship("NombreDelModeloHijo", back_populates="NombreDeLaVariableEnElOtroModelo")
    ciudad = relationship("Ciudad", back_populates="departamento")


class IVA(Base):
    __tablename__ = "iva" #Nombre de la tabla en la Base de Datos
    idIVA = Column(Integer, primary_key=True, index=True)
    porcentaje = Column(Integer, unique=True)


class Marca_camion(Base):
    __tablename__ = "marca_camion" #Nombre de la tabla en la Base de Datos
    idmarcacamion = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)


class Marca_carreta(Base):
    __tablename__ = "marca_carreta" #Nombre de la tabla en la Base de Datos
    idmarcacarreta = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    

class Moneda(Base):
    __tablename__ = "moneda" #Nombre de la tabla en la Base de Datos
    idmoneda = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)


class Proveedor(Base):
    __tablename__ = "proveedor" #Nombre de la tabla en la Base de Datos
    idproveedor = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    ruc = Column(String(15), unique=True)
    idciudad = Column(Integer, ForeignKey("ciudad.idciudad"))
    direccion = Column(String(45))
    mail = Column(String(45))
    telefono = Column(String(45))


class Rol(Base):
    __tablename__ = "rol" #Nombre de la tabla en la Base de Datos
    idrol = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    usuario = relationship("Usuario", uselist=False, back_populates="rol")


#-----LLAVES FORÁNEAS-----

class Camion(Base):
    __tablename__ = "camion" #Nombre de la tabla en la Base de Datos
    idcamion = Column(Integer, primary_key=True, index=True)
    chapa = Column(String(45), unique=True)
    idmarcacamion = Column(Integer, ForeignKey("marca_camion.idmarca_camion"))
    idcarreta = Column(Integer, ForeignKey("carreta.idcarreta"))
    #idchofer = Column(Integer, ForeignKey("choferes.idchofer"))


class Carreta(Base):
    __tablename__ = "carreta" #Nombre de la tabla en la Base de Datos
    id_carreta = Column(Integer, primary_key=True, index=True)
    chapa = Column(String(45), unique=True)
    idmarca_carreta = Column(Integer, ForeignKey("marca_camion.idmarca_camion"))


class Chofer(Base):
    __tablename__ = "chofer" #Nombre de la tabla en la Base de Datos
    idchofer = Column(Integer, primary_key=True, index=True)
    choferci = Column(Integer, unique=True)
    chofernombre = Column(String(45))
    choferapellido = Column(String(45))
    idciudad = Column(Integer, ForeignKey("ciudad.idciudad"))
    chofertel = Column(Integer, unique=True)


class Ciudad(Base):
    __tablename__ = "ciudad" #Nombre de la tabla en la Base de Datos
    idciudad = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    iddepartamento = Column(Integer, ForeignKey("departamento.iddepartamento"))
    # Para incluir todas las ciudades de un departamento...
    # campo Padre = relationship("NombreDelModeloPadre", back_populates="NombreDeLaVariableEnElOtroModelo")
    departamento = relationship("Departamento", back_populates="ciudad")


# class Comprobante(Base):
#     __tablename__ = "comprobantes" #Nombre de la tabla en la Base de Datos
#     id_comprobante  = Column(Integer, primary_key=True, index=True)
#     id_tipo_comprobante  = Column(Integer, ForeignKey("tiposcomprobantes.idtipocomprobante"))
#     fechaemision = Column(DateTime(timezone=True), server_default=func.now())
#     Nro = Column(Integer, unique=True)
#     idproducto  = Column(Integer, ForeignKey("productos.idproducto"))
#     idproveedor = Column(Integer, ForeignKey ("proveedores.idproveedor"))
#     idcliente = Column(Integer, ForeignKey("clientes.idcliente"))
#     comprobpunit = Column(Integer)
#     cant = Column(Integer)
#     total = Column(Integer)
#     totaliva = Column(Integer)


class Contrato(Base):
    __tablename__= "contrato" #Nombre de la tabla en la Base de Datos
    idcontrato = Column(Integer, primary_key=True, index=True)
    nro = Column(Integer)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    idproducto = Column(Integer, ForeignKey("producto.idproducto"))
    cantidad = Column(Integer)
    precio_compra = Column(Integer)
    origen = Column(Integer, ForeignKey("ciudad.idciudad"))
    idproveedor = Column(Integer, ForeignKey("proveedor.idproveedor"))
    cuenta_proveedor = Column(String(45))
    precio_venta = Column(Integer)
    destino = Column(Integer, ForeignKey("ciudad.idciudad"))
    idcliente = Column(Integer, ForeignKey("cliente.idcliente"))
    cuenta_cliente = Column(String(45))


class Cuenta(Base):
    __tablename__= "cuenta"
    idcuenta = Column(Integer, primary_key=True, index=True)
    idbanco = Column(Integer, ForeignKey("banco.idbanco"))
    idcliente = Column(Integer, ForeignKey("cliente.idcliente"))
    idproveedor = Column(Integer, ForeignKey("proveedor.idproveedor"))
    nro = Column(String(45))


class Producto(Base):
    __tablename__="producto"
    idproducto=Column(Integer, primary_key=True, index=True)
    descripcion=Column(String(45), unique=True)
    idIVA=Column(Integer, ForeignKey("iva.idIVA"))
    stock=Column(Integer)

class Remision(Base):
    __tablename__="remision"
    idremision=Column(Integer, primary_key=True, index=True)
    idcamion=Column(Integer, ForeignKey("camion.idcamion"))
    flete_precio=Column(Double)
    fecha_carga=Column(DateTime(timezone=True), server_default=func.now())
    fecha_descarga=Column(DateTime(timezone=True), server_default=func.now())
    bruto=Column(Double)
    tara=Column(Double)
    neto=Column(Double)

class Usuario(Base):
    __tablename__="usuarios"
    idusuario=Column(Integer, primary_key=True, index=True)
    name=Column(String(45))
    username=Column(String(45))
    password=Column(String(45))
    idrol=Column(Integer, ForeignKey("rol.idrol"))
    rol=rol = relationship("Rol", back_populates="usuario")
