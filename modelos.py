from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DECIMAL
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "Usuarios"

    ID_usuario = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(50), nullable=False)
    CorreoElectronico = Column(String(100), nullable=False)
    Contraseña = Column(String(50), nullable=False)
    InformacionPerfil = Column(Text)
    transacciones = relationship("Transaccion", back_populates="usuario")
    carrito_compras = relationship("CarritoCompra", back_populates="usuario")
    reseñas = relationship("Reseña", back_populates="usuario")

class Videojuego(Base):
    __tablename__ = "Videojuegos"

    ID_juego = Column(Integer, primary_key=True, autoincrement=True)
    Titulo = Column(String(100), nullable=False)
    Descripcion = Column(Text)
    Precio = Column(DECIMAL(10, 2), nullable=False)
    Genero = Column(String(50), nullable=False)
    Plataforma = Column(String(50), nullable=False)
    Imagen = Column(String(255))
    carrito_compras = relationship("CarritoCompra", back_populates="videojuego")
    reseñas = relationship("Reseña", back_populates="videojuego")

class CarritoCompra(Base):
    __tablename__ = "CarritoCompras"

    ID_compras = Column(Integer, primary_key=True, autoincrement=True)
    ID_usuario = Column(Integer, ForeignKey("Usuarios.ID_usuario"), nullable=False)
    ID_juego = Column(Integer, ForeignKey("Videojuegos.ID_juego"), nullable=False)
    Cantidad = Column(Integer, nullable=False)
    usuario = relationship("Usuario", back_populates="carrito_compras")
    videojuego = relationship("Videojuego", back_populates="carrito_compras")

class Transaccion(Base):
    __tablename__ = "Transacciones"

    ID_transaccion = Column(Integer, primary_key=True, autoincrement=True)
    ID_usuario = Column(Integer, ForeignKey("Usuarios.ID_usuario"), nullable=False)
    Fecha = Column(Date, nullable=False)
    Total = Column(DECIMAL(10, 2), nullable=False)
    usuario = relationship("Usuario", back_populates="transacciones")

class Reseña(Base):
    __tablename__ = "Reseñas"

    ID_reseña = Column(Integer, primary_key=True, autoincrement=True)
    ID_usuario = Column(Integer, ForeignKey("Usuarios.ID_usuario"), nullable=False)
    ID_juego = Column(Integer, ForeignKey("Videojuegos.ID_juego"), nullable=False)
    Comentario = Column(Text)
    Calificacion = Column(Integer, nullable=False)
    usuario = relationship("Usuario", back_populates="reseñas")
    videojuego = relationship("Videojuego", back_populates="reseñas")
