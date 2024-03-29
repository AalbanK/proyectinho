-- MySQL Script generated by MySQL Workbench
-- Thu Oct  5 18:29:28 2023
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema evolucion2.0
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema evolucion2.0
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `evolucion2.0` DEFAULT CHARACTER SET utf8 ;
USE `evolucion2.0` ;

-- -----------------------------------------------------
-- Table `evolucion2.0`.`IVA`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`IVA` (
  `idIVA` INT NOT NULL AUTO_INCREMENT,
  `porcentaje` INT NOT NULL,
  PRIMARY KEY (`idIVA`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`producto`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`producto` (
  `idproducto` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(45) NOT NULL,
  `stock` INT NOT NULL,
  `idIVA` INT NOT NULL,
  PRIMARY KEY (`idproducto`),
  INDEX `fk_producto_IVA1_idx` (`idIVA` ASC)  ,
  CONSTRAINT `fk_producto_IVA1`
    FOREIGN KEY (`idIVA`)
    REFERENCES `evolucion2.0`.`IVA` (`idIVA`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = '				';


-- -----------------------------------------------------
-- Table `evolucion2.0`.`departamento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`departamento` (
  `iddepartamento` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`iddepartamento`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`ciudad`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`ciudad` (
  `idciudad` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(45) NOT NULL,
  `iddepartamento` INT NOT NULL,
  PRIMARY KEY (`idciudad`),
  INDEX `fk_ciudad_departamentos1_idx` (`iddepartamento` ASC)  ,
  CONSTRAINT `fk_ciudad_departamentos1`
    FOREIGN KEY (`iddepartamento`)
    REFERENCES `evolucion2.0`.`departamento` (`iddepartamento`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`proveedor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`proveedor` (
  `idproveedor` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(45) NOT NULL,
  `ruc` VARCHAR(15) NOT NULL,
  `idciudad` INT NOT NULL,
  `direccion` VARCHAR(45) NOT NULL,
  `mail` VARCHAR(45) NOT NULL,
  `telefono` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idproveedor`),
  INDEX `fk_proveedor_ciudad1_idx` (`idciudad` ASC)  ,
  CONSTRAINT `fk_proveedor_ciudad1`
    FOREIGN KEY (`idciudad`)
    REFERENCES `evolucion2.0`.`ciudad` (`idciudad`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`cliente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`cliente` (
  `idcliente` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(45) NOT NULL,
  `ruc` VARCHAR(15) NOT NULL,
  `idciudad` INT NOT NULL,
  `direccion` VARCHAR(45) NOT NULL,
  `mail` VARCHAR(45) NOT NULL,
  `telefono` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idcliente`),
  INDEX `fk_cliente_ciudad1_idx` (`idciudad` ASC)  ,
  CONSTRAINT `fk_cliente_ciudad1`
    FOREIGN KEY (`idciudad`)
    REFERENCES `evolucion2.0`.`ciudad` (`idciudad`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`rol`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`rol` (
  `idrol` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idrol`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`usuario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`usuario` (
  `idusuario` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(300) NOT NULL,
  `idrol` INT NOT NULL,
  PRIMARY KEY (`idusuario`),
  INDEX `fk_usuario_rol1_idx` (`idrol` ASC)  ,
  CONSTRAINT `fk_usuario_rol1`
    FOREIGN KEY (`idrol`)
    REFERENCES `evolucion2.0`.`rol` (`idrol`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`auditoria`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`auditoria` (
  `idauditoria` INT NOT NULL AUTO_INCREMENT,
  `accion` VARCHAR(45) NOT NULL,
  `accion_fecha` INT NOT NULL,
  `valor_viejo` VARCHAR(45) NOT NULL,
  `valor_nuevo` VARCHAR(45) NOT NULL,
  `idusuario` INT NOT NULL,
  PRIMARY KEY (`idauditoria`),
  INDEX `fk_auditoria_usuario1_idx` (`idusuario` ASC)  ,
  CONSTRAINT `fk_auditoria_usuario1`
    FOREIGN KEY (`idusuario`)
    REFERENCES `evolucion2.0`.`usuario` (`idusuario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`factura_venta_cabecera`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`factura_venta_cabecera` (
  `idfactura_venta` INT NOT NULL AUTO_INCREMENT,
  `nro` INT NOT NULL,
  `fecha` DATETIME NOT NULL,
  `idcliente` INT NOT NULL,
  `total_iva` INT NOT NULL,
  `total_monto` INT NOT NULL,
  `idcontrato` INT NOT NULL,
  PRIMARY KEY (`idfactura_venta`),
  INDEX `fk_factura_venta_cliente1_idx` (`idcliente` ASC)  ,
  CONSTRAINT `fk_factura_venta_cliente1`
    FOREIGN KEY (`idcliente`)
    REFERENCES `evolucion2.0`.`cliente` (`idcliente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`factura_compra_cabecera`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`factura_compra_cabecera` (
  `idfactura_venta` INT NOT NULL AUTO_INCREMENT,
  `nro` INT NOT NULL,
  `fecha` DATETIME NOT NULL,
  `tipo` INT NOT NULL,
  `vencimiento` DATETIME NULL,
  `saldo` INT NULL,
  `idproveedor` INT NOT NULL,
  `total_iva` INT NOT NULL,
  `total_monto` INT NOT NULL,
  `idcontrato` INT NOT NULL,
  PRIMARY KEY (`idfactura_venta`),
  INDEX `fk_factura_compra_proveedor1_idx` (`idproveedor` ASC)  ,
  CONSTRAINT `fk_factura_compra_proveedor1`
    FOREIGN KEY (`idproveedor`)
    REFERENCES `evolucion2.0`.`proveedor` (`idproveedor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`factura_compra_detalle`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`factura_compra_detalle` (
  `idcabecera_venta` INT NOT NULL AUTO_INCREMENT,
  `idproducto` INT NOT NULL,
  `cantidad` INT NOT NULL,
  `precio` INT NOT NULL,
  `subtotaliva` INT NOT NULL,
  `subtotal` INT NOT NULL,
  PRIMARY KEY (`idcabecera_venta`, `idproducto`),
  INDEX `fk_producto_has_factura_compra_factura_compra1_idx` (`idcabecera_venta` ASC)  ,
  INDEX `fk_producto_has_factura_compra_producto1_idx` (`idproducto` ASC)  ,
  CONSTRAINT `fk_producto_has_factura_compra_producto1`
    FOREIGN KEY (`idproducto`)
    REFERENCES `evolucion2.0`.`producto` (`idproducto`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_producto_has_factura_compra_factura_compra1`
    FOREIGN KEY (`idcabecera_venta`)
    REFERENCES `evolucion2.0`.`factura_compra_cabecera` (`idfactura_venta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`factura_venta_detalle`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`factura_venta_detalle` (
  `idcabecera_venta` INT NOT NULL,
  `idproducto` INT NOT NULL,
  `cantidad` INT NOT NULL,
  `precio` INT NOT NULL,
  `subtotal` INT NOT NULL,
  `subtotiva` INT NOT NULL,
  PRIMARY KEY (`idcabecera_venta`, `idproducto`),
  INDEX `fk_factura_venta_has_producto_producto1_idx` (`idproducto` ASC)  ,
  INDEX `fk_factura_venta_has_producto_factura_venta1_idx` (`idcabecera_venta` ASC)  ,
  CONSTRAINT `fk_factura_venta_has_producto_factura_venta1`
    FOREIGN KEY (`idcabecera_venta`)
    REFERENCES `evolucion2.0`.`factura_venta_cabecera` (`idfactura_venta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_factura_venta_has_producto_producto1`
    FOREIGN KEY (`idproducto`)
    REFERENCES `evolucion2.0`.`producto` (`idproducto`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`chofer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`chofer` (
  `idchofer` INT NOT NULL AUTO_INCREMENT,
  `ci` INT NOT NULL,
  `nombre` VARCHAR(45) NOT NULL,
  `apellido` VARCHAR(45) NOT NULL,
  `idciudad` INT NOT NULL,
  `chofer_dir` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idchofer`),
  INDEX `fk_chofer_ciudad1_idx` (`idciudad` ASC)  ,
  CONSTRAINT `fk_chofer_ciudad1`
    FOREIGN KEY (`idciudad`)
    REFERENCES `evolucion2.0`.`ciudad` (`idciudad`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`marca_camion`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`marca_camion` (
  `idmarca_camion` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idmarca_camion`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`marca_carreta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`marca_carreta` (
  `idmarca_carreta` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idmarca_carreta`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`carreta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`carreta` (
  `idcarreta` INT NOT NULL AUTO_INCREMENT,
  `chapa` VARCHAR(7) NOT NULL,
  `idmarca_carreta` INT NOT NULL,
  PRIMARY KEY (`idcarreta`),
  INDEX `fk_carreta_marca_carreta1_idx` (`idmarca_carreta` ASC)  ,
  CONSTRAINT `fk_carreta_marca_carreta1`
    FOREIGN KEY (`idmarca_carreta`)
    REFERENCES `evolucion2.0`.`marca_carreta` (`idmarca_carreta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`camion`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`camion` (
  `idcamion` INT NOT NULL AUTO_INCREMENT,
  `camion_chapa` VARCHAR(7) NOT NULL,
  `idmarca_camion` INT NOT NULL,
  `idcarreta` INT NOT NULL,
  PRIMARY KEY (`idcamion`),
  INDEX `fk_camion_marca_camion1_idx` (`idmarca_camion` ASC)  ,
  INDEX `fk_camion_carreta1_idx` (`idcarreta` ASC)  ,
  CONSTRAINT `fk_camion_marca_camion1`
    FOREIGN KEY (`idmarca_camion`)
    REFERENCES `evolucion2.0`.`marca_camion` (`idmarca_camion`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_camion_carreta1`
    FOREIGN KEY (`idcarreta`)
    REFERENCES `evolucion2.0`.`carreta` (`idcarreta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`remision`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`remision` (
  `idremision` INT NOT NULL AUTO_INCREMENT,
  `fecha_carga` DATETIME NOT NULL,
  `fecha_descarga` DATETIME NOT NULL,
  `bruto` INT NOT NULL,
  `tara` INT NOT NULL,
  `neto` INT NOT NULL,
  `idchofer` INT NOT NULL,
  `idcontrato` INT NOT NULL,
  `idcamion` INT NOT NULL,
  PRIMARY KEY (`idremision`),
  INDEX `fk_remision_chofer1_idx` (`idchofer` ASC)  ,
  INDEX `fk_remision_camion1_idx` (`idcamion` ASC)  ,
  CONSTRAINT `fk_remision_chofer1`
    FOREIGN KEY (`idchofer`)
    REFERENCES `evolucion2.0`.`chofer` (`idchofer`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_remision_camion1`
    FOREIGN KEY (`idcamion`)
    REFERENCES `evolucion2.0`.`camion` (`idcamion`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`banco`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`banco` (
  `idbanco` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idbanco`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`cuenta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`cuenta` (
  `idcuenta` INT NOT NULL AUTO_INCREMENT,
  `idbanco` INT NOT NULL,
  `nro` VARCHAR(45) NOT NULL,
  `idcliente` INT NULL,
  `idproveedor` INT NULL,
  PRIMARY KEY (`idcuenta`),
  INDEX `fk_cuenta_banco1_idx` (`idbanco` ASC)  ,
  INDEX `fk_cuenta_cliente1_idx` (`idcliente` ASC)  ,
  INDEX `fk_cuenta_proveedor1_idx` (`idproveedor` ASC)  ,
  CONSTRAINT `fk_cuenta_banco1`
    FOREIGN KEY (`idbanco`)
    REFERENCES `evolucion2.0`.`banco` (`idbanco`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_cuenta_cliente1`
    FOREIGN KEY (`idcliente`)
    REFERENCES `evolucion2.0`.`cliente` (`idcliente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_cuenta_proveedor1`
    FOREIGN KEY (`idproveedor`)
    REFERENCES `evolucion2.0`.`proveedor` (`idproveedor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`contrato_compra`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`contrato_compra` (
  `idcontrato_compra` INT NOT NULL,
  `nro` INT NOT NULL,
  `fecha` DATETIME NOT NULL,
  `proveedor_idproveedor` INT NOT NULL,
  `producto_idproducto` INT NOT NULL,
  `precio` INT NOT NULL,
  `cantidad` INT NOT NULL,
  `fecha_inicio` DATETIME NOT NULL,
  `fecha_fin` DATETIME NOT NULL,
  PRIMARY KEY (`idcontrato_compra`),
  INDEX `fk_contrato_compra_proveedor1_idx` (`proveedor_idproveedor` ASC)  ,
  INDEX `fk_contrato_compra_producto1_idx` (`producto_idproducto` ASC)  ,
  CONSTRAINT `fk_contrato_compra_proveedor1`
    FOREIGN KEY (`proveedor_idproveedor`)
    REFERENCES `evolucion2.0`.`proveedor` (`idproveedor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_contrato_compra_producto1`
    FOREIGN KEY (`producto_idproducto`)
    REFERENCES `evolucion2.0`.`producto` (`idproducto`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`contrato_venta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`contrato_venta` (
  `idcontrato_venta` INT NOT NULL,
  `nro` INT NOT NULL,
  `fecha` DATETIME NOT NULL,
  `cliente_idcliente` INT NOT NULL,
  `producto_idproducto` INT NOT NULL,
  `precio` INT NOT NULL,
  `cantidad` INT NOT NULL,
  `fecha_inicio` DATETIME NOT NULL,
  `fecha_fin` DATETIME NOT NULL,
  PRIMARY KEY (`idcontrato_venta`),
  INDEX `fk_contrato_compra_producto1_idx` (`producto_idproducto` ASC)  ,
  INDEX `fk_contrato_venta_cliente1_idx` (`cliente_idcliente` ASC)  ,
  CONSTRAINT `fk_contrato_compra_producto10`
    FOREIGN KEY (`producto_idproducto`)
    REFERENCES `evolucion2.0`.`producto` (`idproducto`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_contrato_venta_cliente1`
    FOREIGN KEY (`cliente_idcliente`)
    REFERENCES `evolucion2.0`.`cliente` (`idcliente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `evolucion2.0`.`lote`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `evolucion2.0`.`lote` (
  `idlote` INT NOT NULL,
  `idcontrato_venta` INT NOT NULL,
  `idcontrato_compra` INT NOT NULL,
  `remision_idremision` INT NOT NULL,
  `saldo_carga` INT NULL,
  `saldo_descarga` INT NULL,
  `factura_venta_cabecera_idfactura_venta` INT NOT NULL,
  `factura_compra_cabecera_idfactura_venta` INT NOT NULL,
  PRIMARY KEY (`idlote`, `idcontrato_venta`, `idcontrato_compra`),
  INDEX `fk_lote_contrato_venta1_idx` (`idcontrato_venta` ASC)  ,
  INDEX `fk_lote_contrato_compra1_idx` (`idcontrato_compra` ASC)  ,
  INDEX `fk_lote_remision1_idx` (`remision_idremision` ASC)  ,
  INDEX `fk_lote_factura_venta_cabecera1_idx` (`factura_venta_cabecera_idfactura_venta` ASC)  ,
  INDEX `fk_lote_factura_compra_cabecera1_idx` (`factura_compra_cabecera_idfactura_venta` ASC)  ,
  CONSTRAINT `fk_lote_contrato_venta1`
    FOREIGN KEY (`idcontrato_venta`)
    REFERENCES `evolucion2.0`.`contrato_venta` (`idcontrato_venta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_lote_contrato_compra1`
    FOREIGN KEY (`idcontrato_compra`)
    REFERENCES `evolucion2.0`.`contrato_compra` (`idcontrato_compra`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_lote_remision1`
    FOREIGN KEY (`remision_idremision`)
    REFERENCES `evolucion2.0`.`remision` (`idremision`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_lote_factura_venta_cabecera1`
    FOREIGN KEY (`factura_venta_cabecera_idfactura_venta`)
    REFERENCES `evolucion2.0`.`factura_venta_cabecera` (`idfactura_venta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_lote_factura_compra_cabecera1`
    FOREIGN KEY (`factura_compra_cabecera_idfactura_venta`)
    REFERENCES `evolucion2.0`.`factura_compra_cabecera` (`idfactura_venta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
