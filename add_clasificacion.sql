-- Script para agregar campos de clasificación y stock fijo

-- Agregar columnas a ingresos_usados
ALTER TABLE ingresos_usados 
ADD COLUMN IF NOT EXISTS clasificacion VARCHAR(20) DEFAULT 'USADOS',
ADD COLUMN IF NOT EXISTS es_stock_fijo BOOLEAN DEFAULT FALSE;

-- Actualizar registros existentes (todos son USADOS por defecto)
UPDATE ingresos_usados 
SET clasificacion = 'USADOS', es_stock_fijo = FALSE
WHERE clasificacion IS NULL;

-- Crear índice para mejorar consultas por clasificación
CREATE INDEX IF NOT EXISTS idx_ingresos_clasificacion ON ingresos_usados(clasificacion);
CREATE INDEX IF NOT EXISTS idx_ingresos_stock_fijo ON ingresos_usados(es_stock_fijo);

-- Comentarios de documentación
COMMENT ON COLUMN ingresos_usados.clasificacion IS 'Tipo de vehículo: KINTO, TEST DRIVE, USADOS';
COMMENT ON COLUMN ingresos_usados.es_stock_fijo IS 'TRUE para KINTO y TEST DRIVE (no se eliminan), FALSE para USADOS (stock variable)';
