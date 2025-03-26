def display_analysis(df):
    analysis_options = {
        "📋 Datos Procesados": "Datos Procesados",
        "👥 Análisis Demográfico": "Demográfico",
        "📑 Análisis de Contratos": "Contratos",
        "💰 Análisis Salarial": "Salarial",
        "⏰ Análisis de Asistencia": "Asistencia",
        "📈 Análisis LME": "LME",
        "📉 Análisis de Ausentismo": "Ausentismo"
    }
    st.set_page_config(page_title="RR.HH", page_icon="👥")
    st.sidebar.markdown("### 📈 Tipo de Análisis")
    selected_analysis = st.sidebar.radio("Seleccione qué desea visualizar:", list(analysis_options.keys()))
    analysis_key = analysis_options[selected_analysis]
    st.markdown(f'<h3 class="section-title">{selected_analysis}</h3>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        
        if analysis_key == "Datos Procesados":
            st.write("Datos procesados y normalizados listos para análisis")
            search_term = st.text_input("🔍 Buscar en los datos:", "")
            displayed_df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)] if search_term else df
            page_size = st.selectbox("Registros por página:", [10, 20, 50, 100])
            total_pages = max(1, len(displayed_df) // page_size + (1 if len(displayed_df) % page_size > 0 else 0))
            page = st.slider("Página:", 1, total_pages, 1)
            st.dataframe(displayed_df.iloc[(page - 1)*page_size : page*page_size], height=400)
            st.download_button("📥 Descargar datos filtrados", 
                               data=displayed_df.to_csv(index=False).encode('utf-8'),
                               file_name='datos_rrhh_filtrados.csv',
                               mime='text/csv')
        
        elif analysis_key == "Demográfico":
            st.write("Análisis Demográfico de Empleados")
            fig_default = demographic_analysis(df)
            st.plotly_chart(fig_default, use_container_width=True)
            if st.checkbox("Mapear columnas para análisis Demográfico"):
                req = {
                    "Edad": "Seleccione la columna para la Edad:",
                    "Género": "Seleccione la columna para el Género:",
                    "Nacionalidad": "Seleccione la columna para la Nacionalidad:",
                    "Antigüedad": "Seleccione la columna para la Antigüedad (en años):"
                }
                mapeo = mapping_dinamico_por_dato(df, req)
                if len(mapeo) == len(req):
                    df_demo = df.copy()
                    try:
                        df_demo["AgeGroup"] = pd.cut(pd.to_numeric(df_demo[mapeo["Edad"]], errors="coerce"),
                                                     bins=[18,25,35,45,55,65,100],
                                                     labels=["18-24","25-34","35-44","45-54","55-64","65+"])
                    except Exception as e:
                        st.error("Error en la columna de Edad: " + str(e))
                    df_demo["Gender"] = df_demo[mapeo["Género"]]
                    df_demo["Nationality"] = df_demo[mapeo["Nacionalidad"]]
                    df_demo["TenureYears"] = pd.to_numeric(df_demo[mapeo["Antigüedad"]], errors="coerce")
                    st.plotly_chart(demographic_analysis(df_demo), use_container_width=True)
                else:
                    st.info("Complete el mapeo para el análisis Demográfico.")
        
        elif analysis_key == "Contratos":
            st.write("Análisis de Contratos")
            st.plotly_chart(contract_analysis(df), use_container_width=True)
            if st.checkbox("Mapear columnas para análisis de Contratos"):
                req = {
                    "ContractType": "Seleccione la columna para el Tipo de Contrato:",
                    "Department": "Seleccione la columna para el Departamento:"
                }
                mapeo = mapping_dinamico_por_dato(df, req)
                if len(mapeo) == len(req):
                    df_contrato = df.copy()
                    df_contrato["ContractType"] = df_contrato[mapeo["ContractType"]]
                    df_contrato["Department"] = df_contrato[mapeo["Department"]]
                    st.plotly_chart(contract_analysis(df_contrato), use_container_width=True)
                else:
                    st.info("Complete el mapeo para análisis de Contratos.")
        
        elif analysis_key == "Salarial":
            st.write("Análisis Salarial")
            st.plotly_chart(salary_analysis(df), use_container_width=True)
            if st.checkbox("Mapear columnas para análisis Salarial"):
                req = {
                    "Department": "Seleccione la columna para el Departamento:",
                    "BaseSalary": "Seleccione la columna para el Salario Base:"
                }
                mapeo = mapping_dinamico_por_dato(df, req)
                if len(mapeo) == len(req):
                    df_salarial = df.copy()
                    df_salarial["Department"] = df_salarial[mapeo["Department"]]
                    df_salarial["BaseSalary"] = pd.to_numeric(df_salarial[mapeo["BaseSalary"]], errors="coerce")
                    st.plotly_chart(salary_analysis(df_salarial), use_container_width=True)
                else:
                    st.info("Complete el mapeo para análisis Salarial.")
            # Nueva opción: Convalidación de Licencias
            if st.checkbox("Realizar Convalidación de Licencias", key="convalidar"):
                convalidacion_licencias(df)
        
        elif analysis_key == "Asistencia":
            st.write("Análisis de Asistencia")
            st.plotly_chart(attendance_analysis(df), use_container_width=True)
            if st.checkbox("Mapear columnas para análisis de Asistencia"):
                req = {
                    "DaysWorked": "Seleccione la columna para Días Trabajados:",
                    "AbsenceDays": "Seleccione la columna para Días de Falta:",
                    "VacationDays": "Seleccione la columna para Días de Vacaciones:"
                }
                mapeo = mapping_dinamico_por_dato(df, req)
                if len(mapeo) == len(req):
                    df_asistencia = df.copy()
                    for campo in req.keys():
                        df_asistencia[campo] = pd.to_numeric(df_asistencia[mapeo[campo]], errors="coerce")
                    if "Department" not in df_asistencia.columns:
                        st.error("La columna 'Department' es necesaria para agrupar el análisis de asistencia.")
                    else:
                        st.plotly_chart(attendance_analysis(df_asistencia), use_container_width=True)
                else:
                    st.info("Complete el mapeo para análisis de Asistencia.")
        
        elif analysis_key == "LME":
            st.write("Análisis de Licencias Médicas Electrónicas (LME)")
            # Opciones LME reducidas
            lme_options = ["Total LME", "Grupo Diagnóstico", "Duración Promedio"]
            lme_choice = st.selectbox("Seleccione subanálisis LME:", lme_options)
            
            # Selección del método para mapear 'Tipo de Licencia'
            metodo_tipo = st.radio("Método para mapear 'Tipo de Licencia':", 
                                     options=["Directo desde columna", "Transformar columnas (múltiples)"],
                                     key="metodo_tipo")
            if metodo_tipo == "Transformar columnas (múltiples)":
                # Opción para transformar columnas de diagnóstico sin modificar el Excel original
                transform_diag = st.checkbox("Transformar columnas de diagnóstico (formato ancho a largo)", key="transform_diag")
                if transform_diag:
                    diag_cols = st.multiselect("Seleccione las columnas que contienen diagnósticos", options=list(df.columns))
                    if diag_cols:
                        df_lme = df.copy()
                        id_vars = [col for col in df_lme.columns if col not in diag_cols]
                        # Se transforma: el nombre de la columna se usará como 'Tipo de Licencia' y el valor se asigna a 'Cantidad'
                        df_lme = pd.melt(df_lme, id_vars=id_vars, value_vars=diag_cols,
                                         var_name="Tipo de Licencia", value_name="Cantidad")
                        if st.checkbox("Mapear columnas para análisis LME (Transformación)", key="mapeo_lme_transf"):
                            requeridos_lme = {
                                "Grupo Diagnóstico": "Seleccione la columna para el Grupo Diagnóstico:",
                                "DiasAutorizados": "Seleccione la columna para los Días Autorizados:",
                                "Año": "Seleccione la columna para el Año de Emisión:"
                            }
                            mapping_lme = mapping_dinamico_por_dato(df_lme, requeridos_lme)
                            if len(mapping_lme) == len(requeridos_lme):
                                for campo in ["DiasAutorizados"]:
                                    df_lme[campo] = pd.to_numeric(df_lme[mapping_lme[campo]], errors="coerce")
                                for campo in ["Grupo Diagnóstico", "Año"]:
                                    df_lme[campo] = df_lme[mapping_lme[campo]]
                                if lme_choice == "Total LME":
                                    pivot, fig = analyze_total_LME(df_lme)
                                    st.dataframe(pivot)
                                    st.plotly_chart(fig, use_container_width=True)
                                elif lme_choice == "Grupo Diagnóstico":
                                    pivot, fig = analyze_grupo_diagnostico_LME(df_lme)
                                    st.dataframe(pivot)
                                    st.plotly_chart(fig, use_container_width=True)
                                elif lme_choice == "Duración Promedio":
                                    duracion, fig = analyze_duracion_LME(df_lme)
                                    st.dataframe(duracion)
                                    st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Seleccione todas las columnas requeridas para el análisis de LME.")
                    else:
                        st.info("Seleccione al menos una columna para transformación de diagnóstico.")
                else:
                    st.info("Active la opción de transformación para mapear 'Tipo de Licencia' desde columnas.")
            else:
                # Método directo: mapear 'Tipo de Licencia' desde una columna existente
                if st.checkbox("Mapear columnas para análisis LME", key="mapeo_lme_directo"):
                    requeridos_lme = {
                        "Tipo de Licencia": "Seleccione la columna para el Tipo de Licencia:",
                        "Cantidad": "Seleccione la columna para la Cantidad:",
                        "Grupo Diagnóstico": "Seleccione la columna para el Grupo Diagnóstico:",
                        "DiasAutorizados": "Seleccione la columna para los Días Autorizados:",
                        "Año": "Seleccione la columna para el Año de Emisión:"
                    }
                    mapping_lme = mapping_dinamico_por_dato(df, requeridos_lme)
                    if len(mapping_lme) == len(requeridos_lme):
                        df_lme = df.copy()
                        for campo in ["Cantidad", "DiasAutorizados"]:
                            df_lme[campo] = pd.to_numeric(df_lme[mapping_lme[campo]], errors="coerce")
                        for campo in ["Tipo de Licencia", "Grupo Diagnóstico", "Año"]:
                            df_lme[campo] = df_lme[mapping_lme[campo]]
                        if lme_choice == "Total LME":
                            pivot, fig = analyze_total_LME(df_lme)
                            st.dataframe(pivot)
                            st.plotly_chart(fig, use_container_width=True)
                        elif lme_choice == "Grupo Diagnóstico":
                            pivot, fig = analyze_grupo_diagnostico_LME(df_lme)
                            st.dataframe(pivot)
                            st.plotly_chart(fig, use_container_width=True)
                        elif lme_choice == "Duración Promedio":
                            duracion, fig = analyze_duracion_LME(df_lme)
                            st.dataframe(duracion)
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Seleccione todas las columnas requeridas para el análisis de LME.")
                else:
                    # Si no se realiza el mapeo, se utilizan datos por defecto
                    if lme_choice == "Total LME":
                        pivot, fig = analyze_total_LME(df)
                        st.dataframe(pivot)
                        st.plotly_chart(fig, use_container_width=True)
                    elif lme_choice == "Grupo Diagnóstico":
                        pivot, fig = analyze_grupo_diagnostico_LME(df)
                        st.dataframe(pivot)
                        st.plotly_chart(fig, use_container_width=True)
                    elif lme_choice == "Duración Promedio":
                        duracion, fig = analyze_duracion_LME(df)
                        st.dataframe(duracion)
                        st.plotly_chart(fig, use_container_width=True)
        
        elif analysis_key == "Ausentismo":
            st.write("Análisis de Ausentismo")
            if st.checkbox("Mapear columnas para análisis de Ausentismo"):
                req = {
                    "Fecha": "Seleccione la columna para la Fecha de Ausentismo (opcional):",
                    "AbsenceDays": "Seleccione la columna para los Días de Ausentismo:"
                }
                mapeo = mapping_dinamico_por_dato(df, req)
                if len(mapeo) == len(req):
                    df_abs = df.copy()
                    if mapeo.get("Fecha") and mapeo["Fecha"] != "-- Seleccione --":
                        df_abs['Período'] = pd.to_datetime(df_abs[mapeo["Fecha"]], errors="coerce").dt.strftime("%Y%m")
                    elif 'Período' not in df_abs.columns and 'ContractStartDate' in df_abs.columns:
                        df_abs['Período'] = df_abs['ContractStartDate'].dt.strftime("%Y%m")
                    if mapeo["AbsenceDays"] != "AbsenceDays":
                        df_abs = df_abs.rename(columns={mapeo["AbsenceDays"]: "AbsenceDays"})

                    agg_df, figs, texto_resumen = absenteeism_analysis(df_abs)
                    if agg_df is not None:
                        st.markdown(texto_resumen)
                        st.dataframe(agg_df)
                        st.plotly_chart(figs[0], use_container_width=True)
                        st.plotly_chart(figs[1], use_container_width=True)
                        pie_option = st.selectbox("Seleccione el gráfico de pastel a mostrar:", ["Absoluta", "Porcentual"], key="pie_sel")
                        st.plotly_chart(figs[2][pie_option], use_container_width=True)
                        
                        st.markdown("### Comparativa de Períodos de Ausentismo")
                        available_periods = agg_df['Período'].tolist()
                        col1, col2 = st.columns(2)
                        with col1:
                            period1 = st.selectbox("Seleccione el primer período (YYYYMM):", available_periods, key="comp1")
                        with col2:
                            period2 = st.selectbox("Seleccione el segundo período (YYYYMM):", available_periods, key="comp2")
                        if st.button("Generar Comparativa"):
                            try:
                                comp_df, comp_fig, comp_text = absenteeism_comparison(agg_df, period1, period2)
                                st.dataframe(comp_df)
                                st.plotly_chart(comp_fig, use_container_width=True)
                                st.markdown(comp_text)
                            except Exception as e:
                                st.error(f"Error generando comparativa: {e}")
                    else:
                        st.error("No se encontraron columnas de ausentismo.")
                else:
                    st.info("Complete el mapeo para el análisis de ausentismo.")
            else:
                agg_df, figs, texto_resumen = absenteeism_analysis(df)
                if agg_df is not None:
                    st.markdown(texto_resumen)
                    st.dataframe(agg_df)
                    st.plotly_chart(figs[0], use_container_width=True)
                    st.plotly_chart(figs[1], use_container_width=True)
                    pie_option = st.selectbox("Seleccione el gráfico de pastel a mostrar:", ["Absoluta", "Porcentual"], key="pie_sel_std")
                    st.plotly_chart(figs[2][pie_option], use_container_width=True)
                    
                    st.markdown("### Comparativa de Períodos de Ausentismo")
                    available_periods = agg_df['Período'].tolist()
                    col1, col2 = st.columns(2)
                    with col1:
                        period1 = st.selectbox("Seleccione el primer período (YYYYMM):", available_periods, key="comp1_std")
                    with col2:
                        period2 = st.selectbox("Seleccione el segundo período (YYYYMM):", available_periods, key="comp2_std")
                    if st.button("Generar Comparativa", key="comp_btn_std"):
                        try:
                            comp_df, comp_fig, comp_text = absenteeism_comparison(agg_df, period1, period2)
                            st.dataframe(comp_df)
                            st.plotly_chart(comp_fig, use_container_width=True)
                            st.markdown(comp_text)
                        except Exception as e:
                            st.error(f"Error generando comparativa: {e}")
                else:
                    st.error("No se encontraron columnas de ausentismo con los nombres estándar.")

        st.markdown('</div>', unsafe_allow_html=True)
        
        if analysis_key != "Datos Procesados":
            st.markdown('<h4 class="section-title">🔍 Insights Clave</h4>', unsafe_allow_html=True)
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            if analysis_key == "Demográfico":
                st.markdown("""
                - Distribución por género: Evalúe el balance en la organización.
                - Distribución por edad: Observe cómo se agrupa la plantilla.
                - Diversidad cultural: Analice la procedencia de los empleados.
                """)
            elif analysis_key == "Contratos":
                st.markdown("""
                - Tipos de contrato predominantes: Compare la distribución.
                - Departamentos: Relacione el tipo de contrato con el área.
                """)
            elif analysis_key == "Salarial":
                st.markdown("""
                - Comparación salarial: Revise diferencias entre departamentos.
                - Identificación de brechas: Detecte posibles inequidades.
                - **Convalidación de Licencias:** Calcule cuánto se pagará por licencia médica acumulada, aplicando un mínimo de días a pagar.
                """)
            elif analysis_key == "Asistencia":
                st.markdown("""
                - Patrones de asistencia: Identifique áreas con mayor ausentismo.
                - Correlaciones: Analice la relación entre asistencia y otros factores.
                """)
            elif analysis_key == "LME":
                st.markdown("""
                - Evolución de LME: Compare la cantidad total de licencias emitidas por año.
                - Grupo Diagnóstico: Identifique cuáles diagnósticos son más frecuentes.
                - Duración Promedio: Analice la duración promedio de las licencias por grupo diagnóstico.
                """)
            elif analysis_key == "Ausentismo":
                st.markdown("""
                - Evolución mensual: Observe cómo cambian los días de ausentismo a lo largo del tiempo.
                - Tipos de ausencia: Revise qué tipo de ausencia representa mayor porcentaje.
                - Comparativa: Compare datos entre dos períodos y detecte diferencias estadísticas.
                """)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
