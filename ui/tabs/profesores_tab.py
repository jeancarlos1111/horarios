from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableView, QMessageBox)
from PyQt5.QtCore import Qt

class ProfesoresTab(QWidget):
    def __init__(self, model_manager, db):
        super().__init__()
        self.model_manager = model_manager
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de la pestaña de profesores"""
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
        self.table = QTableView()
        self.table.setModel(self.model_manager.get_model("Profesores"))
        self.table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        self.table.setSelectionBehavior(QTableView.SelectRows)

        layout.addLayout(form)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def add_profesor(self):
        """Agrega un nuevo profesor"""
        nombre = self.prof_nombre.text().strip()
        apellido = self.prof_apellido.text().strip()
        
        if not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return

        model = self.model_manager.get_model("Profesores")
        row = model.rowCount()
        model.insertRow(row)
        model.setData(model.index(row, 1), nombre)
        model.setData(model.index(row, 2), apellido)
        
        if not model.submitAll():
            QMessageBox.critical(self, "Error", "Error al agregar profesor")
            model.revertAll()
        else:
            self.prof_nombre.clear()
            self.prof_apellido.clear()
            self.model_manager.refresh_model("Profesores")

    def delete_profesor(self):
        """Elimina el profesor seleccionado"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            QMessageBox.warning(self, "Error", "Por favor seleccione un profesor")
            return

        if QMessageBox.question(self, "Confirmar", "¿Está seguro de eliminar este profesor?") == QMessageBox.Yes:
            model = self.model_manager.get_model("Profesores")
            for index in indexes:
                if index.column() == 0:  # Solo eliminar una vez por fila
                    model.removeRow(index.row())
            
            if not model.submitAll():
                QMessageBox.critical(self, "Error", "Error al eliminar profesor")
                model.revertAll()
            else:
                self.model_manager.refresh_model("Profesores") 