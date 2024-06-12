from sqlalchemy import Date, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, Double, Integer, String, Text

from db.database import Base


class Auditoria(Base):
    __tablename__ = "auditoria" #Nombre de la tabla en la Base de Datos
    idauditoria = Column(Integer, primary_key=True, index=True)
    accion = Column(String(45))
    accion_fecha = Column(DateTime(timezone=True), server_default=func.now())
    valor_viejo = Column(String(4000), default=None)
    valor_nuevo = Column(String(4000), default=None)
    columnas    = Column(String(4000))


class Banco(Base):
    __tablename__ = "banco" #Nombre de la tabla en la Base de Datos
    idbanco = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)


class Cliente(Base):
    __tablename__ = "cliente" #Nombre de la tabla en la Base de Datos
    idcliente = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    ruc = Column(String(15), unique=True)
    idciudad = Column(Integer, ForeignKey("ciudad.idciudad"))
    direccion = Column(String(45))
    mail = Column(String(45))
    telefono = Column(String(45))
    # campo Hijo = relationship("NombreDelModeloHijo", back_populates="NombreDeLaVariableEnElOtroModelo")
    clienteventa = relationship("Factura_venta_cabecera", back_populates="cliente")
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)


class Departamento(Base):
    __tablename__ = "departamento"
    iddepartamento = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45))
    # Para incluir todas las ciudades de un departamento...
    # campo Hijo = relationship("NombreDelModeloHijo", back_populates="NombreDeLaVariableEnElOtroModelo")
    ciudad = relationship("Ciudad", back_populates="departamento")
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)

class Deposito(Base):
    __tablename__ = "deposito" #Nombre de la tabla en la Base de Datos
    iddeposito = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45))
    # campo Hijo = relationship("NombreDelModeloHijo", back_populates="NombreDeLaVariableEnElOtroModelo")
    depo_producto = relationship("Deposito_y_producto", back_populates="deposito")
    depositocompra = relationship("Factura_compra_cabecera", back_populates="deposito")
    depositoventa = relationship("Factura_venta_cabecera", back_populates="deposito")
    depositoremision = relationship("Remision", back_populates="deposito")
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)


class IVA(Base):
    __tablename__ = "iva" #Nombre de la tabla en la Base de Datos
    idIVA = Column(Integer, primary_key=True, index=True)
    porcentaje = Column(Integer, unique=True)
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)


class Marca_camion(Base):
    __tablename__ = "marca_camion" #Nombre de la tabla en la Base de Datos
    idmarca_camion = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)


class Marca_carreta(Base):
    __tablename__ = "marca_carreta" #Nombre de la tabla en la Base de Datos
    idmarca_carreta = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)

class Proveedor(Base):
    __tablename__ = "proveedor" #Nombre de la tabla en la Base de Datos
    idproveedor = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    ruc = Column(String(15), unique=True)
    idciudad = Column(Integer, ForeignKey("ciudad.idciudad"))
    direccion = Column(String(45))
    mail = Column(String(45))
    telefono = Column(String(45))
    # campo Hijo = relationship("NombreDelModeloHijo", back_populates="NombreDeLaVariableEnElOtroModelo")
    proveedorcompra = relationship("Factura_compra_cabecera", back_populates="proveedor") #relación cruzada para los campos afectados
    proveedorgasto = relationship("Factura_gasto_cabecera", back_populates="proveedor") #relación cruzada para los campos afectados
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)


class Rol(Base):
    __tablename__ = "rol" #Nombre de la tabla en la Base de Datos
    idrol = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    usuario = relationship("Usuario", uselist=False, back_populates="rol")
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)


#-----LLAVES FORÁNEAS-----

class Camion(Base):
    __tablename__ = "camion" #Nombre de la tabla en la Base de Datos
    idcamion = Column(Integer, primary_key=True, index=True)
    camion_chapa = Column(String(45), unique=True)
    idmarca_camion = Column(Integer, ForeignKey("marca_camion.idmarca_camion"))
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)


class Carreta(Base):
    __tablename__ = "carreta" #Nombre de la tabla en la Base de Datos
    idcarreta = Column(Integer, primary_key=True, index=True)
    carreta_chapa = Column(String(45), unique=True)
    idmarca_carreta = Column(Integer, ForeignKey("marca_camion.idmarca_camion"))
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)


class Chofer(Base):
    __tablename__ = "chofer" #Nombre de la tabla en la Base de Datos
    idchofer = Column(Integer, primary_key=True, index=True)
    ci = Column(Integer, unique=True)
    nombre = Column(String(45))
    apellido = Column(String(45))
    idciudad = Column(Integer, ForeignKey("ciudad.idciudad"))
    telefono = Column(Integer, unique=True)
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)


class Ciudad(Base):
    __tablename__ = "ciudad" #Nombre de la tabla en la Base de Datos
    idciudad = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(45), unique=True)
    iddepartamento = Column(Integer, ForeignKey("departamento.iddepartamento")) #FK para id
    # Para incluir todas las ciudades de un departamento...
    # campo Padre = relationship("NombreDelModeloPadre", back_populates="NombreDeLaVariableEnElOtroModelo")
    departamento = relationship("Departamento", back_populates="ciudad")
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)

