from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableView, QMessageBox,
                             QSpinBox)
from PyQt5.QtCore import Qt
from utils.dialog_utils import show_error, confirm_action

class AulasTab(QWidget):
    def __init__(self, model_manager, db):
        super().__init__()
        self.model_manager = model_manager
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de la pestaña de aulas"""
        layout = QVBoxLayout()
        
        # Formulario
        form = QHBoxLayout()
        self.aula_nombre = QLineEdit()
        self.aula_capacidad = QSpinBox()
        self.aula_capacidad.setMinimum(1)
        self.aula_capacidad.setMaximum(999)
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
        self.table = QTableView()
        self.table.setModel(self.model_manager.get_model("Aulas"))
        self.table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        self.table.setSelectionBehavior(QTableView.SelectRows)

        layout.addLayout(form)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def add_aula(self):
        """Agrega una nueva aula"""
        nombre = self.aula_nombre.text().strip()
        capacidad = self.aula_capacidad.value()
        
        if not nombre:
            show_error(self, "Por favor ingrese el nombre del aula")
            return

        model = self.model_manager.get_model("Aulas")
        row = model.rowCount()
        model.insertRow(row)
        model.setData(model.index(row, 1), nombre)
        model.setData(model.index(row, 2), capacidad)
        
        if not model.submitAll():
            show_error(self, "Error al agregar aula")
            model.revertAll()
        else:
            self.aula_nombre.clear()
            self.aula_capacidad.setValue(1)
            self.model_manager.refresh_model("Aulas")

    def delete_aula(self):
        """Elimina el aula seleccionada"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            show_error(self, "Por favor seleccione un aula")
            return

        if confirm_action(self, "¿Está seguro de eliminar este aula?"):
            model = self.model_manager.get_model("Aulas")
            for index in indexes:
                if index.column() == 0:  # Solo eliminar una vez por fila
                    model.removeRow(index.row())
            
            if not model.submitAll():
                show_error(self, "Error al eliminar aula")
                model.revertAll()
            else:
                self.model_manager.refresh_model("Aulas") 