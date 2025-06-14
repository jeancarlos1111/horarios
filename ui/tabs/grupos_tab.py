from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableView, QMessageBox,
                             QFileDialog)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtSql import QSqlQuery
from utils.dialog_utils import show_error, confirm_action
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape

class GruposTab(QWidget):
    def __init__(self, model_manager, db):
        super().__init__()
        self.model_manager = model_manager
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de la pestaña de grupos"""
        layout = QVBoxLayout()
        
        # Formulario
        form = QHBoxLayout()
        self.grupo_nombre = QLineEdit()
        self.grupo_desc = QLineEdit()
        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.add_grupo)
        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.delete_grupo)
        btn_reporte = QPushButton("Generar Reporte de Horario")
        btn_reporte.clicked.connect(self.generar_reporte_grupo)

        form.addWidget(QLabel("Nombre:"))
        form.addWidget(self.grupo_nombre)
        form.addWidget(QLabel("Descripción:"))
        form.addWidget(self.grupo_desc)
        form.addWidget(btn_add)
        form.addWidget(btn_del)
        form.addWidget(btn_reporte)

        # Tabla
        self.table = QTableView()
        self.table.setModel(self.model_manager.get_model("Grupos"))
        self.table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        self.table.setSelectionBehavior(QTableView.SelectRows)

        layout.addLayout(form)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def add_grupo(self):
        """Agrega un nuevo grupo"""
        nombre = self.grupo_nombre.text().strip()
        descripcion = self.grupo_desc.text().strip()
        
        if not nombre:
            show_error(self, "Por favor ingrese el nombre de la sección")
            return

        model = self.model_manager.get_model("Grupos")
        row = model.rowCount()
        model.insertRow(row)
        model.setData(model.index(row, 1), nombre)
        model.setData(model.index(row, 2), descripcion)
        
        if not model.submitAll():
            show_error(self, "Error al agregar sección")
            model.revertAll()
        else:
            self.grupo_nombre.clear()
            self.grupo_desc.clear()
            self.model_manager.refresh_model("Grupos")

    def delete_grupo(self):
        """Elimina el grupo seleccionado"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            show_error(self, "Por favor seleccione una sección")
            return

        if confirm_action(self, "¿Está seguro de eliminar esta sección?"):
            model = self.model_manager.get_model("Grupos")
            for index in indexes:
                if index.column() == 0:  # Solo eliminar una vez por fila
                    model.removeRow(index.row())
            
            if not model.submitAll():
                show_error(self, "Error al eliminar sección")
                model.revertAll()
            else:
                self.model_manager.refresh_model("Grupos")

    def generar_reporte_grupo(self):
        """Genera un reporte PDF con el horario del grupo seleccionado en formato calendario semanal"""
        try:
            # Obtener el grupo seleccionado
            indexes = self.table.selectedIndexes()
            if not indexes:
                show_error(self, "Por favor seleccione una sección")
                return
            
            # Obtener el ID y nombre del grupo
            row = indexes[0].row()
            id_grupo = self.table.model().data(self.table.model().index(row, 0))
            nombre_grupo = self.table.model().data(self.table.model().index(row, 1))
            
            # Consulta SQL para obtener el horario del grupo
            query = QSqlQuery(self.db)
            query.prepare("""
                SELECT 
                    p.nombre || ' ' || p.apellido AS profesor,
                    a.nombre AS asignatura,
                    au.nombre AS aula,
                    d.id_dia,
                    d.nombre AS dia,
                    h.hora_inicio,
                    h.hora_fin
                FROM Horarios h
                JOIN Profesores p ON h.id_profesor = p.id_profesor
                JOIN Asignaturas a ON h.id_asignatura = a.id_asignatura
                JOIN Aulas au ON h.id_aula = au.id_aula
                JOIN DiasSemana d ON h.id_dia = d.id_dia
                WHERE h.id_grupo = ?
                ORDER BY d.id_dia, h.hora_inicio
            """)
            
            query.addBindValue(id_grupo)
            
            if not query.exec_():
                show_error(self, f"Error al ejecutar la consulta: {query.lastError().text()}")
                return
            
            # Organizar horarios por día
            horarios_por_dia = {
                1: [], # Lunes
                2: [], # Martes
                3: [], # Miércoles
                4: [], # Jueves
                5: []  # Viernes
            }
            
            while query.next():
                # Convertir horas a formato 12h con AM/PM
                hora_inicio = QTime.fromString(query.value(5), "HH:mm")
                hora_fin = QTime.fromString(query.value(6), "HH:mm")
                
                registro = {
                    'profesor': query.value(0),
                    'asignatura': query.value(1),
                    'aula': query.value(2),
                    'dia': query.value(4),
                    'hora_inicio': hora_inicio.toString("hh:mm AP"),
                    'hora_fin': hora_fin.toString("hh:mm AP")
                }
                
                id_dia = query.value(3)
                if id_dia in horarios_por_dia:
                    horarios_por_dia[id_dia].append(registro)
            
            # Verificar si hay horarios
            if not any(horarios_por_dia.values()):
                show_error(self, f"No hay horarios asignados para la sección {nombre_grupo}")
                return
            
            # Diálogo para guardar archivo
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Reporte PDF",
                f"Horario_{nombre_grupo}.pdf",
                "PDF Files (*.pdf)"
            )
            if not filename:
                return
            
            # Generar PDF
            c = canvas.Canvas(filename, pagesize=landscape(letter))
            c.setTitle(f"Horario de la Sección {nombre_grupo}")
            
            # Configuración de página
            margen_izq = 40
            margen_der = 40
            margen_sup = 40
            margen_inf = 40
            ancho_pag = landscape(letter)[0]
            alto_pag = landscape(letter)[1]
            
            # Configuración de la cuadrícula
            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
            ancho_columna = (ancho_pag - margen_izq - margen_der) / len(dias)
            alto_celda = 40
            hora_inicio = QTime(7, 0)   # 7:00 AM
            hora_fin = QTime(18, 0)     # 6:00 PM
            intervalo = 60  # 1 hora en minutos
            
            # Dibujar título
            y = alto_pag - margen_sup
            c.setFont("Helvetica-Bold", 16)
            c.drawString(margen_izq, y, f"HORARIO DE LA SECCIÓN: {nombre_grupo}")
            y -= 40
            
            # Dibujar encabezados de días
            c.setFont("Helvetica-Bold", 12)
            for i, dia in enumerate(dias):
                x = margen_izq + (i * ancho_columna)
                c.drawString(x + 10, y, dia)
            
            y -= 20
            
            # Dibujar líneas horizontales y horas
            c.setFont("Helvetica", 8)
            hora_actual = hora_inicio
            while hora_actual < hora_fin:
                # Dibujar línea horizontal
                c.line(margen_izq, y, ancho_pag - margen_der, y)
                
                # Dibujar hora
                hora_texto = hora_actual.toString("hh:mm AP")
                c.drawString(margen_izq - 35, y + 5, hora_texto)
                
                # Dibujar líneas verticales para separar días
                for i in range(len(dias) + 1):
                    x = margen_izq + (i * ancho_columna)
                    c.line(x, y, x, y - alto_celda)
                
                # Buscar y dibujar clases para esta hora
                for dia_id, horarios in horarios_por_dia.items():
                    for horario in horarios:
                        hora_clase_inicio = QTime.fromString(horario['hora_inicio'], "hh:mm AP")
                        hora_clase_fin = QTime.fromString(horario['hora_fin'], "hh:mm AP")
                        
                        # Verificar si la clase está activa en esta hora
                        if hora_clase_inicio <= hora_actual and hora_actual < hora_clase_fin:
                            x = margen_izq + ((dia_id - 1) * ancho_columna)
                            # Dibujar fondo de la clase
                            c.setFillColorRGB(0.9, 0.9, 0.9)
                            c.rect(x + 1, y - alto_celda + 1, ancho_columna - 2, alto_celda - 2, fill=1)
                            c.setFillColorRGB(0, 0, 0)
                            
                            # Dibujar contenido de la clase dentro de la celda
                            margen_texto = 5
                            linea_altura = 10
                            c.setFont("Helvetica-Bold", 8)
                            c.drawString(x + margen_texto, y - 15, horario['asignatura'])
                            c.setFont("Helvetica", 7)
                            c.drawString(x + margen_texto, y - 15 - linea_altura, horario['profesor'])
                            # Aula y horario juntos
                            texto_aula_horario = f"{horario['aula']}  {horario['hora_inicio']} - {horario['hora_fin']}"
                            c.drawString(x + margen_texto, y - 15 - 2*linea_altura, texto_aula_horario)
                
                y -= alto_celda
                hora_actual = hora_actual.addSecs(intervalo * 60)
            
            # Dibujar última línea horizontal
            c.line(margen_izq, y, ancho_pag - margen_der, y)
            
            c.save()
            QMessageBox.information(self, "Éxito", f"Reporte guardado en: {filename}")
            
        except Exception as e:
            show_error(self, f"Error al generar el reporte: {str(e)}")
            print(f"Error detallado: {str(e)}")  # Para depuración 