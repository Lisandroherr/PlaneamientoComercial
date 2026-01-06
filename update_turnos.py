#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Actualizar turnos de lavadero hasta 20:00"""

import psycopg2
from db_config import get_db_connection

conn = get_db_connection()
cur = conn.cursor()
cur.execute("UPDATE turnos_lavadero SET hora_fin = '20:00' WHERE activo = TRUE")
conn.commit()
print('✅ Turnos actualizados hasta 20:00')
cur.close()
conn.close()
