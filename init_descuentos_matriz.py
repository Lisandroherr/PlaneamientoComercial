"""
Script para crear la tabla de descuentos por matriz (fecha/ubicación)
"""
from db_config import get_db_connection

def crear_tabla_descuentos_matriz():
    """Crear tabla de descuentos por modelo, fecha de despacho y ubicación"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Crear tabla de descuentos por matriz
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS descuentos_matriz (
                id SERIAL PRIMARY KEY,
                modelo VARCHAR(255) NOT NULL UNIQUE,
                
                -- Descuentos por Fecha de Despacho (%)
                desc_mes_actual_menos_2 DECIMAL(5,2) DEFAULT 0,
                desc_mes_actual_menos_1 DECIMAL(5,2) DEFAULT 0,
                desc_mes_actual DECIMAL(5,2) DEFAULT 0,
                desc_mes_actual_mas DECIMAL(5,2) DEFAULT 0,
                
                -- Descuentos por Ubicación (%)
                desc_stock DECIMAL(5,2) DEFAULT 0,
                desc_produccion DECIMAL(5,2) DEFAULT 0,
                desc_playa_externa DECIMAL(5,2) DEFAULT 0,
                desc_otro DECIMAL(5,2) DEFAULT 0,
                
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("✅ Tabla 'descuentos_matriz' creada exitosamente")
        
        # Insertar registros para todos los modelos
        modelos = [
            "COROLLA 2.0 SEG CVT",
            "COROLLA 2.0 XEI SAFETY CVT",
            "COROLLA 2.0 XLI CVT",
            "COROLLA 2.0 XLI SAFETY CVT",
            "COROLLA CROSS GR-SPORT SAFETY 2.0 CVT",
            "COROLLA CROSS HEV 1.8 SEG ECVT",
            "COROLLA CROSS SEG HEV SAFETY 1.8 ECVT",
            "COROLLA CROSS SEG SAFETY 2.0 CVT",
            "COROLLA CROSS XEI HEV 1.8 ECVT",
            "COROLLA CROSS XEI HEV SAFETY 1.8 ECVT",
            "COROLLA CROSS XEI SAFETY 2.0 CVT",
            "COROLLA CROSS XLI SAFETY 2.0 CVT",
            "COROLLA HEV 1.8 XEI ECVT",
            "COROLLA HEV 1.8 XEI SAFETY eCVT",
            "ETIOS XLS PACK 1.5 4A/T 4P",
            "GR SUPRA",
            "GR YARIS",
            "HIACE FURGON L1H1 2.8 TDI 6AT 3A 4P",
            "HIACE FURGON L2H2 2.8 TDI 6 AT 3A 5P",
            "HIACE WAGON 2.8 TDI 6AT 10A",
            "HILUX 4X2 C/S DX 2.4 TDI 6 M/T",
            "HILUX 4X2 CC DX 2.4 TDI 6 M/T",
            "HILUX 4X2 D/C DX 2.4 TDI 6 A/T",
            "HILUX 4X2 D/C DX 2.4 TDI 6 M/T",
            "HILUX 4X2 D/C SR 2.4 TDI 6 A/T",
            "HILUX 4X2 D/C SR 2.4 TDI 6 M/T",
            "HILUX 4X2 D/C SRV 2.8 TDI 6 A/T",
            "HILUX 4X2 D/C SRX 2.8 TDI 6A/T",
            "HILUX 4X4 C/S DX 2.4 TDI 6M/T",
            "HILUX 4X4 CC DX 2.4 TDI 6 M/T",
            "HILUX 4X4 D/C DX 2.4 TDI 6 A/T",
            "HILUX 4X4 D/C DX 2.4 TDI 6M/T",
            "HILUX 4X4 D/C SR 2.8 TDI 6A/T",
            "HILUX 4X4 D/C SR 2.8 TDI 6MT",
            "HILUX 4X4 D/C SRV 2.8 TDI 6A/T",
            "HILUX 4X4 D/C SRV 2.8 TDI 6M/T",
            "HILUX 4X4 D/C SRX 2.8 TDI 6A/T",
            "HILUX 4X4 DC GR-SPORT IV 2.8 TDI 6 AT",
            "HILUX 4X4 DC SRV+ 2.8 TDI 6 AT",
            "LAND CRUISER 200 VX",
            "LAND CRUISER 300 VX",
            "LAND CRUISER PRADO VX A/T",
            "RAV 4 HEV 2.5 AWD Limited CVT",
            "SW4 4X4 DIAMOND 2.8 TDI 6 A/T 7A",
            "SW4 4X4 GR-S TDI 6AT 7A",
            "SW4 4X4 SRX 2.8 TDI 6 A/T 7A",
            "YARIS S 1.5 CVT 5P",
            "YARIS XLS 1.5 CVT 5P",
            "YARIS XLS PACK 1.5 CVT 4P",
            "YARIS XLS+ 1.5 CVT 5P",
            "YARIS XS 1.5 6M/T 5P",
            "YARIS XS 1.5 CVT 5P",
            "SC - COROLLA 2.0 SEG SAFETY CVT",
            "SC - COROLLA GR-SPORT SAFETY 2.0 CVT",
            "SC - COROLLA HEV 1.8 SEG SAFETY eCVT",
            "SC - HILUX 4X2 D/C SR 2.4 TDI 6 M/T",
            "SC - HILUX 4X2 D/C SR 2.4 TDI 6A/T",
            "SC - HILUX 4X2 D/C SRV 2.8 TDI 6A/T",
            "SC - HILUX 4X2 D/C SRX 2.8 TDI 6A/T",
            "SC - HILUX 4X4 D/C SR 2.8 TDI 6A/T",
            "SC - HILUX 4X4 D/C SR 2.8 TDI 6MT",
            "SC - HILUX 4X4 D/C SRV 2.8 TDI 6A/T",
            "SC - HILUX 4X4 D/C SRX 2.8 TDI 6A/T",
            "SC - HILUX D/C GR-S SPORT IV 2.8 TDI 6AT",
            "SC - SW4 4X4 DIAMOND 2.8 TDI 6 A/T 7A",
            "SC - SW4 4X4 GR-S TDI 6AT 7A",
            "SC - SW4 4X4 SRX 2.8 TDI 6A/T 7A"
        ]
        
        insertados = 0
        for modelo in modelos:
            try:
                cursor.execute('''
                    INSERT INTO descuentos_matriz (modelo)
                    VALUES (%s)
                    ON CONFLICT (modelo) DO NOTHING
                ''', (modelo,))
                if cursor.rowcount > 0:
                    insertados += 1
            except Exception as e:
                print(f"⚠️  Error insertando {modelo}: {e}")
        
        conn.commit()
        print(f"✅ {insertados} modelos insertados en 'descuentos_matriz'")
        
        # Mostrar resumen
        cursor.execute('SELECT COUNT(*) FROM descuentos_matriz')
        total = dict(cursor.fetchone())['count']
        print(f"📊 Total de modelos en tabla: {total}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("="*60)
    print("INICIALIZACIÓN DE TABLA DE DESCUENTOS POR MATRIZ")
    print("="*60)
    crear_tabla_descuentos_matriz()
    print("="*60)
    print("✅ Proceso completado")
