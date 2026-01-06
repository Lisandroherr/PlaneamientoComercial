// Lista completa de modelos de vehículos
const MODELOS_COMPLETOS = [
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
];

// Datos globales
let preciosData = {
    modelos: [],
    modelos_ocultos: []
};

let descuentosData = [];

// Función para obtener nombres de meses dinámicamente
function obtenerNombresMeses() {
    const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    const hoy = new Date();
    const mesActual = hoy.getMonth(); // 0-11
    
    return {
        menosDos: meses[(mesActual - 2 + 12) % 12],
        menosUno: meses[(mesActual - 1 + 12) % 12],
        actual: meses[mesActual],
        masUno: meses[(mesActual + 1) % 12]
    };
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    cargarPrecios();
    cargarDescuentos();
    initTabs();
    actualizarEncabezadosMeses();
});

// Inicializar pestañas
function initTabs() {
    document.querySelectorAll('.nav-link').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            document.querySelectorAll('.nav-link').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            this.classList.add('active');
            const targetId = this.getAttribute('data-bs-target');
            const targetPane = document.querySelector(targetId);
            if (targetPane) {
                targetPane.classList.add('show', 'active');
            }
        });
    });
}

// ==================== SECCIÓN 1: PRECIOS ====================

function cargarPrecios() {
    console.log('🔄 Cargando precios desde la base de datos...');
    fetch('/api/precios')
        .then(response => response.json())
        .then(data => {
            preciosData = data;
            console.log('✅ Precios cargados:', preciosData);
            renderizarTablasPrecios();
        })
        .catch(error => {
            console.error('❌ Error al cargar precios:', error);
            mostrarAlerta('Error al cargar los precios', 'error');
        });
}

