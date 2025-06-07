from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QMessageBox

class DatabaseManager:
    def __init__(self, db_name='horarios.db'):
        self.db_name = db_name
        self.db = None

    def init_db(self):
        """Inicializa y configura la base de datos SQLite"""
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.db_name)
        
        if not self.db.open():
            QMessageBox.critical(None, "Error", "No se puede conectar a la base de datos")
            return False

        self._create_tables()
        self._init_dias_semana()
        return True

    def _create_tables(self):
        """Crea las tablas necesarias si no existen"""
        query = QSqlQuery(self.db)
        
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

    def _init_dias_semana(self):
        """Inicializa los días de la semana si no existen"""
        query = QSqlQuery(self.db)
        query.exec_("SELECT COUNT(*) FROM DiasSemana")
        if query.next() and query.value(0) == 0:
            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
            for dia in dias:
                query.exec_(f"INSERT INTO DiasSemana (nombre) VALUES ('{dia}')")

    def get_connection(self):
        """Retorna la conexión a la base de datos"""
        return self.db

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.db:
            self.db.close() 