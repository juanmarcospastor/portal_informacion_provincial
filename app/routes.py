from functools import wraps
import json
import os
import secrets

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from plotly.utils import PlotlyJSONEncoder

from .models import (
    BalanceComercial,
    ExportacionDestino,
    ExportacionProducto,
    ExportacionProvincial,
    PrecioMineral,
    RecaudacionNacional,
    RecursoProvincial,
    TransferenciaNacional,
)

bp = Blueprint("main", __name__)


def configured_credentials():
    return (
        os.getenv("DASHBOARD_USER", "admin"),
        os.getenv("DASHBOARD_PASSWORD", "mineria2026"),
    )


def is_authenticated():
    return bool(session.get("authenticated"))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if is_authenticated():
            return view(*args, **kwargs)
        if request.path.startswith("/api/"):
            return jsonify({"error": "No autorizado"}), 401
        return redirect(url_for("main.login", next=request.full_path))
    return wrapped


def empty_fig(title, message="Sin datos para este mes"):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[dict(
            text=message,
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=18, color="#64748b"),
        )],
    )
    return fig


def fig_json(fig, height=410):
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=55, b=35),
        height=height,
        legend_title_text="",
        font=dict(family="Inter, Arial, sans-serif"),
    )
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def price_fig(df_prec, mineral, color):
    df = df_prec[df_prec["mineral"] == mineral].sort_values("fecha")
    title = f"{mineral}"
    if df.empty:
        return empty_fig(title, "Sin datos disponibles")

    unit = df["unidad"].dropna().iloc[-1] if not df["unidad"].dropna().empty else "USD"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["fecha"],
        y=df["precio_usd"],
        mode="lines+markers",
        name=mineral,
        line=dict(color=color, width=2.6),
        marker=dict(size=6, color=color),
        customdata=df[["unidad"]],
        hovertemplate="%{x}<br>Precio: USD %{y:,.1f}<br>Unidad: %{customdata[0]}<extra></extra>",
    ))
    fig.update_layout(title=title, showlegend=False, hovermode="x unified")
    fig.update_yaxes(title=unit, rangemode="tozero", tickformat=",.0f")
    fig.update_xaxes(title="")
    return fig


def money_millions(value):
    if value is None:
        return "s/d"
    return f"USD {value/1_000_000:,.0f} M".replace(",", ".")


def pct(value):
    if value is None:
        return "s/d"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}%".replace(".", ",")


def ratio_pct(value):
    if value is None:
        return "s/d"
    return pct(value * 100)


def share_pct(value):
    if value is None:
        return "s/d"
    return f"{value:.1f}%".replace(".", ",")


def describe_change(value):
    if value is None:
        return "sin dato de variación interanual"
    if value > 0.05:
        return f"con un crecimiento interanual de {ratio_pct(value)}"
    if value < -0.05:
        return f"con una caída interanual de {ratio_pct(value).replace('-', '')}"
    return f"con una variación interanual prácticamente estable de {ratio_pct(value)}"


