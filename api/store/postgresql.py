import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional, Tuple
import logging
from contextlib import contextmanager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLConnector:
    """
    Conector PostgreSQL con funciones básicas para operaciones de base de datos.
    
    Esta clase proporciona métodos para conectar, desconectar y realizar
    operaciones CRUD básicas en una base de datos PostgreSQL.
    """
    
    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432):
        """
        Inicializa el conector PostgreSQL.
        
        Args:
            host (str): Dirección del servidor PostgreSQL
            database (str): Nombre de la base de datos
            user (str): Usuario de la base de datos
            password (str): Contraseña del usuario
            port (int): Puerto del servidor (por defecto 5432)
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        
    def connect(self) -> bool:
        """
        Establece conexión con la base de datos PostgreSQL.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            logger.info(f"Conexión exitosa a PostgreSQL: {self.database}")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error al conectar a PostgreSQL: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Cierra la conexión con la base de datos.
        """
        if self.connection:
            self.connection.close()
            logger.info("Conexión cerrada")
            self.connection = None
    
    def is_connected(self) -> bool:
        """
        Verifica si hay una conexión activa.
        
        Returns:
            bool: True si está conectado, False en caso contrario
        """
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return True
            except psycopg2.Error:
                return False
        return False
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager para obtener un cursor de forma segura.
        
        Yields:
            psycopg2.cursor: Cursor de la base de datos
        """
        if not self.is_connected():
            self.connect()
        
        cursor = None
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            yield cursor
        except psycopg2.Error as e:
            logger.error(f"Error en operación de base de datos: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT y retorna los resultados.
        
        Args:
            query (str): Consulta SQL
            params (Optional[Tuple]): Parámetros para la consulta
            
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los resultados
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]


    def close(self) -> None:
        """
        Cierra la conexión con la base de datos.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_insert(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Ejecuta una consulta INSERT y retorna el ID del registro insertado.
        
        Args:
            query (str): Consulta SQL INSERT
            params (Optional[Tuple]): Parámetros para la consulta
            
        Returns:
            int: ID del registro insertado
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            try:
                result = cursor.fetchone()
                self.connection.commit()
                return result[0] if result else 0
            except Exception as e:
                logger.error(f"Error en execute_insert: {e}")
                self.connection.rollback()
                return 0
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Ejecuta una consulta UPDATE y retorna el número de filas afectadas.
        
        Args:
            query (str): Consulta SQL UPDATE
            params (Optional[Tuple]): Parámetros para la consulta
            
        Returns:
            int: Número de filas afectadas
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
    
    def execute_delete(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Ejecuta una consulta DELETE y retorna el número de filas eliminadas.
        
        Args:
            query (str): Consulta SQL DELETE
            params (Optional[Tuple]): Parámetros para la consulta
            
        Returns:
            int: Número de filas eliminadas
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
    
    def execute_batch_insert(self, query: str, params_list: List[Tuple]) -> int:
        """
        Ejecuta múltiples inserciones en lote.
        
        Args:
            query (str): Consulta SQL INSERT
            params_list (List[Tuple]): Lista de parámetros para cada inserción
            
        Returns:
            int: Número de registros insertados
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            self.connection.commit()
            return cursor.rowcount
    
    def table_exists(self, table_name: str) -> bool:
        """
        Verifica si una tabla existe en la base de datos.
        
        Args:
            table_name (str): Nombre de la tabla
            
        Returns:
            bool: True si la tabla existe, False en caso contrario
        """
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
        """
        result = self.execute_query(query, (table_name,))
        return result[0]['exists'] if result else False
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Obtiene los nombres de las columnas de una tabla.
        
        Args:
            table_name (str): Nombre de la tabla
            
        Returns:
            List[str]: Lista de nombres de columnas
        """
        query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = %s
        ORDER BY ordinal_position;
        """
        result = self.execute_query(query, (table_name,))
        return [row['column_name'] for row in result]
    
    def get_table_count(self, table_name: str) -> int:
        """
        Obtiene el número total de registros en una tabla.
        
        Args:
            table_name (str): Nombre de la tabla
            
        Returns:
            int: Número total de registros
        """
        query = f"SELECT COUNT(*) as count FROM {table_name};"
        result = self.execute_query(query)
        return result[0]['count'] if result else 0
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """
        Crea una nueva tabla con las columnas especificadas.
        
        Args:
            table_name (str): Nombre de la tabla
            columns (Dict[str, str]): Diccionario con nombre_columna: tipo_dato
            
        Returns:
            bool: True si la tabla fue creada exitosamente
        """
        try:
            columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});"
            
            with self.get_cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
            
            logger.info(f"Tabla '{table_name}' creada exitosamente")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error al crear tabla '{table_name}': {e}")
            return False
    
    def drop_table(self, table_name: str) -> bool:
        """
        Elimina una tabla de la base de datos.
        
        Args:
            table_name (str): Nombre de la tabla
            
        Returns:
            bool: True si la tabla fue eliminada exitosamente
        """
        try:
            query = f"DROP TABLE IF EXISTS {table_name};"
            
            with self.get_cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
            
            logger.info(f"Tabla '{table_name}' eliminada exitosamente")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error al eliminar tabla '{table_name}': {e}")
            return False


# Ejemplo de uso
if __name__ == "__main__":
    # Configuración de conexión
    db_config = {
        'host': 'localhost',
        'database': 'vision_analytics',
        'user': 'postgres',
        'password': 'password',
        'port': 5432
    }
