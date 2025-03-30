import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def show_key_metrics(df: pd.DataFrame):
    """
    Muestra las métricas clave de Recursos Humanos en la interfaz de Streamlit.
    
    Métricas:
    - Total Empleados: Se cuentan los registros únicos de "Nombre Completo" (normalizados).
    - Empleados de Planta: Aquellos que en algún registro tienen "Clasificación Contrato" igual a "planta".
    - Empleados Temp/Part-Time: Aquellos que aparecen con "temporada" o "part time" y que nunca tuvieron "planta".
    - Salario Prom.: Se calcula como la suma de 'SueldoBrutoContractual' dividida por el Total Empleados.
    - Gerencias: Cantidad de gerencias únicas (columna "Gerencia").
    """
    st.markdown("## 📊 Métricas Clave")
    
    # Normalizamos la columna "Nombre Completo" para un conteo consistente
    if "Nombre Completo" in df.columns:
        df["nombre_norm"] = df["Nombre Completo"].astype(str).str.strip()
        total_empleados = df["nombre_norm"].dropna().nunique()
    else:
        total_empleados = len(df)
    
    # Clasificación de empleados usando "nombre_norm" y "Clasificación Contrato"
    empleados_planta = 0
    empleados_temp = 0
    if "Clasificación Contrato" in df.columns and "nombre_norm" in df.columns:
        df["contrato_norm"] = df["Clasificación Contrato"].astype(str).str.lower().str.strip()
        # Agrupamos por empleado (nombre normalizado) y obtenemos sus clasificaciones únicas
        clasificaciones = df.groupby("nombre_norm")["contrato_norm"].agg(lambda x: list(x.unique()))
        
        def obtener_clasificacion_final(lista):
            # Si aparece "planta" en cualquiera de los registros, se clasifica como planta.
            if "planta" in lista:
                return "planta"
            # Si no es planta, pero aparece "temporada" o "part time", se clasifica como temporal.
            elif any(val in ["temporada", "part time"] for val in lista):
                return "temporal"
            else:
                return "desconocido"
        
        clasificacion_final = clasificaciones.apply(obtener_clasificacion_final)
        empleados_planta = (clasificacion_final == "planta").sum()
        empleados_temp = (clasificacion_final == "temporal").sum()
    
    # Mostrar las métricas de empleados en tres columnas
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Total Empleados", value=total_empleados)
    with c2:
        st.metric(label="Empleados de Planta", value=empleados_planta)
    with c3:
        st.metric(label="Empleados Temp/Part-Time", value=empleados_temp)
    
    # Segunda fila: Salario Promedio y Gerencias
    c4, c5 = st.columns(2)
    with c4:
        # Calcular Salario Prom. como la suma de 'SueldoBrutoContractual' dividida por total_empleados
        if "SueldoBrutoContractual" in df.columns and pd.api.types.is_numeric_dtype(df["SueldoBrutoContractual"]):
            if total_empleados > 0:
                total_sueldo = df["SueldoBrutoContractual"].sum()
                salario_prom = total_sueldo / total_empleados
                st.metric(label="Salario Prom.", value=f"${salario_prom:,.2f}")
            else:
                st.metric(label="Salario Prom.", value="N/A")
        else:
            st.metric(label="Salario Prom.", value="N/A")
    with c5:
        # Ahora se cuentan las gerencias únicas (columna "Gerencia")
        if "Gerencia" in df.columns:
            gerencias = df["Gerencia"].nunique()
            st.metric(label="Gerencias", value=gerencias)
        else:
            st.metric(label="Gerencias", value="N/A")