class Contrato(Base):
    __tablename__= "contrato" #Nombre de la tabla en la Base de Datos
    idcontrato = Column(Integer, primary_key=True, index=True)
    nro = Column(Integer)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    idproducto = Column(Integer, ForeignKey("producto.idproducto"))
    cantidad = Column(Integer)
    precio_compra = Column(Integer)    
    precio_venta = Column(Integer)
    idproveedor = Column(Integer, ForeignKey("proveedor.idproveedor"))
    idcuentaP= Column(Integer, ForeignKey("cuenta.idcuenta"))
    idcprove=relationship("Cuenta", foreign_keys=[idcuentaP])

    cuenta_proveedor = Column(String(45))
    origen = Column(Integer, ForeignKey("ciudad.idciudad"))
    
    idcliente = Column(Integer, ForeignKey("cliente.idcliente"))
    idcuentaC= Column(Integer, ForeignKey("cuenta.idcuenta"))
    idcclie=relationship("Cuenta", foreign_keys=[idcuentaC])

    cuenta_cliente = Column(String(45))
    destino = Column(Integer, ForeignKey("ciudad.idciudad"))
    
    
    contratocompra = relationship("Factura_compra_cabecera", back_populates="contrato") #
    contratogasto = relationship("Factura_gasto_cabecera", back_populates="contrato") #
    contratoventa = relationship("Factura_venta_cabecera", back_populates="contrato")
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)
    anulado=Column(String(1),default='N')


class Cuenta(Base):
    __tablename__= "cuenta"
    idcuenta = Column(Integer, primary_key=True, index=True)
    idbanco = Column(Integer, ForeignKey("banco.idbanco"))
    idcliente = Column(Integer, ForeignKey("cliente.idcliente"))
    idproveedor = Column(Integer, ForeignKey("proveedor.idproveedor"))
    nro = Column(String(45))
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)
    #idcuentaprove=relationship("Contrato", back_populates="idcprove")
    #idcuentaclie=relationship("Contrato", back_populates="idcclie")

class Producto(Base):
    __tablename__="producto"
    idproducto=Column(Integer, primary_key=True, index=True)
    descripcion=Column(String(45), unique=True)
    idIVA=Column(Integer, ForeignKey("iva.idIVA"))
    # campo Hijo = relationship("NombreDelModeloHijo", back_populates="NombreDeLaVariableEnElOtroModelo")
    productocompra = relationship("Factura_compra_detalle", back_populates="producto") #
    productoventa = relationship("Factura_venta_detalle", back_populates="producto")    
    productogasto = relationship("Factura_gasto_detalle", back_populates="producto")
    producto_deposito_y_producto = relationship("Deposito_y_producto", back_populates="producto")
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)

class Remision(Base):
    __tablename__="remision"
    idremision=Column(Integer, primary_key=True, index=True)
    numero=Column(String(45))
    fecha_carga=Column(DateTime(timezone=True), server_default=func.now())
    fecha_descarga=Column(DateTime(timezone=True), server_default=func.now())
    idcontrato=Column(Integer, ForeignKey("contrato.idcontrato"))
    bruto=Column(Integer)
    tara=Column(Integer)
    neto=Column(Integer)
    brutod=Column(Integer)
    tarad=Column(Integer)
    netod=Column(Integer)
    idchofer=Column(Integer, ForeignKey("chofer.idchofer"))
    idcamion=Column(Integer, ForeignKey("camion.idcamion"))
    idcarreta=Column(Integer, ForeignKey("carreta.idcarreta"))
    iddeposito=Column(Integer, ForeignKey("deposito.iddeposito"))
    deposito = relationship("Deposito", back_populates="depositoremision")
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)
    anulado=Column(String(1),default='N')

class Usuario(Base):
    __tablename__="usuario"
    idusuario=Column(Integer, primary_key=True, index=True)
    name=Column(String(45))
    username=Column(String(45))
    password=Column(String(45))
    idrol=Column(Integer, ForeignKey("rol.idrol"))
    rol = relationship("Rol", back_populates="usuario")
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)

class Factura_compra_cabecera(Base):
    __tablename__ = "factura_compra_cabecera"
    idfactura_compra = Column(Integer, primary_key=True, index=True)
    numero = Column(String)
    timbrado = Column(Integer)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    idproveedor = Column(Integer, ForeignKey("proveedor.idproveedor")) #FK del proveedor
    # campo Padre = relationship("NombreDelModeloPadre", back_populates="NombreDeLaVariableEnElOtroModelo")
    proveedor = relationship("Proveedor", back_populates="proveedorcompra") #Relación cruzada en ambos modelos afectados
    total_monto = Column(Integer)
    idcontrato = Column(Integer, ForeignKey("contrato.idcontrato"))      #FK del cliente
    contrato = relationship("Contrato", back_populates="contratocompra") #relación necesaria para que funcione el FK
    iddeposito = Column(Integer, ForeignKey("deposito.iddeposito"))
    deposito = relationship("Deposito", back_populates="depositocompra")
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)
    detalles =  relationship("Factura_compra_detalle", back_populates="detalle")
    anulado=Column(String(1),default='N')

