// Variables globales
let datosConvencional = [];
let datosPlanAhorro = [];
let datosFiltrados = [];
let chartMensual = null;

// Elementos del DOM
const dropZoneConv = document.getElementById('dropZoneConvencional');
const dropZonePA = document.getElementById('dropZonePlanAhorro');
const fileConv = document.getElementById('fileConvencional');
const filePA = document.getElementById('filePlanAhorro');
const btnProcesar = document.getElementById('btnProcesar');
const successAlert = document.getElementById('successAlert');
const errorAlert = document.getElementById('errorAlert');
const loadingSpinner = document.getElementById('loadingSpinner');

// Ocultar alertas al inicio
successAlert.style.display = 'none';
errorAlert.style.display = 'none';

// Setup Drag & Drop - Convencional
setupDropZone(dropZoneConv, fileConv, 'convencional');
setupDropZone(dropZonePA, filePA, 'planAhorro');

function setupDropZone(dropZone, fileInput, tipo) {
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#EB0A1E';
        dropZone.style.background = '#fff5f5';
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '';
        dropZone.style.background = '';
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '';
        dropZone.style.background = '';
        
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file, tipo);
    });
    
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFile(file, tipo);
    });
}

function handleFile(file, tipo) {
    const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (extension !== '.xlsx' && extension !== '.xls') {
        showError('Por favor, selecciona un archivo Excel válido (.xlsx o .xls)');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        const data = new Uint8Array(e.target.result);
        procesarExcel(data, tipo, file.name);
    };
    reader.readAsArrayBuffer(file);
}

function procesarExcel(data, tipo, nombreArchivo) {
    console.log(`Procesando archivo Excel: ${nombreArchivo}`);
    
    try {
        // Leer el archivo Excel
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        
        console.log(`Hoja: ${sheetName}`);
        
        // Convertir a JSON (array de arrays)
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });
        
        console.log(`Total de filas: ${jsonData.length}`);
        
        const datos = [];
        
        // Determinar columnas según el tipo
        let colRemito, colFecha, colModelo, colNroFabrica;
        
        if (tipo === 'convencional') {
            // Convencionales y Especiales
            // P = columna 15 (0-indexed)
            // Q = columna 16
            // T = columna 19
            // U = columna 20
            colRemito = 15;     // P
            colFecha = 16;      // Q
            colModelo = 19;     // T
            colNroFabrica = 20; // U
        } else {
            // Plan de Ahorro
            // K = columna 10
            // L = columna 11
            // N = columna 13
            // O = columna 14
            colRemito = 10;     // K
            colFecha = 11;      // L
            colModelo = 13;     // N
            colNroFabrica = 14; // O
        }
        
        console.log(`Columnas a leer: Remito=${colRemito}, Fecha=${colFecha}, Modelo=${colModelo}, NroFabrica=${colNroFabrica}`);
        
        // Procesar filas (saltar la primera que suele ser encabezados)
        for (let i = 1; i < jsonData.length; i++) {
            const fila = jsonData[i];
            
            if (!fila || fila.length === 0) continue;
            
            const nroRemito = fila[colRemito] ? String(fila[colRemito]).trim() : '';
            const fechaStr = fila[colFecha] ? String(fila[colFecha]).trim() : '';
            const modelo = fila[colModelo] ? String(fila[colModelo]).trim() : '';
            const nroFabrica = fila[colNroFabrica] ? String(fila[colNroFabrica]).trim() : '';
            
            // Debug primera fila
            if (i === 1) {
                console.log('Primera fila de datos:', {
                    nroRemito,
                    fechaStr,
                    modelo,
                    nroFabrica
                });
            }
            
            // Validar datos mínimos
            if (!nroRemito || !fechaStr || !nroFabrica) {
                continue;
            }
            
            // Validar formato de remito
            if (!nroRemito.startsWith('R-')) {
                continue;
            }
            
            // Parsear fecha
            let fecha;
            if (typeof fila[colFecha] === 'number') {
                // Excel guarda fechas como números (días desde 1900)
                fecha = XLSX.SSF.parse_date_code(fila[colFecha]);
                fecha = new Date(fecha.y, fecha.m - 1, fecha.d);
            } else {
                // Formato texto DD/MM/YY o DD/MM/YYYY
                fecha = parsearFecha(fechaStr);
            }
            
            if (fecha && !isNaN(fecha.getTime())) {
                datos.push({
                    nroRemito,
                    fecha,
                    nroFabrica,
                    modelo: modelo || '',
                    tipo: determinarTipoVenta(nroFabrica),
                    sucursal: determinarSucursal(nroRemito, nroFabrica)
                });
            }
        }
        
        console.log(`${tipo}: ${datos.length} registros procesados de ${jsonData.length - 1} filas`);
        
        if (datos.length > 0) {
            console.log('Muestra de datos procesados:', datos.slice(0, 3));
        }
        
        if (tipo === 'convencional') {
            datosConvencional = datos;
            mostrarEstadoArchivo('convencional', nombreArchivo, datos.length);
        } else {
            datosPlanAhorro = datos;
            mostrarEstadoArchivo('planAhorro', nombreArchivo, datos.length);
        }
        
        verificarArchivosListos();
        
    } catch (error) {
        console.error('Error al procesar Excel:', error);
        showError(`Error al procesar el archivo: ${error.message}`);
    }
}

