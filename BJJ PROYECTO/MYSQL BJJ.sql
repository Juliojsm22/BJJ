create database BJJ;
USE BJJ;


Create table Clientes(
	id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre varchar(50) not null,
    telefono varchar(24) not null,
    correo varchar(50) not null,
    cedula varchar(50) not null
);

Create table Facturas(
	id_facturas INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente int not null,
    fecha_emision datetime,
    total float not null,
    pdf_path varchar(255) not null,
    foreign key (id_cliente) references Clientes(id_cliente)
);

Create table Paquetes(
	id_paquete INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente int not null,
    id_facturas int not null,
    warehouse varchar(50) not null,
    tracking varchar(50) not null,
    peso float not null,
    costo float not null,
    fecha datetime not null,
    facturado bit not null,
    foreign key (id_cliente) references Clientes(id_cliente),
    foreign key (id_facturas) references Facturas(id_facturas)
);

Create table DetalleFactura(
	id_factura INT AUTO_INCREMENT PRIMARY KEY,
    id_facturas int not null,
    id_paquete int not null,
    precio int not null,
    foreign key (id_facturas) references Facturas(id_facturas),
    foreign key (id_paquete) references Paquetes(id_paquete)
);


select * from Clientes;
