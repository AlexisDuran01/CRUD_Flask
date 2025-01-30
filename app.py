import sqlite3

# Importamos la clase `Flask` para crear nuestra aplicación web.
from flask import Flask, render_template,request, url_for, flash, redirect

# `render_template` se utiliza para renderizar plantillas HTML y devolverlas como respuestas.
# Nos permite generar dinámicamente las páginas HTML que el cliente verá en su navegador.

# `request` es un objeto global que nos permite acceder a los datos de la solicitud entrante,
# tales como los datos enviados a través de un formulario HTML o parámetros en la URL.

# `url_for()` genera URLs basadas en el nombre de una función de vista.
# Es útil para construir enlaces de manera dinámica sin tener que escribir las rutas manualmente.

# `flash()` se usa para mostrar mensajes que pueden ser útiles para el usuario, como notificaciones
# de éxito, error o advertencia, después de que se procesa una solicitud, por ejemplo, tras enviar un formulario.

# `redirect()` permite redirigir al cliente a otra URL. Esto es útil cuando queremos redirigir
# a una página diferente después de procesar una acción, como enviar un formulario o realizar un cambio.


# Importamos la función `abort` desde el módulo `werkzeug.exceptions`.
# Esta función se utiliza para interrumpir la ejecución y devolver una respuesta de error HTTP.
# Por ejemplo, `abort(404)` generará una respuesta con el código de estado HTTP 404, 
# lo que indica que la página o recurso solicitado no se encontró.

from werkzeug.exceptions import abort 

def get_db_connection():
    conn=sqlite3.connect("database.db")
    conn.row_factory=sqlite3.Row
    return conn

def get_post(post_id):
    print("Obtiendo registro con id:", post_id)   
    conexion=get_db_connection()
    post= conexion.execute ('SELECT*FROM posts WHERE id= ?',
                            (post_id,)).fetchone()
    conexion.close()
    if post is None:
        print('Registro no encontrado')
        abort(404)

     # Convertir a diccionario para una mejor visualización    
    print("Registro encontrado:", dict(post)) 
    return post

def get_allpost():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    
    # Convertir los registros a una lista de diccionarios
    posts_list = [dict(post) for post in posts]
    
    # Imprimir cada registro en una nueva línea
    print("Listados registros:")
    for post in posts_list:
        print(post)  # Imprime cada registro en una nueva línea

    return posts


# Creamos una instancia de la clase Flask.
# `__name__` es una variable especial en Python que indica el nombre del módulo actual.
# - Si el archivo se ejecuta directamente, `__name__` será igual a '__main__'.
# - Si el archivo se importa como módulo, `__name__` será el nombre del archivo (por ejemplo, 'mi_app').
# Flask usa este valor para localizar recursos como plantillas HTML y archivos estáticos,
# y para configurar el manejo de errores y rutas.
app = Flask(__name__)

# Esto es necesario para que la función `flash()` pueda almacenar mensajes de manera segura en la sesión del navegador
# Flask usa esta clave para firmar y encriptar la información almacenada en las sesiones del navegador del cliente,
# como los mensajes que se pasan entre las páginas utilizando `flash()`.
# Es como una "contraseña" que asegura que los datos guardados en la sesión no puedan ser manipulados por los usuarios.
app.config['SECRET_KEY'] = '12qwe3'


# Definimos una ruta para la URL raíz ('/').
@app.route('/')
def index():
    posts=get_allpost()
    return render_template("index.html", posts=posts)

# Definimos una nueva ruta que incluye una regla de variable '<int:post_id>'.
# Esta regla especifica que la parte tras la barra (/) debe ser un entero positivo.
# Flask reconoce esta regla y pasa el valor capturado como argumento al parámetro `post_id` de la función `post()`.
@app.route('/post/<int:post_id>')
def post(post_id):
    # Imprimimos el ID del post recibido para depuración o registro.
    print(post_id)

    # Llamamos a la función `get_post()` con el ID especificado para obtener
    # la entrada del blog asociada. El resultado se almacena en la variable `post`.
    post = get_post(post_id)

    # Renderizamos la plantilla 'post.html', pasando la información del post
    # para que pueda mostrarse en la interfaz de usuario.
    return render_template("post.html", post=post)


# Definimos una ruta para la URL '/acerca'.
# Este decorador asocia la URL '/acerca' con la función `acerca`.
#  No necesita especificar los métodos, ya que por defecto Flask 
#  maneja las solicitudes GET en cualquier ruta, si no se indica lo contrario.
@app.route('/acerca')
def acerca():
    # Cuando alguien accede a la URL '/acerca', esta función se ejecuta.
    # Renderiza y devuelve la plantilla "acerca.html".
    return render_template("acerca.html")

