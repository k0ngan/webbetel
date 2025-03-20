from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.express as px
import plotly.io as pio
from analisis_hr import load_hr_data, demographic_analysis, contract_analysis, salary_analysis, attendance_analysis
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Asegurarse de que exista la carpeta uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    chart_html = None
    if request.method == 'POST':
        file = request.files.get('datafile')
        analysis_type = request.form.get('analysis')
        year = request.form.get('year')
        month = request.form.get('month')
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = load_hr_data(filepath)
            
            # Filtrado según año y mes, similar a lo realizado en PyQt
            if year or month:
                if year and month:
                    target_period = f"{year}{month}"
                    mask = df['Period'].astype(str).str.strip() == target_period
                elif year:
                    mask = df['Period'].astype(str).str.strip().str.startswith(year)
                else:
                    mask = df['Period'].astype(str).str.strip().str.endswith(month)
                df = df[mask]
                
            if df.empty:
                chart_html = "<p>No hay datos para el período seleccionado</p>"
            else:
                # Seleccionar análisis según el formulario
                if analysis_type == "demografico":
                    fig = demographic_analysis(df)
                elif analysis_type == "contratos":
                    fig = contract_analysis(df)
                elif analysis_type == "salarial":
                    fig = salary_analysis(df)
                elif analysis_type == "asistencia":
                    fig = attendance_analysis(df)
                else:
                    fig = None
                
                if fig:
                    # Convertir figura a HTML
                    chart_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
        else:
            return redirect(url_for('index'))
    return render_template('index.html', chart_html=chart_html)

if __name__ == '__main__':
    app.run(debug=True)