def generar_lectura(provincia, fecha, actual, total_arg, top_producto, top_destino, part_mineria, part_nacional):
    if not actual:
        return [
            f"No hay datos de exportaciones mineras para {provincia} en {fecha}.",
            "Completando exportaciones_provinciales.csv para ese mes se habilitan los KPIs y la lectura económica automática.",
        ]

    ranking = ExportacionProvincial.query.filter(
        ExportacionProvincial.fecha == fecha,
        ExportacionProvincial.provincia != "Argentina",
    ).order_by(ExportacionProvincial.exportaciones_mineras_usd.desc()).all()
    posicion = next((i + 1 for i, row in enumerate(ranking) if row.provincia == provincia), None)
    lider = ranking[0] if ranking else None

    lectura = [
        f"En {fecha}, {provincia} registró exportaciones mineras por {money_millions(actual.exportaciones_mineras_usd)}, {describe_change(actual.variacion_interanual_pct)}.",
    ]

    contexto = []
    if part_mineria is not None:
        contexto.append(f"la minería explicó {share_pct(part_mineria)} de las exportaciones provinciales")
    if part_nacional is not None and total_arg:
        contexto.append(f"representó {share_pct(part_nacional)} de las exportaciones mineras nacionales")
    elif not total_arg:
        contexto.append("no se puede calcular la participación nacional porque falta la fila Argentina para el mes")
    if posicion and ranking:
        contexto.append(f"ocupó el puesto {posicion} entre {len(ranking)} provincias cargadas")
    if contexto:
        lectura.append("En términos relativos, " + "; ".join(contexto) + ".")

    if lider and lider.provincia != provincia:
        diferencia = lider.exportaciones_mineras_usd - actual.exportaciones_mineras_usd
        lectura.append(f"La provincia líder del mes fue {lider.provincia}, con {money_millions(lider.exportaciones_mineras_usd)}, una diferencia de {money_millions(diferencia)} frente a {provincia}.")
    elif lider and lider.provincia == provincia and len(ranking) > 1:
        lectura.append(f"{provincia} lideró la comparación provincial del mes entre las provincias cargadas en la base.")

    composicion = []
    if top_producto:
        composicion.append(f"el principal producto fue {top_producto.producto}, con {share_pct(top_producto.participacion_pct)} de participación")
    else:
        composicion.append("todavía falta cargar la composición por producto para este mes")
    if top_destino:
        composicion.append(f"el principal destino fue {top_destino.destino}, con {share_pct(top_destino.participacion_pct)} de participación")
    else:
        composicion.append("todavía falta cargar la apertura por destino")
    lectura.append("En la apertura comercial, " + "; ".join(composicion) + ".")

    return lectura



def pesos_reales_millions(value):
    if value is None:
        return "s/d"
    return f"$ {value/1_000_000:,.0f} M".replace(",", ".")


def pct_direct(value):
    if value is None:
        return "s/d"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}%".replace(".", ",")


def recursos_filters():
    provincias = [p[0] for p in RecursoProvincial.query.with_entities(RecursoProvincial.provincia).distinct().order_by(RecursoProvincial.provincia).all()]
    fechas = set()
    fechas.update(f[0] for f in RecursoProvincial.query.with_entities(RecursoProvincial.fecha).distinct().all())
    fechas.update(f[0] for f in TransferenciaNacional.query.with_entities(TransferenciaNacional.fecha).distinct().all())
    fechas.update(f[0] for f in RecaudacionNacional.query.with_entities(RecaudacionNacional.fecha).distinct().all())
    return provincias or ["San Juan"], sorted(fechas, reverse=True)


def recursos_lectura(provincia, fecha, total, transferencia, nacional, top_impuesto):
    if not total:
        return [
            f"No hay datos de recursos provinciales para {provincia} en {fecha}.",
            "Completando recursos_provinciales.csv se habilitan los indicadores, gráficos y lectura automática.",
        ]

    lectura = [
        f"En {fecha}, {provincia} registró recursos provinciales por {pesos_reales_millions(total.valor_real)} en términos reales, con una variación interanual de {pct_direct(total.variacion_interanual_pct)}.",
    ]
    if top_impuesto:
        lectura.append(f"El principal componente tributario fue {top_impuesto.concepto}, con {pesos_reales_millions(top_impuesto.valor_real)}.")
    if transferencia:
        lectura.append(f"Los envíos nacionales por {transferencia.concepto} sumaron {pesos_reales_millions(transferencia.valor_real)}, con una variación interanual de {pct_direct(transferencia.variacion_interanual_pct)}.")
    if nacional:
        lectura.append(f"La recaudación nacional total alcanzó {pesos_reales_millions(nacional.valor_real)} en términos reales, con una variación interanual de {pct_direct(nacional.variacion_interanual_pct)}.")
    return lectura


