// Módulo 5: Procesador SIAC e INTEGRA - VERSIÓN CORREGIDA

let siacData = null;
let integraData = null;
let processedData = null;

// Base de datos de Ejecutivos de Venta (editable)
let EJECUTIVOS_MAP = {
    'ARROYO, JAVIER': 'NACHO',
    'BONTORNO, MARCELO': 'ALDI',
    'BRUNO DAMELIO': 'JUANMA',
    'CHIRINO, RAUL': 'FACU',
    'DIEGO DALPRA': 'SR.',
    'F01': 'ALDI',
    'Fernanda Lucero': 'NACHO',
    'GABRIEL, PABLO': 'CHOCO',
    'GALLEGO, NADIA': 'SR.',
    'GARAY, LUIS': 'SM.',
    'GARCIA, LAUTARO FEDERICO': 'SR.',
    'GERENCIA': 'NACHO',
    'GRIFFOULIERE, PABLO': 'FACU',
    'HERNAN DASMI': 'NACHO',
    'Iván Riveros': 'NACHO',
    'JOSE, RODRIGO': 'JUANMA',
    'KINTO': 'ALDI',
    'KINTO - ALQUILER DE VEHICULOS': 'ALDI',
    'LIMA, MARCELO': 'SM.',
    'MONSERRAT, JUAN JOSE': 'FACU',
    'QUIROGA, LUIS': 'CHOCO',
    'SORGONI, ENZO': 'SR.',
    'TAPIA, NICOLÁS': 'FACU',
    'TEST DRIVE': 'ALDI',
    'TOCCHETTO BRUNO': 'FACU',
    'TORRES, GERARDO': 'JUANMA',
    'ULLOA, JONATHAN': 'SR.',
    'ZAWELS, FEDERICO': 'NACHO'
};

// Cargar mapa desde localStorage al iniciar
function cargarEjecutivosMap() {
    const saved = localStorage.getItem('EJECUTIVOS_MAP');
    if (saved) {
        try {
            EJECUTIVOS_MAP = JSON.parse(saved);
        } catch (e) {
            console.error('Error cargando mapa de ejecutivos:', e);
        }
    }
}

// Guardar mapa en localStorage
function guardarEjecutivosMap() {
    localStorage.setItem('EJECUTIVOS_MAP', JSON.stringify(EJECUTIVOS_MAP));
}

// Encabezados procesados (39 columnas finales)
const SIAC_HEADERS_PROCESSED = [
    'N° Fábrica', 'N° Chasis', 'Modelo/Versión', 'Color', 'Color 2', 
    'Hab. Financiera', 'Fecha Est. Despacho', 'Est. Entrega', 'Fecha Recepción', 'Ubicación Unidad', 
    'Cód. Cliente', 'Cliente', 'Vendedor', 'Operación', 'Ejecutivo', 
    'Estado Operación', 'Estado Seguimiento Op.', 'Ubicación Carpeta', 'Teléfono', 'E-mail', 
    'Mdto. Vta.', 'Fec. Carga', 'Fec. Asig. Op.', 'Días Asignación', 'Días Stock', 
    'Precio Venta Total', 'Total Seña', 'Usa.Pte.Pgo', 'Créd. Bco.', 'Efectivo Pendiente', 
    'Clase', 'Factura', 'Fecha Venta', 'Observaciones', 'Estado S.F.', 
    'Fecha Entrega S.F.', 'Seguimiento Crédito', 'Banco del Crédito', 'Prob. Entrega'
];

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    cargarEjecutivosMap();
    initializeDropZones();
    initializeTabs();
    setupEventListeners();
    cargarConfiguracionSilenciosa(); // Cargar configuración silenciosa al inicio (para cálculos)
});

function setupEventListeners() {
    document.getElementById('btnProcesar').addEventListener('click', procesarArchivos);
    document.getElementById('btnDescargar').addEventListener('click', descargarResultado);
    document.getElementById('btnLimpiar').addEventListener('click', limpiarTodo);
}

function initializeDropZones() {
    setupDropZone('dropZoneSIAC', 'fileSIAC', handleSIACFile);
    setupDropZone('dropZoneINTEGRA', 'fileINTEGRA', handleINTEGRAFile);
}

function setupDropZone(dropZoneId, inputId, handler) {
    const dropZone = document.getElementById(dropZoneId);
    const fileInput = document.getElementById(inputId);
    
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file) handler(file);
    });
    
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handler(file);
    });
}

async function handleSIACFile(file) {
    showAlert('Cargando archivo SIAC...', 'info');
    
    try {
        const data = await readExcelFile(file);
        siacData = { filename: file.name, data: data, rows: data.length };
        
        document.getElementById('siacStatus').style.display = 'block';
        document.getElementById('siacFileName').textContent = file.name;
        document.getElementById('siacInfo').textContent = `${data.length} filas cargadas`;
        
        showAlert('Archivo SIAC cargado correctamente', 'success');
        checkReadyToProcess();
    } catch (error) {
        showAlert('Error al cargar archivo SIAC: ' + error.message, 'error');
    }
}

async function handleINTEGRAFile(file) {
    showAlert('Cargando archivo INTEGRA...', 'info');
    
    try {
        const data = await readExcelFile(file);
        integraData = { filename: file.name, data: data, rows: data.length };
        
        // Debug: Mostrar estructura del archivo INTEGRA
        console.log('📊 Archivo INTEGRA cargado:');
        console.log('- Total filas:', data.length);
        console.log('- Encabezados:', data[0]);
        console.log('- Primera fila de datos:', data[1]);
        console.log('- Segunda fila de datos:', data[2]);
        console.log('- Tercera fila de datos:', data[3]);
        console.log('- Número de columnas:', data[0] ? data[0].length : 0);
        
        // Verificar las primeras 10 operaciones de INTEGRA (normalizadas)
        console.log('🔢 Primeras 10 operaciones en INTEGRA (normalizadas):');
        for (let i = 1; i <= Math.min(10, data.length - 1); i++) {
            const operacOriginal = data[i][0];
            const operacNormalizada = String(operacOriginal || '').trim().replace(/\./g, '').replace(/\s/g, '');
            console.log(`   ${i}. Original: "${operacOriginal}" → Normalizada: "${operacNormalizada}"`);
        }
        
        // Función auxiliar para buscar una operación específica
        window.buscarEnINTEGRA = function(operacion) {
            const operacionStr = String(operacion).trim().replace(/\./g, '').replace(/\s/g, '');
            const operacionNum = parseInt(operacionStr, 10);
            console.log('🔍 Buscando manualmente:', operacion, '→ String:', operacionStr, '→ Número:', operacionNum);
            
            for (let i = 1; i < integraData.data.length; i++) {
                const operacINTEGRAraw = integraData.data[i][0];
                const operacINTEGRAstr = String(operacINTEGRAraw || '').trim().replace(/\./g, '').replace(/\s/g, '');
                const operacINTEGRAnum = parseInt(operacINTEGRAstr, 10);
                
                if (operacINTEGRAnum === operacionNum) {
                    console.log('✅ Encontrada en fila', i, ':', integraData.data[i]);
                    console.log('   - Operac (raw):', operacINTEGRAraw, '(tipo:', typeof operacINTEGRAraw + ')');
                    console.log('   - Operac (num):', operacINTEGRAnum);
                    console.log('   - Ubicación:', integraData.data[i][1]);
                    return;
                }
            }
            console.log('❌ No encontrada');
        };
        console.log('💡 Tip: Usa buscarEnINTEGRA("66539") o buscarEnINTEGRA("66.539") en la consola');
        
        document.getElementById('integraStatus').style.display = 'block';
        document.getElementById('integraFileName').textContent = file.name;
        document.getElementById('integraInfo').textContent = `${data.length} filas cargadas (${data[0] ? data[0].length : 0} columnas)`;
        
        showAlert('Archivo INTEGRA cargado correctamente', 'success');
        checkReadyToProcess();
    } catch (error) {
        showAlert('Error al cargar archivo INTEGRA: ' + error.message, 'error');
    }
}

function readExcelFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            try {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array', cellDates: true });
                const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                const jsonData = XLSX.utils.sheet_to_json(firstSheet, { 
                    header: 1, 
                    defval: '',
                    raw: false,
                    dateNF: 'dd/mm/yyyy'
                });
                resolve(jsonData);
            } catch (error) {
                reject(error);
            }
        };
        
        reader.onerror = () => reject(new Error('Error al leer el archivo'));
        reader.readAsArrayBuffer(file);
    });
}

function checkReadyToProcess() {
    const btnProcesar = document.getElementById('btnProcesar');
    if (siacData && integraData) {
        btnProcesar.disabled = false;
        btnProcesar.style.opacity = '1';
    }
}

async function procesarArchivos() {
    if (!siacData || !integraData) {
        showAlert('Debes cargar ambos archivos antes de procesar', 'error');
        return;
    }
    
    showSpinner(true);
    document.getElementById('btnProcesar').disabled = true;
    
    try {
        showAlert('Iniciando procesamiento...', 'info');
        
        let cleanedData = limpiarDatos(siacData.data);
        console.log('Paso 1 - Limpieza:', cleanedData.length, 'filas');
        
        let mappedData = mapearColumnas(cleanedData);
        console.log('Paso 2 - Mapeo:', mappedData.length, 'filas');
        
        mappedData = ordenarPorOperacion(mappedData);
        console.log('Paso 3 - Ordenamiento completado');
        
        processedData = await procesarFilas(mappedData);
        console.log('Paso 4 - Procesamiento:', processedData.length, 'filas');
        
        await mostrarResultados();
        
        showSpinner(false);
        document.getElementById('btnDescargar').style.display = 'inline-block';
        showAlert('Procesamiento completado exitosamente', 'success');
        
    } catch (error) {
        showSpinner(false);
        showAlert('Error en el procesamiento: ' + error.message, 'error');
        console.error('Error detallado:', error);
    }
}

function limpiarDatos(data) {
    let cleaned = data.slice(8);
    cleaned = cleaned.filter(row => row.some(cell => cell !== '' && cell !== null && cell !== undefined));
    console.log(`Limpieza: ${data.length} filas → ${cleaned.length} filas`);
    return cleaned;
}

function limpiarNumero(valor) {
    if (!valor) return '';
    // Convertir a string y limpiar formato de puntos/comas
    let str = String(valor).trim();
    // Remover puntos de miles y reemplazar coma decimal por punto
    str = str.replace(/\./g, '').replace(',', '.');
    // Convertir a número
    const num = parseFloat(str);
    // Retornar como número o string vacío si no es válido
    return isNaN(num) ? '' : num;
}

function mapearColumnas(data) {
    const header = data[0];
    const rows = data.slice(1);
    
    const colIndex = {};
    header.forEach((col, idx) => { colIndex[col] = idx; });
    
    const mappedRows = rows.map(row => {
        const m = new Array(39).fill('');
        m[0] = row[colIndex['Nº Fábrica']] || '';
        m[1] = row[colIndex['Nº Chasis']] || '';
        m[2] = row[colIndex['Modelo / Versión Extendida']] || '';
        m[3] = row[colIndex['Color']] || '';
        m[4] = row[colIndex['Color 2']] || '';
        m[5] = '';
        m[6] = row[colIndex['Estim Despacho']] || '';
        m[7] = '';
        m[8] = row[colIndex['Fec.Recep.']] || '';
        m[9] = row[colIndex['Ubicación']] || '';
        m[10] = row[colIndex['Cód. Cliente']] || '';
        m[11] = row[colIndex['Cliente']] || '';
        m[12] = row[colIndex['Vendedor']] || '';
        m[13] = row[colIndex['Operación']] || '';
        m[14] = '';
        m[15] = '';
        m[16] = '';
        m[17] = '';
        m[18] = row[colIndex['Teléfono']] || '';
        m[19] = row[colIndex['E-mail']] || '';
        m[20] = limpiarNumero(row[colIndex['Mdto.Vta.']]);
        m[21] = row[colIndex['Fec.Carga']] || '';
        m[22] = row[colIndex['Fec.Asig.Ope.']] || '';
        m[23] = row[colIndex['Días Asig']] || '';
        m[24] = row[colIndex['Días Stock']] || '';
        m[25] = limpiarNumero(row[colIndex['Pcio.Vta.Tot']]);
        m[26] = limpiarNumero(row[colIndex['Total Señas']]);
        m[27] = limpiarNumero(row[colIndex['Usa.Pte.Pgo']]);
        m[28] = limpiarNumero(row[colIndex['Créd. Bco.']]);
        m[29] = '';
        m[30] = '';
        m[31] = row[colIndex['Fact.']] || '';
        m[32] = row[colIndex['Fec. Vta.']] || '';
        m[33] = row[colIndex['Observaciones (Asig.Uni)']] || '';
        m[34] = '';
        m[35] = '';
        m[36] = row[colIndex['Seguimiento de Crédito (Asig.Uni.)']] || '';
        m[37] = row[colIndex['Banco del Crédito']] || '';
        m[38] = row[colIndex['Prob. Entr']] || '';
        return m;
    });
    
    return [SIAC_HEADERS_PROCESSED, ...mappedRows];
}

function ordenarPorOperacion(data) {
    const header = data[0];
    const rows = data.slice(1);
    rows.sort((a, b) => String(a[13] || '').localeCompare(String(b[13] || ''), undefined, { numeric: true }));
    return [header, ...rows];
}

async function procesarFilas(data) {
    const header = data[0];
    const rows = data.slice(1);
    const processed = [];
    
    // Resetear contador de debug
    window.vlookupDebugCount = 0;
    
    let stats = { ejecutivosAsignados: 0, ubicacionesEncontradas: 0, clasesCalculadas: 0 };
    
    console.log('🔄 Iniciando procesamiento de', rows.length, 'filas...');
    console.log('📁 INTEGRA tiene', integraData ? integraData.data.length - 1 : 0, 'operaciones disponibles');
    
    for (let i = 0; i < rows.length; i++) {
        let row = [...rows[i]];
        
        const vendedor = String(row[12] || '').trim();
        if (vendedor && EJECUTIVOS_MAP[vendedor]) {
            row[14] = EJECUTIVOS_MAP[vendedor];
            stats.ejecutivosAsignados++;
        } else if (vendedor) {
            row[14] = 'Sin asignar';
        }
        
        const operacion = String(row[13] || '').trim();
        if (operacion) {
            const ubicacion = buscarUbicacionINTEGRA(operacion);
            row[17] = ubicacion;
            if (ubicacion !== 'Carpeta no generada') stats.ubicacionesEncontradas++;
        } else {
            row[17] = 'Carpeta no generada';
        }
        
        if (!row[6] || row[6] === '') row[6] = calcularFechaDespachoDefault();
        row[6] = formatearFecha(row[6]);
        row[7] = calcularFechaEntrega(row[6]);
        row[8] = formatearFecha(row[8]);
        row[21] = formatearFecha(row[21]);
        row[22] = formatearFecha(row[22]);
        row[32] = formatearFecha(row[32]);
        row[35] = formatearFecha(row[35]);
        
        // Calcular Efectivo Pendiente (Sdo.Tot.Pend) = Precio Venta Total - Total Señas - Usa.Pte.Pgo - Créd. Bco.
        const precioTotal = parseFloat(row[25]) || 0;
        const totalSenas = parseFloat(row[26]) || 0;
        const usaPte = parseFloat(row[27]) || 0;
        const credBco = parseFloat(row[28]) || 0;
        const efectivoPendiente = precioTotal - totalSenas - usaPte - credBco;
        row[29] = efectivoPendiente !== 0 ? efectivoPendiente.toFixed(2) : '';
        
        const clase = calcularClase(row[26], row[27], row[28]);
        row[30] = clase;
        if (clase) stats.clasesCalculadas++;
        
        processed.push(row);
    }
    
    // Mostrar resumen en consola
    console.log('✅ Procesamiento completado:');
    console.log('   - Total filas procesadas:', processed.length);
    console.log('   - Ejecutivos asignados:', stats.ejecutivosAsignados);
    console.log('   - Ubicaciones encontradas:', stats.ubicacionesEncontradas, 'de', processed.length, '(' + Math.round(stats.ubicacionesEncontradas / processed.length * 100) + '%)');
    console.log('   - Clases calculadas:', stats.clasesCalculadas);
    console.log('   - Ubicaciones NO encontradas:', processed.length - stats.ubicacionesEncontradas);
    
    document.getElementById('rowsProcessed').textContent = processed.length;
    document.getElementById('ejecutivosAsignados').textContent = stats.ejecutivosAsignados;
    document.getElementById('ubicacionesEncontradas').textContent = stats.ubicacionesEncontradas;
    document.getElementById('clasesCalculadas').textContent = stats.clasesCalculadas;
    document.getElementById('processingInfo').style.display = 'block';
    
    return [header, ...processed];
}

