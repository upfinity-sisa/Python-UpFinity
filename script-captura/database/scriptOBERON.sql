create database oberon;

use oberon;

create table empresa (
idEmpresa int primary key auto_increment,
nome varchar(45),
CNPJ char(14),
logradouro varchar(45),
num char(5),
bairro varchar(45),
cidade varchar(45),
UF char(2),
CEP char(8)
);

create table token (
idToken int auto_increment,
statusToken boolean,
dtCriacao datetime,
duracaoHoras int,
idEmpresa int,
constraint pkTokenEmpresa primary key (idToken, idEmpresa),
constraint fkEmpresa foreign key (idEmpresa) references empresa(idEmpresa)
);

create table nivelAcesso (
idAcesso int primary key auto_increment,
descricao varchar(45),
tipo int
);

create table funcionario (
idFuncionario int auto_increment,
nome varchar(45),
CPF char(11),
email varchar(45),
senha varchar(45),
idEmpresa int,
idAcesso int,
constraint pkFuncionarioEmpresa primary key (idFuncionario, idEmpresa),
constraint fkEmpresaFuncionario foreign key (idEmpresa) references empresa(idEmpresa),
constraint fkAcesso foreign key (idAcesso) references nivelAcesso(idAcesso)
);

create table maquina (
idMaquina int auto_increment,
nome varchar(45),
enderecoIP char(15),
idEmpresa int,
constraint pkMaquinaEmpresa primary key (idMaquina, idEmpresa),
constraint fkEmpresaMaquina foreign key (idEmpresa) references empresa(idEmpresa)
);

create table statusMaquina (
idStatus int auto_increment,
nome varchar(45),
tipo int,
idMaquina int,
constraint pkStatusMaquina primary key (idStatus, idMaquina),
constraint fkMaquina foreign key (idMaquina) references maquina(idMaquina)
);

create table tipoComponente (
idTipoCP int primary key auto_increment,
nome varchar(45),
descricao varchar(45),
unidadeMedida varchar(45)
);

create table componente (
idComponente int auto_increment,
nome varchar(45),
idMaquina int,
idTipoCP int,
constraint pkComponenteMaquina primary key (idComponente, idMaquina),
constraint fkMaquinaComponente foreign key (idMaquina) references maquina(idMaquina),
constraint fkTipoCP foreign key (idTipoCP) references tipoComponente(idTipoCP)
);

create table captura (
idCaptura int auto_increment,
valor float,
dtCaptura datetime,
idComponente int,
constraint pkComponente primary key (idCaptura, idComponente),
constraint fkComponente foreign key (idComponente) references componente(idComponente)
);

create table tipoAlerta (
idTPalerta int primary key auto_increment,
nome varchar(45),
descricao varchar(45),
nivel int
);

create table alerta (
idAlerta int auto_increment,
idCaptura int,
idTPalerta int,
constraint pkAlertaCaptura primary  key (idAlerta, idCaptura),
constraint fkCaptura foreign key (idCaptura) references captura(idCaptura),
constraint fkTPalerta foreign key (idTPalerta) references tipoAlerta(idTPalerta)
);