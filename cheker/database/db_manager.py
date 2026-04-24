import sqlite3
import json
from typing import Dict, List, Optional
from utils.logger import Logger

class DatabaseManager:
    """
    Gestor de base de datos local para almacenar resultados y caché.
    """

    def __init__(self, db_path: str = "card_checker.db"):
        self.db_path = db_path
        self.logger = Logger("DatabaseManager")
        self._initialize()

    def _initialize(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Tabla de resultados
                cursor.execute("""
                               CREATE TABLE IF NOT EXISTS results (
                                                                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                      card_number TEXT NOT NULL,
                                                                      card_month TEXT NOT NULL,
                                                                      card_year TEXT NOT NULL,
                                                                      gate TEXT NOT NULL,
                                                                      success BOOLEAN NOT NULL,
                                                                      message TEXT,
                                                                      response_time REAL,
                                                                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                               )
                               """)

                # Tabla de proxies cacheados
                cursor.execute("""
                               CREATE TABLE IF NOT EXISTS proxies (
                                                                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                      proxy TEXT UNIQUE NOT NULL,
                                                                      success_count INTEGER DEFAULT 0,
                                                                      failure_count INTEGER DEFAULT 0,
                                                                      avg_response_time REAL DEFAULT 0,
                                                                      last_used DATETIME,
                                                                      last_checked DATETIME DEFAULT CURRENT_TIMESTAMP
                               )
                               """)

                # Tabla de patrones de BIN
                cursor.execute("""
                               CREATE TABLE IF NOT EXISTS bin_patterns (
                                                                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                           bin TEXT UNIQUE NOT NULL,
                                                                           score REAL DEFAULT 0.5,
                                                                           success_count INTEGER DEFAULT 0,
                                                                           failure_count INTEGER DEFAULT 0,
                                                                           last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                               )
                               """)

                conn.commit()

            self.logger.info("Base de datos inicializada correctamente")

        except Exception as e:
            self.logger.error(f"Error al inicializar la base de datos: {str(e)}")

    def save_result(self, result: Dict):
        """Guarda un resultado de verificación en la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                card = result["card"]
                cursor.execute("""
                               INSERT INTO results (
                                   card_number, card_month, card_year, gate,
                                   success, message, response_time
                               ) VALUES (?, ?, ?, ?, ?, ?, ?)
                               """, (
                                   card["number"], card["month"], card["year"],
                                   result["gate"], result["success"],
                                   result.get("message", ""), result["response_time"]
                               ))

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error al guardar resultado: {str(e)}")

    def get_results(self, limit: int = 100) -> List[Dict]:
        """Obtiene resultados de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                               SELECT * FROM results
                               ORDER BY timestamp DESC
                                   LIMIT ?
                               """, (limit,))

                results = []
                for row in cursor.fetchall():
                    results.append(dict(row))

                return results

        except Exception as e:
            self.logger.error(f"Error al obtener resultados: {str(e)}")
            return []

    def save_proxy(self, proxy: str, success_count: int, failure_count: int, avg_response_time: float):
        """Guarda o actualiza un proxy en la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Verificar si el proxy ya existe
                cursor.execute("SELECT id FROM proxies WHERE proxy = ?", (proxy,))
                existing = cursor.fetchone()

                if existing:
                    # Actualizar proxy existente
                    cursor.execute("""
                                   UPDATE proxies SET
                                                      success_count = ?, failure_count = ?, avg_response_time = ?,
                                                      last_checked = CURRENT_TIMESTAMP
                                   WHERE proxy = ?
                                   """, (success_count, failure_count, avg_response_time, proxy))
                else:
                    # Insertar nuevo proxy
                    cursor.execute("""
                                   INSERT INTO proxies (
                                       proxy, success_count, failure_count, avg_response_time
                                   ) VALUES (?, ?, ?, ?)
                                   """, (proxy, success_count, failure_count, avg_response_time))

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error al guardar proxy: {str(e)}")

    def get_proxies(self, limit: int = 1000) -> List[Dict]:
        """Obtiene proxies de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                               SELECT * FROM proxies
                               ORDER BY success_count / (success_count + failure_count + 1) DESC
                                   LIMIT ?
                               """, (limit,))

                proxies = []
                for row in cursor.fetchall():
                    proxies.append(dict(row))

                return proxies

        except Exception as e:
            self.logger.error(f"Error al obtener proxies: {str(e)}")
            return []

    def update_bin_pattern(self, bin: str, success: bool):
        """Actualiza el patrón de un BIN"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Verificar si el BIN ya existe
                cursor.execute("SELECT id, success_count, failure_count FROM bin_patterns WHERE bin = ?", (bin,))
                existing = cursor.fetchone()

                if existing:
                    id_, success_count, failure_count = existing

                    # Actualizar contadores
                    if success:
                        success_count += 1
                    else:
                        failure_count += 1

                    # Calcular nueva puntuación
                    total = success_count + failure_count
                    score = success_count / max(1, total)

                    # Actualizar BIN existente
                    cursor.execute("""
                                   UPDATE bin_patterns SET
                                                           success_count = ?, failure_count = ?, score = ?,
                                                           last_updated = CURRENT_TIMESTAMP
                                   WHERE id = ?
                                   """, (success_count, failure_count, score, id_))
                else:
                    # Insertar nuevo BIN
                    score = 1.0 if success else 0.0
                    success_count = 1 if success else 0
                    failure_count = 0 if success else 1

                    cursor.execute("""
                                   INSERT INTO bin_patterns (
                                       bin, score, success_count, failure_count
                                   ) VALUES (?, ?, ?, ?)
                                   """, (bin, score, success_count, failure_count))

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error al actualizar patrón de BIN: {str(e)}")

    def get_bin_pattern(self, bin: str) -> Optional[Dict]:
        """Obtiene el patrón de un BIN"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                               SELECT * FROM bin_patterns WHERE bin = ?
                               """, (bin,))

                row = cursor.fetchone()
                return dict(row) if row else None

        except Exception as e:
            self.logger.error(f"Error al obtener patrón de BIN: {str(e)}")
            return None