
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Jugador(db.Model):
    __tablename__ = 'jugador'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ap_paterno = db.Column(db.String(100), nullable=False)
    ap_materno = db.Column(db.String(100), nullable=False)
    equipo = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Jugador {self.nombre}>'

# Función para verificar e inicializar la base de datos
def init_database():
    try:
        with app.app_context():
            # Verificar si la tabla ya existe
            inspector = db.inspect(db.engine)
            if 'jugador' not in inspector.get_table_names():
                print("Creando tablas...")
                db.create_all()
                print("Tablas creadas exitosamente")
            else:
                print("Las tablas ya existen")
    except Exception as e:
        print(f"Error al inicializar base de datos: {e}")

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            ap_paterno = request.form['ap_paterno']
            ap_materno = request.form['ap_materno']
            equipo = request.form['equipo']
            edad = int(request.form['edad'])
            
            # Verificar si la tabla existe antes de insertar
            inspector = db.inspect(db.engine)
            if 'jugador' not in inspector.get_table_names():
                flash('La base de datos no está inicializada. Por favor, contacta al administrador.')
                return render_template('create_jugador.html')
            
            jugador = Jugador(nombre=nombre, ap_paterno=ap_paterno, ap_materno=ap_materno, equipo=equipo, edad=edad)
            db.session.add(jugador)
            db.session.commit()
            return render_template('jugador_creado.html')
            
        except Exception as e:
            flash(f'Error al crear jugador: {str(e)}')
            return render_template('create_jugador.html')
    
    return render_template('create_jugador.html')
# Ruta para listar jugadores
@app.route('/jugadores')
def listar_jugadores():
    jugadores = Jugador.query.all()
    return render_template('listar_jugadores.html', jugadores=jugadores)
@app.route('/admin/init-db')
def admin_init_db():
    try:
        with app.app_context():
            db.create_all()
            return 'Base de datos inicializada correctamente. <a href="/">Volver</a>'
    except Exception as e:
        return f'Error: {str(e)}'



# Inicializar la base de datos antes de cada request (solo la primera vez)
_db_initialized = False
@app.before_request
def before_request_func():
    global _db_initialized
    if not _db_initialized:
        init_database()
        _db_initialized = True

if __name__ == '__main__':
    app.run(debug=True)