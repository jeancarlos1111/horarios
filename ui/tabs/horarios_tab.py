from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableView, QMessageBox, QComboBox,
                             QTimeEdit, QFileDialog)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtSql import QSqlRelationalTableModel, QSqlRelation, QSqlQuery
from utils.dialog_utils import show_error, confirm_action
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape

class HorariosTab(QWidget):
    def __init__(self, model_manager, db):
        super().__init__()
        self.model_manager = model_manager
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de la pestaña de horarios"""
        layout = QVBoxLayout()
        
        # Formulario
        form = QVBoxLayout()
        
        # Combos para selección
        self.hor_prof = QComboBox()
        self.hor_asig = QComboBox()
        self.hor_seccion = QComboBox()
        self.hor_aula = QComboBox()
        self.hor_dia = QComboBox()
        
        # Campos de tiempo
        self.hora_inicio = QTimeEdit()
        self.hora_inicio.setDisplayFormat("hh:mm AP")  # Formato 12 horas con AM/PM
        self.hora_inicio.setTime(QTime(8, 0))
        self.hora_fin = QTimeEdit()
        self.hora_fin.setDisplayFormat("hh:mm AP")  # Formato 12 horas con AM/PM
        self.hora_fin.setTime(QTime(9, 0))
        
        # Botones
        btn_add = QPushButton("Agregar Horario")
        btn_add.clicked.connect(self.add_horario)
        btn_del = QPushButton("Eliminar Horario")
        btn_del.clicked.connect(self.delete_horario)
        btn_reporte = QPushButton("Generar Reporte Completo")
        btn_reporte.clicked.connect(self.generar_reporte_completo)
        
        # Agregar widgets al formulario
        form.addWidget(QLabel("Profesor:"))
        form.addWidget(self.hor_prof)
        form.addWidget(QLabel("Asignatura:"))
        form.addWidget(self.hor_asig)
        form.addWidget(QLabel("Sección:"))
        form.addWidget(self.hor_seccion)
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
        form.addWidget(btn_reporte)
        
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
        
        # Configurar encabezados
        self.horario_model.setHeaderData(1, Qt.Horizontal, "Profesor")
        self.horario_model.setHeaderData(2, Qt.Horizontal, "Asignatura")
        self.horario_model.setHeaderData(3, Qt.Horizontal, "Sección")
        self.horario_model.setHeaderData(4, Qt.Horizontal, "Aula")
        self.horario_model.setHeaderData(5, Qt.Horizontal, "Día")
        self.horario_model.setHeaderData(6, Qt.Horizontal, "Hora Inicio")
        self.horario_model.setHeaderData(7, Qt.Horizontal, "Hora Fin")
        
        # Tabla
        self.table = QTableView()
        self.table.setModel(self.horario_model)
        self.table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.resizeColumnsToContents()
        
        # Cargar datos en los combos
        self.load_combos()
        
        # Agregar widgets al layout principal
        layout.addLayout(form)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_combos(self):
        """Carga los datos en los comboboxes"""
        # Limpiar combos
        self.hor_prof.clear()
        self.hor_asig.clear()
        self.hor_seccion.clear()
        self.hor_aula.clear()
        self.hor_dia.clear()
        
        # Cargar profesores
        query = QSqlQuery(self.db)
        if query.exec_("SELECT id_profesor, nombre, apellido FROM Profesores ORDER BY apellido, nombre"):
            while query.next():
                nombre_completo = f"{query.value(1)} {query.value(2)}"
                self.hor_prof.addItem(nombre_completo, query.value(0))
        
        # Cargar asignaturas
        if query.exec_("SELECT id_asignatura, nombre FROM Asignaturas ORDER BY nombre"):
            while query.next():
                self.hor_asig.addItem(query.value(1), query.value(0))
        
        # Cargar secciones
        if query.exec_("SELECT id_grupo, nombre FROM Grupos ORDER BY nombre"):
            while query.next():
                self.hor_seccion.addItem(query.value(1), query.value(0))
        
        # Cargar aulas
        if query.exec_("SELECT id_aula, nombre FROM Aulas ORDER BY nombre"):
            while query.next():
                self.hor_aula.addItem(query.value(1), query.value(0))
        
        # Cargar días
        if query.exec_("SELECT id_dia, nombre FROM DiasSemana ORDER BY id_dia"):
            while query.next():
                self.hor_dia.addItem(query.value(1), query.value(0))

    def add_horario(self):
        """Agrega un nuevo horario"""
        # Verificar selecciones
        if self.hor_prof.currentIndex() < 0:
            show_error(self, "Seleccione un profesor")
            return
        if self.hor_asig.currentIndex() < 0:
            show_error(self, "Seleccione una asignatura")
            return
        if self.hor_seccion.currentIndex() < 0:
            show_error(self, "Seleccione una sección")
            return
        if self.hor_aula.currentIndex() < 0:
            show_error(self, "Seleccione un aula")
            return
        if self.hor_dia.currentIndex() < 0:
            show_error(self, "Seleccione un día")
            return
        
        # Obtener valores
        id_prof = self.hor_prof.currentData()
        id_asig = self.hor_asig.currentData()
        id_seccion = self.hor_seccion.currentData()
        id_aula = self.hor_aula.currentData()
        id_dia = self.hor_dia.currentData()
        hora_inicio = self.hora_inicio.time().toString("HH:mm")  # Guardamos en formato 24h
        hora_fin = self.hora_fin.time().toString("HH:mm")  # Guardamos en formato 24h
        
        # Verificar solapamiento
        if self.hay_solapamiento(id_prof, id_aula, id_dia, hora_inicio, hora_fin):
            show_error(self, "Conflicto de horario (profesor o aula ocupada)")
            return
        
        # Insertar horario
        row = self.horario_model.rowCount()
        self.horario_model.insertRow(row)
        self.horario_model.setData(self.horario_model.index(row, 1), id_prof)
        self.horario_model.setData(self.horario_model.index(row, 2), id_asig)
        self.horario_model.setData(self.horario_model.index(row, 3), id_seccion)
        self.horario_model.setData(self.horario_model.index(row, 4), id_aula)
        self.horario_model.setData(self.horario_model.index(row, 5), id_dia)
        self.horario_model.setData(self.horario_model.index(row, 6), hora_inicio)
        self.horario_model.setData(self.horario_model.index(row, 7), hora_fin)
        
        if not self.horario_model.submitAll():
            show_error(self, "Error al agregar horario")
            self.horario_model.revertAll()
        else:
            self.horario_model.select()

    def delete_horario(self):
        """Elimina el horario seleccionado"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            show_error(self, "Por favor seleccione un horario")
            return
        
        if confirm_action(self, "¿Está seguro de eliminar este horario?"):
            for index in indexes:
                if index.column() == 0:  # Solo eliminar una vez por fila
                    self.horario_model.removeRow(index.row())
            
            if not self.horario_model.submitAll():
                show_error(self, "Error al eliminar horario")
                self.horario_model.revertAll()
            else:
                self.horario_model.select()

    def hay_solapamiento(self, id_profesor, id_aula, id_dia, hora_inicio, hora_fin):
        """Verifica si hay solapamiento de horarios"""
        query = QSqlQuery(self.db)
        query.prepare("""
            SELECT COUNT(*) FROM Horarios
            WHERE id_dia = ? AND (
                (hora_inicio < ? AND hora_fin > ?) OR
                (hora_inicio < ? AND hora_fin > ?) OR
                (hora_inicio >= ? AND hora_fin <= ?)
            ) AND (id_profesor = ? OR id_aula = ?)
        """)
        
        query.addBindValue(id_dia)
        query.addBindValue(hora_inicio)
        query.addBindValue(hora_inicio)
        query.addBindValue(hora_fin)
        query.addBindValue(hora_inicio)
        query.addBindValue(hora_inicio)
        query.addBindValue(hora_fin)
        query.addBindValue(id_profesor)
        query.addBindValue(id_aula)
        
        if not query.exec_():
            show_error(self, f"Error al verificar solapamiento: {query.lastError().text()}")
            return True
        
        if query.next():
            return query.value(0) > 0
        return True

    def generar_reporte_completo(self):
        """Genera un reporte PDF con todos los horarios"""
        try:
            # Consulta SQL para obtener todos los horarios
            query = QSqlQuery(self.db)
            query.prepare("""
                SELECT 
                    p.nombre || ' ' || p.apellido AS profesor,
                    a.nombre AS asignatura,
                    g.nombre AS seccion,
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
                ORDER BY p.apellido, p.nombre, d.id_dia, h.hora_inicio
            """)
            
            if not query.exec_():
                show_error(self, f"Error al ejecutar la consulta: {query.lastError().text()}")
                return
            
            registros = []
            while query.next():
                # Convertir horas a formato 12h con AM/PM
                hora_inicio = QTime.fromString(query.value(5), "HH:mm")
                hora_fin = QTime.fromString(query.value(6), "HH:mm")
                
                registros.append({
                    'profesor': query.value(0),
                    'asignatura': query.value(1),
                    'seccion': query.value(2),
                    'aula': query.value(3),
                    'dia': query.value(4),
                    'hora_inicio': hora_inicio.toString("hh:mm AP"),
                    'hora_fin': hora_fin.toString("hh:mm AP")
                })
            
            if not registros:
                show_error(self, "No hay horarios asignados")
                return
            
            # Diálogo para guardar archivo
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte PDF",
                "Reporte_Horarios.pdf",
                "PDF Files (*.pdf)"
            )
            if not filename:
                return
            
            # Generar PDF
            c = canvas.Canvas(filename, pagesize=landscape(letter))
            c.setTitle("Reporte de Horarios")
            
            # Configuración de página
            margen_izq = 40
            margen_der = 40
            ancho_pag = landscape(letter)[0]
            
            # Encabezados y anchos de columna
            encabezados = ["Profesor", "Asignatura", "Sección", "Aula", "Día", "Hora Inicio", "Hora Fin"]
            anchos = {
                'profesor': 140,    # Reducido para dar más espacio a las horas
                'asignatura': 140,  # Reducido para dar más espacio a las horas
                'seccion': 80,      # Reducido para dar más espacio a las horas
                'aula': 80,         # Reducido para dar más espacio a las horas
                'dia': 60,          # Reducido para dar más espacio a las horas
                'hora_inicio': 100, # Aumentado para mostrar la hora completa
                'hora_fin': 100     # Aumentado para mostrar la hora completa
            }
            
            # Calcular posiciones
            x_pos = [margen_izq]
            for i in range(1, len(encabezados)):
                x_pos.append(x_pos[i-1] + anchos[list(anchos.keys())[i-1]] + 10)  # Reducido el espacio entre columnas
            
            # Título
            y = 550
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margen_izq, y, "REPORTE DE HORARIOS")
            y -= 30
            
            # Encabezados
            c.setFont("Helvetica-Bold", 10)
            for i, (x, enc) in enumerate(zip(x_pos, encabezados)):
                if enc in ["Hora Inicio", "Hora Fin"]:
                    # Centrar los encabezados de hora
                    c.drawCentredString(x + anchos[list(anchos.keys())[i]]/2, y, enc)
                else:
                    c.drawString(x, y, enc)
            y -= 20
            
            # Línea separadora
            c.line(margen_izq, y, ancho_pag - margen_der, y)
            y -= 20
            
            # Contenido
            c.setFont("Helvetica", 9)
            for reg in registros:
                if y < 50:  # Nueva página
                    c.showPage()
                    y = 550
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(margen_izq, y, "REPORTE DE HORARIOS")
                    y -= 30
                    c.setFont("Helvetica-Bold", 10)
                    for i, (x, enc) in enumerate(zip(x_pos, encabezados)):
                        if enc in ["Hora Inicio", "Hora Fin"]:
                            c.drawCentredString(x + anchos[list(anchos.keys())[i]]/2, y, enc)
                        else:
                            c.drawString(x, y, enc)
                    y -= 20
                    c.line(margen_izq, y, ancho_pag - margen_der, y)
                    y -= 20
                    c.setFont("Helvetica", 9)
                
                # Truncar textos largos solo para campos de texto
                max_chars = {
                    'profesor': 25,
                    'asignatura': 25,
                    'seccion': 15,
                    'aula': 15,
                    'dia': 12
                }
                
                # Dibujar cada campo
                for i, (key, val) in enumerate(reg.items()):
                    if key in ['hora_inicio', 'hora_fin']:
                        # Para las horas, centrar y no truncar
                        c.drawCentredString(x_pos[i] + anchos[key]/2, y, str(val))
                    else:
                        # Para los demás campos, truncar si es necesario
                        if len(str(val)) > max_chars[key]:
                            val = str(val)[:max_chars[key]-3] + "..."
                        c.drawString(x_pos[i], y, str(val))
                
                y -= 20
            
            c.save()
            QMessageBox.information(self, "Éxito", f"Reporte guardado en: {filename}")
            
        except Exception as e:
            show_error(self, f"Error al generar el reporte: {str(e)}")
            print(f"Error detallado: {str(e)}")  # Para depuración 