function parsearLineaCSV(linea) {
    const campos = [];
    let campoActual = '';
    let dentroComillas = false;
    
    for (let i = 0; i < linea.length; i++) {
        const char = linea[i];
        
        if (char === '"') {
            // Manejar comillas dobles escapadas ("")
            if (dentroComillas && i + 1 < linea.length && linea[i + 1] === '"') {
                campoActual += '"';
                i++; // Saltar la segunda comilla
            } else {
                dentroComillas = !dentroComillas;
            }
        } else if (char === ',' && !dentroComillas) {
            campos.push(campoActual);
            campoActual = '';
        } else {
            campoActual += char;
        }
    }
    
    // Agregar el último campo
    campos.push(campoActual);
    
    // Limpiar campos (eliminar comillas al inicio/final y espacios)
    return campos.map(campo => {
        campo = campo.trim();
        // Eliminar comillas al inicio y al final si existen
        if (campo.startsWith('"') && campo.endsWith('"')) {
            campo = campo.substring(1, campo.length - 1);
        }
        return campo;
    });
}

function parsearFecha(fechaStr) {
    if (!fechaStr) return null;
    
    // Limpiar la fecha de espacios y comillas
    fechaStr = fechaStr.trim().replace(/"/g, '');
    
    // Formato: DD/MM/YY o DD/MM/YYYY
    const partes = fechaStr.split('/');
    if (partes.length !== 3) return null;
    
    let [dia, mes, anio] = partes.map(p => parseInt(p));
    
    // Validar valores
    if (isNaN(dia) || isNaN(mes) || isNaN(anio)) return null;
    
    // Convertir año de 2 dígitos a 4
    if (anio < 100) {
        anio = anio < 50 ? 2000 + anio : 1900 + anio;
    }
    
    // Crear fecha (mes es 0-indexed en JavaScript)
    const fecha = new Date(anio, mes - 1, dia);
    
    // Validar que la fecha es válida
    if (isNaN(fecha.getTime())) return null;
    
    return fecha;
}

function determinarTipoVenta(nroFabrica) {
    if (nroFabrica.startsWith('YAC')) return 'Convencional';
    if (nroFabrica.startsWith('TPA') || nroFabrica.startsWith('TAP')) return 'Plan de Ahorro';
    if (nroFabrica.startsWith('F01') || nroFabrica.startsWith('F02')) return 'Especial';
    return 'Otro';
}

function determinarSucursal(nroRemito, nroFabrica) {
    // Extraer código de sucursal del remito (R-XXXX-...)
    const match = nroRemito.match(/R-(\d{4})-/);
    if (!match) return 'Sin clasificar';
    
    const codigo = match[1];
    const tipoVenta = determinarTipoVenta(nroFabrica);
    
    // Para Plan de Ahorro
    if (tipoVenta === 'Plan de Ahorro') {
        if (codigo === '0021') return 'Casa Central';
        if (codigo === '0022') return 'San Rafael';
        if (codigo === '0002') return 'San Rafael'; // Plan de Ahorro con código 0002
        return 'Sin clasificar';
    }
    
    // Para Convencionales y Especiales
    if (codigo === '0001') return 'Casa Central';
    if (codigo === '0002') return 'San Rafael';
    if (codigo === '0004') return 'Bombal';
    
    return 'Sin clasificar';
}

function mostrarEstadoArchivo(tipo, nombre, cantidad) {
    const status = document.getElementById(`${tipo}Status`);
    const fileName = document.getElementById(`${tipo}FileName`);
    const info = document.getElementById(`${tipo}Info`);
    
    status.style.display = 'block';
    fileName.textContent = nombre;
    info.textContent = `${cantidad} registros encontrados`;
}

function verificarArchivosListos() {
    // Habilitar botón procesar si hay al menos un archivo cargado
    btnProcesar.disabled = datosConvencional.length === 0 && datosPlanAhorro.length === 0;
}

function procesarArchivos() {
    loadingSpinner.classList.add('show');
    
    // Combinar todos los datos
    const todosDatos = [...datosConvencional, ...datosPlanAhorro];
    
    if (todosDatos.length === 0) {
        showError('No hay datos para procesar');
        loadingSpinner.classList.remove('show');
        return;
    }
    
    // Configurar fechas por defecto
    const fechas = todosDatos.map(d => d.fecha).sort((a, b) => a - b);
    const fechaMin = fechas[0];
    const fechaMax = fechas[fechas.length - 1];
    
    document.getElementById('fechaDesde').valueAsDate = fechaMin;
    document.getElementById('fechaHasta').valueAsDate = fechaMax;
    
    datosFiltrados = todosDatos;
    
    setTimeout(() => {
        loadingSpinner.classList.remove('show');
        document.getElementById('dashboardSection').style.display = 'block';
        aplicarFiltros();
        showSuccess(`${todosDatos.length} registros procesados correctamente`);
    }, 500);
}

function aplicarFiltros() {
    const fechaDesde = document.getElementById('fechaDesde').valueAsDate;
    const fechaHasta = document.getElementById('fechaHasta').valueAsDate;
    
    if (!fechaDesde || !fechaHasta) {
        showError('Por favor, selecciona ambas fechas');
        return;
    }
    
    // Filtrar datos por rango de fechas
    const todosDatos = [...datosConvencional, ...datosPlanAhorro];
    datosFiltrados = todosDatos.filter(d => d.fecha >= fechaDesde && d.fecha <= fechaHasta);
    
    actualizarDashboard();
}

function actualizarDashboard() {
    // Calcular totales
    const totalRemitos = datosFiltrados.length;
    const totalConv = datosFiltrados.filter(d => d.tipo === 'Convencional').length;
    const totalPA = datosFiltrados.filter(d => d.tipo === 'Plan de Ahorro').length;
    const totalEsp = datosFiltrados.filter(d => d.tipo === 'Especial').length;
    
    document.getElementById('totalRemitos').textContent = totalRemitos;
    document.getElementById('totalConvencionales').textContent = totalConv;
    document.getElementById('totalPlanAhorro').textContent = totalPA;
    document.getElementById('totalEspeciales').textContent = totalEsp;
    
    // Estadísticas por sucursal
    actualizarEstadisticasSucursal('Casa Central', 'statsCasaCentral');
    actualizarEstadisticasSucursal('San Rafael', 'statsSanRafael');
    actualizarEstadisticasSucursal('Bombal', 'statsBombal');
    
    // Diagnóstico: remitos sin clasificar
    mostrarDiagnosticoSinClasificar();
    
    // Gráfico mensual
    actualizarGraficoMensual();
}

function mostrarDiagnosticoSinClasificar() {
    const sinClasificar = datosFiltrados.filter(d => d.sucursal === 'Sin clasificar');
    
    if (sinClasificar.length > 0) {
        document.getElementById('diagnosticoPanel').style.display = 'block';
        document.getElementById('cantidadSinClasificar').textContent = sinClasificar.length;
        
        const tbody = document.getElementById('tablaSinClasificar');
        tbody.innerHTML = '';
        
        sinClasificar.forEach(dato => {
            // Extraer código del remito
            const match = dato.nroRemito.match(/R-(\d{4})-/);
            const codigo = match ? match[1] : 'N/A';
            
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid #e2e8f0';
            tr.innerHTML = `
                <td style="padding: 8px; color: #2D2D2D;">${dato.nroRemito}</td>
                <td style="padding: 8px; color: #EB0A1E; font-weight: 600;">${codigo}</td>
                <td style="padding: 8px; color: #4a5568;">${dato.tipo}</td>
                <td style="padding: 8px; color: #4a5568;">${dato.nroFabrica}</td>
                <td style="padding: 8px; color: #718096;">${dato.fecha.toLocaleDateString('es-AR')}</td>
            `;
            tbody.appendChild(tr);
        });
        
        console.log(`⚠️ DIAGNÓSTICO: ${sinClasificar.length} remitos sin clasificar encontrados`);
        console.log('Códigos únicos sin clasificar:', [...new Set(sinClasificar.map(d => {
            const match = d.nroRemito.match(/R-(\d{4})-/);
            return match ? match[1] : 'Sin código';
        }))]);
    } else {
        document.getElementById('diagnosticoPanel').style.display = 'none';
    }
}

function actualizarEstadisticasSucursal(sucursal, elementId) {
    const datosSucursal = datosFiltrados.filter(d => d.sucursal === sucursal);
    const conv = datosSucursal.filter(d => d.tipo === 'Convencional').length;
    const pa = datosSucursal.filter(d => d.tipo === 'Plan de Ahorro').length;
    const esp = datosSucursal.filter(d => d.tipo === 'Especial').length;
    
    const html = `
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: #4a5568;">Total:</span>
                <span style="font-weight: 700; font-size: 1.3em; color: #2D2D2D;">${datosSucursal.length}</span>
            </div>
        </div>
        <div style="border-top: 2px solid #e2e8f0; padding-top: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #718096;">Convencionales:</span>
                <span style="font-weight: 600; color: #EB0A1E;">${conv}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #718096;">Plan de Ahorro:</span>
                <span style="font-weight: 600; color: #2D2D2D;">${pa}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #718096;">Especiales:</span>
                <span style="font-weight: 600; color: #C8102E;">${esp}</span>
            </div>
        </div>
    `;
    
    document.getElementById(elementId).innerHTML = html;
}

function actualizarGraficoMensual() {
    // Agrupar por mes
    const datosPorMes = {};
    
    datosFiltrados.forEach(d => {
        const mesAnio = `${d.fecha.getFullYear()}-${String(d.fecha.getMonth() + 1).padStart(2, '0')}`;
        
        if (!datosPorMes[mesAnio]) {
            datosPorMes[mesAnio] = {
                Convencional: 0,
                'Plan de Ahorro': 0,
                Especial: 0
            };
        }
        
        datosPorMes[mesAnio][d.tipo]++;
    });
    
    // Ordenar meses
    const meses = Object.keys(datosPorMes).sort();
    const labels = meses.map(m => {
        const [anio, mes] = m.split('-');
        const fecha = new Date(anio, parseInt(mes) - 1);
        return fecha.toLocaleDateString('es-AR', { month: 'short', year: 'numeric' });
    });
    
    const datasets = [
        {
            label: 'Convencionales',
            data: meses.map(m => datosPorMes[m].Convencional),
            backgroundColor: 'rgba(235, 10, 30, 0.85)',
            borderColor: 'rgba(235, 10, 30, 1)',
            borderWidth: 2
        },
        {
            label: 'Plan de Ahorro',
            data: meses.map(m => datosPorMes[m]['Plan de Ahorro']),
            backgroundColor: 'rgba(70, 70, 70, 0.85)',
            borderColor: 'rgba(70, 70, 70, 1)',
            borderWidth: 2
        },
        {
            label: 'Especiales',
            data: meses.map(m => datosPorMes[m].Especial),
            backgroundColor: 'rgba(59, 90, 117, 0.85)',
            borderColor: 'rgba(59, 90, 117, 1)',
            borderWidth: 2
        }
    ];
    
    const ctx = document.getElementById('chartMensual');
    
    if (chartMensual) {
        chartMensual.destroy();
    }
    
    chartMensual = new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'top' },
                title: {
                    display: false
                }
            },
            scales: {
                x: { stacked: true },
                y: { 
                    stacked: true,
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

function exportarReporte() {
    const wb = XLSX.utils.book_new();
    
    // Hoja 1: Resumen General
    const resumen = [
        ['REPORTE DE ENTREGAS'],
        [''],
        ['Período:', `${document.getElementById('fechaDesde').value} a ${document.getElementById('fechaHasta').value}`],
        [''],
        ['RESUMEN GENERAL'],
        ['Total Remitos', datosFiltrados.length],
        ['Ventas Convencionales', datosFiltrados.filter(d => d.tipo === 'Convencional').length],
        ['Plan de Ahorro', datosFiltrados.filter(d => d.tipo === 'Plan de Ahorro').length],
        ['Ventas Especiales', datosFiltrados.filter(d => d.tipo === 'Especial').length]
    ];
    
    const ws1 = XLSX.utils.aoa_to_sheet(resumen);
    XLSX.utils.book_append_sheet(wb, ws1, 'Resumen');
    
    // Hoja 2: Detalle por Sucursal
    const detalleSucursal = [
        ['Sucursal', 'Convencionales', 'Plan de Ahorro', 'Especiales', 'Total']
    ];
    
    ['Casa Central', 'San Rafael', 'Bombal'].forEach(suc => {
        const datos = datosFiltrados.filter(d => d.sucursal === suc);
        detalleSucursal.push([
            suc,
            datos.filter(d => d.tipo === 'Convencional').length,
            datos.filter(d => d.tipo === 'Plan de Ahorro').length,
            datos.filter(d => d.tipo === 'Especial').length,
            datos.length
        ]);
    });
    
    const ws2 = XLSX.utils.aoa_to_sheet(detalleSucursal);
    XLSX.utils.book_append_sheet(wb, ws2, 'Por Sucursal');
    
    // Hoja 3: Listado Completo
    const datosExportar = datosFiltrados.map(d => ({
        'Nro. Remito': d.nroRemito,
        'Fecha': d.fecha.toLocaleDateString('es-AR'),
        'Nro. Fábrica': d.nroFabrica,
        'Modelo': d.modelo,
        'Tipo Venta': d.tipo,
        'Sucursal': d.sucursal
    }));
    
    const ws3 = XLSX.utils.json_to_sheet(datosExportar);
    XLSX.utils.book_append_sheet(wb, ws3, 'Detalle Completo');
    
    // Descargar
    const fecha = new Date().toISOString().split('T')[0];
    XLSX.writeFile(wb, `reporte_entregas_${fecha}.xlsx`);
    
    showSuccess('Reporte exportado correctamente');
}

function limpiarTodo() {
    datosConvencional = [];
    datosPlanAhorro = [];
    datosFiltrados = [];
    
    document.getElementById('convencionalStatus').style.display = 'none';
    document.getElementById('planAhorroStatus').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'none';
    
    fileConv.value = '';
    filePA.value = '';
    
    btnProcesar.disabled = true;
    
    if (chartMensual) {
        chartMensual.destroy();
        chartMensual = null;
    }
    
    showSuccess('Datos limpiados correctamente');
}

function showSuccess(message) {
    successAlert.querySelector('#successMessage').textContent = message;
    successAlert.style.display = 'block';
    errorAlert.style.display = 'none';
    
    setTimeout(() => {
        successAlert.style.display = 'none';
    }, 5000);
}

function showError(message) {
    errorAlert.querySelector('#errorMessage').textContent = message;
    errorAlert.style.display = 'block';
    successAlert.style.display = 'none';
    
    setTimeout(() => {
        errorAlert.style.display = 'none';
    }, 5000);
}