def evolution_with_variation_fig(df, title, value_label):
    if df.empty:
        return empty_fig(title)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["fecha"],
        y=df["variacion_interanual_pct"],
        name="Variación interanual",
        marker_color="#cbd5e1",
        opacity=0.35,
        yaxis="y2",
        hovertemplate="%{x}<br>Variación interanual: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["fecha"],
        y=df["valor_real"],
        mode="lines+markers",
        name=value_label,
        line=dict(color="#25315d", width=3),
        marker=dict(size=7),
        hovertemplate="%{x}<br>Valor real: $ %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        hovermode="x unified",
        yaxis=dict(title="Pesos reales"),
        yaxis2=dict(title="Variación interanual (%)", overlaying="y", side="right", ticksuffix="%", showgrid=False, zeroline=True),
    )
    fig.update_xaxes(title="")
    return fig
def get_filters():
    provincias = [p[0] for p in ExportacionProvincial.query.with_entities(ExportacionProvincial.provincia).distinct().order_by(ExportacionProvincial.provincia).all()]
    fechas = [f[0] for f in ExportacionProvincial.query.with_entities(ExportacionProvincial.fecha).distinct().order_by(ExportacionProvincial.fecha.desc()).all()]
    return provincias, fechas


@bp.route("/")
def index():
    if is_authenticated():
        return redirect(url_for("main.portal"))
    return redirect(url_for("main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if is_authenticated():
        return redirect(url_for("main.portal"))

    error = None
    if request.method == "POST":
        expected_user, expected_password = configured_credentials()
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        valid_user = secrets.compare_digest(username, expected_user)
        valid_password = secrets.compare_digest(password, expected_password)
        if valid_user and valid_password:
            session["authenticated"] = True
            session["user"] = username
            next_url = request.args.get("next") or url_for("main.portal")
            return redirect(next_url)
        error = "Usuario o contraseña incorrectos."

    return render_template("login.html", error=error)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/portal")
@login_required
def portal():
    modules = [
        {
            "title": "Minería",
            "description": "Exportaciones mineras, productos, destinos y precios internacionales relevantes.",
            "href": url_for("main.dashboard"),
            "status": "Disponible",
        },
        {
            "title": "Recursos provinciales",
            "description": "Recaudación provincial, coparticipación y recaudación nacional en términos reales.",
            "href": url_for("main.recursos_provinciales"),
            "status": "Disponible",
        },
    ]
    return render_template("portal.html", modules=modules)


@bp.route("/recursos-provinciales")
@login_required
def recursos_provinciales():
    provincias, fechas = recursos_filters()
    provincia = request.args.get("provincia", "San Juan")
    fecha = request.args.get("fecha", fechas[0] if fechas else "2026-05")

    total = RecursoProvincial.query.filter_by(provincia=provincia, fecha=fecha, concepto="Total").first()
    impuestos = RecursoProvincial.query.filter(
        RecursoProvincial.provincia == provincia,
        RecursoProvincial.fecha == fecha,
        RecursoProvincial.concepto != "Total",
    ).order_by(RecursoProvincial.valor_real.desc()).all()
    top_impuesto = impuestos[0] if impuestos else None
    transferencia = TransferenciaNacional.query.filter_by(provincia=provincia, fecha=fecha).order_by(TransferenciaNacional.valor_real.desc()).first()
    nacional = RecaudacionNacional.query.filter_by(fecha=fecha, concepto="Total").first()
    iva = RecaudacionNacional.query.filter_by(fecha=fecha, concepto="IVA").first()
    ganancias = RecaudacionNacional.query.filter_by(fecha=fecha, concepto="Ganancias").first()

    kpis = {
        "total": pesos_reales_millions(total.valor_real if total else None),
        "var_total": pct_direct(total.variacion_interanual_pct if total else None),
        "principal": f"{top_impuesto.concepto} ({pesos_reales_millions(top_impuesto.valor_real)})" if top_impuesto else "s/d",
        "coparticipacion": pesos_reales_millions(transferencia.valor_real if transferencia else None),
        "nacional": pesos_reales_millions(nacional.valor_real if nacional else None),
        "iva_ganancias": pesos_reales_millions((iva.valor_real if iva else 0) + (ganancias.valor_real if ganancias else 0)) if iva or ganancias else "s/d",
    }
    lectura = recursos_lectura(provincia, fecha, total, transferencia, nacional, top_impuesto)

    return render_template(
        "recursos_provinciales.html",
        provincias=provincias,
        fechas=fechas,
        provincia=provincia,
        fecha=fecha,
        kpis=kpis,
        lectura=lectura,
    )


@bp.route("/mineria")
@login_required
def dashboard():
    provincias, fechas = get_filters()
    provincia = request.args.get("provincia", "San Juan")
    fecha = request.args.get("fecha", fechas[0] if fechas else "2026-04")

    actual = ExportacionProvincial.query.filter_by(provincia=provincia, fecha=fecha).first()
    total_arg = ExportacionProvincial.query.filter_by(provincia="Argentina", fecha=fecha).first()

    total_prov = actual.exportaciones_totales_usd if actual and actual.exportaciones_totales_usd else None
    part_mineria = (actual.exportaciones_mineras_usd / total_prov * 100) if actual and total_prov else None
    part_nacional = (actual.exportaciones_mineras_usd / total_arg.exportaciones_mineras_usd * 100) if actual and total_arg and total_arg.exportaciones_mineras_usd else None

    top_producto = ExportacionProducto.query.filter_by(provincia=provincia, fecha=fecha).order_by(ExportacionProducto.valor_fob_usd.desc()).first()
    top_destino = ExportacionDestino.query.filter_by(provincia=provincia, fecha=fecha).order_by(ExportacionDestino.valor_fob_usd.desc()).first()

    kpis = {
        "exportaciones": money_millions(actual.exportaciones_mineras_usd if actual else None),
        "var_ia": ratio_pct(actual.variacion_interanual_pct if actual else None),
        "part_mineria": share_pct(part_mineria),
        "part_nacional": share_pct(part_nacional),
        "producto": f"{top_producto.producto} ({share_pct(top_producto.participacion_pct)})" if top_producto else "s/d",
        "destino": f"{top_destino.destino} ({share_pct(top_destino.participacion_pct)})" if top_destino else "s/d",
    }

    lectura = generar_lectura(provincia, fecha, actual, total_arg, top_producto, top_destino, part_mineria, part_nacional)

    return render_template("dashboard.html", provincias=provincias, fechas=fechas, provincia=provincia, fecha=fecha, kpis=kpis, lectura=lectura)


@bp.route("/api/charts")
@login_required
def charts():
    provincia = request.args.get("provincia", "San Juan")
    fecha = request.args.get("fecha", "2026-04")

    rows = ExportacionProvincial.query.filter(ExportacionProvincial.provincia == provincia).order_by(ExportacionProvincial.fecha).all()
    df_exp = pd.DataFrame([{
        "fecha": r.fecha,
        "exportaciones_mineras_usd": r.exportaciones_mineras_usd,
        "variacion_interanual_pct": r.variacion_interanual_pct,
    } for r in rows], columns=["fecha", "exportaciones_mineras_usd", "variacion_interanual_pct"])
    if df_exp.empty:
        fig_exp = empty_fig(f"Exportaciones mineras de {provincia}")
    else:
        df_exp["variacion_interanual_pct_plot"] = df_exp["variacion_interanual_pct"] * 100
        fig_exp = go.Figure()
        fig_exp.add_trace(go.Bar(
            x=df_exp["fecha"],
            y=df_exp["variacion_interanual_pct_plot"],
            name="Variación interanual",
            marker_color="#cbd5e1",
            opacity=0.35,
            yaxis="y2",
            hovertemplate="%{x}<br>Variación interanual: %{y:.1f}%<extra></extra>",
        ))
        fig_exp.add_trace(go.Scatter(
            x=df_exp["fecha"],
            y=df_exp["exportaciones_mineras_usd"],
            mode="lines+markers",
            name="Exportaciones mineras",
            line=dict(color="#0f766e", width=3),
            marker=dict(size=7),
            hovertemplate="%{x}<br>Exportaciones: USD %{y:,.0f}<extra></extra>",
        ))
        fig_exp.update_layout(
            title=f"Exportaciones mineras de {provincia}",
            barmode="relative",
            yaxis=dict(title="USD FOB"),
            yaxis2=dict(title="Variación interanual (%)", overlaying="y", side="right", ticksuffix="%", showgrid=False, zeroline=True),
        )
        fig_exp.update_xaxes(title="")

    rows = ExportacionProvincial.query.filter(ExportacionProvincial.fecha == fecha, ExportacionProvincial.provincia != "Argentina").all()
    df_prov = pd.DataFrame([{"provincia": r.provincia, "valor": r.exportaciones_mineras_usd} for r in rows], columns=["provincia", "valor"])
    if df_prov.empty:
        fig_prov = empty_fig(f"Comparación provincial - {fecha}")
    else:
        fig_prov = px.bar(df_prov.sort_values("valor", ascending=False), x="provincia", y="valor", title=f"Comparación provincial - {fecha}")
        fig_prov.update_yaxes(title="USD FOB")
        fig_prov.update_xaxes(title="")

    rows = ExportacionProducto.query.filter_by(provincia=provincia, fecha=fecha).all()
    df_prod = pd.DataFrame([{"producto": r.producto, "valor": r.valor_fob_usd, "participacion": r.participacion_pct} for r in rows], columns=["producto", "valor", "participacion"])
    if df_prod.empty:
        fig_prod = empty_fig(f"Composición por producto - {provincia} {fecha}")
    else:
        fig_prod = px.pie(df_prod, names="producto", values="valor", title=f"Composición por producto - {provincia} {fecha}", hole=0.45)

    rows = ExportacionDestino.query.filter_by(provincia=provincia, fecha=fecha).all()
    df_dest = pd.DataFrame([{"destino": r.destino, "valor": r.valor_fob_usd, "participacion": r.participacion_pct} for r in rows], columns=["destino", "valor", "participacion"])
    if df_dest.empty:
        fig_dest = empty_fig(f"Destinos de exportación - {provincia} {fecha}")
    else:
        fig_dest = px.bar(df_dest.sort_values("valor", ascending=True), x="valor", y="destino", orientation="h", title=f"Destinos de exportación - {provincia} {fecha}")
        fig_dest.update_xaxes(title="USD FOB")
        fig_dest.update_yaxes(title="")

    rows = PrecioMineral.query.order_by(PrecioMineral.fecha).all()
    df_prec = pd.DataFrame([{"fecha": r.fecha, "mineral": r.mineral, "precio_usd": r.precio_usd, "unidad": r.unidad} for r in rows], columns=["fecha", "mineral", "precio_usd", "unidad"])
    fig_prec_oro = price_fig(df_prec, "Oro", "#b7791f")
    fig_prec_plata = price_fig(df_prec, "Plata", "#64748b")
    fig_prec_cobre = price_fig(df_prec, "Cobre", "#b45309")
    fig_prec_litio = price_fig(df_prec, "Carbonato de litio", "#0f766e")

    rows = BalanceComercial.query.order_by(BalanceComercial.fecha).all()
    df_bal = pd.DataFrame([{"fecha": r.fecha, "alcance": r.alcance, "balance_usd": r.balance_usd} for r in rows], columns=["fecha", "alcance", "balance_usd"])
    if df_bal.empty:
        fig_bal = empty_fig("Balance comercial minero", "Sin datos disponibles")
    else:
        fig_bal = px.line(df_bal, x="fecha", y="balance_usd", color="alcance", markers=True, title="Balance comercial minero")
        fig_bal.update_yaxes(title="USD")
        fig_bal.update_xaxes(title="")

    return jsonify({
        "exportaciones": fig_json(fig_exp),
        "provincias": fig_json(fig_prov),
        "productos": fig_json(fig_prod),
        "destinos": fig_json(fig_dest),
        "precio_oro": fig_json(fig_prec_oro, height=300),
        "precio_plata": fig_json(fig_prec_plata, height=300),
        "precio_cobre": fig_json(fig_prec_cobre, height=300),
        "precio_litio": fig_json(fig_prec_litio, height=300),
        "balance": fig_json(fig_bal),
    })



@bp.route("/api/recursos-charts")
@login_required
def recursos_charts():
    provincia = request.args.get("provincia", "San Juan")
    fecha = request.args.get("fecha", "2026-05")

    rows = RecursoProvincial.query.filter_by(provincia=provincia, concepto="Total").order_by(RecursoProvincial.fecha).all()
    df_total = pd.DataFrame([{"fecha": r.fecha, "valor_real": r.valor_real, "variacion_interanual_pct": r.variacion_interanual_pct} for r in rows], columns=["fecha", "valor_real", "variacion_interanual_pct"])
    fig_total = evolution_with_variation_fig(df_total, f"Recursos provinciales de {provincia}", "Recursos provinciales")

    rows = RecursoProvincial.query.filter(
        RecursoProvincial.provincia == provincia,
        RecursoProvincial.fecha == fecha,
        RecursoProvincial.concepto != "Total",
    ).all()
    df_imp = pd.DataFrame([{"concepto": r.concepto, "valor_real": r.valor_real} for r in rows], columns=["concepto", "valor_real"])
    if df_imp.empty:
        fig_imp = empty_fig(f"Composición de recursos - {provincia} {fecha}")
    else:
        fig_imp = px.bar(df_imp.sort_values("valor_real", ascending=True), x="valor_real", y="concepto", orientation="h", title=f"Composición de recursos - {provincia} {fecha}")
        fig_imp.update_xaxes(title="Pesos reales")
        fig_imp.update_yaxes(title="")

    rows = TransferenciaNacional.query.filter_by(provincia=provincia).order_by(TransferenciaNacional.fecha).all()
    df_trans = pd.DataFrame([{"fecha": r.fecha, "valor_real": r.valor_real, "variacion_interanual_pct": r.variacion_interanual_pct} for r in rows], columns=["fecha", "valor_real", "variacion_interanual_pct"])
    fig_trans = evolution_with_variation_fig(df_trans, f"Coparticipación y envíos nacionales a {provincia}", "Transferencias nacionales")

    rows = RecaudacionNacional.query.order_by(RecaudacionNacional.fecha).all()
    df_nac = pd.DataFrame([{"fecha": r.fecha, "concepto": r.concepto, "valor_real": r.valor_real, "variacion_interanual_pct": r.variacion_interanual_pct} for r in rows], columns=["fecha", "concepto", "valor_real", "variacion_interanual_pct"])
    if df_nac.empty:
        fig_nac = empty_fig("Recaudación nacional")
        fig_var = empty_fig("Variaciones interanuales")
    else:
        conceptos = ["Total", "IVA", "Ganancias"]
        df_nac_main = df_nac[df_nac["concepto"].isin(conceptos)]
        fig_nac = px.line(df_nac_main, x="fecha", y="valor_real", color="concepto", markers=True, title="Recaudación nacional en términos reales")
        fig_nac.update_yaxes(title="Pesos reales")
        fig_nac.update_xaxes(title="")

        df_var = df_nac_main[df_nac_main["fecha"] == fecha]
        fig_var = px.bar(df_var, x="concepto", y="variacion_interanual_pct", title=f"Variaciones interanuales - {fecha}")
        fig_var.update_yaxes(title="Variación interanual (%)", ticksuffix="%", zeroline=True)
        fig_var.update_xaxes(title="")

    return jsonify({
        "recursos_total": fig_json(fig_total),
        "recursos_composicion": fig_json(fig_imp),
        "transferencias": fig_json(fig_trans),
        "recaudacion_nacional": fig_json(fig_nac),
        "variaciones": fig_json(fig_var),
    })

@bp.route("/datos")
@login_required
def datos():
    provincia = request.args.get("provincia", "San Juan")
    rows = ExportacionProvincial.query.filter_by(provincia=provincia).order_by(ExportacionProvincial.fecha.desc()).all()
    return render_template("datos.html", provincia=provincia, rows=rows)