function buscarUbicacionINTEGRA(operacion) {
    if (!integraData || !operacion) {
        console.log('⚠️ INTEGRA no cargado o operación vacía');
        return 'Carpeta no generada';
    }
    
    // Normalizar el número de operación: eliminar puntos, espacios y convertir a número
    const operacionStr = String(operacion).trim().replace(/\./g, '').replace(/\s/g, '');
    const operacionNum = parseInt(operacionStr, 10);
    
    // Solo mostrar los primeros 5 para no saturar la consola
    if (window.vlookupDebugCount === undefined) window.vlookupDebugCount = 0;
    if (window.vlookupDebugCount < 5) {
        console.log('🔍 Búsqueda #' + (window.vlookupDebugCount + 1) + ' - Operación SIAC:', operacion, '→ String:', operacionStr, '→ Number:', operacionNum);
        window.vlookupDebugCount++;
    }
    
    // Buscar en INTEGRA (archivo completo: operac[0] y ubicacion[11])
    for (let i = 1; i < integraData.data.length; i++) {
        const row = integraData.data[i];
        
        // Obtener valor de operac - puede ser número o string
        const operacINTEGRAraw = row[0];
        const operacINTEGRAstr = String(operacINTEGRAraw || '').trim().replace(/\./g, '').replace(/\s/g, '');
        const operacINTEGRAnum = parseInt(operacINTEGRAstr, 10);
        
        // Mostrar las primeras 3 comparaciones para debugging
        if (window.vlookupDebugCount <= 5 && i <= 3) {
            console.log(`   Fila ${i}: INTEGRA raw="${operacINTEGRAraw}" (type: ${typeof operacINTEGRAraw}), normalizada="${operacINTEGRAstr}", num=${operacINTEGRAnum}`);
            console.log(`   Comparación: ${operacINTEGRAnum} === ${operacionNum} ?`, operacINTEGRAnum === operacionNum);
        }
        
        // Comparar como números para evitar problemas con tipos
        if (!isNaN(operacINTEGRAnum) && !isNaN(operacionNum) && operacINTEGRAnum === operacionNum) {
            // La ubicación está en el índice 11 (columna 12)
            const ubicacion = String(row[11] || '').trim();
            if (window.vlookupDebugCount <= 5) {
                console.log('✅ Match encontrado! Operación:', operacionNum, '→ Ubicación:', ubicacion);
            }
            return ubicacion || 'Carpeta no generada';
        }
    }
    return 'Carpeta no generada';
}

function calcularFechaDespachoDefault() {
    const hoy = new Date();
    return `31/12/${hoy.getFullYear() + 1}`;
}

function calcularFechaEntrega(fechaDespacho) {
    if (!fechaDespacho) return '';
    const fecha = parseFecha(fechaDespacho);
    if (!fecha) return '';
    fecha.setMonth(fecha.getMonth() + 1);
    return formatearFechaObj(fecha);
}

function parseFecha(fechaStr) {
    if (!fechaStr) return null;
    
    // Si es un número (serial de Excel), convertirlo a fecha
    if (typeof fechaStr === 'number' || (!isNaN(fechaStr) && !isNaN(parseFloat(fechaStr)))) {
        const serialNumber = parseFloat(fechaStr);
        
        // Verificar que sea un número razonable para una fecha (entre 1900 y 2100 aprox)
        // Excel cuenta desde 1/1/1900, serial 1 = 1/1/1900
        if (serialNumber > 0 && serialNumber < 100000) {
            // Convertir serial de Excel a fecha JavaScript
            // Excel tiene un bug: cuenta 1900 como año bisiesto cuando no lo fue
            const excelEpoch = new Date(1899, 11, 30); // 30 de diciembre de 1899
            const fecha = new Date(excelEpoch.getTime() + serialNumber * 86400000);
            return fecha;
        }
    }
    
    const str = String(fechaStr).trim();
    
    // Detectar si es solo dígitos (número serial como string)
    if (/^\d+$/.test(str) || /^\d+\.\d+$/.test(str)) {
        const serialNumber = parseFloat(str);
        if (serialNumber > 0 && serialNumber < 100000) {
            const excelEpoch = new Date(1899, 11, 30);
            const fecha = new Date(excelEpoch.getTime() + serialNumber * 86400000);
            return fecha;
        }
    }
    
    let match = str.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
    if (match) return new Date(parseInt(match[3]), parseInt(match[2]) - 1, parseInt(match[1]));
    
    match = str.match(/^(\d{1,2})-(\d{1,2})-(\d{4})$/);
    if (match) return new Date(parseInt(match[3]), parseInt(match[2]) - 1, parseInt(match[1]));
    
    match = str.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
    if (match) return new Date(parseInt(match[1]), parseInt(match[2]) - 1, parseInt(match[3]));
    
    const fecha = new Date(str);
    return !isNaN(fecha.getTime()) ? fecha : null;
}

function formatearFecha(fechaStr) {
    if (!fechaStr) return '';
    const fecha = parseFecha(fechaStr);
    return fecha ? formatearFechaObj(fecha) : fechaStr;
}

function formatearFechaObj(fecha) {
    const dia = String(fecha.getDate()).padStart(2, '0');
    const mes = String(fecha.getMonth() + 1).padStart(2, '0');
    return `${dia}/${mes}/${fecha.getFullYear()}`;
}

function calcularClase(totalSena, usaPtePgo, credBco) {
    const sena = parseFloat(totalSena) || 0;
    const usaPte = parseFloat(usaPtePgo) || 0;
    const credito = parseFloat(credBco) || 0;
    
    // Verificar que al menos uno tenga valor para poder clasificar
    if (sena === 0 && usaPte === 0 && credito === 0) {
        return 'CLASE X'; // No se puede clasificar si todos son cero
    }
    
    // Clasificación según reglas
    if (sena !== 0 && usaPte !== 0 && credito !== 0) return 'CLASE E';
    if (sena !== 0 && usaPte === 0 && credito === 0) return 'CLASE A';
    if (sena !== 0 && usaPte !== 0 && credito === 0) return 'CLASE B';
    if (sena !== 0 && usaPte === 0 && credito !== 0) return 'CLASE C';
    if (sena === 0 && usaPte === 0 && credito !== 0) return 'CLASE D';
    
    // Cualquier otra combinación no contemplada
    return 'CLASE X';
}

