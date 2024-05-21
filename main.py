from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
from fastapi.responses import JSONResponse
import base64
from typing import Optional
from datetime import datetime

# Crear instancia de FastAPI
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Agrega aquí el origen de tu aplicación Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar la conexión a la base de datos MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'Videojuegos'
}

# Función para establecer la conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Definir modelos Pydantic para las entidades de la base de datos
class Usuario(BaseModel):
    nombre: str
    correo: str
    password: str

class Credenciales(BaseModel):
    correo: str
    password: str
    
class Videojuegos(BaseModel):
    titulo: str
    descripcion: str
    precio: float
    genero: str
    plataforma:str
    imagen:Optional[bytes] = None
    
    

# Ruta para registrar un nuevo usuario
@app.post("/registro")
async def crear_usuario(usuario: Usuario):
    nombre = usuario.nombre
    correo = usuario.correo
    password = usuario.password
    
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insertar el usuario en la base de datos con la fecha de registro actual
        query = """
        INSERT INTO Usuarios (Nombre, CorreoElectronico, Contraseña, FechaRegistro) 
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, correo, password, datetime.now()))
        connection.commit()

        return {"mensaje": "Usuario creado exitosamente"}
    except mysql.connector.Error as e:
        return {"error": f"Error al registrar usuario: {e.msg}"}
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

@app.post("/login")
async def iniciar_sesion(credenciales: Credenciales):
    correo = credenciales.correo
    password = credenciales.password

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Consultar la base de datos para verificar las credenciales de administrador
        query_admin = "SELECT * FROM Administradores WHERE CorreoElectronico = %s AND Contraseña = %s"
        cursor.execute(query_admin, (correo, password))
        administrador = cursor.fetchone()

        if administrador:
            return {"mensaje": "Inicio de sesión exitoso", "tipo": "admin"}
        else:
            # Si no es administrador, verificar si es un usuario normal
            query_usuario = "SELECT * FROM Usuarios WHERE CorreoElectronico = %s AND Contraseña = %s"
            cursor.execute(query_usuario, (correo, password))
            usuario = cursor.fetchone()

            if usuario:
                return {"mensaje": "Inicio de sesión exitoso", "tipo": "usuario"}
            else:
                return {"error": "Credenciales inválidas"}
    except mysql.connector.Error as e:
        return {"error": f"Error al iniciar sesión: {e.msg}"}
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
            
@app.get("/tablausuarios")
async def obtener_usuarios():
    connection = None
    cursor=None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query_usuarios = "SELECT * FROM Usuarios"
        cursor.execute(query_usuarios)
        usuarios=cursor.fetchall()
        return{"usuarios":usuarios}
    except mysql.connector.Error as e:
        return{"error":f"Error al obtener usuarios:{e.msg}"}
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()    

@app.get("/buscarusuario/{dato}")
async def buscar_usuario(dato: str):
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        if dato:
            # Consultar la base de datos para buscar usuarios por nombre o correo electrónico (búsqueda parcial)
            query_buscar = "SELECT * FROM Usuarios WHERE Nombre LIKE %s OR CorreoElectronico LIKE %s"
            cursor.execute(query_buscar, (f"%{dato}%", f"%{dato}%"))
        else:
            # Consultar la base de datos para obtener todos los usuarios
            query_todos = "SELECT * FROM Usuarios"
            cursor.execute(query_todos)
        
        usuarios = cursor.fetchall()
        
        return {"usuarios": usuarios}
    except mysql.connector.Error as e:
        return {"error": f"Error al buscar usuarios: {e.msg}"}
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


@app.delete("/eliminarusuario/{dato}")
async def eliminar_usuario(dato:str):
    connection=None
    cursor=None
    
    try:
        connection=get_db_connection()
        cursor=connection.cursor(dictionary=True)
        query_eliminar="DELETE FROM Usuarios WHERE Nombre = %s OR CorreoElectronico = %s"
        cursor.execute(query_eliminar,(dato,dato))
        connection.commit()
        return {"mensaje":"Usuario eliminado correctamente"}
    except mysql.connector.Error as e:
        return{"error":f"Error al eliminar usuario: {e.msg}"}
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

@app.post("/agregar-videojuego")
async def agregar_videojuego(videojuego: Videojuegos):
    print("Solicitud recibida para agregar un nuevo videojuego.")
    try:
        titulo = videojuego.titulo
        descripcion = videojuego.descripcion
        precio = videojuego.precio
        genero = videojuego.genero
        plataforma = videojuego.plataforma

        print("Datos del videojuego recibidos:")
        print(f"Título: {titulo}")
        print(f"Descripción: {descripcion}")
        print(f"Precio: {precio}")
        print(f"Género: {genero}")
        print(f"Plataforma: {plataforma}")

        connection = get_db_connection()
        cursor = connection.cursor()

        query = "INSERT INTO Videojuegos (Titulo, Descripcion, Precio, Genero, Plataforma) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (titulo, descripcion, precio, genero, plataforma))
        connection.commit()

        print("El videojuego se ha agregado exitosamente.")

        return {"mensaje": "Videojuego agregado exitosamente"}
    except mysql.connector.Error as e:
        error_msg = f"Error al agregar el videojuego: {e.msg}"
        print(error_msg)
        return {"error": error_msg}
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


@app.post("/subir-imagen")
async def subir_imagen(imagen: UploadFile = File(...)):
    try:
        # Leer la imagen del videojuego.
        imagen_data = await imagen.read()
        
        # Logs para verificar los datos de la imagen recibida.
        print("Datos de la imagen recibidos:")
        print(f"Nombre del archivo: {imagen.filename}")
        print(f"Tamaño de la imagen: {len(imagen_data)} bytes")
        
        # Establecer conexión a la base de datos.
        connection = get_db_connection()
        cursor = connection.cursor()

        # Verificar si hay algún registro con el campo imagen nulo en la base de datos.
        cursor.execute("SELECT COUNT(*) FROM Videojuegos WHERE Imagen IS NULL")
        count_null_imagen = cursor.fetchone()[0]

        if count_null_imagen > 0:
            # Insertar los datos binarios de la imagen en la base de datos.
            query = "UPDATE Videojuegos SET Imagen = %s WHERE Imagen IS NULL LIMIT 1"
            cursor.execute(query, (imagen_data,))
            connection.commit()

            # Log para indicar que la imagen ha sido subida exitosamente.
            print("La imagen se ha subido exitosamente.")

            # Retornar una respuesta indicando que la imagen se ha subido exitosamente.
            return {"mensaje": "Imagen subida exitosamente"}
        else:
            # No hay registros con el campo imagen nulo, por lo tanto, no se puede subir la imagen.
            error_msg = "No se puede subir la imagen. Todos los registros ya tienen una imagen."
            print(error_msg)
            return {"error": error_msg}
    except Exception as e:
        # En caso de error, retornar un mensaje de error y registrar el error.
        error_msg = f"Error al subir la imagen: {str(e)}"
        print(error_msg)
        return {"error": error_msg}
    finally:
        # Cerrar la conexión a la base de datos.
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


@app.get("/mostrarimagenes", response_model=List[Videojuegos])
async def obtener_imagenes():
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query_imagenes = "SELECT ID_juego, imagen FROM Videojuegos WHERE imagen IS NOT NULL"
        cursor.execute(query_imagenes)
        imagenes = cursor.fetchall()
        
        # Convertir los datos de imagen a base64 para enviarlos al frontend
        for imagen in imagenes:
            imagen['imagen'] = base64.b64encode(imagen['imagen']).decode('utf-8')
        
        return JSONResponse(content={"imagenes": imagenes})
    except mysql.connector.Error as e:
        return JSONResponse(content={"error": f"Error al obtener imágenes: {e.msg}"}, status_code=500)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
            
from fastapi import HTTPException

@app.get("/mostrarvideojuegos", response_model=List[Videojuegos])
async def obtener_videojuegos():
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query_videojuegos = "SELECT Titulo, Descripcion, Precio, Genero, Plataforma FROM Videojuegos"
        cursor.execute(query_videojuegos)
        videojuegos_data = cursor.fetchall()
        
        # Convertir los datos obtenidos de la base de datos en objetos Videojuegos
        videojuegos = []
        for juego in videojuegos_data:
            videojuego = Videojuegos(titulo=juego['Titulo'],
                                     descripcion=juego['Descripcion'],
                                     precio=juego['Precio'],
                                     genero=juego['Genero'],
                                     plataforma=juego['Plataforma'])
            videojuegos.append(videojuego)
        
        return videojuegos
    except mysql.connector.Error as e:
        return JSONResponse(content={"error": f"Error al obtener videojuegos: {e.msg}"}, status_code=500)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

@app.post("/change-password")
async def cambiar_contraseña(data: dict):
    correo = data.get('email')
    nueva_contraseña = data.get('password')

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Actualizar la contraseña del usuario en la base de datos
        query = "UPDATE Usuarios SET Contraseña = %s WHERE CorreoElectronico = %s"
        cursor.execute(query, (nueva_contraseña, correo))
        connection.commit()

        return {"mensaje": "Contraseña actualizada correctamente"}
    except mysql.connector.Error as e:
        return {"error": f"Error al cambiar la contraseña: {e.msg}"}
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
