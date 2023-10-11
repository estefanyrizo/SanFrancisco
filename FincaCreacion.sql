
CREATE TABLE IF NOT EXISTS tipoentidad
(
    id serial NOT NULL,
    tipoEntidad varchar(20) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS entidadcomercial
(
    id serial NOT NULL,
    nombre varchar(100) NOT NULL,
    apellido varchar(100),
    telefono varchar(20),
    identificacion varchar(50) NOT NULL,
    tipoEntidadId integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS venta
(
    id serial NOT NULL,
    fecha date NOT NULL,
    cantidad integer NOT NULL,
    montoTotal real NOT NULL,
    cartaVenta varchar(255),
    usuarioId integer NOT NULL,
    entidadComercialId integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS detalleventa
(
    id serial NOT NULL,
    ganadoId integer NOT NULL,
    ventaId integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS registroProduccion
(
    id serial NOT NULL,
    fecha date NOT NULL,
    peso real NOT NULL,
    comentario varchar(255),
    ganadoId integer NOT NULL,
    usuarioId integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS raza
(
    id serial NOT NULL,
    nombreRaza varchar(100) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS ganado
(
    id serial NOT NULL,
    nombre varchar(255),
    fechaNacimiento date NOT NULL,
    peso real NOT NULL,
    tamaño real NOT NULL,
    color varchar(255) NOT NULL,
    codigoChapa varchar NOT NULL,
    foto varchar(255) NOT NULL,
    comentario varchar(255),
    estadoGanadoId integer NOT NULL,
    razaId integer NOT NULL,
    origenGanadoId integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS origenganado
(
    id serial NOT NULL,
    origen varchar(10) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS detallealimento
(
    id serial NOT NULL,
    cantidadSuministrada real NOT NULL,
    costo real NOT NULL,
    alimentoId integer NOT NULL,
    ganadoId integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS alimento
(
    id serial NOT NULL,
    nombre varchar(255) NOT NULL,
    precioCompra real NOT NULL,
    cantidadComprada integer NOT NULL,
    fechaCompra date NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS registromedico
(
    id serial NOT NULL,
    dosis varchar(255) NOT NULL,
    fecha date NOT NULL,
    diagnostico varchar(255) NOT NULL,
    medicinaId integer NOT NULL,
    enfermedadId integer NOT NULL,
    ganadoId integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS detallecompra
(
    id serial NOT NULL,
    compraId integer NOT NULL,
    ganadoId integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS enfermedad
(
    id serial NOT NULL,
    nombre varchar(150) NOT NULL,
    contagiosa boolean NOT NULL DEFAULT false,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS compra
(
    id serial NOT NULL,
    fecha date NOT NULL,
    cantidad integer NOT NULL,
    montoTotal real NOT NULL,
    cartaCompra varchar(255) NOT NULL,
    usuarioId integer NOT NULL,
    entidadComercialId integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS medicina
(
    id serial NOT NULL,
    nombre varchar(255) NOT NULL,
    fechaVencimiento date NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS detallepresentacion
(
    id serial NOT NULL,
    contenido real NOT NULL,
    precio real NOT NULL,
    presentacionId integer NOT NULL,
    medicinaId integer NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS presentacion
(
    id serial NOT NULL,
    presentacion varchar(50) NOT NULL,
    viaAplicacion varchar(30) NOT NULL,
    unidadMedida varchar(20) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS usuario
(
    id serial NOT NULL,
    nombre varchar(100) NOT NULL,
    apellido varchar(100) NOT NULL,
    usuario varchar(30) NOT NULL,
    hash varchar(255) NOT NULL,
    isAdmin boolean NOT NULL DEFAULT false,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS estadoganado
(
    id serial NOT NULL,
    estado varchar(20) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS entidadcomercial
    ADD CONSTRAINT tipoEntidadId FOREIGN KEY (tipoEntidadId)
    REFERENCES tipoentidad (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS venta
    ADD CONSTRAINT entidadComercialId FOREIGN KEY (entidadComercialId)
    REFERENCES entidadcomercial (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS venta
    ADD CONSTRAINT usuarioId FOREIGN KEY (usuarioId)
    REFERENCES usuario (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS detalleventa
    ADD CONSTRAINT ganadoId FOREIGN KEY (ganadoId)
    REFERENCES ganado (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS detalleventa
    ADD CONSTRAINT ventaId FOREIGN KEY (ventaId)
    REFERENCES venta (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS registroProduccion
    ADD CONSTRAINT ganadoId FOREIGN KEY (ganadoId)
    REFERENCES ganado (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS registroProduccion
    ADD CONSTRAINT usuarioId FOREIGN KEY (usuarioId)
    REFERENCES usuario (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS ganado
    ADD CONSTRAINT origenGanado FOREIGN KEY (origenGanadoId)
    REFERENCES origenganado (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS ganado
    ADD CONSTRAINT razaId FOREIGN KEY (razaId)
    REFERENCES raza (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS ganado
    ADD CONSTRAINT estadoGanadoId FOREIGN KEY (estadoGanadoId)
    REFERENCES estadoganado (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS detallealimento
    ADD CONSTRAINT alimentoId FOREIGN KEY (alimentoId)
    REFERENCES alimento (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS detallealimento
    ADD CONSTRAINT ganadoId FOREIGN KEY (ganadoId)
    REFERENCES ganado (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS registromedico
    ADD CONSTRAINT medicinaId FOREIGN KEY (medicinaId)
    REFERENCES medicina (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS registromedico
    ADD CONSTRAINT enfermedadId FOREIGN KEY (enfermedadId)
    REFERENCES enfermedad (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS registromedico
    ADD CONSTRAINT ganadoId FOREIGN KEY (ganadoId)
    REFERENCES ganado (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS detallecompra
    ADD CONSTRAINT compraId FOREIGN KEY (compraId)
    REFERENCES compra (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS detallecompra
    ADD CONSTRAINT ganadoId FOREIGN KEY (ganadoId)
    REFERENCES ganado (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS compra
    ADD CONSTRAINT entidadComercialId FOREIGN KEY (entidadComercialId)
    REFERENCES entidadcomercial (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS compra
    ADD CONSTRAINT usuarioId FOREIGN KEY (usuarioId)
    REFERENCES usuario (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS detallepresentacion
    ADD CONSTRAINT presentacionId FOREIGN KEY (presentacionId)
    REFERENCES presentacion (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS detallepresentacion
    ADD CONSTRAINT medicinaId FOREIGN KEY (medicinaId)
    REFERENCES medicina (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

END;