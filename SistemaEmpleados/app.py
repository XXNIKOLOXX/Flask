#Incluimos las librerías para hacer el renderizado de templates
from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL 
from datetime import datetime
import os
from flask import send_from_directory

#Quedamos en el Bloque 4 apartado 15
#https://www.youtube.com/watch?v=gUED5uFmyQI&t=204s
#XAMPP
 
#Creamos la aplicación
app = Flask(__name__)

app.secret_key = "Develoteca"


#Instrucciones del host de la base de datos
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sistema'
mysql.init_app(app)     #Crear conexión con los datos

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA     # Creando una referencia a una variable para almacenar la ruta a la carpeta 

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)



#Mostrar todos los datos de los empleados
@app.route('/')
def index():
                                                            # sql = "SELECT * FROM `empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados")               #cursor.execute(sql)

    empleados = cursor.fetchall()
    print(empleados) 

    conn.commit()
    return render_template('empleados/index.html', empleados=empleados)

#Eliminar Datos
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
    fila =  cursor.fetchall()
        
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
    cursor.execute("DELETE FROM empleados WHERE id=%s", (id))
    conn.commit()
    return redirect('/')



@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))
    empleados = cursor.fetchall()
    conn.commit

    return render_template('empleados/edit.html', empleados = empleados)


@app.route('/update', methods=['POST'])
def update():

    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    id=request.form['txtID']

    sql = "UPDATE `empleados` SET `nombre`=%s, `correo`=%s WHERE `id`=%s;"
    datos = (_nombre, _correo, id)


    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename !='':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
        fila =  cursor.fetchall()
        
        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE empleados set foto=%s WHERE id=%s", (nuevoNombreFoto, id))
        conn.commit()

    cursor.execute(sql,datos) 

    conn.commit()

    return redirect('/')



#Crear nuevo empleado
@app.route('/create')
def create():

    return render_template('empleados/create.html')



#Añadir info del empleado
@app.route('/store', methods=['POST'])
def storage():
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']

    if _nombre == '' or _correo == '' or _foto =='':
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))
    
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename !='':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)



    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    
    datos = (_nombre, _correo, nuevoNombreFoto)


    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos) 
    conn.commit()

    return redirect('/')
    

#Ejecucción de la aplicación
if __name__ == '__main__':
    app.run(debug=True)


