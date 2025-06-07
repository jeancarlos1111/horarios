from PyQt5.QtSql import QSqlTableModel

class ModelManager:
    def __init__(self, db):
        self.db = db
        self.modelos = {}

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

    def get_model(self, table_name):
        """Retorna el modelo para una tabla específica"""
        return self.modelos.get(table_name)

    def refresh_all(self):
        """Actualiza todos los modelos"""
        for modelo in self.modelos.values():
            modelo.select()

    def refresh_model(self, table_name):
        """Actualiza un modelo específico"""
        if table_name in self.modelos:
            self.modelos[table_name].select() 