# Funciones Disponibles en PostgreSQLConnector

## Funciones de Conexión
- `__init__(host, database, user, password, port=5432)` - Inicializa el conector
- `connect()` - Establece conexión con PostgreSQL (retorna bool)
- `disconnect()` - Cierra la conexión
- `is_connected()` - Verifica si hay conexión activa (retorna bool)
- `close()` - Cierra la conexión (alias de disconnect)

## Funciones de Cursor
- `get_cursor()` - Obtiene un cursor con context manager

## Funciones de Consulta (SELECT)
- `execute_query(query, params=None)` - Ejecuta consultas SELECT (retorna List[Dict])

## Funciones de Inserción (INSERT)
- `execute_insert(query, params=None)` - Ejecuta INSERT y retorna ID del registro insertado (retorna int)
- `execute_batch_insert(query, params_list)` - Ejecuta múltiples INSERT en lote (retorna int - número de registros insertados)

## Funciones de Actualización (UPDATE)
- `execute_update(query, params=None)` - Ejecuta UPDATE (retorna int - número de filas afectadas)

## Funciones de Eliminación (DELETE)
- `execute_delete(query, params=None)` - Ejecuta DELETE (retorna int - número de filas eliminadas)

## Funciones de Metadatos
- `table_exists(table_name)` - Verifica si una tabla existe (retorna bool)
- `get_table_columns(table_name)` - Obtiene columnas de una tabla (retorna List[str])
- `get_table_count(table_name)` - Obtiene número de registros en una tabla (retorna int)

## Funciones de Estructura
- `create_table(table_name, columns)` - Crea una nueva tabla (retorna bool)
- `drop_table(table_name)` - Elimina una tabla (retorna bool)

## Uso Recomendado

### Para Consultas (SELECT):
```python
connection = db(host, database, user, password, port)
if connection.connect():
    result = connection.execute_query("SELECT * FROM table WHERE id = %s", (id,))
    connection.close()
```

### Para Inserciones (INSERT):
```python
# Inserción individual
connection = db(host, database, user, password, port)
if connection.connect():
    inserted_id = connection.execute_insert(
        "INSERT INTO table (col1, col2) VALUES (%s, %s) RETURNING id", 
        (value1, value2)
    )
    connection.close()

# Inserción múltiple
connection = db(host, database, user, password, port)
if connection.connect():
    params_list = [(val1, val2), (val3, val4), (val5, val6)]
    count = connection.execute_batch_insert(
        "INSERT INTO table (col1, col2) VALUES (%s, %s)", 
        params_list
    )
    connection.close()
```

### Para Actualizaciones (UPDATE):
```python
connection = db(host, database, user, password, port)
if connection.connect():
    affected_rows = connection.execute_update(
        "UPDATE table SET col1 = %s WHERE id = %s", 
        (new_value, id)
    )
    connection.close()
```

### Para Eliminaciones (DELETE):
```python
connection = db(host, database, user, password, port)
if connection.connect():
    deleted_rows = connection.execute_delete(
        "DELETE FROM table WHERE id = %s", 
        (id,)
    )
    connection.close()
```

## Notas Importantes
- Siempre cerrar la conexión con `connection.close()` después de usar
- Usar `execute_insert` para INSERT con RETURNING
- Usar `execute_batch_insert` para múltiples inserciones (más eficiente)
- Los parámetros deben ser tuplas para consultas con parámetros
- Para batch insert, params_list debe ser List[Tuple]