#Si necesitamos manejar ambos métodos (GET para mostrar el formulario 
# y POST para procesarlo), tenemos que indicarlo explicitamente.
@app.route('/crear', methods=('GET', 'POST'))
# Creamos una ruta '/crear' que acepta tanto solicitudes GET (por defecto) como POST.
# GET se usa para mostrar el formulario inicialmente y POST para manejar el envío de datos desde el formulario.
def create():
    # Inicializamos las variables antes de procesar la solicitud
    title = ''  
    contenido = ''  

    # Manejo cuando la solicitud es GET (cuando el usuario accede al formulario)
    if request.method == 'GET':
        # Mostramos el formulario vacío para crear un nuevo post
        return render_template('crear.html')

    elif request.method == 'POST':
        # Manejo cuando la solicitud es POST (cuando el formulario se envía)
        title = request.form['title']  # Extraemos el título del formulario
        contenido = request.form['content']  # Extraemos el contenido del formulario

        if not title:
            # Si el título está vacío, mostramos un mensaje de error

            '''
            La función flash es utilizada para almacenar un mensaje que se puede
            mostrar después en la interfaz de usuario.

            El primer argumento es el mensaje (texto que se mostrará al usuario),
            y el segundo es la categoría del mensaje

            El mensaje se almacena en la sesión que estará disponible solo durante 
            la siguiente solicitud. Este mensaje se mostrará una vez y luego se 
            eliminará automáticamente
            '''
            flash('El título es necesario', 'danger')
           
            '''
            Cuando recargamos la pagina se envia el formualario nuevamente por eso se
            muestra la alerta de error y no se quita, para que se quite se debe de 
            usar redirect(url_for('')) en lugar de render_template.
            '''
            #Se renderizar el formulario con los datos actuales y el mensaje de error
            return render_template("crear.html")

        else:
            # Si el título está presente, guardamos los datos en la base de datos
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, contenido))
            conn.commit()  # Confirmamos la inserción en la base de datos
            conn.close()  # Cerramos la conexión

            #mostramos un mensaje de exito
            flash('Post creado correctamente', 'success')
            # Redirigimos al índice después de guardar el post
            return redirect(url_for('index'))


# Define una ruta para editar un registro existente.
# La URL incluye un parámetro dinámico <int:post_id>, que es el ID del post a editar
# y se debe de llamar igual que el paramatro que recibe la funcion.

@app.route('/editar/<int:post_id>', methods=('GET', 'POST'))
def edit(post_id):
    # Llama a la función get_post(post_id) para obtener el post que se desea editar
    # El post se busca por su ID, que se pasa como argumento.
    post = get_post(post_id)


    # Manejo cuando la solicitud es GET (cuando el usuario accede al formulario)
    if request.method == 'GET':
        # Mostramos el formulario lleno para actualizar un  post
        return render_template('editar.html', post=post)


    # Comprueba si la solicitud es de tipo POST (es decir, si se envió el formulario).
    if request.method == 'POST':
        # Obtiene el título ingresado por el usuario desde el formulario.
        title = request.form['title']
        # Obtiene el contenido ingresado por el usuario desde el formulario.
        content = request.form['content']

        # Valida si se ingresó un título. Si no, muestra un mensaje de error.
        if not title:
            flash('El título es necesario', 'danger')
            return render_template("editar.html", post=post)

        else:
            # Abre una conexión a la base de datos.
            conn = get_db_connection()
            # Ejecuta una consulta SQL para actualizar el título y el contenido del post con el ID correspondiente.
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, post_id))
            # Confirma los cambios realizados en la base de datos.
            conn.commit()
            # Cierra la conexión con la base de datos.
            conn.close()

            flash('Post actualizado correctamente', 'success')

            # Redirige al usuario a la página principal después de actualizar el post.
            return redirect(url_for('index'))
  
#El parametro methods necesita una lista de strings por eso se pone la coma
@app.route('/eliminar/<int:id>', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    #Tambien se necesita una lista de strings por eso se pone la coma 
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    # Formateamos la cadena con el título del post (post['title']) usando .format().
    # Esto reemplaza '{}' con el valor del título del post, por ejemplo, si el título es "My Post", 
    # el mensaje resultante será "My Post fue eliminado correctamente".
    flash('"{}" fue elimado correctamente'.format(post['title']),"success")
    return redirect(url_for('index')) 

# Este bloque garantiza que el servidor web solo se inicie
# si este archivo se ejecuta directamente (no cuando se importa como módulo).
if __name__ == '__main__':
    # Ejecutamos la aplicación Flask.
        app.run()
    # Por defecto, el servidor se inicia en http://127.0.0.1:5000.

