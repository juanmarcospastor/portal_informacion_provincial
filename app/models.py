from . import db


class ExportacionProvincial(db.Model):
    __tablename__ = "exportaciones_provinciales"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(7), index=True, nullable=False)  # YYYY-MM
    provincia = db.Column(db.String(80), index=True, nullable=False)
    exportaciones_mineras_usd = db.Column(db.Float, nullable=False)
    exportaciones_totales_usd = db.Column(db.Float, nullable=True)
    variacion_interanual_pct = db.Column(db.Float, nullable=True)
    fuente = db.Column(db.String(200), nullable=True)


class ExportacionProducto(db.Model):
    __tablename__ = "exportaciones_productos"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(7), index=True, nullable=False)
    provincia = db.Column(db.String(80), index=True, nullable=False)
    producto = db.Column(db.String(80), index=True, nullable=False)
    valor_fob_usd = db.Column(db.Float, nullable=False)
    participacion_pct = db.Column(db.Float, nullable=True)
    fuente = db.Column(db.String(200), nullable=True)


class ExportacionDestino(db.Model):
    __tablename__ = "exportaciones_destinos"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(7), index=True, nullable=False)
    provincia = db.Column(db.String(80), index=True, nullable=False)
    destino = db.Column(db.String(100), index=True, nullable=False)
    valor_fob_usd = db.Column(db.Float, nullable=False)
    participacion_pct = db.Column(db.Float, nullable=True)
    fuente = db.Column(db.String(200), nullable=True)


class PrecioMineral(db.Model):
    __tablename__ = "precios_minerales"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(7), index=True, nullable=False)
    mineral = db.Column(db.String(80), index=True, nullable=False)
    precio_usd = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(40), nullable=False)
    variacion_interanual_pct = db.Column(db.Float, nullable=True)
    variacion_mensual_pct = db.Column(db.Float, nullable=True)
    fuente = db.Column(db.String(200), nullable=True)


class BalanceComercial(db.Model):
    __tablename__ = "balances_comerciales"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(7), index=True, nullable=False)
    alcance = db.Column(db.String(80), index=True, nullable=False)  # Argentina, Proyectos, San Juan estimado
    exportaciones_usd = db.Column(db.Float, nullable=False)
    importaciones_usd = db.Column(db.Float, nullable=False)
    balance_usd = db.Column(db.Float, nullable=False)
    fuente = db.Column(db.String(200), nullable=True)


class RecursoProvincial(db.Model):
    __tablename__ = "recursos_provinciales"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(7), index=True, nullable=False)
    provincia = db.Column(db.String(80), index=True, nullable=False)
    concepto = db.Column(db.String(100), index=True, nullable=False)
    categoria = db.Column(db.String(80), index=True, nullable=True)
    valor_real = db.Column(db.Float, nullable=False)
    variacion_interanual_pct = db.Column(db.Float, nullable=True)
    fuente = db.Column(db.String(200), nullable=True)


class TransferenciaNacional(db.Model):
    __tablename__ = "transferencias_nacionales"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(7), index=True, nullable=False)
    provincia = db.Column(db.String(80), index=True, nullable=False)
    concepto = db.Column(db.String(100), index=True, nullable=False)
    valor_real = db.Column(db.Float, nullable=False)
    variacion_interanual_pct = db.Column(db.Float, nullable=True)
    fuente = db.Column(db.String(200), nullable=True)


class RecaudacionNacional(db.Model):
    __tablename__ = "recaudacion_nacional"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(7), index=True, nullable=False)
    concepto = db.Column(db.String(100), index=True, nullable=False)
    valor_real = db.Column(db.Float, nullable=False)
    variacion_interanual_pct = db.Column(db.Float, nullable=True)
    fuente = db.Column(db.String(200), nullable=True)