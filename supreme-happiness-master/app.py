#!/usr/bin/env python
import csv
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_bootstrap import Bootstrap
from forms import LoginForm, SaludarForm, RegistrarForm, ConsultaPaisForm, ConsultaEdadForm




app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'un string que funcione como llave'


@app.route('/')
def index():
    return render_template('index.html', fecha_actual=datetime.utcnow())


@app.route('/saludar', methods=['GET', 'POST'])
def saludar():
    formulario = SaludarForm()
    if formulario.validate_on_submit():  # Acá hice el POST si es True
        print(formulario.usuario.name)
        return redirect(url_for('saludar_persona', usuario=formulario.usuario.data))
    return render_template('saludar.html', form=formulario)


@app.route('/saludar/<usuario>')
def saludar_persona(usuario):
    return render_template('usuarios.html', nombre=usuario)


@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500


@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    formulario = LoginForm()
    if formulario.validate_on_submit():
        with open('usuarios') as archivo:
            archivo_csv = csv.reader(archivo)
            registro = next(archivo_csv)
            while registro:
                if formulario.usuario.data == registro[0] and formulario.password.data == registro[1]:
                    flash('Bienvenido')
                    session['username'] = formulario.usuario.data
                    return render_template('ingresado.html')
                registro = next(archivo_csv, None)
            else:
                flash('Revisá nombre de usuario y contraseña')
                return redirect(url_for('ingresar'))
    return render_template('login.html', formulario=formulario)


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    formulario = RegistrarForm()
    if formulario.validate_on_submit():
        if formulario.password.data == formulario.password_check.data:
            with open('usuarios', 'a+') as archivo:
                archivo_csv = csv.writer(archivo)
                registro = [formulario.usuario.data, formulario.password.data]
                archivo_csv.writerow(registro)
            flash('Usuario creado correctamente')
            return redirect(url_for('ingresar'))
        else:
            flash('Las passwords no matchean')
    return render_template('registrar.html', form=formulario)


@app.route('/secret', methods=['GET'])
def secreto():
    if 'username' in session:
        return render_template('private.html', username=session['username'])
    else:
        return render_template('sin_permiso.html')


@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username')
        return render_template('logged_out.html')
    else:
        return redirect(url_for('index'))


@app.route('/cargacsv', methods=['GET'])
def cargacsv():
    if 'username' in session:
        filas = []
        with open('clientes.csv', encoding='utf8') as archivo:
            archivo_csv = csv.reader(archivo)
            titulos = next(archivo_csv)
            registro = next(archivo_csv, None)
            while registro:
                filas.append(registro)
                registro = next(archivo_csv, None)
            archivo.close()
            return render_template('cargacsv.html', filas = filas, titulos = titulos)
    return redirect(url_for('sin_permiso.html'))

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/consulta/pais', methods = ['GET', 'POST'])
def consultaPorPais():
    if 'username' in session:
        paisForm = ConsultaPaisForm()
        if paisForm.validate_on_submit():
            validar = str(paisForm.pais.data).lower()
            with open("clientes.csv", encoding="utf-8") as archivo:
                archivo_csv = csv.reader(archivo)
                registro = next(archivo_csv)
                paises = []
                while registro:
                    foo = str(registro[3]).lower()
                    if validar in foo and registro[3] not in paises:
                        paises.append(registro[3])
                    registro = next(archivo_csv, None)
                return render_template('consultapais.html', formulario = paisForm, paises = paises, submit = paisForm.validate_on_submit())
        return render_template('consultapais.html', formulario = paisForm)
    return redirect(url_for('ingresar'))

@app.route('/consultafinal/pais/<pais>')
def consultafinal(pais):
    if 'username' in session:
        if pais:
            with open("clientes.csv", encoding="utf-8") as archivo:
                archivo_csv = csv.reader(archivo)
                titulos = next(archivo_csv)
                registro = next(archivo_csv, None)
                paisArg = str(pais).lower()
                filas = []
                while registro:
                    reg = str(registro[3]).lower()
                    if paisArg in reg:
                        filas.append(registro)
                    registro = next(archivo_csv, None)
                return render_template("cargacsv.html", filas = filas, titulos = titulos)
        return render_template("consultapais.html")
    return redirect(url_for('ingresar'))


@app.route('/consulta/edad' , methods = ['GET', 'POST'])
def consultaPorEdad():
    if 'username' in session:
       
        EdadForm = ConsultaEdadForm()

        if EdadForm.validate_on_submit():
            edad_min = int(EdadForm.desde.data)
            edad_max = int (EdadForm.hasta.data)
            filas = []
            with open("clientes.csv", encoding="utf-8") as archivo:
                archivo_csv = csv.reader(archivo)
                titulos = next(archivo_csv)
                registro = next(archivo_csv, None)
                
                if edad_min < 0 or edad_max < 0 :
                    flash('solo se permiten numeros positivos.')
                    return render_template("consultaedad.html", formulario = EdadForm)
 
                
                if edad_max  < edad_min :
                    flash('valores incorrectos, intente nuevamente.')
                    return render_template("consultaedad.html",formulario = EdadForm)

                while registro:
                    reg = int(registro[1])
                    if reg >= edad_min and reg <= edad_max :
                        filas.append(registro)
                    registro = next(archivo_csv, None)
                if len(filas) < 1:
                    flash('No se encontraron registros relacionados a la búsqueda.')
                return render_template("consultaedad.html", titulos = titulos, filas = filas, formulario = EdadForm)
        return render_template("consultaedad.html", formulario = EdadForm)
    return redirect(url_for('ingresar'))



if __name__ == "__main__":
    app.run(debug=True)