async function mostrarResultados() {
    document.getElementById('previewSection').style.display = 'block';
    
    // Resetear filtros
    document.getElementById('filtroEjecutivo').value = '';
    document.getElementById('filtroClase').value = '';
    
    // Cargar configuración de observaciones si no está cargada
    if (!configDias || !matrizCodigos) {
        console.log('🔄 Cargando configuración de observaciones desde la base de datos...');
        await cargarConfiguracionSilenciosa();
    }
    
    // Aplicar filtros iniciales (mostrar todos)
    aplicarFiltros();
    
    generarEstadisticas();
}

function aplicarFiltros() {
    const filtroEjecutivo = document.getElementById('filtroEjecutivo').value;
    const filtroClase = document.getElementById('filtroClase').value;
    
    if (!processedData || processedData.length === 0) {
        console.warn('⚠️ No hay datos procesados para filtrar');
        document.getElementById('totalCount').textContent = '0';
        document.getElementById('filteredCount').textContent = '0';
        return;
    }
    
    const rows = processedData.slice(1);
    let filteredRows = rows;
    
    console.log('📊 Filtrado - Total filas:', rows.length);
    
    // Filtrar filas con operación vacía PRIMERO (más tolerante)
    const rowsConOperacion = filteredRows.filter(row => {
        const operacion = row[13];
        const tieneOperacion = operacion && String(operacion).trim() !== '';
        return tieneOperacion;
    });
    
    console.log('📊 Filtrado - Con operación:', rowsConOperacion.length);
    
    // Si no hay filtros adicionales seleccionados, mostrar TODAS las filas con operación
    if (!filtroEjecutivo && !filtroClase) {
        filteredRows = rowsConOperacion;
    } else {
        filteredRows = rowsConOperacion;
        
        // Filtrar por ejecutivo (solo si se seleccionó)
        if (filtroEjecutivo) {
            filteredRows = filteredRows.filter(row => {
                const ejecutivo = String(row[14] || '').trim();
                return ejecutivo === filtroEjecutivo;
            });
            console.log('📊 Filtrado - Por ejecutivo "' + filtroEjecutivo + '":', filteredRows.length);
        }
        
        // Filtrar por clase (solo si se seleccionó)
        if (filtroClase) {
            filteredRows = filteredRows.filter(row => {
                const clase = String(row[30] || '').trim();
                return clase === filtroClase;
            });
            console.log('📊 Filtrado - Por clase "' + filtroClase + '":', filteredRows.length);
        }
    }
    
    // Actualizar contadores
    document.getElementById('totalCount').textContent = rows.length;
    document.getElementById('filteredCount').textContent = filteredRows.length;
    
    console.log('✅ Resultado final del filtrado:', filteredRows.length, 'de', rows.length, 'filas');
    
    // Renderizar tabla
    const tbody = document.getElementById('previewTableBody');
    tbody.innerHTML = '';
    
    // Limitar a primeras 100 filas para rendimiento
    const displayRows = filteredRows.slice(0, 100);
    
    displayRows.forEach(row => {
        const tr = document.createElement('tr');
        
        // Calcular zona actual y validación
        // Manejar valores vacíos: asignar 0 si no hay valor o es NaN
        let diasAsig = parseInt(row[23]);
        let diasStock = parseInt(row[24]);
        if (isNaN(diasAsig) || diasAsig === null || diasAsig === undefined || row[23] === '' || row[23] === null) {
            diasAsig = 0;
        }
        if (isNaN(diasStock) || diasStock === null || diasStock === undefined || row[24] === '' || row[24] === null) {
            diasStock = 0;
        }
        
        const clase = row[30];
        const codigoObs = row[33]; // Observaciones (Asig.Uni)
        const operacion = row[13];
        
        const zonaInfo = calcularZonaActual(diasAsig, diasStock, clase);
        const validacionInfo = validarCodigoObservacion(codigoObs, clase, zonaInfo.zona);
        
        // Columnas: Operación(13), Cliente(11), Modelo(2), Vendedor(12), Ejecutivo(14), 
        //           Ubicación(17), Est.Entrega(7), TotalSeñas(26), UsaPtePgo(27), CrédBco(28), 
        //           Clase(30), DíasAsig, DíasStock, Diferencia, Secuencia, HoldStock, Observaciones(33), ZonaTeórica, EstadoCódigo, Sospechoso
        const columnas = [
            row[13], // Operación
            row[11], // Cliente
            row[2],  // Modelo/Versión
            row[12], // Vendedor
            row[14], // Ejecutivo
            row[17], // Ubicación Carpeta
            row[7],  // Est. Entrega
            row[26], // Total Señas (EFECTIVO)
            row[27], // Usa.Pte.Pgo (USADO)
            row[28], // Créd. Bco. (CRÉDITO)
            row[30], // Clase
            diasAsig, // Días Asig (ya procesado como número o 0)
            diasStock, // Días Stock (ya procesado como número o 0)
            zonaInfo.diferencia, // Diferencia (número)
            Array.isArray(zonaInfo.secuencia) ? zonaInfo.secuencia.join('-') : zonaInfo.secuencia, // Secuencia (convertir array a string)
            zonaInfo.holdStock ? 'Sí' : 'No', // Hold Stock
            row[33] || '', // Observaciones (Asig.Uni)
            zonaInfo.descripcion, // Zona Teórica
            validacionInfo.icono + ' ' + validacionInfo.mensaje, // Estado Código
            '' // 🚨 (se llenará después)
        ];
        
        columnas.forEach((valor, idx) => {
            const td = document.createElement('td');
            td.textContent = valor || '';
            
            // Formatear como moneda (índices 7, 8, 9 son EFECTIVO, USADO, CRÉDITO)
            if (idx >= 7 && idx <= 9) {
                const num = parseFloat(valor);
                if (!isNaN(num) && num !== 0) {
                    td.textContent = '$' + num.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                    td.style.textAlign = 'right';
                } else {
                    td.textContent = '-';
                    td.style.textAlign = 'right';
                }
            }
            
            // Colorear Clase (índice 10) - SOLO CENTRAR, SIN COLORES
            if (idx === 10 && valor) {
                td.style.textAlign = 'center';
                td.style.fontWeight = '600';
            }
            
            // Días Asig y Días Stock - centrar y formatear (índices 11 y 12) - SIN COLORES
            if (idx === 11 || idx === 12) {
                td.style.textAlign = 'center';
                const dias = typeof valor === 'number' ? valor : parseInt(valor);
                if (!isNaN(dias) && dias > 0) {
                    td.textContent = dias + ' días';
                    td.style.fontWeight = '600';
                } else {
                    td.textContent = '-';
                }
            }
            
            // Diferencia (índice 13) - centrar - SIN COLORES
            if (idx === 13) {
                td.style.textAlign = 'center';
                td.style.fontWeight = '600';
                const diff = typeof valor === 'number' ? valor : parseInt(valor);
                if (!isNaN(diff) && diff > 0) {
                    td.textContent = diff + ' días';
                } else {
                    td.textContent = '-';
                }
            }
            
            // Secuencia (índice 14) - centrar y usar fuente mono - SIN COLORES
            if (idx === 14) {
                td.style.textAlign = 'center';
                td.style.fontFamily = 'monospace';
                td.style.fontSize = '0.9em';
            }
            
            // Hold Stock (índice 15) - centrar - SIN COLORES
            if (idx === 15) {
                td.style.textAlign = 'center';
                td.style.fontWeight = '600';
            }
            
            // Observaciones (Asig.Uni) (índice 16) - alinear izquierda, fuente pequeña
            if (idx === 16) {
                td.style.textAlign = 'left';
                td.style.fontSize = '0.85em';
                td.style.maxWidth = '200px';
                td.style.overflow = 'hidden';
                td.style.textOverflow = 'ellipsis';
                td.style.whiteSpace = 'nowrap';
            }
            
            // Zona Teórica (índice 17) - SIN COLORES
            if (idx === 17) {
                td.style.textAlign = 'center';
                td.style.fontWeight = '600';
                td.style.padding = '8px';
            }
            
            // Estado Código (índice 18) - SIN COLORES
            if (idx === 18) {
                td.style.textAlign = 'center';
                td.style.fontWeight = '600';
                td.style.fontSize = '0.9em';
            }
            
            tr.appendChild(td);
        });
        
        // Agregar columna de alerta (🚨) verificando si está marcada como sospechosa
        const tdAlerta = document.createElement('td');
        tdAlerta.style.textAlign = 'center';
        tdAlerta.style.fontSize = '1.5em';
        
        // Verificar si está marcada como sospechosa (async, se puede mejorar con cache)
        verificarOperacionSospechosa(operacion).then(sospechosa => {
            if (sospechosa) {
                tdAlerta.textContent = '🚨';
                tdAlerta.title = 'Operación marcada como sospechosa';
            }
        });
        
        tr.appendChild(tdAlerta);
        
        tbody.appendChild(tr);
    });
    
    // Mostrar mensaje si se limitó la vista
    if (filteredRows.length > 100) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 20; // 19 columnas de datos + 1 columna de alerta (🚨)
        td.style.textAlign = 'center';
        td.style.padding = '15px';
        td.style.background = '#fff5f5';
        td.style.color = '#C8102E';
        td.style.fontWeight = '600';
        td.innerHTML = `<i class="fas fa-info-circle"></i> Mostrando primeras 100 filas de ${filteredRows.length}. Usa los filtros para refinar la búsqueda.`;
        tr.appendChild(td);
        tbody.appendChild(tr);
    }
}

