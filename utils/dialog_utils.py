from PyQt5.QtWidgets import QMessageBox

def show_error(parent, message):
    """Muestra un mensaje de error"""
    QMessageBox.critical(parent, "Error", message)

def show_warning(parent, message):
    """Muestra un mensaje de advertencia"""
    QMessageBox.warning(parent, "Advertencia", message)

def confirm_action(parent, message):
    """Muestra un diálogo de confirmación"""
    return QMessageBox.question(parent, "Confirmar", message) == QMessageBox.Yes 