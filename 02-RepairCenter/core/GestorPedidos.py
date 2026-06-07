from core.BaseDatos import BaseDatos

class GestorPedidos:
    def __init__(self, db: BaseDatos):
        # Inyección de la dependencia de base de datos.
        self.db = db

    def registrar_pedido(self, nombre: str, apellido: str, calle: str, altura: str, inconveniente: str, tecnico: str, fecha_hora: str) -> tuple[bool, str]:
        # Patrón Fail-Fast: Se aborta la ejecución inmediatamente si faltan campos críticos.
        # Retornamos una tupla (Booleano de éxito, Mensaje de feedback para la UI).
        if not all([nombre.strip(), apellido.strip(), calle.strip(), altura.strip(), inconveniente.strip()]):
            return False, "Faltan completar campos obligatorios del cliente o el inconveniente."

        # Validación de dominio: La altura es un atributo matemático, debe ser casteable a entero.
        try:
            altura_int = int(altura)
            if altura_int <= 0:
                return False, "La altura del domicilio debe ser mayor a 0."
        except ValueError:
            return False, "La altura del domicilio debe contener solo números."

        # Sanitización y asignación de valores por defecto lógicos para datos no estrictos.
        # Si no se asigna técnico o fecha al crear el ticket, no bloqueamos la inserción,
        # pero dejamos constancia del estado.
        tecnico_final = tecnico.strip() if tecnico.strip() else "Sin asignar"
        fecha_final = fecha_hora.strip() if fecha_hora.strip() else "Sin agendar"

        query = '''
            INSERT INTO pedidos 
            (nombre, apellido, calle, altura, inconveniente, tecnico, fecha_hora_visita, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendiente')
        '''
        parametros = (nombre.strip(), apellido.strip(), calle.strip(), altura_int, inconveniente.strip(), tecnico_final, fecha_final)

        # Delegamos la persistencia física a la capa de datos.
        exito = self.db.ejecutar_escritura(query, parametros)

        if exito:
            return True, "Pedido registrado exitosamente."
        else:
            return False, "Error interno al guardar en la base de datos. Verifique los logs."

    def obtener_todos_los_pedidos(self) -> list:
        # Método de lectura expuesto para que la UI pueda poblar una grilla (Treeview)
        # y visualizar el estado actual del Repair Center.
        query = "SELECT id_ticket, nombre, apellido, inconveniente, tecnico, fecha_hora_visita, estado FROM pedidos"
        return self.db.ejecutar_lectura(query)