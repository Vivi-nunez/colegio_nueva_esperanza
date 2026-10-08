import re
from datetime import date
from typing import Optional

from dao.conexion import ConexionBD


class CobroMensualDAO:
    """Registra cargos mensuales y mantiene el historial de pagos y saldos."""

    @staticmethod
    def emitir(rut_estudiante: str, periodo: str, arancel_uf: float, valor_uf: float) -> Optional[int]:
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", periodo):
            raise ValueError("El período debe tener formato AAAA-MM.")
        if arancel_uf <= 0 or valor_uf <= 0:
            raise ValueError("El arancel y el valor de UF deben ser positivos.")

        total_pesos = round(arancel_uf * valor_uf)
        sql = """
        INSERT INTO cobro_mensual (
            rut_estudiante, periodo, arancel_uf, valor_uf, total_pesos, fecha_emision
        ) VALUES (?, ?, ?, ?, ?, ?);
        """
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.execute(
                    sql,
                    (rut_estudiante.strip().upper(), periodo, arancel_uf, valor_uf, total_pesos, date.today().isoformat()),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as error:
            print(f"[CobroMensualDAO] No se pudo emitir el cobro: {error}")
            return None

    @staticmethod
    def registrar_pago(
        id_cobro: int,
        monto_pesos: int,
        observacion: str = "",
        fecha_pago: Optional[str] = None,
    ) -> bool:
        if monto_pesos <= 0:
            return False

        try:
            with ConexionBD.obtener_conexion() as conn:
                conn.execute("BEGIN IMMEDIATE;")
                cobro = conn.execute(
                    "SELECT total_pesos FROM cobro_mensual WHERE id_cobro = ?;", (id_cobro,)
                ).fetchone()
                if cobro is None:
                    return False
                pagado = conn.execute(
                    "SELECT COALESCE(SUM(monto_pesos), 0) FROM pago_mensual WHERE id_cobro = ?;", (id_cobro,)
                ).fetchone()[0]
                saldo = cobro["total_pesos"] - pagado
                if monto_pesos > saldo:
                    return False
                conn.execute(
                    "INSERT INTO pago_mensual (id_cobro, monto_pesos, fecha_pago, observacion) VALUES (?, ?, ?, ?);",
                    (id_cobro, monto_pesos, fecha_pago or date.today().isoformat(), observacion.strip()),
                )
                conn.commit()
                return True
        except Exception as error:
            print(f"[CobroMensualDAO] No se pudo registrar el pago: {error}")
            return False

    @staticmethod
    def listar_por_estudiante(rut_estudiante: str) -> list[dict]:
        sql = """
        SELECT c.id_cobro, c.rut_estudiante, c.periodo, c.arancel_uf,
               c.valor_uf, c.total_pesos, c.fecha_emision,
               COALESCE(SUM(p.monto_pesos), 0) AS pagado
        FROM cobro_mensual c
        LEFT JOIN pago_mensual p ON p.id_cobro = c.id_cobro
        WHERE c.rut_estudiante = ?
        GROUP BY c.id_cobro
        ORDER BY c.periodo, c.id_cobro;
        """
        with ConexionBD.obtener_conexion() as conn:
            rows = conn.execute(sql, (rut_estudiante.strip().upper(),)).fetchall()

        resultado = []
        for row in rows:
            cobro = dict(row)
            cobro["saldo"] = cobro["total_pesos"] - cobro["pagado"]
            if cobro["saldo"] == 0:
                cobro["estado"] = "Pagado"
            elif cobro["pagado"] > 0:
                cobro["estado"] = "Abono parcial"
            else:
                cobro["estado"] = "Pendiente"
            resultado.append(cobro)
        return resultado

    @staticmethod
    def tiene_deuda_del_anio_anterior(rut_estudiante: str, anio_matricula: int) -> bool:
        anio_anterior = str(anio_matricula - 1)
        cobros = CobroMensualDAO.listar_por_estudiante(rut_estudiante)
        return any(cobro["periodo"].startswith(f"{anio_anterior}-") and cobro["saldo"] > 0 for cobro in cobros)