def horas_extras_vs_sueldos(df: pd.DataFrame):
    st.header("Análisis: Horas Extras vs. Sueldos")
    required_cols = ["Periodo", "HrsExt_Normales", "HrsExt_Dobles", "HrsExt_215", "SueldoBrutoDiasTrab"]
    if not all(col in df.columns for col in required_cols):
        st.warning(f"Faltan columnas: {set(required_cols) - set(df.columns)}")
        return

    group_data = df.groupby("Periodo").agg({
        "HrsExt_Normales": "sum",
        "HrsExt_Dobles": "sum",
        "HrsExt_215": "sum",
        "SueldoBrutoDiasTrab": "sum"
    }).reset_index()

    st.write("Resumen por Período")
    st.dataframe(group_data)

    fig_bar = px.bar(
        group_data,
        x="Periodo",
        y="HrsExt_Normales",
        title="Horas Extras Normales por Período",
        labels={"HrsExt_Normales": "Horas Extras Normales"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    fig_line = px.line(
        group_data,
        x="Periodo",
        y="SueldoBrutoDiasTrab",
        title="Sueldo Bruto (Días Trabajados) por Período",
        labels={"SueldoBrutoDiasTrab": "Sueldo Bruto"}
    )
    st.plotly_chart(fig_line, use_container_width=True)

def faltas_vs_sueldo(df: pd.DataFrame):
    st.header("Análisis: Faltas vs. Sueldo")
    required_cols = ["Periodo", "DiasFalta", "SueldoBrutoContractual", "SueldoBrutoDiasTrab"]
    if not all(col in df.columns for col in required_cols):
        st.warning(f"Faltan columnas: {set(required_cols) - set(df.columns)}")
        return

    group_data = df.groupby("Periodo").agg({
        "DiasFalta": "sum",
        "SueldoBrutoContractual": "sum",
        "SueldoBrutoDiasTrab": "sum"
    }).reset_index()

    group_data["DescuentoTotal"] = group_data["SueldoBrutoContractual"] - group_data["SueldoBrutoDiasTrab"]
    group_data["DescuentoPromedioPorDiaFalta"] = np.where(
        group_data["DiasFalta"] > 0,
        group_data["DescuentoTotal"] / group_data["DiasFalta"],
        0
    )

    st.write("Resumen por Período")
    st.dataframe(group_data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=group_data["Periodo"],
        y=group_data["SueldoBrutoContractual"],
        mode="lines+markers",
        name="Sueldo Contractual"
    ))
    fig.add_trace(go.Scatter(
        x=group_data["Periodo"],
        y=group_data["SueldoBrutoDiasTrab"],
        mode="lines+markers",
        name="Sueldo Efectivo"
    ))
    fig.update_layout(
        title="Comparación de Sueldo Contractual vs. Sueldo Efectivo",
        xaxis_title="Período",
        yaxis_title="Sueldo"
    )
    st.plotly_chart(fig, use_container_width=True)

def antiguedad(df: pd.DataFrame):
    st.header("Análisis: Antigüedad de Empleados")
    if "AntiguedadMes" not in df.columns:
        st.warning("No se encontró la columna 'AntiguedadMes'.")
        return
    if "Rut" not in df.columns:
        st.warning("No se encontró la columna 'Rut'.")
        return

    bins = [0, 1, 3, 5, 10, 20, 50]
    labels = ["0-1", "1-3", "3-5", "5-10", "10-20", "20+"]
    df["RangoAntiguedad"] = pd.cut(df["AntiguedadMes"], bins=bins, labels=labels, right=False)
    count_antiguedad = df.groupby("RangoAntiguedad")["Rut"].nunique().reset_index(name="NumEmpleados")

    st.write("Distribución de empleados por rango de antigüedad")
    st.dataframe(count_antiguedad)

    fig_pie = px.pie(
        count_antiguedad,
        names="RangoAntiguedad",
        values="NumEmpleados",
        title="Distribución de Antigüedad"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

def dotacion(df: pd.DataFrame):
    st.header("Análisis: Dotación")
    needed_cols = ["Rut", "Periodo", "Gerencia"]
    missing = [col for col in needed_cols if col not in df.columns]
    if missing:
        st.warning(f"Faltan columnas para este análisis de dotación: {missing}")
        return

    dotacion_total = df["Rut"].nunique()
    st.write(f"**Dotación total:** {dotacion_total} empleados únicos.")

    dotacion_por_periodo_depto = (
        df.groupby(["Periodo", "Gerencia"])["Rut"]
        .nunique()
        .reset_index(name="NumEmpleados")
    )

    st.subheader("Distribución de empleados por Período y Departamento")
    st.dataframe(dotacion_por_periodo_depto)

    fig_bar = px.bar(
        dotacion_por_periodo_depto,
        x="Periodo",
        y="NumEmpleados",
        color="Gerencia",
        barmode="group",
        title="Cantidad de Empleados por Año-Mes y Departamento",
        labels={"NumEmpleados": "Número de Empleados"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

def composicion_ausencias(df: pd.DataFrame):
    st.header("Análisis: Composición de Ausencias")
    ausencias_cols = [
        "DiasTrabajados",
        "DiasFalta",
        "DiasLicenciaNormales",
        "DiasLicenciaMaternales",
        "DiasVacaciones"
    ]
    ausencias_cols = [col for col in ausencias_cols if col in df.columns]

    if len(ausencias_cols) > 1 and "Periodo" in df.columns:
        comp_ausencias = df.groupby("Periodo")[ausencias_cols].sum().reset_index()
        st.write("Resumen de Ausencias por Período")
        st.dataframe(comp_ausencias)

        fig_area = go.Figure()
        for col in ausencias_cols:
            fig_area.add_trace(go.Scatter(
                x=comp_ausencias["Periodo"],
                y=comp_ausencias[col],
                mode="lines",
                stackgroup="one",
                name=col
            ))
        fig_area.update_layout(
            title="Composición de Ausencias",
            xaxis_title="Período",
            yaxis_title="Días"
        )
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.warning("No se encontraron las columnas de ausencias requeridas o la columna 'Periodo'.")

def empleados_activos(df: pd.DataFrame):
    st.header("Análisis: Empleados Activos (Corte)")
    if "FechaTerminoContrato" not in df.columns:
        st.warning("La columna 'FechaTerminoContrato' no está presente en el DataFrame.")
        return
    if "Rut" not in df.columns or "Periodo" not in df.columns:
        st.warning("Falta la columna 'Rut' o 'Periodo' para este análisis.")
        return

    df_activos = df[df["FechaTerminoContrato"].isna()]
    activos_por_periodo = (
        df_activos.groupby("Periodo")["Rut"]
        .nunique()
        .reset_index(name="NumEmpleadosActivos")
    )

    st.write("Empleados activos por Período")
    st.dataframe(activos_por_periodo)

    fig_line_activos = px.line(
        activos_por_periodo,
        x="Periodo",
        y="NumEmpleadosActivos",
        title="Empleados Activos a lo largo del tiempo",
        labels={"NumEmpleadosActivos": "Número de Empleados Activos"}
    )
    st.plotly_chart(fig_line_activos, use_container_width=True)

def faltas_por_cargo_y_departamento(df: pd.DataFrame):
    st.header("Porcentaje de Faltas por Cargo y Departamento (Tablas)")
    needed_cols = ["Cargo", "Gerencia", "DiasFalta"]
    missing_cols = [col for col in needed_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Faltan columnas para este análisis: {missing_cols}")
        return

    # Agrupar por Cargo y Gerencia sumando los días de falta
    df_grouped = (
        df.groupby(["Cargo", "Gerencia"])["DiasFalta"]
        .sum()
        .reset_index()
    )

    # Eliminar registros con 0 días de falta
    df_grouped = df_grouped[df_grouped["DiasFalta"] > 0]

    # Calcular el total de faltas por departamento y el porcentaje por cargo
    df_grouped["TotalDepto"] = df_grouped.groupby("Gerencia")["DiasFalta"].transform("sum")
    df_grouped["Porcentaje"] = (df_grouped["DiasFalta"] / df_grouped["TotalDepto"]) * 100

    # Iterar por cada Gerencia y mostrar la tabla correspondiente
    for depto in sorted(df_grouped["Gerencia"].unique()):
        st.subheader(f"Gerencia: {depto}")
        df_depto = df_grouped[df_grouped["Gerencia"] == depto].copy()
        df_depto = df_depto.sort_values("Porcentaje", ascending=False)
        st.table(df_depto[["Cargo", "DiasFalta", "Porcentaje"]].reset_index(drop=True))

def grafico_causales_termino(df: pd.DataFrame):
    st.header("Causales de Término de Contrato por Periodo")
    if "Causal de Término" not in df.columns or "Periodo" not in df.columns:
        st.warning("No se encuentra la columna 'Causal de Término' o 'Periodo' en el DataFrame.")
        return

    # Filtrar registros para excluir "Sin definir"
    df_filtrado = df[df["Causal de Término"].astype(str).str.strip() != "Sin definir"]

    # Agrupar por Periodo y Causal, contando empleados únicos (usando "Rut")
    df_agg = df_filtrado.groupby(["Periodo", "Causal de Término"])["Rut"].nunique().reset_index(name="Cantidad")
    df_agg = df_agg.sort_values("Periodo")

    st.dataframe(df_agg)

    # Gráfico de líneas para visualizar la evolución de cada causal a lo largo del tiempo
    fig = px.line(
        df_agg,
        x="Periodo",
        y="Cantidad",
        color="Causal de Término",
        markers=True,
        title="Causales de Término de Contrato por Periodo (sin 'Sin definir')",
        labels={"Cantidad": "Número de Empleados", "Periodo": "Periodo"}
    )
    st.plotly_chart(fig, use_container_width=True)

def filtrar_empleados_activos_inactivos(df: pd.DataFrame):
    st.header("Empleados Activos vs Inactivos")
    # Verificar que la columna exista
    if "Causal de Término" not in df.columns:
        st.warning("La columna 'Causal de Término' no se encuentra en el DataFrame.")
        return
    # Lista de causales que indican inactividad
    causales_inactivos = [
        "Abandonar el trabajo en forma injustificada",
        "Conclusión del trabajo o servicio que dio origen al contrato",
        "Falta de probidad del trabajador en el desempeño de sus funciones",
        "Incumplimiento grave de las obligaciones que impone el contrato",
        "Muerte del trabajador",
        "Mutuo acuerdo entre las partes",
        "Necesidades de la empresa establecimiento o servicio",
        "No concurrencia del trabajador a sus labores sin causa dos días seguidos",
        "Renuncia del Trabajador",
        "Vencimiento del plazo convenido en el contrato",
        "Vías de hecho ejercidas por el trabajador en contra del empleador"
    ]
    # Asegurarse de que los valores no tengan espacios adicionales
    df["Causal de Término"] = df["Causal de Término"].astype(str).str.strip()

    # Filtrar empleados activos e inactivos
    df_activos = df[df["Causal de Término"] == "Sin definir"]
    df_inactivos = df[df["Causal de Término"].isin(causales_inactivos)]
    
    st.subheader("Empleados Activos")
    st.write(f"Total activos: {df_activos.shape[0]}")
    st.dataframe(df_activos.head(10))
    
    st.subheader("Empleados Inactivos")
    st.write(f"Total inactivos: {df_inactivos.shape[0]}")
    st.dataframe(df_inactivos.head(10))
    
    # Agrupar por Periodo y contar empleados (únicos según Rut)
    activos_por_periodo = df_activos.groupby("Periodo")["Rut"].nunique().reset_index(name="Activos")
    inactivos_por_periodo = df_inactivos.groupby("Periodo")["Rut"].nunique().reset_index(name="Inactivos")
    
    # Combinar ambos DataFrames para tener la comparación
    df_comparacion = activos_por_periodo.merge(inactivos_por_periodo, on="Periodo", how="outer").fillna(0)
    df_comparacion = df_comparacion.sort_values("Periodo")
    
    st.subheader("Comparación de Empleados Activos vs Inactivos en el Tiempo")
    fig_comparacion = px.line(
        df_comparacion,
        x="Periodo",
        y=["Activos", "Inactivos"],
        title="Comparación de Empleados Activos vs Inactivos a lo largo del tiempo",
        labels={"value": "Número de Empleados", "Periodo": "Período"}
    )
    st.plotly_chart(fig_comparacion, use_container_width=True)
