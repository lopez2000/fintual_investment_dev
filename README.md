# Servicio de Optimización de Portafolio

Este servicio implementa Modern Portfolio Theory (MPT) para optimizar portafolios de inversión utilizando la optimización de media-varianza de Markowitz para maximizar el ratio de Sharpe.

## Tabla de Contenidos
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Método de Optimización](#método-de-optimizacion)
- [Supuestos Clave](#supuestos-clave)
- [Uso de la API](#uso-de-la-api)
- [Ejecución del Servicio](#ejecución-del-servicio)
- [Ejecución de Pruebas](#ejecución-de-pruebas)
- [Mejores Prácticas](#mejores-prácticas)
- [Dependencias](#dependencias)

## Estructura del Proyecto

```
fintual_investment_dev/
├── app/
│   ├── __init__.py
│   ├── main.py           # Endpoint FastAPI
│   ├── optimizer.py      # Lógica de optimización de portafolio
│   ├── schemas.py        # Modelos Pydantic para solicitudes/respuestas
│   └── utils.py          # (Opcional) Funciones auxiliares
├── tests/
│   └── test_optimizer.py # Pruebas unitarias
├── requirements.txt
├── README.md
└── returns.csv           # Datos de ejemplo
```

## Método de Optimización

El servicio implementa una estrategia basada en la Modern Portfolio Theory (MPT) con las siguientes características:

### 1. Maximización del Ratio de Sharpe
- El optimizador maximiza el ratio de Sharpe, que mide los retornos ajustados al riesgo.
- El ratio de Sharpe se calcula como: `(wᵀμ - rf) / √(wᵀΣw)`.
- Por simplicidad, asumimos una tasa libre de riesgo de `rf = 0`.

### 2. Restricciones Implementadas
- Los pesos deben sumar 1 (inversión total).
- Pesos entre 0 y un valor máximo definido por el usuario (`max_weight`).
- La volatilidad del portafolio no debe exceder el `risk_level` especificado por el usuario.

### 3. Algoritmo
- Se utiliza el método SLSQP (Sequential Least Squares Programming) de `scipy.optimize.minimize`, adecuado para problemas con restricciones no lineales.

### 4. Justificación del Modelo

La elección de este modelo de optimización se basa en varios factores clave:

1. **Eficiencia de Mercado**:
   - Modern Portfolio Theory (MPT) es un marco teórico probado y validado que ha demostrado su efectividad en mercados eficientes.
   - El enfoque de media-varianza proporciona una base sólida para la toma de decisiones de inversión.

2. **Balance entre Riesgo y Retorno**:
   - La maximización del ratio de Sharpe asegura que obtenemos el mejor retorno posible por unidad de riesgo asumido.
   - Este enfoque es particularmente útil para inversores que buscan optimizar su perfil de riesgo-retorno.

3. **Flexibilidad y Control**:
   - El modelo permite un control sobre el riesgo a través del parámetro `risk_level`.
   - La restricción de `max_weight` ayuda a prevenir la concentración excesiva en un solo activo.
   - Estas restricciones hacen que el modelo sea adaptable a diferentes perfiles de riesgo y políticas de inversión.

4. **Robustez Computacional**:
   - El algoritmo SLSQP es particularmente adecuado para este tipo de optimización porque:
     - Maneja eficientemente restricciones no lineales.
     - Es estable numéricamente.
     - Converge de manera confiable a soluciones óptimas.
     - Puede manejar portafolios con un gran número de activos.

5. **Implementación Práctica**:
   - El modelo es relativamente simple de implementar y mantener.
   - La optimización es eficiente, permitiendo actualizaciones frecuentes del portafolio.

## Supuestos Clave

- La tasa libre de riesgo es 0.
- Se asume que los retornos están limpios y correctamente formateados.
- Los retornos siguen una distribución aproximadamente normal.
- El riesgo del portafolio se controla explícitamente con una restricción de volatilidad (`risk_level`).

## Uso de la API

- **Endpoint:** `POST /optimize-portfolio`
- **Entrada:**
  - `file`: archivo CSV con retornos históricos (fecha en la primera columna, activos en columnas siguientes).
  - `risk_level`: nivel máximo de riesgo (volatilidad diaria).
  - `max_weight`: peso máximo permitido por activo.
- **Respuesta:**
  ```json
  {
    "optimal_portfolio": {
      "ticker_1": peso_1,
      "ticker_2": peso_2,
      ...
    }
  }
  ```

### Ejemplo con `curl`

```bash
curl -X POST "http://127.0.0.1:8000/optimize-portfolio" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@returns.csv;type=text/csv" \
  -F "risk_level=0.15" \
  -F "max_weight=0.3"
```

## Ejecución del Servicio

1. Instala dependencias:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Inicia el servidor:
```bash
uvicorn app.main:app --reload
```

## Ejecución de Pruebas

```bash
pytest
```

## Dependencias

- `fastapi`: framework web para APIs.
- `pandas`, `numpy`: análisis y procesamiento numérico.
- `scipy`: optimización científica.
- `uvicorn`: servidor ASGI.
- `python-multipart`: manejo de archivos subidos.
- `pytest`: pruebas unitarias.