function renderizarTablasPrecios() {
    // Obtener todas las tablas
    const tablas = {
        corollaSedan: document.getElementById('tablaCorollaSedan'),
        corollaCross: document.getElementById('tablaCorollaCross'),
        hiace: document.getElementById('tablaHiace'),
        hilux4x2: document.getElementById('tablaHilux4x2'),
        hilux4x4: document.getElementById('tablaHilux4x4'),
        sw4: document.getElementById('tablaSw4'),
        yaris: document.getElementById('tablaYaris'),
        otros: document.getElementById('tablaOtros')
    };
    
    // Limpiar todas las tablas
    Object.values(tablas).forEach(tabla => tabla.innerHTML = '');
    
    // Contadores
    const contadores = {
        corollaSedan: 0,
        corollaCross: 0,
        hiace: 0,
        hilux4x2: 0,
        hilux4x4: 0,
        sw4: 0,
        yaris: 0,
        otros: 0
    };
    
    // Ordenar modelos por ID antes de renderizar
    const modelosOrdenados = [...preciosData.modelos].sort((a, b) => {
        const idA = parseInt(a.id_modelo) || 999;
        const idB = parseInt(b.id_modelo) || 999;
        return idA - idB;
    });
    
    modelosOrdenados.forEach((modelo, index) => {
        // Obtener el índice real en el array original para las actualizaciones
        const indexReal = preciosData.modelos.findIndex(m => m.nombre === modelo.nombre);
        // Saltar modelos ocultos
        if (preciosData.modelos_ocultos.includes(modelo.nombre)) {
            return;
        }
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <input type="text" class="form-input" value="${modelo.id_modelo || ''}" 
                       placeholder="ID" style="width: 70px;"
                       onchange="actualizarPrecio(${indexReal}, 'id_modelo', this.value)">
            </td>
            <td>
                <input type="text" class="form-input" value="${modelo.id_salesforce || ''}" 
                       placeholder="ID SF" style="width: 110px;"
                       onchange="actualizarPrecio(${indexReal}, 'id_salesforce', this.value)">
            </td>
            <td style="font-weight: 600;">${modelo.nombre}</td>
            <td>
                <input type="number" class="form-input" value="${modelo.precio_ars || 0}" 
                       onchange="actualizarPrecio(${indexReal}, 'precio_ars', this.value)">
            </td>
            <td>
                <input type="number" class="form-input" value="${modelo.precio_usd || 0}" 
                       onchange="actualizarPrecio(${indexReal}, 'precio_usd', this.value)">
            </td>
            <td>
                <input type="number" class="form-input" value="${modelo.cotizacion || 1000}" 
                       onchange="actualizarPrecio(${indexReal}, 'cotizacion', this.value)">
            </td>
        `;
        
        // Determinar a qué tabla pertenece según el ID
        const idModelo = parseInt(modelo.id_modelo);
        
        if (idModelo >= 1 && idModelo <= 6) {
            tablas.corollaSedan.appendChild(tr);
            contadores.corollaSedan++;
        } else if (idModelo >= 7 && idModelo <= 12) {
            tablas.corollaCross.appendChild(tr);
            contadores.corollaCross++;
        } else if (idModelo >= 13 && idModelo <= 15) {
            tablas.hiace.appendChild(tr);
            contadores.hiace++;
        } else if ((idModelo >= 16 && idModelo <= 23)) {
            tablas.hilux4x2.appendChild(tr);
            contadores.hilux4x2++;
        } else if (idModelo >= 24 && idModelo <= 33) {
            tablas.hilux4x4.appendChild(tr);
            contadores.hilux4x4++;
        } else if ([36, 37, 38].includes(idModelo)) {
            tablas.sw4.appendChild(tr);
            contadores.sw4++;
        } else if ([39, 40, 41, 42].includes(idModelo)) {
            tablas.yaris.appendChild(tr);
            contadores.yaris++;
        } else {
            tablas.otros.appendChild(tr);
            contadores.otros++;
        }
    });
    
    // Actualizar contadores
    document.getElementById('countCorollaSedan').textContent = contadores.corollaSedan;
    document.getElementById('countCorollaCross').textContent = contadores.corollaCross;
    document.getElementById('countHiace').textContent = contadores.hiace;
    document.getElementById('countHilux4x2').textContent = contadores.hilux4x2;
    document.getElementById('countHilux4x4').textContent = contadores.hilux4x4;
    document.getElementById('countSw4').textContent = contadores.sw4;
    document.getElementById('countYaris').textContent = contadores.yaris;
    document.getElementById('countOtros').textContent = contadores.otros;
}

function actualizarPrecio(index, campo, valor) {
    if (campo === 'id_modelo' || campo === 'id_salesforce') {
        preciosData.modelos[index][campo] = valor;
    } else {
        preciosData.modelos[index][campo] = parseFloat(valor) || 0;
    }
}

function guardarPrecios() {
    const btnGuardar = event.target;
    const textoOriginal = btnGuardar.innerHTML;
    
    btnGuardar.disabled = true;
    btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    
    fetch('/api/precios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preciosData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            btnGuardar.innerHTML = '<i class="fas fa-check-circle"></i> ¡Guardado!';
            btnGuardar.style.background = '#48bb78';
            mostrarAlerta('Precios guardados exitosamente', 'success');
            
            setTimeout(() => {
                btnGuardar.innerHTML = textoOriginal;
                btnGuardar.disabled = false;
                btnGuardar.style.background = '';
            }, 2000);
        } else {
            btnGuardar.innerHTML = textoOriginal;
            btnGuardar.disabled = false;
            mostrarAlerta('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        btnGuardar.innerHTML = textoOriginal;
        btnGuardar.disabled = false;
        mostrarAlerta('Error al guardar los precios', 'error');
    });
}

// ==================== SECCIÓN 2: DESCUENTOS ====================

function actualizarEncabezadosMeses() {
    const nombresMeses = obtenerNombresMeses();
    
    // Actualizar encabezados de la tabla - seleccionar la segunda fila de encabezados
    const segundaFilaHeaders = document.querySelectorAll('#tablaDescuentos thead tr:nth-child(2) th');
    
    // Los encabezados de fecha son los primeros 4 en la segunda fila (índices 0-3)
    if (segundaFilaHeaders.length >= 4) {
        segundaFilaHeaders[0].innerHTML = nombresMeses.menosDos;
        segundaFilaHeaders[1].innerHTML = nombresMeses.menosUno;
        segundaFilaHeaders[2].innerHTML = nombresMeses.actual;
        segundaFilaHeaders[3].innerHTML = 'Posterior';
    }
}

function cargarDescuentos() {
    console.log('🔄 Cargando descuentos matriz...');
    fetch('/api/descuentos_matriz')
        .then(response => {
            console.log('📡 Respuesta descuentos:', response.status);
            return response.json();
        })
        .then(data => {
            descuentosData = data;
            console.log('✅ Descuentos cargados:', descuentosData.length, 'modelos');
            console.log('📊 Primer modelo:', descuentosData[0]);
            renderizarTablaDescuentos();
        })
        .catch(error => {
            console.error('❌ Error al cargar descuentos:', error);
            mostrarAlerta('Error al cargar los descuentos', 'error');
        });
}

function renderizarTablaDescuentos() {
    const tbody = document.getElementById('tablaDescuentosBody');
    tbody.innerHTML = '';
    
    descuentosData.forEach((modelo, index) => {
        // Saltar modelos ocultos
        if (preciosData.modelos_ocultos.includes(modelo.modelo)) {
            return;
        }
        
        const tr = document.createElement('tr');
        tr.setAttribute('data-modelo', modelo.modelo.toLowerCase());
        tr.setAttribute('data-index', index); // Guardar índice real
        
        tr.innerHTML = `
            <td style="font-weight: 600; position: sticky; left: 0; background: white; z-index: 5;">
                ${modelo.modelo}
            </td>
            <!-- Fecha de Despacho -->
            <td class="fecha-cell">
                <input type="number" class="desc-input" min="0" max="100" step="0.5" 
                       value="${modelo.desc_mes_actual_menos_2 || 0}"
                       data-index="${index}" data-campo="desc_mes_actual_menos_2"
                       onchange="actualizarDescuentoPorEvento(this)">
            </td>
            <td class="fecha-cell">
                <input type="number" class="desc-input" min="0" max="100" step="0.5" 
                       value="${modelo.desc_mes_actual_menos_1 || 0}"
                       data-index="${index}" data-campo="desc_mes_actual_menos_1"
                       onchange="actualizarDescuentoPorEvento(this)">
            </td>
            <td class="fecha-cell">
                <input type="number" class="desc-input" min="0" max="100" step="0.5" 
                       value="${modelo.desc_mes_actual || 0}"
                       data-index="${index}" data-campo="desc_mes_actual"
                       onchange="actualizarDescuentoPorEvento(this)">
            </td>
            <td class="fecha-cell">
                <input type="number" class="desc-input" min="0" max="100" step="0.5" 
                       value="${modelo.desc_mes_actual_mas || 0}"
                       data-index="${index}" data-campo="desc_mes_actual_mas"
                       onchange="actualizarDescuentoPorEvento(this)">
            </td>
            <!-- Ubicación -->
            <td class="ubicacion-cell">
                <input type="number" class="desc-input" min="0" max="100" step="0.5" 
                       value="${modelo.desc_stock || 0}"
                       data-index="${index}" data-campo="desc_stock"
                       onchange="actualizarDescuentoPorEvento(this)">
            </td>
            <td class="ubicacion-cell">
                <input type="number" class="desc-input" min="0" max="100" step="0.5" 
                       value="${modelo.desc_produccion || 0}"
                       data-index="${index}" data-campo="desc_produccion"
                       onchange="actualizarDescuentoPorEvento(this)">
            </td>
            <td class="ubicacion-cell">
                <input type="number" class="desc-input" min="0" max="100" step="0.5" 
                       value="${modelo.desc_playa_externa || 0}"
                       data-index="${index}" data-campo="desc_playa_externa"
                       onchange="actualizarDescuentoPorEvento(this)">
            </td>
            <td class="ubicacion-cell">
                <input type="number" class="desc-input" min="0" max="100" step="0.5" 
                       value="${modelo.desc_otro || 0}"
                       data-index="${index}" data-campo="desc_otro"
                       onchange="actualizarDescuentoPorEvento(this)">
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

function actualizarDescuento(index, campo, valor) {
    descuentosData[index][campo] = parseFloat(valor) || 0;
}

function actualizarDescuentoPorEvento(input) {
    const index = parseInt(input.getAttribute('data-index'));
    const campo = input.getAttribute('data-campo');
    const valor = parseFloat(input.value) || 0;
    
    console.log(`📝 Actualizando descuento: índice=${index}, campo=${campo}, valor=${valor}`);
    
    if (descuentosData[index]) {
        descuentosData[index][campo] = valor;
        console.log('✅ Actualizado:', descuentosData[index].modelo, campo, '=', valor);
    } else {
        console.error('❌ Índice inválido:', index);
    }
}

function filtrarTablaDescuentos() {
    const busqueda = document.getElementById('buscarModelo').value.toLowerCase();
    const filas = document.querySelectorAll('#tablaDescuentosBody tr');
    
    filas.forEach(fila => {
        const modelo = fila.getAttribute('data-modelo');
        if (modelo.includes(busqueda)) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
}

function expandirTodos() {
    // Funcionalidad futura para agrupar por familia
    mostrarAlerta('Función en desarrollo', 'info');
}

function contraerTodos() {
    // Funcionalidad futura para agrupar por familia
    mostrarAlerta('Función en desarrollo', 'info');
}

function guardarDescuentos() {
    const btnGuardar = event.target;
    const textoOriginal = btnGuardar.innerHTML;
    
    console.log('💾 Guardando descuentos...', descuentosData);
    
    btnGuardar.disabled = true;
    btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    
    fetch('/api/descuentos_matriz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(descuentosData)
    })
    .then(response => {
        console.log('📡 Respuesta del servidor:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📦 Datos recibidos:', data);
        if (data.success) {
            btnGuardar.innerHTML = '<i class="fas fa-check-circle"></i> ¡Guardado!';
            btnGuardar.style.background = '#48bb78';
            mostrarAlerta('Descuentos guardados exitosamente', 'success');
            
            setTimeout(() => {
                btnGuardar.innerHTML = textoOriginal;
                btnGuardar.disabled = false;
                btnGuardar.style.background = '';
            }, 2000);
        } else {
            btnGuardar.innerHTML = textoOriginal;
            btnGuardar.disabled = false;
            mostrarAlerta('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        btnGuardar.innerHTML = textoOriginal;
        btnGuardar.disabled = false;
        mostrarAlerta('Error al guardar los descuentos', 'error');
    });
}

// ==================== GESTIÓN DE MODELOS ====================

function abrirModalGestionModelos() {
    const modal = document.getElementById('modalGestionModelos');
    const lista = document.getElementById('listaGestionModelos');
    
    lista.innerHTML = '';
    
    let contadorSeleccionados = 0;
    
    MODELOS_COMPLETOS.forEach(modelo => {
        const isVisible = !preciosData.modelos_ocultos.includes(modelo);
        if (isVisible) contadorSeleccionados++;
        
        const div = document.createElement('div');
        div.style.cssText = 'display: flex; align-items: center; gap: 8px; padding: 8px; background: #f7fafc; border-radius: 4px;';
        const checkboxId = 'check_' + modelo.replace(/[^a-zA-Z0-9]/g, '_');
        div.innerHTML = `
            <input type="checkbox" id="${checkboxId}" 
                   ${isVisible ? 'checked' : ''} 
                   style="cursor: pointer;"
                   onchange="actualizarContadorModelos()">
            <label for="${checkboxId}" 
                   style="cursor: pointer; flex: 1; font-size: 0.9em; user-select: none;">
                ${modelo}
            </label>
        `;
        lista.appendChild(div);
    });
    
    // Actualizar contador inicial
    document.getElementById('contadorModelos').textContent = contadorSeleccionados;
    
    modal.style.display = 'flex';
}

function actualizarContadorModelos() {
    let contador = 0;
    MODELOS_COMPLETOS.forEach(modelo => {
        const checkbox = document.getElementById('check_' + modelo.replace(/[^a-zA-Z0-9]/g, '_'));
        if (checkbox && checkbox.checked) {
            contador++;
        }
    });
    document.getElementById('contadorModelos').textContent = contador;
}

function cerrarModalGestionModelos() {
    const modal = document.getElementById('modalGestionModelos');
    modal.style.display = 'none';
}

function aplicarCambiosModelos() {
    const btnAplicar = document.getElementById('btnAplicarModelos');
    const textoOriginal = btnAplicar.innerHTML;
    
    // Deshabilitar botón y mostrar spinner
    btnAplicar.disabled = true;
    btnAplicar.style.opacity = '0.7';
    btnAplicar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    
    const nuevosOcultos = [];
    
    MODELOS_COMPLETOS.forEach(modelo => {
        const checkbox = document.getElementById('check_' + modelo.replace(/[^a-zA-Z0-9]/g, '_'));
        if (checkbox && !checkbox.checked) {
            nuevosOcultos.push(modelo);
        }
    });
    
    preciosData.modelos_ocultos = nuevosOcultos;
    
    console.log('🔄 Aplicando cambios de visibilidad:', nuevosOcultos);
    
    // Guardar cambios en la base de datos
    fetch('/api/precios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preciosData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar éxito temporalmente
            btnAplicar.innerHTML = '<i class="fas fa-check-circle"></i> ¡Guardado!';
            btnAplicar.style.background = '#48bb78';
            
            // Re-renderizar tanto precios como descuentos con los nuevos filtros
            renderizarTablasPrecios();
            renderizarTablaDescuentos();
            
            mostrarAlerta(`Visibilidad guardada: ${MODELOS_COMPLETOS.length - nuevosOcultos.length} modelos visibles`, 'success');
            
            // Cerrar modal y restaurar botón después de 1 segundo
            setTimeout(() => {
                cerrarModalGestionModelos();
                btnAplicar.innerHTML = textoOriginal;
                btnAplicar.disabled = false;
                btnAplicar.style.opacity = '1';
                btnAplicar.style.background = '';
            }, 1000);
        } else {
            btnAplicar.innerHTML = textoOriginal;
            btnAplicar.disabled = false;
            btnAplicar.style.opacity = '1';
            mostrarAlerta('Error al guardar: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        btnAplicar.innerHTML = textoOriginal;
        btnAplicar.disabled = false;
        btnAplicar.style.opacity = '1';
        mostrarAlerta('Error al guardar la visibilidad', 'error');
    });
}

// ==================== UTILIDADES ====================

function mostrarAlerta(mensaje, tipo) {
    const colores = {
        success: { bg: '#48bb78', icon: 'check-circle' },
        error: { bg: '#f56565', icon: 'exclamation-circle' },
        info: { bg: '#4299e1', icon: 'info-circle' }
    };
    
    const color = colores[tipo] || colores.info;
    
    const alerta = document.createElement('div');
    alerta.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${color.bg};
        color: white;
        padding: 15px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 9999;
        font-weight: 600;
        animation: slideIn 0.3s ease-out;
    `;
    alerta.innerHTML = `<i class="fas fa-${color.icon}"></i> ${mensaje}`;
    
    document.body.appendChild(alerta);
    
    setTimeout(() => {
        alerta.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => alerta.remove(), 300);
    }, 3000);
}

// ==================== EXPORTAR A EXCEL ====================

function exportarPreciosExcel() {
    // IDs que no deben tener precio total calculado
    const idsExcluidos = [13, 15, 35, 34, 42];
    
    // Orden de grupos para exportación
    const ordenGrupos = [
        { nombre: 'HILUX 4X2', rango: (id) => id >= 16 && id <= 23 },
        { nombre: 'HILUX 4X4', rango: (id) => id >= 24 && id <= 33 },
        { nombre: 'SW4', rango: (id) => [36, 37, 38].includes(id) },
        { nombre: 'YARIS', rango: (id) => [39, 40, 41, 42].includes(id) },
        { nombre: 'COROLLA SEDAN', rango: (id) => id >= 1 && id <= 6 },
        { nombre: 'COROLLA CROSS', rango: (id) => id >= 7 && id <= 12 },
        { nombre: 'HIACE', rango: (id) => id >= 13 && id <= 15 },
        { nombre: 'OTROS', rango: (id) => true } // Captura todo lo demás
    ];
    
    // Filtrar modelos visibles, excluir los que empiezan con "SC" (excepto ID 5 y 6) y ordenar por ID
    const modelosVisibles = preciosData.modelos
        .filter(m => !preciosData.modelos_ocultos.includes(m.nombre))
        .filter(m => {
            const id = parseInt(m.id_modelo);
            // Permitir ID 5 y 6 aunque empiecen con SC
            if (id === 5 || id === 6) return true;
            // Excluir todos los demás que empiecen con SC
            return !m.nombre.startsWith('SC');
        })
        .sort((a, b) => {
            const idA = parseInt(a.id_modelo) || 999;
            const idB = parseInt(b.id_modelo) || 999;
            return idA - idB;
        });
    
    // Eliminar duplicados de ID - quedarse solo con la primera ocurrencia de cada ID
    const idsVistos = new Set();
    const modelosSinDuplicados = modelosVisibles.filter(m => {
        const id = m.id_modelo;
        if (idsVistos.has(id)) {
            return false;
        }
        idsVistos.add(id);
        return true;
    });
    
    // Organizar modelos por grupo
    const modelosPorGrupo = {};
    ordenGrupos.forEach(grupo => {
        modelosPorGrupo[grupo.nombre] = [];
    });
    
    modelosSinDuplicados.forEach(modelo => {
        const idModelo = parseInt(modelo.id_modelo);
        let asignado = false;
        
        // Asignar a grupo específico (excepto OTROS)
        for (let i = 0; i < ordenGrupos.length - 1; i++) {
            if (ordenGrupos[i].rango(idModelo)) {
                modelosPorGrupo[ordenGrupos[i].nombre].push(modelo);
                asignado = true;
                break;
            }
        }
        
        // Si no fue asignado, va a OTROS
        if (!asignado) {
            modelosPorGrupo['OTROS'].push(modelo);
        }
    });
    
    // Crear datos para Excel
    const datos = [];
    
    // Encabezados
    datos.push(['Grupo', 'ID', 'ID SalesForce', 'Modelo', 'Precio Total', 'Precio Unidad', 'Flete y Formulario', 'Patentamiento']);
    
    // Agregar datos por grupo
    ordenGrupos.forEach(grupo => {
        const modelos = modelosPorGrupo[grupo.nombre];
        
        if (modelos.length > 0) {
            modelos.forEach(modelo => {
                const idModelo = parseInt(modelo.id_modelo);
                let precioTotal = '';
                
                // Calcular precio total solo si no está en la lista de excluidos
                if (!idsExcluidos.includes(idModelo)) {
                    const precioUnidad = parseFloat(modelo.precio_ars) || 0;
                    const flete = parseFloat(modelo.precio_usd) || 0;
                    const patentamiento = parseFloat(modelo.cotizacion) || 0;
                    precioTotal = precioUnidad + flete + patentamiento;
                }
                
                // Truncar "SC - " del nombre si es ID 5 o 6
                let nombreModelo = modelo.nombre;
                if ((idModelo === 5 || idModelo === 6) && nombreModelo.startsWith('SC - ')) {
                    nombreModelo = nombreModelo.substring(5);
                }
                
                datos.push([
                    grupo.nombre,
                    modelo.id_modelo || '',
                    modelo.id_salesforce || '',
                    nombreModelo,
                    precioTotal,
                    parseFloat(modelo.precio_ars) || 0,
                    parseFloat(modelo.precio_usd) || 0,
                    parseFloat(modelo.cotizacion) || 0
                ]);
            });
        }
    });
    
    // Crear workbook y worksheet
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(datos);
    
    // Configurar anchos de columna
    ws['!cols'] = [
        { wch: 18 }, // Grupo
        { wch: 5 },  // ID
        { wch: 15 }, // ID SalesForce
        { wch: 40 }, // Modelo
        { wch: 15 }, // Precio Total
        { wch: 15 }, // Precio Unidad
        { wch: 20 }, // Flete y Formulario
        { wch: 15 }  // Patentamiento
    ];
    
    // Agregar hoja al libro
    XLSX.utils.book_append_sheet(wb, ws, 'Lista de Precios');
    
    // Descargar archivo
    const fecha = new Date().toISOString().split('T')[0];
    XLSX.writeFile(wb, `Lista_Precios_${fecha}.xlsx`);
    
    mostrarAlerta('Archivo Excel exportado exitosamente', 'success');
}
