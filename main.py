import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from database.db_manager import DatabaseManager
from models.model_manager import ModelManager
from ui.tabs.profesores_tab import ProfesoresTab
from ui.tabs.asignaturas_tab import AsignaturasTab
from ui.tabs.grupos_tab import GruposTab
from ui.tabs.aulas_tab import AulasTab
from ui.tabs.horarios_tab import HorariosTab

class HorarioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Horarios")
        self.setGeometry(100, 100, 800, 600)
        
        # Inicializar la base de datos
        self.db_manager = DatabaseManager()
        if not self.db_manager.init_db():
            sys.exit(1)
        
        # Inicializar los modelos
        self.model_manager = ModelManager(self.db_manager.get_connection())
        self.model_manager.create_models()
        
        # Configurar la interfaz
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz gráfica"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Crear las pestañas
        self.create_tabs()

    def create_tabs(self):
        """Crea todas las pestañas de la aplicación"""
        # Pestaña de Profesores
        self.tabs.addTab(ProfesoresTab(self.model_manager, self.db_manager.get_connection()), "Profesores")
        
        # Agregar las demás pestañas
        self.tabs.addTab(AsignaturasTab(self.model_manager, self.db_manager.get_connection()), "Asignaturas")
        self.tabs.addTab(GruposTab(self.model_manager, self.db_manager.get_connection()), "Secciones")
        self.tabs.addTab(AulasTab(self.model_manager, self.db_manager.get_connection()), "Aulas")
        self.tabs.addTab(HorariosTab(self.model_manager, self.db_manager.get_connection()), "Horarios")

    def closeEvent(self, event):
        """Maneja el evento de cierre de la aplicación"""
        self.db_manager.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = HorarioApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()