class Factura_compra_detalle(Base):
    __tablename__ = "factura_compra_detalle"
    iddetalle=Column(Integer, primary_key=True, index=True)
    idcabecera_compra = Column(Integer, ForeignKey("factura_compra_cabecera.idfactura_compra"))
    idproducto = Column(Integer, ForeignKey("producto.idproducto"))
    producto = relationship("Producto", back_populates="productocompra")
    descripcion_producto = Column(String)
    cantidad = Column(Integer)
    precio = Column(Integer)
    porcentaje_iva = Column(Integer)
    subtotal = Column(Integer)
    subtotal_iva = Column(Integer)
    detalle=relationship("Factura_compra_cabecera", back_populates="detalles")

class Factura_venta_cabecera(Base):
    __tablename__ = "factura_venta_cabecera"
    idfactura_venta = Column(Integer, primary_key=True, index=True)
    numero = Column(String)
    timbrado = Column(Integer)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    idcliente = Column(Integer, ForeignKey("cliente.idcliente"))
    # campo Padre = relationship("NombreDelModeloPadre", back_populates="NombreDeLaVariableEnElOtroModelo")
    cliente = relationship("Cliente", back_populates="clienteventa")
    total_monto = Column(Integer)
    idcontrato = Column(Integer, ForeignKey("contrato.idcontrato"))
    contrato = relationship("Contrato", back_populates="contratoventa")
    iddeposito = Column(Integer, ForeignKey("deposito.iddeposito"))
    deposito = relationship("Deposito", back_populates="depositoventa")
    anulado=Column(String(1),default='N')
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)
    detalles =  relationship("Factura_venta_detalle", back_populates="detalle")

class Factura_venta_detalle(Base):
    __tablename__ = "factura_venta_detalle"
    iddetalle=Column(Integer, primary_key=True, index=True)
    idcabecera_venta = Column(Integer, ForeignKey("factura_venta_cabecera.idfactura_venta"))
    idproducto = Column(Integer, ForeignKey("producto.idproducto"))
    producto = relationship("Producto", back_populates="productoventa")
    descripcion_producto = Column(String)
    cantidad = Column(Integer)
    precio = Column(Integer)
    porcentaje_iva = Column(Integer)
    subtotal_iva = Column(Integer)
    subtotal = Column(Integer)
    detalle=relationship("Factura_venta_cabecera", back_populates="detalles")

class Deposito_y_producto(Base):
    __tablename__ = "deposito_y_producto"
    iddeposito  = Column(Integer, ForeignKey("deposito.iddeposito"), primary_key=True ) #debe ser relación cruzada "Mapper[Deposito_y_producto(deposito_y_producto)] could not assemble any primary key columns for mapped table 'deposito_y_producto'"
    deposito = relationship("Deposito", back_populates="depo_producto")
    idproducto  = Column(Integer, ForeignKey("producto.idproducto"), primary_key=True )
    producto = relationship("Producto", back_populates="producto_deposito_y_producto")
    cantidad = Column(Integer)
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)

class Factura_gasto_cabecera(Base):
    __tablename__ = "factura_gasto_cabecera"
    idfactura_gasto = Column(Integer, primary_key=True, index=True)
    numero = Column(String(15))
    timbrado = Column(Integer)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    idproveedor = Column(Integer, ForeignKey("proveedor.idproveedor")) #FK del proveedor
    # campo Padre = relationship("NombreDelModeloPadre", back_populates="NombreDeLaVariableEnElOtroModelo")
    proveedor = relationship("Proveedor", back_populates="proveedorgasto") #Relación cruzada en ambos modelos afectados
    total_monto = Column(Integer)
    idcontrato = Column(Integer, ForeignKey("contrato.idcontrato"))      #FK del cliente
    contrato = relationship("Contrato", back_populates="contratogasto") #relación necesaria para que funcione el FK
    anulado=Column(String(1),default='N')
    alta_usuario = Column(Integer)
    alta_fecha = Column(DateTime(), server_default=func.now(), default=func.now())
    modif_usuario = Column(Integer)
    detalles =  relationship("Factura_gasto_detalle", back_populates="detalle")

class Factura_gasto_detalle(Base):
    __tablename__ = "factura_gasto_detalle"
    iddetalle=Column(Integer, primary_key=True, index=True)
    idfactura_gasto = Column(Integer, ForeignKey("factura_gasto_cabecera.idfactura_gasto"))
    idproducto = Column(Integer, ForeignKey("producto.idproducto"))
    producto = relationship("Producto", back_populates="productogasto")
    descripcion_producto = Column(String(300))
    cantidad = Column(Integer)
    precio = Column(Integer)
    porcentaje_iva = Column(Integer)
    subtotal = Column(Integer)
    subtotal_iva = Column(Integer)
    detalle=relationship("Factura_gasto_cabecera", back_populates="detalles")