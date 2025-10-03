from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QHBoxLayout, QTextEdit, QComboBox
)
import pandas as pd
from data_handler import cargar_csv, obtener_resumen, obtener_tipos, obtener_mediciones, obtener_columnas_numericas

ROWS_PER_PAGE = 100  # filas por página en paginación

class DataAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador de Datos con Pandas")
        self.resize(1000, 750)

        self.df = None
        self.view_df = None
        self.current_page = 0
        self.total_pages = 0

        self.layout = QVBoxLayout()

        # Etiqueta principal
        self.label = QLabel("📂 Carga un archivo CSV para analizarlo")
        self.layout.addWidget(self.label)

        # Botones principales
        btn_layout = QHBoxLayout()
        self.btn_cargar = QPushButton("Cargar CSV")
        self.btn_resumen = QPushButton("Resumen")
        self.btn_tipos = QPushButton("Tipos de datos")
        self.btn_head5 = QPushButton("Primeros 5 registros")
        self.btn_tail5 = QPushButton("Últimos 5 registros")
        self.btn_mediciones = QPushButton("Mediciones estadísticas")
        btn_layout.addWidget(self.btn_cargar)
        btn_layout.addWidget(self.btn_resumen)
        btn_layout.addWidget(self.btn_tipos)
        btn_layout.addWidget(self.btn_head5)
        btn_layout.addWidget(self.btn_tail5)
        btn_layout.addWidget(self.btn_mediciones)
        self.layout.addLayout(btn_layout)

        # ComboBox para seleccionar columna numérica
        self.layout.addWidget(QLabel("Selecciona columna numérica:"))
        self.combo_columnas = QComboBox()
        self.layout.addWidget(self.combo_columnas)

        # --- Nuevos controles para ordenamiento (por requisito: sort_values) ---
        self.layout.addWidget(QLabel("Ordenar por columna:"))
        sort_layout = QHBoxLayout()
        self.combo_sort_columns = QComboBox()
        self.combo_sort_order = QComboBox()
        self.combo_sort_order.addItems(["Ascendente", "Descendente"])
        self.btn_sort = QPushButton("Ordenar")
        sort_layout.addWidget(self.combo_sort_columns)
        sort_layout.addWidget(self.combo_sort_order)
        sort_layout.addWidget(self.btn_sort)
        self.layout.addLayout(sort_layout)

        # Botones de paginación
        page_layout = QHBoxLayout()
        self.btn_prev = QPushButton("⬅ Anterior")
        self.page_label = QLabel("Página: 0 / 0")
        self.btn_next = QPushButton("Siguiente ➡")
        page_layout.addWidget(self.btn_prev)
        page_layout.addWidget(self.page_label)
        page_layout.addWidget(self.btn_next)
        self.layout.addLayout(page_layout)

        # Tabla para mostrar datos
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Área de texto para resultados de mediciones
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.layout.addWidget(self.text_area)

        self.setLayout(self.layout)

        # Conexiones
        self.btn_cargar.clicked.connect(self.cargar_csv_ui)
        self.btn_resumen.clicked.connect(self.mostrar_resumen)
        self.btn_tipos.clicked.connect(self.mostrar_tipos)
        self.btn_head5.clicked.connect(self.mostrar_head5)
        self.btn_tail5.clicked.connect(self.mostrar_tail5)
        self.btn_prev.clicked.connect(self.pagina_anterior)
        self.btn_next.clicked.connect(self.pagina_siguiente)
        self.btn_mediciones.clicked.connect(self.mostrar_mediciones)
        # conexión del nuevo botón de ordenamiento
        self.btn_sort.clicked.connect(self.ordenar_por_columna)

    # ---------------- Funciones ----------------
    def cargar_csv_ui(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo CSV", "", "CSV Files (*.csv)")
        if ruta:
            try:
                self.df = cargar_csv(ruta)
                self.view_df = self.df
                self.current_page = 0
                self.total_pages = (len(self.view_df) - 1) // ROWS_PER_PAGE + 1
                self.label.setText(f"✅ Dataset cargado: {ruta}")
                QMessageBox.information(self, "Éxito", f"{len(self.df)} filas y {len(self.df.columns)} columnas cargadas.")

                # Llenar comboBox con columnas numéricas
                numeric_cols = obtener_columnas_numericas(self.df)
                self.combo_columnas.clear()
                self.combo_columnas.addItems(numeric_cols)

                # Llenar combo para ordenar (todas las columnas)
                self.combo_sort_columns.clear()
                self.combo_sort_columns.addItems([str(c) for c in self.df.columns])

                # Mostrar primera página del dataset (mejor que sólo head5 para paginación)
                self.mostrar_pagina()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def mostrar_resumen(self):
        if self.df is not None:
            resumen = obtener_resumen(self.df)
            self.mostrar_dataframe(resumen)
            # Actualizar etiqueta de página para indicar que se muestra un objeto resumen
            self.page_label.setText("Resumen estadístico (describe())")
        else:
            QMessageBox.warning(self, "Atención", "Primero carga un CSV.")

    def mostrar_tipos(self):
        if self.df is not None:
            tipos = obtener_tipos(self.df)
            self.mostrar_dataframe(tipos)
            # Sugerencias de análisis según tipos detectados
            sugerencias = []
            num_cols = obtener_columnas_numericas(self.df)
            obj_cols = self.df.select_dtypes(include=["object", "category"]).columns.tolist()
            if num_cols:
                sugerencias.append(f"Columnas numéricas: {', '.join(num_cols)} -> analizar correlación, outliers, distribución y medidas de tendencia.")
            if obj_cols:
                sugerencias.append(f"Columnas categóricas/texto: {', '.join(obj_cols)} -> usar value_counts(), moda, y agrupar para ver frecuencias.")
            if not sugerencias:
                sugerencias.append("No se detectaron columnas numéricas ni categóricas claramente definidas.")
            self.text_area.setText("Sugerencias de análisis según tipos de dato:\n- " + "\n- ".join(sugerencias))
        else:
            QMessageBox.warning(self, "Atención", "Primero carga un CSV.")

    # ---------- Head/Tail ----------
    def mostrar_head5(self):
        if self.df is not None:
            self.mostrar_dataframe(self.df.head(5))
            self.page_label.setText("Mostrando primeros 5 registros")
        else:
            QMessageBox.warning(self, "Atención", "Primero carga un CSV.")

    def mostrar_tail5(self):
        if self.df is not None:
            self.mostrar_dataframe(self.df.tail(5))
            self.page_label.setText("Mostrando últimos 5 registros")
        else:
            QMessageBox.warning(self, "Atención", "Primero carga un CSV.")

    # ---------- Paginación ----------
    def pagina_anterior(self):
        if self.view_df is not None and self.current_page > 0:
            self.current_page -= 1
            self.mostrar_pagina()

    def pagina_siguiente(self):
        if self.view_df is not None and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.mostrar_pagina()

    def mostrar_pagina(self):
        if self.view_df is None:
            return
        start = self.current_page * ROWS_PER_PAGE
        end = min(start + ROWS_PER_PAGE, len(self.view_df))
        sub_df = self.view_df.iloc[start:end]
        self.mostrar_dataframe(sub_df)
        self.page_label.setText(f"Página: {self.current_page + 1} / {self.total_pages}")

    # ---------- Ordenamiento ----------
    def ordenar_por_columna(self):
        if self.df is None:
            QMessageBox.warning(self, "Atención", "Primero carga un CSV.")
            return
        col = self.combo_sort_columns.currentText()
        if not col:
            QMessageBox.warning(self, "Atención", "Selecciona una columna para ordenar.")
            return
        ascending = True if self.combo_sort_order.currentText() == "Ascendente" else False
        try:
            # Actualiza la vista ordenada pero mantiene el dataset original
            self.view_df = self.df.sort_values(by=col, ascending=ascending)
            self.current_page = 0
            self.total_pages = (len(self.view_df) - 1) // ROWS_PER_PAGE + 1
            self.mostrar_pagina()
        except Exception as e:
            QMessageBox.critical(self, "Error al ordenar", str(e))

    # ---------- Mediciones estadísticas ----------
    def mostrar_mediciones(self):
        if self.df is not None:
            col = self.combo_columnas.currentText()
            if not col:
                QMessageBox.warning(self, "Atención", "No hay columnas numéricas seleccionables.")
                return
            resultado = obtener_mediciones(self.df, col)
            if resultado is None:
                QMessageBox.warning(self, "Atención", "Columna no encontrada.")
                return
            media, mediana, std = resultado
            # Manejo de valores NaN
            def fmt(x):
                return "NaN" if pd.isna(x) else f"{x:.2f}"
            self.text_area.setText(
                f"📐 Medidas estadísticas de la columna '{col}':\n"
                f"- Media: {fmt(media)}\n"
                f"- Mediana: {fmt(mediana)}\n"
                f"- Desviación estándar: {fmt(std)}"
            )
        else:
            QMessageBox.warning(self, "Atención", "Primero carga un CSV.")

    # ---------- Mostrar DataFrame ----------
    def mostrar_dataframe(self, data):
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data.columns))
        self.table.setHorizontalHeaderLabels([str(col) for col in data.columns])
        for i, row in enumerate(data.values):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