function limpiarFiltros() {
    document.getElementById('filtroEjecutivo').value = '';
    document.getElementById('filtroClase').value = '';
    aplicarFiltros();
}

function generarEstadisticas() {
    const rows = processedData.slice(1);
    
    const clases = {};
    rows.forEach(row => { if (row[30]) clases[row[30]] = (clases[row[30]] || 0) + 1; });
    let clasesHTML = '';
    Object.keys(clases).sort().forEach(clase => { clasesHTML += `<p style="margin: 5px 0;"><strong>${clase}:</strong> ${clases[clase]} operaciones</p>`; });
    document.getElementById('statClases').innerHTML = clasesHTML || 'Sin datos';
    
    const ejecutivos = {};
    rows.forEach(row => { if (row[14] && row[14] !== 'Sin asignar') ejecutivos[row[14]] = (ejecutivos[row[14]] || 0) + 1; });
    let ejecutivosHTML = '';
    Object.keys(ejecutivos).sort().forEach(ejecutivo => { ejecutivosHTML += `<p style="margin: 5px 0;"><strong>${ejecutivo}:</strong> ${ejecutivos[ejecutivo]} operaciones</p>`; });
    document.getElementById('statEjecutivos').innerHTML = ejecutivosHTML || 'Sin datos';
    
    const ubicaciones = { encontradas: 0, noGeneradas: 0 };
    rows.forEach(row => { if (row[17] === 'Carpeta no generada') ubicaciones.noGeneradas++; else if (row[17]) ubicaciones.encontradas++; });
    document.getElementById('statUbicaciones').innerHTML = `<p style="margin: 5px 0;"><strong>Encontradas:</strong> ${ubicaciones.encontradas}</p><p style="margin: 5px 0;"><strong>No generadas:</strong> ${ubicaciones.noGeneradas}</p>`;
}

function descargarResultado() {
    if (!processedData) {
        showAlert('No hay datos procesados para descargar', 'error');
        return;
    }
    
    try {
        const ws = XLSX.utils.aoa_to_sheet(processedData);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'SIAC Procesado');
        
        const fecha = new Date().toISOString().split('T')[0];
        XLSX.writeFile(wb, `SIAC_Procesado_${fecha}.xlsx`);
        showAlert('Archivo descargado correctamente', 'success');
    } catch (error) {
        showAlert('Error al generar el archivo: ' + error.message, 'error');
    }
}

function limpiarTodo() {
    if (confirm('¿Estás seguro de limpiar todos los datos cargados?')) {
        siacData = null;
        integraData = null;
        processedData = null;
        
        document.getElementById('siacStatus').style.display = 'none';
        document.getElementById('integraStatus').style.display = 'none';
        document.getElementById('processingInfo').style.display = 'none';
        document.getElementById('previewSection').style.display = 'none';
        document.getElementById('btnProcesar').disabled = true;
        document.getElementById('btnDescargar').style.display = 'none';
        
        document.getElementById('fileSIAC').value = '';
        document.getElementById('fileINTEGRA').value = '';
        
        showAlert('Datos limpiados correctamente', 'info');
    }
}

function initializeTabs() {
    const tabs = document.querySelectorAll('.nav-link');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            const targetTab = this.getAttribute('data-tab');
            
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById('tab' + targetTab.charAt(0).toUpperCase() + targetTab.slice(1)).classList.add('active');
        });
    });
}

function showSpinner(show) {
    const spinner = document.getElementById('spinner');
    if (show) spinner.classList.add('show');
    else spinner.classList.remove('show');
}

function showAlert(message, type) {
    const container = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} show`;
    alert.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i> ${message}`;
    
    container.innerHTML = '';
    container.appendChild(alert);
    
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    }
}

// ========== ADMINISTRADOR DE EJECUTIVOS ==========

function abrirAdministradorEjecutivos() {
    document.getElementById('modalEjecutivos').style.display = 'block';
    actualizarListaRelaciones();
}

function cerrarAdministradorEjecutivos() {
    document.getElementById('modalEjecutivos').style.display = 'none';
}

