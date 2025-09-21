from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos
# 'sqlite:///pedidos.db' significa que los datos se guardarán en un archivo llamado 'pedidos.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pedidos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definición del modelo de datos (la tabla de la base de datos)
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_cliente = db.Column(db.String(100), nullable=False)
    producto = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_pedido = db.Column(db.Date, nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(50), default='Pendiente')

    def __repr__(self):
        return f'<Pedido {self.id}>'

# Creamos la base de datos y la tabla la primera vez que se ejecuta la aplicación
with app.app_context():
    db.create_all()

# Ruta para la página principal (dashboard)
@app.route('/')
def dashboard():
    # Consulta todos los pedidos de la base de datos
    pedidos = Pedido.query.order_by(Pedido.fecha_entrega).all()
    
    # Calcula alertas para cada pedido
    for pedido in pedidos:
        dias_restantes = (pedido.fecha_entrega - date.today()).days
        if dias_restantes <= 3 and dias_restantes >= 0:
            pedido.alerta = True
        else:
            pedido.alerta = False
    
    return render_template('dashboard.html', pedidos=pedidos)

# Ruta para agregar un nuevo pedido
@app.route('/agregar_pedido', methods=['GET', 'POST'])
def agregar_pedido():
    if request.method == 'POST':
        nombre = request.form['nombre']
        producto = request.form['producto']
        cantidad = int(request.form['cantidad'])
        fecha_entrega_str = request.form['fecha_entrega']
        
        fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
        
        # Crea una nueva instancia de Pedido y la añade a la base de datos
        nuevo_pedido = Pedido(
            nombre_cliente=nombre,
            producto=producto,
            cantidad=cantidad,
            fecha_pedido=date.today(),
            fecha_entrega=fecha_entrega
        )
        db.session.add(nuevo_pedido)
        db.session.commit()  # Guarda el cambio en la base de datos
        
        return redirect(url_for('dashboard'))
        
    return render_template('agregar_pedido.html')

# ---
# Nuevas rutas para eliminar y modificar pedidos

# Ruta para eliminar un pedido
@app.route('/eliminar_pedido/<int:id>')
def eliminar_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    db.session.delete(pedido)
    db.session.commit()
    return redirect(url_for('dashboard'))

# Ruta para modificar un pedido (GET para mostrar el formulario, POST para guardar)
@app.route('/modificar_pedido/<int:id>', methods=['GET', 'POST'])
def modificar_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    if request.method == 'POST':
        pedido.nombre_cliente = request.form['nombre']
        pedido.producto = request.form['producto']
        pedido.cantidad = int(request.form['cantidad'])
        pedido.fecha_entrega = datetime.strptime(request.form['fecha_entrega'], '%Y-%m-%d').date()
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('modificar_pedido.html', pedido=pedido)
# ---

if __name__ == '__main__':
    app.run(debug=True)