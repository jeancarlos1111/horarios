import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                             QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QTimeEdit, QTableView,
                             QMessageBox, QFileDialog)
from PyQt5.QtSql import (QSqlDatabase, QSqlTableModel, QSqlQuery,
                         QSqlRelationalTableModel, QSqlRelation)
from PyQt5.QtCore import Qt, QTime

class HorarioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Horarios")
        self.setGeometry(100, 100, 800, 600)
        
        self.init_db()
        self.create_models()
        self.setup_ui()

    def init_db(self):
        """Inicializa y configura la base de datos SQLite"""
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('horarios.db')
        
        if not self.db.open():
            QMessageBox.critical(None, "Error", "No se puede conectar a la base de datos")
            return False

        query = QSqlQuery(self.db)
        
        # Crear tablas si no existen
        tablas = [
            """CREATE TABLE IF NOT EXISTS Profesores (
                id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                UNIQUE (nombre, apellido))""",
                
            """CREATE TABLE IF NOT EXISTS Asignaturas (
                id_asignatura INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT)""",
                
            """CREATE TABLE IF NOT EXISTS Grupos (
                id_grupo INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT)""",
                
            """CREATE TABLE IF NOT EXISTS Aulas (
                id_aula INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                capacidad INTEGER)""",
                
            """CREATE TABLE IF NOT EXISTS DiasSemana (
                id_dia INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE)""",
                
            """CREATE TABLE IF NOT EXISTS Horarios (
                id_horario INTEGER PRIMARY KEY AUTOINCREMENT,
                id_profesor INTEGER NOT NULL,
                id_asignatura INTEGER NOT NULL,
                id_grupo INTEGER NOT NULL,
                id_aula INTEGER NOT NULL,
                id_dia INTEGER NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fin TEXT NOT NULL,
                FOREIGN KEY (id_profesor) REFERENCES Profesores(id_profesor),
                FOREIGN KEY (id_asignatura) REFERENCES Asignaturas(id_asignatura),
                FOREIGN KEY (id_grupo) REFERENCES Grupos(id_grupo),
                FOREIGN KEY (id_aula) REFERENCES Aulas(id_aula),
                FOREIGN KEY (id_dia) REFERENCES DiasSemana(id_dia),
                CONSTRAINT unique_horario_profesor UNIQUE (id_profesor, id_dia, hora_inicio, hora_fin),
                CONSTRAINT unique_horario_aula UNIQUE (id_aula, id_dia, hora_inicio, hora_fin))"""
        ]

        for tabla in tablas:
            if not query.exec_(tabla):
                QMessageBox.critical(None, "Error", f"Error al crear tabla: {query.lastError().text()}")

        # Insertar días de la semana si no existen
        query.exec_("SELECT COUNT(*) FROM DiasSemana")
        if query.next() and query.value(0) == 0:
            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            for dia in dias:
                query.exec_(f"INSERT INTO DiasSemana (nombre) VALUES ('{dia}')")

    def create_models(self):
        """Crea los modelos de datos para cada tabla"""
        self.modelos = {
            "Profesores": QSqlTableModel(db=self.db),
            "Asignaturas": QSqlTableModel(db=self.db),
            "Grupos": QSqlTableModel(db=self.db),
            "Aulas": QSqlTableModel(db=self.db),
            "DiasSemana": QSqlTableModel(db=self.db)
        }
        
        for nombre, modelo in self.modelos.items():
            modelo.setTable(nombre)
            modelo.select()

    def setup_ui(self):
        """Configura la interfaz gráfica"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.create_profesores_tab()
        self.create_asignaturas_tab()
        self.create_grupos_tab()
        self.create_aulas_tab()
        self.create_horarios_tab()

    def create_profesores_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Formulario
        form = QHBoxLayout()
        self.prof_nombre = QLineEdit()
        self.prof_apellido = QLineEdit()
        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.add_profesor)
        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.delete_profesor)

        form.addWidget(QLabel("Nombre:"))
        form.addWidget(self.prof_nombre)
        form.addWidget(QLabel("Apellido:"))
        form.addWidget(self.prof_apellido)
        form.addWidget(btn_add)
        form.addWidget(btn_del)

        # Tabla
        table = QTableView()
        table.setModel(self.modelos["Profesores"])
        table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        table.setSelectionBehavior(QTableView.SelectRows)

        layout.addLayout(form)
        layout.addWidget(table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Profesores")

    def create_asignaturas_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Formulario
        form = QHBoxLayout()
        self.asig_nombre = QLineEdit()
        self.asig_desc = QLineEdit()
        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.add_asignatura)
        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.delete_asignatura)

        form.addWidget(QLabel("Nombre:"))
        form.addWidget(self.asig_nombre)
        form.addWidget(QLabel("Descripción:"))
        form.addWidget(self.asig_desc)
        form.addWidget(btn_add)
        form.addWidget(btn_del)

        # Tabla
        table = QTableView()
        table.setModel(self.modelos["Asignaturas"])
        table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        table.setSelectionBehavior(QTableView.SelectRows)

        layout.addLayout(form)
        layout.addWidget(table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Asignaturas")

    def create_grupos_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Formulario
        form = QHBoxLayout()
        self.grupo_nombre = QLineEdit()
        self.grupo_desc = QLineEdit()
        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.add_grupo)
        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.delete_grupo)

        form.addWidget(QLabel("Nombre:"))
        form.addWidget(self.grupo_nombre)
        form.addWidget(QLabel("Descripción:"))
        form.addWidget(self.grupo_desc)
        form.addWidget(btn_add)
        form.addWidget(btn_del)

        # Tabla
        table = QTableView()
        table.setModel(self.modelos["Grupos"])
        table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        table.setSelectionBehavior(QTableView.SelectRows)

        layout.addLayout(form)
        layout.addWidget(table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Grupos")

    def create_aulas_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Formulario
        form = QHBoxLayout()
        self.aula_nombre = QLineEdit()
        self.aula_capacidad = QLineEdit()
        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.add_aula)
        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.delete_aula)

        form.addWidget(QLabel("Nombre:"))
        form.addWidget(self.aula_nombre)
        form.addWidget(QLabel("Capacidad:"))
        form.addWidget(self.aula_capacidad)
        form.addWidget(btn_add)
        form.addWidget(btn_del)

        # Tabla
        table = QTableView()
        table.setModel(self.modelos["Aulas"])
        table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        table.setSelectionBehavior(QTableView.SelectRows)

        layout.addLayout(form)
        layout.addWidget(table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Aulas")

    def create_horarios_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Formulario
        form = QVBoxLayout()
        self.hor_prof = QComboBox()
        self.hor_asig = QComboBox()
        self.hor_grupo = QComboBox()
        self.hor_aula = QComboBox()
        self.hor_dia = QComboBox()
        self.load_combos()
        
        self.hora_inicio = QTimeEdit()
        self.hora_inicio.setTime(QTime(8, 0))
        self.hora_fin = QTimeEdit()
        self.hora_fin.setTime(QTime(9, 0))
        
        btn_add = QPushButton("Agregar Horario")
        btn_add.clicked.connect(self.add_horario)
        btn_del = QPushButton("Eliminar Horario")
        btn_del.clicked.connect(self.delete_horario)
        
        # Botón para generar el reporte de todos los profesores con horarios
        btn_reporte_completo = QPushButton("Generar Reporte Completo de Horarios")
        btn_reporte_completo.clicked.connect(self.generar_reporte_completo_profesores)
        form.addWidget(btn_reporte_completo)

        # Configurar modelo relacional
        self.horario_model = QSqlRelationalTableModel(db=self.db)
        self.horario_model.setTable("Horarios")
        
        # Establecer relaciones
        self.horario_model.setRelation(
            self.horario_model.fieldIndex("id_profesor"),
            QSqlRelation("Profesores", "id_profesor", "nombre || ' ' || apellido AS nombre_completo")
        )
        self.horario_model.setRelation(
            self.horario_model.fieldIndex("id_asignatura"),
            QSqlRelation("Asignaturas", "id_asignatura", "nombre")
        )
        self.horario_model.setRelation(
            self.horario_model.fieldIndex("id_grupo"),
            QSqlRelation("Grupos", "id_grupo", "nombre")
        )
        self.horario_model.setRelation(
            self.horario_model.fieldIndex("id_aula"),
            QSqlRelation("Aulas", "id_aula", "nombre")
        )
        self.horario_model.setRelation(
            self.horario_model.fieldIndex("id_dia"),
            QSqlRelation("DiasSemana", "id_dia", "nombre")
        )
        
        self.horario_model.select()

        self.horario_model.setHeaderData(1, Qt.Horizontal, "Profesor")
        self.horario_model.setHeaderData(2, Qt.Horizontal, "Asignatura")
        self.horario_model.setHeaderData(3, Qt.Horizontal, "Grupo")
        self.horario_model.setHeaderData(4, Qt.Horizontal, "Aula")
        self.horario_model.setHeaderData(5, Qt.Horizontal, "Día")
        self.horario_model.setHeaderData(6, Qt.Horizontal, "Hora Inicio")
        self.horario_model.setHeaderData(7, Qt.Horizontal, "Hora Fin")
        
        # Configurar tabla (VIEW)
        self.horario_table = QTableView()
        self.horario_table.setModel(self.horario_model)
        self.horario_table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        self.horario_table.setSelectionBehavior(QTableView.SelectRows)
        self.horario_table.resizeColumnsToContents()

        # Ensamblar interfaz
        form.addWidget(QLabel("Profesor:"))
        form.addWidget(self.hor_prof)
        form.addWidget(QLabel("Asignatura:"))
        form.addWidget(self.hor_asig)
        form.addWidget(QLabel("Grupo:"))
        form.addWidget(self.hor_grupo)
        form.addWidget(QLabel("Aula:"))
        form.addWidget(self.hor_aula)
        form.addWidget(QLabel("Día:"))
        form.addWidget(self.hor_dia)
        form.addWidget(QLabel("Hora Inicio:"))
        form.addWidget(self.hora_inicio)
        form.addWidget(QLabel("Hora Fin:"))
        form.addWidget(self.hora_fin)
        form.addWidget(btn_add)
        form.addWidget(btn_del)

        layout.addLayout(form)
        layout.addWidget(self.horario_table)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Horarios")

    def load_combos(self):
        """Carga datos en los comboboxes"""
        # Limpiar combos
        self.hor_prof.clear()
        self.hor_asig.clear()
        self.hor_grupo.clear()
        self.hor_aula.clear()
        self.hor_dia.clear()

        # Cargar profesores
        query = QSqlQuery(self.db)
        query.exec_("SELECT id_profesor, nombre, apellido FROM Profesores ORDER BY apellido, nombre")
        while query.next():
            nombre_completo = f"{query.value(1)} {query.value(2)}"
            self.hor_prof.addItem(nombre_completo, query.value(0))

        # Cargar asignaturas
        query.exec_("SELECT id_asignatura, nombre FROM Asignaturas ORDER BY nombre")
        while query.next():
            self.hor_asig.addItem(query.value(1), query.value(0))

        # Cargar grupos
        query.exec_("SELECT id_grupo, nombre FROM Grupos ORDER BY nombre")
        while query.next():
            self.hor_grupo.addItem(query.value(1), query.value(0))

        # Cargar aulas
        query.exec_("SELECT id_aula, nombre FROM Aulas ORDER BY nombre")
        while query.next():
            self.hor_aula.addItem(query.value(1), query.value(0))

        # Cargar días
        query.exec_("SELECT id_dia, nombre FROM DiasSemana ORDER BY id_dia")
        while query.next():
            self.hor_dia.addItem(query.value(1), query.value(0))

    def add_profesor(self):
        nombre = self.prof_nombre.text().strip()
        apellido = self.prof_apellido.text().strip()
        
        if nombre and apellido:
            record = self.modelos["Profesores"].record()
            record.setValue("nombre", nombre)
            record.setValue("apellido", apellido)
            
            if self.modelos["Profesores"].insertRecord(-1, record):
                self.modelos["Profesores"].submitAll()
                self.modelos["Profesores"].select()
                self.prof_nombre.clear()
                self.prof_apellido.clear()

    def delete_profesor(self):
        index = self.tabs.currentWidget().findChild(QTableView).currentIndex()
        if index.isValid() and self.confirm_action("¿Eliminar este profesor?"):
            self.modelos["Profesores"].removeRow(index.row())
            self.modelos["Profesores"].submitAll()
            self.modelos["Profesores"].select()

    def add_asignatura(self):
        nombre = self.asig_nombre.text().strip()
        desc = self.asig_desc.text().strip()
        
        if nombre:
            record = self.modelos["Asignaturas"].record()
            record.setValue("nombre", nombre)
            record.setValue("descripcion", desc)
            
            if self.modelos["Asignaturas"].insertRecord(-1, record):
                self.modelos["Asignaturas"].submitAll()
                self.modelos["Asignaturas"].select()
                self.asig_nombre.clear()
                self.asig_desc.clear()

    def delete_asignatura(self):
        index = self.tabs.currentWidget().findChild(QTableView).currentIndex()
        if index.isValid() and self.confirm_action("¿Eliminar esta asignatura?"):
            self.modelos["Asignaturas"].removeRow(index.row())
            self.modelos["Asignaturas"].submitAll()
            self.modelos["Asignaturas"].select()

    def add_grupo(self):
        nombre = self.grupo_nombre.text().strip()
        desc = self.grupo_desc.text().strip()
        
        if nombre:
            record = self.modelos["Grupos"].record()
            record.setValue("nombre", nombre)
            record.setValue("descripcion", desc)
            
            if self.modelos["Grupos"].insertRecord(-1, record):
                self.modelos["Grupos"].submitAll()
                self.modelos["Grupos"].select()
                self.grupo_nombre.clear()
                self.grupo_desc.clear()

    def delete_grupo(self):
        index = self.tabs.currentWidget().findChild(QTableView).currentIndex()
        if index.isValid() and self.confirm_action("¿Eliminar este grupo?"):
            self.modelos["Grupos"].removeRow(index.row())
            self.modelos["Grupos"].submitAll()
            self.modelos["Grupos"].select()

    def add_aula(self):
        nombre = self.aula_nombre.text().strip()
        capacidad = self.aula_capacidad.text().strip()
        
        if nombre and capacidad.isdigit():
            record = self.modelos["Aulas"].record()
            record.setValue("nombre", nombre)
            record.setValue("capacidad", int(capacidad))
            
            if self.modelos["Aulas"].insertRecord(-1, record):
                self.modelos["Aulas"].submitAll()
                self.modelos["Aulas"].select()
                self.aula_nombre.clear()
                self.aula_capacidad.clear()

    def delete_aula(self):
        index = self.tabs.currentWidget().findChild(QTableView).currentIndex()
        if index.isValid() and self.confirm_action("¿Eliminar este aula?"):
            self.modelos["Aulas"].removeRow(index.row())
            self.modelos["Aulas"].submitAll()
            self.modelos["Aulas"].select()

    def add_horario(self):
        """Agrega un nuevo horario"""
        # Verificar que haya selección en todos los comboboxes
        if self.hor_prof.currentIndex() < 0:
            self.show_error("Seleccione un profesor")
            return
        if self.hor_asig.currentIndex() < 0:
            self.show_error("Seleccione una asignatura")
            return
        if self.hor_grupo.currentIndex() < 0:
            self.show_error("Seleccione un grupo")
            return
        if self.hor_aula.currentIndex() < 0:
            self.show_error("Seleccione un aula")
            return
        if self.hor_dia.currentIndex() < 0:
            self.show_error("Seleccione un día")
            return

        # Obtener IDs usando currentData()
        id_prof = self.hor_prof.currentData()
        id_asig = self.hor_asig.currentData()
        id_grupo = self.hor_grupo.currentData()
        id_aula = self.hor_aula.currentData()
        id_dia = self.hor_dia.currentData()

        # Mensajes de depuración
        print("Valores obtenidos:")
        print(f"ID Profesor: {id_prof} (Tipo: {type(id_prof)})")
        print(f"ID Asignatura: {id_asig} (Tipo: {type(id_asig)})")
        print(f"ID Grupo: {id_grupo} (Tipo: {type(id_grupo)})")
        print(f"ID Aula: {id_aula} (Tipo: {type(id_aula)})")
        print(f"ID Día: {id_dia} (Tipo: {type(id_dia)})")

        # Validar que los IDs sean válidos
        if None in [id_prof, id_asig, id_grupo, id_aula, id_dia]:
            self.show_error("Error al obtener los IDs de las entidades seleccionadas")
            return

        # Verificar que los IDs sean enteros
        try:
            id_prof = int(id_prof)
            id_asig = int(id_asig)
            id_grupo = int(id_grupo)
            id_aula = int(id_aula)
            id_dia = int(id_dia)
        except (ValueError, TypeError) as e:
            self.show_error(f"Error en el formato de los IDs: {str(e)}")
            return

        hora_inicio = self.hora_inicio.time().toString("HH:mm")
        hora_fin = self.hora_fin.time().toString("HH:mm")

        if self.hay_solapamiento(id_prof, id_aula, id_dia, hora_inicio, hora_fin):
            self.show_error("Conflicto de horario (profesor o aula ocupada)")
            return

        # Usar consulta SQL directa en lugar del modelo
        query = QSqlQuery(self.db)
        query.prepare("""
            INSERT INTO Horarios 
            (id_profesor, id_asignatura, id_grupo, id_aula, id_dia, hora_inicio, hora_fin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """)
        
        query.addBindValue(id_prof)
        query.addBindValue(id_asig)
        query.addBindValue(id_grupo)
        query.addBindValue(id_aula)
        query.addBindValue(id_dia)
        query.addBindValue(hora_inicio)
        query.addBindValue(hora_fin)

        if query.exec_():
            # Actualizar el modelo de la tabla después de la inserción
            self.horario_model.select()
            QMessageBox.information(self, "Éxito", "Horario agregado correctamente")
        else:
            error = query.lastError().text()
            self.show_error(f"Error al insertar: {error}")

    def delete_horario(self):
        index = self.tabs.currentWidget().findChild(QTableView).currentIndex()
        if index.isValid() and self.confirm_action("¿Eliminar este horario?"):
            self.horario_model.removeRow(index.row())
            self.horario_model.submitAll()
            self.horario_model.select()

    def show_error(self, message):
        QMessageBox.warning(self, "Error", message)

    def confirm_action(self, message):
        return QMessageBox.question(self, "Confirmar", message,
                                  QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes
    def hay_solapamiento(self, id_profesor, id_aula, id_dia, hora_inicio, hora_fin):
        query = QSqlQuery(self.db)
        sql = """SELECT COUNT(*) FROM Horarios
                WHERE id_dia = ? AND (
                    (hora_inicio < ? AND hora_fin > ?) OR
                    (hora_inicio < ? AND hora_fin > ?) OR
                    (hora_inicio >= ? AND hora_fin <= ?)
                ) AND (id_profesor = ? OR id_aula = ?)"""
        
        query.prepare(sql)
        query.addBindValue(id_dia)
        query.addBindValue(hora_inicio)
        query.addBindValue(hora_inicio)
        query.addBindValue(hora_fin)
        query.addBindValue(hora_inicio)
        query.addBindValue(hora_inicio)
        query.addBindValue(hora_fin)
        query.addBindValue(id_profesor)
        query.addBindValue(id_aula)
        
        if query.exec_() and query.next():
            return query.value(0) > 0
        return True
    
    def generar_reporte_completo_profesores(self):
        try:
            # Consulta SQL para obtener todos los horarios con datos relacionales
            query = QSqlQuery(self.db)
            query.exec_("""
                SELECT 
                    p.nombre || ' ' || p.apellido AS profesor,
                    a.nombre AS asignatura,
                    g.nombre AS grupo,
                    au.nombre AS aula,
                    d.nombre AS dia,
                    h.hora_inicio,
                    h.hora_fin
                FROM Horarios h
                JOIN Profesores p ON h.id_profesor = p.id_profesor
                JOIN Asignaturas a ON h.id_asignatura = a.id_asignatura
                JOIN Grupos g ON h.id_grupo = g.id_grupo
                JOIN Aulas au ON h.id_aula = au.id_aula
                JOIN DiasSemana d ON h.id_dia = d.id_dia
                ORDER BY p.apellido, p.nombre, d.nombre, h.hora_inicio
            """)

            registros = []
            while query.next():
                registros.append({
                    'profesor': query.value(0),
                    'asignatura': query.value(1),
                    'grupo': query.value(2),
                    'aula': query.value(3),
                    'dia': query.value(4),
                    'hora_inicio': query.value(5),
                    'hora_fin': query.value(6)
                })

            if not registros:
                QMessageBox.warning(self, "Sin datos", "No hay horarios asignados.")
                return

            # Diálogo para guardar el archivo
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte PDF",
                "Reporte_Profesores_Con_Horarios_Completo.pdf",
                "PDF Files (*.pdf)"
            )
            if not filename:
                return

            # Generar PDF en orientación horizontal
            c = canvas.Canvas(filename, pagesize=landscape(letter))
            c.setTitle("Reporte Completo de Horarios")

            # Definir encabezados primero
            encabezados = ["Profesor", "Asignatura", "Grupo", "Aula", "Día", "Hora Inicio", "Hora Fin"]

            # Configurar márgenes y espaciado
            margen_izquierdo = 40
            margen_derecho = 40  # Aumentado para evitar que se corte al final
            ancho_pagina = landscape(letter)[0]  # Ancho de la página en horizontal
            ancho_disponible = ancho_pagina - margen_izquierdo - margen_derecho
            espaciado_columnas = 15  # Reducido para dar más espacio a las columnas

            # Encabezado
            y = 550  # Ajustado para orientación horizontal
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margen_izquierdo, y, "REPORTE COMPLETO DE HORARIOS DE PROFESORES")
            y -= 30

            # Definir anchos de columnas en puntos (ajustados para orientación horizontal)
            # Calculamos el ancho total disponible y lo distribuimos proporcionalmente
            anchos_columnas = {
                'profesor': 160,    # Reducido para dar espacio a otras columnas
                'asignatura': 160,  # Reducido para dar espacio a otras columnas
                'grupo': 90,        # Reducido para dar espacio a otras columnas
                'aula': 90,         # Reducido para dar espacio a otras columnas
                'dia': 70,          # Reducido para dar espacio a otras columnas
                'hora_inicio': 90,  # Aumentado para asegurar visibilidad
                'hora_fin': 90      # Aumentado para asegurar visibilidad
            }

            # Calcular posiciones de las columnas
            x_positions = [margen_izquierdo]
            for i in range(1, len(encabezados)):
                x_positions.append(x_positions[i-1] + anchos_columnas[list(anchos_columnas.keys())[i-1]] + espaciado_columnas)

            # Verificar que el último elemento no se salga de la página
            ultima_columna = x_positions[-1] + anchos_columnas['hora_fin']
            if ultima_columna > ancho_pagina - margen_derecho:
                # Ajustar proporcionalmente todos los anchos
                factor_ajuste = (ancho_pagina - margen_derecho - margen_izquierdo) / (ultima_columna - margen_izquierdo)
                for key in anchos_columnas:
                    anchos_columnas[key] = int(anchos_columnas[key] * factor_ajuste)
                
                # Recalcular posiciones
                x_positions = [margen_izquierdo]
                for i in range(1, len(encabezados)):
                    x_positions.append(x_positions[i-1] + anchos_columnas[list(anchos_columnas.keys())[i-1]] + espaciado_columnas)

            # Dibujar encabezados
            c.setFont("Helvetica-Bold", 10)
            for x, encabezado in zip(x_positions, encabezados):
                c.drawString(x, y, encabezado)
            y -= 20

            # Línea separadora
            c.line(margen_izquierdo, y, ancho_pagina - margen_derecho, y)
            y -= 20

            # Contenido
            c.setFont("Helvetica", 9)
            for registro in registros:
                # Verificar si hay espacio suficiente para la siguiente línea
                if y < 50:
                    c.showPage()
                    y = 550  # Ajustado para orientación horizontal
                    # Volver a encabezado en nueva página
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(margen_izquierdo, y, "REPORTE COMPLETO DE HORARIOS DE PROFESORES")
                    y -= 30
                    c.setFont("Helvetica-Bold", 10)
                    for x, encabezado in zip(x_positions, encabezados):
                        c.drawString(x, y, encabezado)
                    y -= 20
                    c.line(margen_izquierdo, y, ancho_pagina - margen_derecho, y)
                    y -= 20
                    c.setFont("Helvetica", 9)

                # Dibujar cada campo del registro con truncamiento si es necesario
                max_chars = {
                    'profesor': 30,    # Ajustado para los nuevos anchos
                    'asignatura': 30,  # Ajustado para los nuevos anchos
                    'grupo': 18,       # Ajustado para los nuevos anchos
                    'aula': 18,        # Ajustado para los nuevos anchos
                    'dia': 15,         # Ajustado para los nuevos anchos
                    'hora_inicio': 8,  # Aumentado para asegurar visibilidad
                    'hora_fin': 8      # Aumentado para asegurar visibilidad
                }

                # Profesor
                profesor = registro['profesor']
                if len(profesor) > max_chars['profesor']:
                    profesor = profesor[:max_chars['profesor']-3] + "..."
                c.drawString(x_positions[0], y, profesor)

                # Asignatura
                asignatura = registro['asignatura']
                if len(asignatura) > max_chars['asignatura']:
                    asignatura = asignatura[:max_chars['asignatura']-3] + "..."
                c.drawString(x_positions[1], y, asignatura)

                # Grupo
                grupo = registro['grupo']
                if len(grupo) > max_chars['grupo']:
                    grupo = grupo[:max_chars['grupo']-3] + "..."
                c.drawString(x_positions[2], y, grupo)

                # Aula
                aula = registro['aula']
                if len(aula) > max_chars['aula']:
                    aula = aula[:max_chars['aula']-3] + "..."
                c.drawString(x_positions[3], y, aula)

                # Día
                dia = registro['dia']
                if len(dia) > max_chars['dia']:
                    dia = dia[:max_chars['dia']-3] + "..."
                c.drawString(x_positions[4], y, dia)

                # Horas (centradas en su columna)
                hora_inicio = registro['hora_inicio']
                hora_fin = registro['hora_fin']
                
                # Calcular el centro de cada columna de hora
                centro_hora_inicio = x_positions[5] + (anchos_columnas['hora_inicio'] / 2)
                centro_hora_fin = x_positions[6] + (anchos_columnas['hora_fin'] / 2)
                
                # Dibujar las horas centradas
                c.drawCentredString(centro_hora_inicio, y, hora_inicio)
                c.drawCentredString(centro_hora_fin, y, hora_fin)

                y -= 20

            c.save()
            QMessageBox.information(self, "Éxito", f"Reporte guardado en: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar el reporte: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HorarioApp()
    window.show()
    sys.exit(app.exec_())