function actualizarListaRelaciones() {
    const lista = document.getElementById('listaRelaciones');
    const search = document.getElementById('searchVendedor').value.toLowerCase();
    
    const vendedores = Object.keys(EJECUTIVOS_MAP).filter(v => 
        v.toLowerCase().includes(search)
    ).sort();
    
    document.getElementById('totalRelaciones').textContent = vendedores.length;
    
    if (vendedores.length === 0) {
        lista.innerHTML = '<p style="text-align: center; color: #a0aec0; padding: 20px;">No se encontraron relaciones</p>';
        return;
    }
    
    lista.innerHTML = vendedores.map(vendedor => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: white; border-bottom: 1px solid #e2e8f0; transition: all 0.2s;" onmouseover="this.style.background='#f7fafc'" onmouseout="this.style.background='white'">
            <div style="flex: 1;">
                <strong style="color: #2D2D2D; font-size: 0.95em;">${vendedor}</strong>
            </div>
            <div style="flex: 0 0 150px; text-align: center;">
                <span style="background: linear-gradient(135deg, #EB0A1E, #C8102E); color: white; padding: 5px 12px; border-radius: 5px; font-size: 0.85em; font-weight: 600;">${EJECUTIVOS_MAP[vendedor]}</span>
            </div>
            <div style="flex: 0 0 80px; text-align: right;">
                <button onclick="eliminarRelacion('${vendedor.replace(/'/g, "\\'")}')' style="background: #e53e3e; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 0.85em; transition: all 0.3s;" onmouseover="this.style.background='#c53030'" onmouseout="this.style.background='#e53e3e'">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

function agregarRelacion() {
    const vendedor = document.getElementById('nuevoVendedor').value.trim();
    const ejecutivo = document.getElementById('nuevoEjecutivo').value;
    
    if (!vendedor) {
        showAlert('Ingresa el nombre del vendedor', 'error');
        return;
    }
    
    if (!ejecutivo) {
        showAlert('Selecciona un ejecutivo', 'error');
        return;
    }
    
    EJECUTIVOS_MAP[vendedor] = ejecutivo;
    guardarEjecutivosMap();
    
    document.getElementById('nuevoVendedor').value = '';
    document.getElementById('nuevoEjecutivo').value = '';
    
    actualizarListaRelaciones();
    showAlert(`Relación agregada: ${vendedor} → ${ejecutivo}`, 'success');
}

function eliminarRelacion(vendedor) {
    if (confirm(`¿Eliminar la relación de "${vendedor}"?`)) {
        delete EJECUTIVOS_MAP[vendedor];
        guardarEjecutivosMap();
        actualizarListaRelaciones();
        showAlert('Relación eliminada correctamente', 'info');
    }
}

function filtrarRelaciones() {
    actualizarListaRelaciones();
}

// ============================================
// SISTEMA DE CONFIGURACIÓN DE OBSERVACIONES
// ============================================

let configDias = null;
let matrizCodigos = null;

// Abrir modal de configuración
function abrirConfiguradorObservaciones() {
    document.getElementById('modalConfigObservaciones').style.display = 'block';
    cargarConfiguracionObservaciones();
}

// Cerrar modal
function cerrarConfiguradorObservaciones() {
    document.getElementById('modalConfigObservaciones').style.display = 'none';
}

// Cargar configuración desde el backend sin mostrar en modal (silencioso)
async function cargarConfiguracionSilenciosa() {
    try {
        console.log('🔄 Iniciando carga silenciosa de configuración...');
        
        // Cargar configuración de días
        try {
            const resDias = await fetch('/api/observaciones/config_dias');
            console.log('📡 Response config_dias - Status:', resDias.status, resDias.statusText);
            
            if (resDias.ok) {
                const data = await resDias.json();
                console.log('📦 Datos recibidos config_dias:', data);
                
                if (Array.isArray(data) && data.length > 0) {
                    configDias = data;
                    console.log('✅ Config de días cargada:', configDias.length, 'zonas');
                } else {
                    console.warn('⚠️ Config de días vacía o formato incorrecto:', typeof data, data);
                    configDias = null;
                }
            } else {
                console.error('❌ Error HTTP en config_dias:', resDias.status);
                configDias = null;
            }
        } catch (errDias) {
            console.error('❌ Excepción al cargar config_dias:', errDias);
            configDias = null;
        }
        
        // Cargar matriz de códigos
        try {
            const resCodigos = await fetch('/api/observaciones/matriz_codigos');
            console.log('📡 Response matriz_codigos - Status:', resCodigos.status, resCodigos.statusText);
            
            if (resCodigos.ok) {
                const data = await resCodigos.json();
                console.log('📦 Datos recibidos matriz_codigos:', data);
                
                if (Array.isArray(data) && data.length > 0) {
                    matrizCodigos = data;
                    console.log('✅ Matriz de códigos cargada:', matrizCodigos.length, 'registros');
                } else {
                    console.warn('⚠️ Matriz de códigos vacía o formato incorrecto:', typeof data, data);
                    matrizCodigos = null;
                }
            } else {
                console.error('❌ Error HTTP en matriz_codigos:', resCodigos.status);
                matrizCodigos = null;
            }
        } catch (errMatriz) {
            console.error('❌ Excepción al cargar matriz_codigos:', errMatriz);
            matrizCodigos = null;
        }
        
        console.log('🏁 Carga silenciosa finalizada. configDias:', !!configDias, 'matrizCodigos:', !!matrizCodigos);
    } catch (error) {
        console.error('❌ Error general en carga silenciosa:', error);
    }
}

// Cargar configuración actual desde el backend y mostrar en modal
async function cargarConfiguracionObservaciones() {
    try {
        console.log('🔄 Cargando configuración para modal...');
        
        // Cargar configuración de días
        const resDias = await fetch('/api/observaciones/config_dias');
        console.log('📡 Response config_dias (modal) - Status:', resDias.status);
        
        if (resDias.ok) {
            const data = await resDias.json();
            console.log('📦 Datos config_dias (modal):', data);
            
            // Verificar si es un array o tiene error
            if (Array.isArray(data) && data.length > 0) {
                configDias = data;
                
                // Poblar campos de días
                configDias.forEach(zona => {
                    const estandarInput = document.getElementById(`diasEstandarZona${zona.zona}`);
                    const desvioInput = document.getElementById(`diasDesvioZona${zona.zona}`);
                    
                    if (estandarInput) estandarInput.value = zona.dias_estandar;
                    if (desvioInput) desvioInput.value = zona.dias_desvio;
                    
                    actualizarRangoZona(zona.zona);
                });
                console.log('✅ Campos de días poblados en modal');
            } else {
                console.error('❌ Formato inesperado de config_dias:', data);
                showAlert('Error: Configuración de días tiene formato incorrecto', 'error');
            }
        } else {
            console.error('❌ Error HTTP config_dias:', resDias.status);
            showAlert(`No se pudo cargar la configuración de días (HTTP ${resDias.status})`, 'error');
        }
        
        // Cargar matriz de códigos
        const resCodigos = await fetch('/api/observaciones/matriz_codigos');
        console.log('📡 Response matriz_codigos (modal) - Status:', resCodigos.status);
        
        if (resCodigos.ok) {
            const data = await resCodigos.json();
            console.log('📦 Datos matriz_codigos (modal):', data);
            
            // Verificar si es un array o tiene error
            if (Array.isArray(data) && data.length > 0) {
                matrizCodigos = data;
                
                // Poblar matriz y detectar zonas de arribo
                const zonasArribo = {};
                matrizCodigos.forEach(registro => {
                    const claseLetra = registro.clase.replace('CLASE ', '');
                    const inputId = `codigos${claseLetra}${registro.zona}`;
                    const input = document.getElementById(inputId);
                    if (input) {
                        input.value = registro.codigos;
                        
                        // Si está marcado como "-", deshabilitar
                        if (registro.codigos === '-') {
                            input.disabled = true;
                            input.style.background = '#f7fafc';
                            input.style.color = '#a0aec0';
                        }
                    }
                    
                    // Guardar zona de arribo
                    if (registro.es_zona_arribo) {
                        zonasArribo[claseLetra] = registro.zona;
                    }
                });
                
                // Configurar selectores de zona de arribo
                Object.keys(zonasArribo).forEach(clase => {
                    const arriboSelect = document.getElementById(`arribo${clase}`);
                    if (arriboSelect) {
                        arriboSelect.value = zonasArribo[clase];
                        actualizarCamposMatriz(clase);
                    }
                });
                console.log('✅ Matriz de códigos poblada en modal. Zonas de arribo:', zonasArribo);
            } else {
                console.error('❌ Formato inesperado de matriz_codigos:', data);
                showAlert('Error: Matriz de códigos tiene formato incorrecto', 'error');
            }
        } else {
            console.error('❌ Error HTTP matriz_codigos:', resCodigos.status);
            showAlert(`No se pudo cargar la matriz de códigos (HTTP ${resCodigos.status})`, 'error');
        }
    } catch (error) {
        console.error('❌ Error cargando configuración:', error);
        showAlert('Error de conexión: ' + error.message, 'error');
    }
}

// Actualizar rango mostrado cuando cambian los valores
function actualizarRangoZona(zonaNum) {
    const estandar = parseInt(document.getElementById(`diasEstandarZona${zonaNum}`).value) || 0;
    const desvio = parseInt(document.getElementById(`diasDesvioZona${zonaNum}`).value) || 0;
    const min = Math.max(0, estandar - desvio);
    const max = estandar + desvio;
    document.getElementById(`rangoZona${zonaNum}`).textContent = `${min} - ${max} días`;
}

// Agregar listeners para actualizar rangos automáticamente
document.addEventListener('DOMContentLoaded', () => {
    for (let i = 1; i <= 3; i++) {
        const estandarInput = document.getElementById(`diasEstandarZona${i}`);
        const desvioInput = document.getElementById(`diasDesvioZona${i}`);
        
        if (estandarInput) estandarInput.addEventListener('input', () => actualizarRangoZona(i));
        if (desvioInput) desvioInput.addEventListener('input', () => actualizarRangoZona(i));
    }
    
    // Listeners para zonas de arribo - deshabilitar campos que no aplican
    const clases = ['A', 'B', 'C', 'D', 'E'];
    clases.forEach(clase => {
        const arriboSelect = document.getElementById(`arribo${clase}`);
        if (arriboSelect) {
            arriboSelect.addEventListener('change', () => actualizarCamposMatriz(clase));
        }
    });
});

// Actualizar campos de matriz cuando cambia zona de arribo
function actualizarCamposMatriz(clase) {
    const arriboSelect = document.getElementById(`arribo${clase}`);
    const zonaArribo = parseInt(arriboSelect.value);
    
    for (let zona = 1; zona <= 4; zona++) {
        const input = document.getElementById(`codigos${clase}${zona}`);
        if (!input) continue;
        
        if (zona > zonaArribo) {
            // Deshabilitar zonas posteriores al arribo
            input.disabled = true;
            input.value = '-';
            input.style.background = '#f7fafc';
            input.style.color = '#a0aec0';
        } else {
            // Habilitar zonas hasta el arribo
            input.disabled = false;
            input.style.background = 'white';
            input.style.color = '#2D2D2D';
        }
    }
}

// Guardar configuración de días
async function guardarConfigDias() {
    const nuevaConfig = [];
    
    for (let i = 1; i <= 3; i++) {
        const estandar = parseInt(document.getElementById(`diasEstandarZona${i}`).value);
        const desvio = parseInt(document.getElementById(`diasDesvioZona${i}`).value);
        
        if (isNaN(estandar) || isNaN(desvio)) {
            showAlert(`Completa todos los campos de la Zona ${i}`, 'error');
            return;
        }
        
        if (estandar < 0 || desvio < 0) {
            showAlert('Los valores no pueden ser negativos', 'error');
            return;
        }
        
        nuevaConfig.push({
            zona: i,
            dias_estandar: estandar,
            dias_desvio: desvio
        });
    }
    
    try {
        const response = await fetch('/api/observaciones/config_dias', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ zonas: nuevaConfig })
        });
        
        if (response.ok) {
            configDias = nuevaConfig;
            showAlert('Configuración de días guardada correctamente', 'success');
            // Recargar tabla si hay datos procesados
            if (processedData) {
                renderTable(processedData);
            }
        } else {
            const error = await response.json();
            showAlert('Error al guardar: ' + (error.error || 'Error desconocido'), 'error');
        }
    } catch (error) {
        console.error('Error guardando configuración de días:', error);
        showAlert('Error al guardar la configuración', 'error');
    }
}

