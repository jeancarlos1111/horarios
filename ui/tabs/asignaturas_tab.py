from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableView, QMessageBox)
from PyQt5.QtCore import Qt
from utils.dialog_utils import show_error, confirm_action

class AsignaturasTab(QWidget):
    def __init__(self, model_manager, db):
        super().__init__()
        self.model_manager = model_manager
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de la pestaña de asignaturas"""
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
        self.table = QTableView()
        self.table.setModel(self.model_manager.get_model("Asignaturas"))
        self.table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        self.table.setSelectionBehavior(QTableView.SelectRows)

        layout.addLayout(form)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def add_asignatura(self):
        """Agrega una nueva asignatura"""
        nombre = self.asig_nombre.text().strip()
        descripcion = self.asig_desc.text().strip()
        
        if not nombre:
            show_error(self, "Por favor ingrese el nombre de la asignatura")
            return

        model = self.model_manager.get_model("Asignaturas")
        row = model.rowCount()
        model.insertRow(row)
        model.setData(model.index(row, 1), nombre)
        model.setData(model.index(row, 2), descripcion)
        
        if not model.submitAll():
            show_error(self, "Error al agregar asignatura")
            model.revertAll()
        else:
            self.asig_nombre.clear()
            self.asig_desc.clear()
            self.model_manager.refresh_model("Asignaturas")

    def delete_asignatura(self):
        """Elimina la asignatura seleccionada"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            show_error(self, "Por favor seleccione una asignatura")
            return

        if confirm_action(self, "¿Está seguro de eliminar esta asignatura?"):
            model = self.model_manager.get_model("Asignaturas")
            for index in indexes:
                if index.column() == 0:  # Solo eliminar una vez por fila
                    model.removeRow(index.row())
            
            if not model.submitAll():
                show_error(self, "Error al eliminar asignatura")
                model.revertAll()
            else:
                self.model_manager.refresh_model("Asignaturas") 