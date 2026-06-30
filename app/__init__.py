import os
from pathlib import Path

import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]

db = SQLAlchemy()


def database_uri():
    uri = os.getenv("DATABASE_URL")
    if uri:
        if uri.startswith("postgres://"):
            return uri.replace("postgres://", "postgresql://", 1)
        return uri
    if os.getenv("VERCEL"):
        return "sqlite:////tmp/mineria_sanjuan.db"
    return "sqlite:///mineria_sanjuan.db"


def read_csv(path):
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return pd.read_csv(path, sep=None, engine="python", encoding=encoding)
        except Exception:
            continue
    return pd.read_csv(path, sep=None, engine="python")


def normalize_percent_columns(df):
    if "participacion_pct" in df.columns:
        values = pd.to_numeric(df["participacion_pct"], errors="coerce")
        if not values.dropna().empty and values.dropna().max() <= 1:
            df["participacion_pct"] = values * 100
    return df


def load_seed_data():
    from .models import (
        BalanceComercial,
        ExportacionDestino,
        ExportacionProducto,
        ExportacionProvincial,
        PrecioMineral,
    )

    datasets = [
        (ExportacionProvincial, ROOT / "data" / "exportaciones_provinciales.csv", ["fecha", "provincia", "exportaciones_mineras_usd"]),
        (ExportacionProducto, ROOT / "data" / "exportaciones_productos.csv", ["fecha", "provincia", "producto", "valor_fob_usd"]),
        (ExportacionDestino, ROOT / "data" / "exportaciones_destinos.csv", ["fecha", "provincia", "destino", "valor_fob_usd"]),
        (PrecioMineral, ROOT / "data" / "precios_minerales.csv", ["fecha", "mineral", "precio_usd", "unidad"]),
        (BalanceComercial, ROOT / "data" / "balances_comerciales.csv", ["fecha", "alcance", "exportaciones_usd", "importaciones_usd", "balance_usd"]),
    ]

    if os.getenv("VERCEL"):
        for model, _, _ in datasets:
            db.session.query(model).delete()
        db.session.commit()

    for model, path, required_columns in datasets:
        if not path.exists() or db.session.query(model.id).first():
            continue
        df = normalize_percent_columns(read_csv(path))
        missing_columns = [column for column in required_columns if column not in df.columns]
        if missing_columns:
            continue
        df = df.dropna(subset=required_columns)
        valid_columns = {column.name for column in model.__table__.columns}
        for record in df.to_dict("records"):
            clean = {
                key: (None if pd.isna(value) else value)
                for key, value in record.items()
                if key in valid_columns and key != "id"
            }
            db.session.add(model(**clean))
        db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-mineria-sanjuan")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        from . import models  # noqa
        db.create_all()
        load_seed_data()

    return app