// Guardar matriz de códigos
async function guardarMatrizCodigos() {
    const nuevaMatriz = [];
    const clases = ['A', 'B', 'C', 'D', 'E'];
    
    console.log('🔄 Iniciando guardado de matriz de códigos...');
    
    for (const clase of clases) {
        // Obtener zona de arribo para esta clase
        const arriboSelect = document.getElementById(`arribo${clase}`);
        
        if (!arriboSelect) {
            console.error(`❌ No se encontró selector arribo${clase}`);
            showAlert(`Error: No se encuentra el selector de arribo para CLASE ${clase}`, 'error');
            return;
        }
        
        const zonaArriboStr = arriboSelect.value;
        const zonaArribo = parseInt(zonaArriboStr);
        
        if (isNaN(zonaArribo) || zonaArribo < 1 || zonaArribo > 4) {
            console.error(`❌ Zona de arribo inválida para CLASE ${clase}:`, zonaArriboStr);
            showAlert(`Error: Zona de arribo inválida para CLASE ${clase}`, 'error');
            return;
        }
        
        console.log(`📍 CLASE ${clase}: Zona de arribo = ${zonaArribo}`);
        
        for (let zona = 1; zona <= 4; zona++) {
            const inputId = `codigos${clase}${zona}`;
            const input = document.getElementById(inputId);
            
            // Si el campo no existe, saltar
            if (!input) {
                console.warn(`⚠️ No se encontró input ${inputId}`);
                continue;
            }
            
            const codigos = input.value.trim();
            const esZonaArribo = (zona === zonaArribo);
            
            // Si la zona está después del arribo, guardar como "-"
            if (zona > zonaArribo) {
                nuevaMatriz.push({
                    clase: `CLASE ${clase}`,
                    zona: zona,
                    codigos: '-',
                    es_zona_arribo: false
                });
                console.log(`   Zona ${zona}: "-" (después de arribo)`);
                continue;
            }
            
            // Validar que las zonas hasta el arribo tengan códigos
            if (!codigos && zona <= zonaArribo) {
                showAlert(`Falta código para CLASE ${clase}, ZONA ${zona}`, 'error');
                return;
            }
            
            nuevaMatriz.push({
                clase: `CLASE ${clase}`,
                zona: zona,
                codigos: codigos || '-',
                es_zona_arribo: esZonaArribo
            });
            
            const arriboMark = esZonaArribo ? ' ✨ ARRIBO' : '';
            console.log(`   Zona ${zona}: "${codigos}"${arriboMark}`);
        }
    }
    
    console.log('📦 Matriz completa a enviar:', JSON.stringify(nuevaMatriz, null, 2));
    
    try {
        console.log('📤 Enviando petición POST a /api/observaciones/matriz_codigos...');
        console.log('📦 Payload:', JSON.stringify({ matriz: nuevaMatriz }, null, 2));
        
        const response = await fetch('/api/observaciones/matriz_codigos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matriz: nuevaMatriz })
        });
        
        console.log('📡 Response status:', response.status, response.statusText);
        
        let result;
        try {
            result = await response.json();
            console.log('📦 Response body:', result);
        } catch (parseError) {
            console.error('❌ Error parsing response JSON:', parseError);
            showAlert('Error: El servidor devolvió una respuesta inválida. Ver consola para detalles.', 'error');
            return;
        }
        
        if (response.ok && result.success) {
            matrizCodigos = nuevaMatriz;
            console.log('✅ Matriz guardada exitosamente en base de datos');
            showAlert('✅ Matriz de códigos guardada correctamente. ' + (result.message || ''), 'success');
            
            // Recargar configuración para verificar que se guardó
            setTimeout(async () => {
                await cargarConfiguracionSilenciosa();
                console.log('🔄 Configuración recargada desde DB');
                
                // Recargar tabla si hay datos procesados
                if (processedData) {
                    aplicarFiltros();
                }
            }, 500);
        } else {
            console.error('❌ Error del servidor:', result);
            const errorMsg = result.error || 'Error desconocido';
            showAlert('❌ Error al guardar la matriz:\n\n' + errorMsg + '\n\nRevisa la consola para más detalles.', 'error');
        }
    } catch (error) {
        console.error('❌ Excepción guardando matriz de códigos:', error);
        showAlert('❌ Error de red o conexión:\n\n' + error.message + '\n\nVerifica que el servidor esté corriendo.', 'error');
    }
}

// ============================================
// LÓGICA DE ZONAS Y VALIDACIÓN
// ============================================

// Calcular zona actual basándose en días asignación, días stock, y clase
function calcularZonaActual(diasAsignacion, diasStock, clase) {
    // Verificar que configDias esté cargada y sea válida
    if (!configDias || !Array.isArray(configDias) || configDias.length === 0) {
        return { 
            zona: '-', 
            color: '#718096', 
            descripcion: 'Config no cargada',
            diferencia: 0,
            secuencia: '-',
            holdStock: false
        };
    }
    
    // Si no hay días válidos (ambos 0 o null)
    if ((diasAsignacion === 0 && diasStock === 0) || 
        diasAsignacion == null || diasStock == null || 
        isNaN(diasAsignacion) || isNaN(diasStock)) {
        return { 
            zona: '-', 
            color: '#718096', 
            descripcion: 'Sin datos',
            diferencia: 0,
            secuencia: '-',
            holdStock: false
        };
    }
    
    // PASO 1: Obtener zona de arribo configurada para esta clase
    let zonaArribo = 4; // Por defecto zona 4
    if (matrizCodigos && Array.isArray(matrizCodigos)) {
        const arriboConfig = matrizCodigos.find(r => r.clase === clase && r.es_zona_arribo === true);
        if (arriboConfig) {
            zonaArribo = arriboConfig.zona;
        }
    }
    
    // PASO 2: Calcular diferencia (Días Asig - Días Stock)
    const diferencia = diasAsignacion - diasStock;
    
    // PASO 2.5: Obtener días estándar de Zona 1 y Zona 2
    let diasEstandarZona1 = 5; // Valor por defecto
    let diasEstandarZona2 = 10; // Valor por defecto
    
    const zona1Config = configDias.find(z => z.zona === 1);
    if (zona1Config && typeof zona1Config.dias_estandar !== 'undefined') {
        diasEstandarZona1 = zona1Config.dias_estandar;
    }
    
    const zona2Config = configDias.find(z => z.zona === 2);
    if (zona2Config && typeof zona2Config.dias_estandar !== 'undefined') {
        diasEstandarZona2 = zona2Config.dias_estandar;
    }
    
    // PASO 3: Determinar si pasó por zona 2
    // Regla: Incluir zona 2 SI diferencia > días estándar zona 1
    const pasaPorZona2 = diferencia > diasEstandarZona1;
    
    // PASO 4: Determinar Hold Stock
    // Para CLASE D (arribo zona 2): Hold Stock si diferencia > zona 1
    // Para otras clases (pasan por zona 2): Hold Stock si diferencia > zona 1 + zona 2
    let holdStock;
    if (clase === 'CLASE D') {
        // CLASE D: Hold Stock = superó el tiempo de zona 1
        holdStock = diferencia > diasEstandarZona1;
    } else {
        // Clases A, B, C, E: Hold Stock = superó zona 1 + zona 2 (solo si pasó por zona 2)
        if (pasaPorZona2) {
            holdStock = diferencia > (diasEstandarZona1 + diasEstandarZona2);
        } else {
            // Si no pasó por zona 2, no puede haber hold stock
            holdStock = false;
        }
    }
    
    let secuencia;
    if (zonaArribo === 3) {
        // Zona de arribo 3: termina en zona 3
        if (pasaPorZona2) {
            secuencia = [1, 2, 3]; // Pasó por zona 2
        } else {
            secuencia = [1, 3]; // NO pasó por zona 2
        }
    } else if (zonaArribo === 4) {
        // Zona de arribo 4: termina en zona 4
        if (pasaPorZona2) {
            secuencia = [1, 2, 3, 4]; // Pasó por zona 2
        } else {
            secuencia = [1, 3, 4]; // NO pasó por zona 2
        }
    } else if (zonaArribo === 2) {
        // Zona de arribo 2: termina en zona 2
        if (pasaPorZona2) {
            secuencia = [1, 2]; // Pasó por zona 2
        } else {
            secuencia = [1]; // Solo zona 1 (no alcanzó a zona 2)
        }
    } else {
        // Zona de arribo no reconocida, usar defecto zona 4
        if (pasaPorZona2) {
            secuencia = [1, 2, 3, 4];
        } else {
            secuencia = [1, 3, 4];
        }
    }
    
    // PASO 5: Calcular ZONA TEÓRICA basándose en días de asignación acumulados
    // La zona teórica indica dónde DEBERÍA estar el proceso según el tiempo transcurrido
    let zonaTeorica = 1;
    let diasAcumulados = 0;
    
    // Sumar días estándar de cada zona para determinar en cuál debería estar
    for (let i = 0; i < configDias.length; i++) {
        const zonaConfig = configDias[i];
        if (!zonaConfig || typeof zonaConfig.dias_estandar === 'undefined') {
            continue;
        }
        
        diasAcumulados += zonaConfig.dias_estandar;
        
        // Si los días de asignación superan el acumulado de esta zona, avanzar a la siguiente
        if (diasAsignacion > diasAcumulados) {
            // Determinar la siguiente zona según la secuencia
            if (i === 0) {
                // Después de zona 1: puede ir a zona 2 o zona 3 (según secuencia)
                zonaTeorica = pasaPorZona2 ? 2 : 3;
            } else if (i === 1) {
                // Después de zona 2: va a zona 3
                zonaTeorica = 3;
            } else if (i === 2) {
                // Después de zona 3: va a zona 4 (arribo)
                zonaTeorica = 4;
            }
        } else {
            // Los días de asignación están dentro del rango de esta zona
            break;
        }
    }
    
    // Limitar zona teórica a la zona de arribo configurada
    if (zonaTeorica > zonaArribo) {
        zonaTeorica = zonaArribo;
    }
    
    // Determinar color y descripción
    const colores = {
        1: '#48bb78',  // Verde - Zona 1
        2: '#ecc94b',  // Amarillo - Zona 2
        3: '#f56565',  // Rojo - Zona 3
        4: '#805ad5'   // Morado - Zona 4
    };
    
    const esArribo = (zonaTeorica === zonaArribo);
    const descripcion = esArribo ? `Zona ${zonaTeorica} (Arribo)` : `Zona ${zonaTeorica}`;
    const secuenciaStr = '[' + secuencia.join(',') + ']';
    
    return {
        zona: zonaTeorica,
        color: colores[zonaTeorica] || '#718096',
        descripcion: descripcion,
        diferencia: diferencia,
        secuencia: secuenciaStr,
        holdStock: holdStock
    };
}

// Validar código de observación
function validarCodigoObservacion(codigoObs, clase, zonaActual) {
    if (!matrizCodigos || matrizCodigos.length === 0) {
        return { valido: null, mensaje: 'Matriz no cargada', icono: '⚠️', color: '#718096' };
    }
    
    if (!codigoObs || codigoObs.trim() === '') {
        return { valido: false, mensaje: 'Sin código', icono: '⚠️', color: '#ecc94b' };
    }
    
    if (zonaActual === '-' || zonaActual == null) {
        return { valido: null, mensaje: 'Zona no determinada', icono: '⚠️', color: '#718096' };
    }
    
    // Buscar códigos permitidos para esta clase y zona
    const registro = matrizCodigos.find(r => r.clase === clase && r.zona === zonaActual);
    
    if (!registro) {
        return { valido: null, mensaje: 'Sin config para clase/zona', icono: '⚠️', color: '#718096' };
    }
    
    // Parsear códigos permitidos (separados por comas)
    const codigosPermitidos = registro.codigos.split(',').map(c => c.trim());
    const codigoLimpio = codigoObs.toString().trim();
    
    if (codigosPermitidos.includes(codigoLimpio)) {
        return { valido: true, mensaje: 'Código válido', icono: '✅', color: '#48bb78' };
    } else {
        return { valido: false, mensaje: 'Código inválido para zona', icono: '❌', color: '#f56565' };
    }
}

// Verificar si operación está marcada como sospechosa
async function verificarOperacionSospechosa(operacion) {
    try {
        const response = await fetch(`/api/observaciones/stats/${operacion}`);
        if (response.ok) {
            const stats = await response.json();
            return stats.marcado_sospechoso || false;
        }
    } catch (error) {
        console.error('Error verificando operación sospechosa:', error);
    }
    return false;
}

