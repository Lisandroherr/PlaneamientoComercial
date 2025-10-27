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

// Mapeo de modelos SC a sus equivalentes convencionales
const SC_MAPPING = {
    "SC - COROLLA 2.0 SEG SAFETY CVT": "COROLLA 2.0 SEG CVT",
    "SC - COROLLA GR-SPORT SAFETY 2.0 CVT": "COROLLA CROSS GR-SPORT SAFETY 2.0 CVT",
    "SC - COROLLA HEV 1.8 SEG SAFETY eCVT": "COROLLA HEV 1.8 XEI SAFETY eCVT",
    "SC - HILUX 4X2 D/C SR 2.4 TDI 6 M/T": "HILUX 4X2 D/C SR 2.4 TDI 6 M/T",
    "SC - HILUX 4X2 D/C SR 2.4 TDI 6A/T": "HILUX 4X2 D/C SR 2.4 TDI 6 A/T",
    "SC - HILUX 4X2 D/C SRV 2.8 TDI 6A/T": "HILUX 4X4 D/C SRV 2.8 TDI 6A/T",
    "SC - HILUX 4X2 D/C SRX 2.8 TDI 6A/T": "HILUX 4X2 D/C SRX 2.8 TDI 6A/T",
    "SC - HILUX 4X4 D/C SR 2.8 TDI 6A/T": "HILUX 4X4 D/C SR 2.8 TDI 6A/T",
    "SC - HILUX 4X4 D/C SR 2.8 TDI 6MT": "HILUX 4X4 D/C SR 2.8 TDI 6MT",
    "SC - HILUX 4X4 D/C SRV 2.8 TDI 6A/T": "HILUX 4X4 D/C SRV 2.8 TDI 6A/T",
    "SC - HILUX 4X4 D/C SRX 2.8 TDI 6A/T": "HILUX 4X4 D/C SRX 2.8 TDI 6A/T",
    "SC - HILUX D/C GR-S SPORT IV 2.8 TDI 6AT": "HILUX 4X4 DC GR-SPORT IV 2.8 TDI 6 AT",
    "SC - SW4 4X4 DIAMOND 2.8 TDI 6 A/T 7A": "SW4 4X4 DIAMOND 2.8 TDI 6 A/T 7A",
    "SC - SW4 4X4 GR-S TDI 6AT 7A": "SW4 4X4 GR-S TDI 6AT 7A",
    "SC - SW4 4X4 SRX 2.8 TDI 6A/T 7A": "SW4 4X4 SRX 2.8 TDI 6 A/T 7A"
};

// Datos de precios
let preciosData = {
    modelos: [],
    modelos_ocultos: []
};

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    cargarPrecios();
    cargarDescuentosAdicionales();
    initTabs();
});

// Función para inicializar las pestañas
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

// Cargar precios desde el servidor o inicializar
function cargarPrecios() {
    console.log('🔄 Cargando precios desde la base de datos...');
    fetch('/api/precios')
        .then(response => {
            console.log('📡 Respuesta de precios:', response.status);
            return response.json();
        })
        .then(data => {
            preciosData = data;
            
            console.log('✅ Precios cargados desde BD:', preciosData);
            console.log('📊 Total de modelos:', preciosData.modelos.length);
            console.log('🚫 Modelos ocultos:', preciosData.modelos_ocultos.length);
            
            renderizarControlesFamilias();
            renderizarTablas();
        })
        .catch(error => {
            console.error('❌ Error al cargar precios:', error);
            mostrarAlerta('Error al cargar los precios', 'error');
        });
}

// Renderizar controles de descuentos por familia
function renderizarControlesFamilias() {
    const familias = ['COROLLA', 'COROLLA CROSS', 'HILUX', 'SW4', 'YARIS', 'YARIS GR', 'HIACE', 'LAND CRUISER', 'RAV 4'];
    const container = document.getElementById('familiaControls');
    
    container.innerHTML = familias.map(familia => {
        const familiaId = familia.replace(/ /g, '_').replace(/\//g, '_');
        return `
        <div style="display: flex; align-items: center; gap: 8px; background: white; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">
            <label style="font-weight: 600; color: #2d3748; min-width: 130px; font-size: 0.88em; flex-shrink: 0;">${familia}:</label>
            <input type="number" id="desc_${familiaId}" min="0" max="100" step="0.5" 
                   style="width: 80px; padding: 8px; border: 1px solid #cbd5e0; border-radius: 4px; text-align: center; flex-shrink: 0;"
                   placeholder="0">
            <button onclick="aplicarDescuentoFamilia('${familia.replace(/'/g, "\\'")}')" 
                    class="btn-aplicar-familia"
                    style="background: #EB0A1E; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 0.88em; white-space: nowrap; flex-shrink: 0; transition: background 0.2s;">
                <i class="fas fa-check"></i> Aplicar
            </button>
        </div>
        `;
    }).join('');
    
    // Agregar hover effect
    document.querySelectorAll('.btn-aplicar-familia').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.background = '#C8102E';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.background = '#EB0A1E';
        });
    });
}

// Aplicar descuento a toda una familia
function aplicarDescuentoFamilia(familia) {
    const inputId = 'desc_' + familia.replace(/ /g, '_');
    const descuento = parseFloat(document.getElementById(inputId).value) || 0;
    
    if (descuento < 0 || descuento > 100) {
        mostrarAlerta('El descuento debe estar entre 0 y 100', 'error');
        return;
    }
    
    fetch('/api/descuento_familia', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ familia: familia, descuento: descuento })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarAlerta(`Descuento del ${descuento}% aplicado a ${data.modelos_actualizados} modelos de ${familia}`, 'success');
            cargarPrecios(); // Recargar para ver los cambios
        } else {
            mostrarAlerta('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al aplicar descuento', 'error');
    });
}

// Cargar descuentos adicionales desde el servidor
function cargarDescuentosAdicionales() {
    fetch('/api/descuentos_adicionales')
        .then(response => response.json())
        .then(data => {
            // Cargar descuento por stock
            if (data.stock) {
                document.getElementById('descuentoStock').value = data.stock.descuento_stock || 0;
            }
            
            // Cargar descuentos por color
            if (data.color) {
                document.getElementById('descuento_super_blanco').value = data.color.super_blanco || 0;
                document.getElementById('descuento_blanco_perlado').value = data.color.blanco_perlado || 0;
                document.getElementById('descuento_gris_plata').value = data.color.gris_plata || 0;
                document.getElementById('descuento_gris_azulado').value = data.color.gris_azulado || 0;
                document.getElementById('descuento_gris_oscuro').value = data.color.gris_oscuro || 0;
                document.getElementById('descuento_rojo_metalizado').value = data.color.rojo_metalizado || 0;
                document.getElementById('descuento_negro_mica').value = data.color.negro_mica || 0;
            }
            
            // Cargar descuento por antigüedad
            if (data.antiguedad) {
                document.getElementById('mesesAntiguedad').value = data.antiguedad.meses || 3;
                document.getElementById('descuentoAntiguedad').value = data.antiguedad.descuento || 0;
            }
        })
        .catch(error => {
            console.error('Error al cargar descuentos adicionales:', error);
        });
}

// Guardar descuentos adicionales
function guardarDescuentosAdicionales() {
    const descuentos = {
        stock: {
            descuento_stock: parseFloat(document.getElementById('descuentoStock').value) || 0
        },
        color: {
            super_blanco: parseFloat(document.getElementById('descuento_super_blanco').value) || 0,
            blanco_perlado: parseFloat(document.getElementById('descuento_blanco_perlado').value) || 0,
            gris_plata: parseFloat(document.getElementById('descuento_gris_plata').value) || 0,
            gris_azulado: parseFloat(document.getElementById('descuento_gris_azulado').value) || 0,
            gris_oscuro: parseFloat(document.getElementById('descuento_gris_oscuro').value) || 0,
            rojo_metalizado: parseFloat(document.getElementById('descuento_rojo_metalizado').value) || 0,
            negro_mica: parseFloat(document.getElementById('descuento_negro_mica').value) || 0
        },
        antiguedad: {
            meses: parseFloat(document.getElementById('mesesAntiguedad').value) || 3,
            descuento: parseFloat(document.getElementById('descuentoAntiguedad').value) || 0
        }
    };
    
    fetch('/api/descuentos_adicionales', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(descuentos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarAlerta('Descuentos adicionales guardados correctamente. Se aplicarán en el Módulo 4 (Disponible)', 'success');
        } else {
            mostrarAlerta('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al guardar descuentos adicionales', 'error');
    });
}


// Renderizar las tablas
function renderizarTablas() {
    const tablaConv = document.getElementById('tablaConvencionales');
    const tablaSC = document.getElementById('tablaSC');
    
    tablaConv.innerHTML = '';
    tablaSC.innerHTML = '';
    
    let contConv = 0;
    let contSC = 0;
    
    preciosData.modelos.forEach((modelo, index) => {
        // Verificar si el modelo está oculto
        if (preciosData.modelos_ocultos.includes(modelo.nombre)) {
            return; // Saltar modelos ocultos
        }
        
        if (modelo.nombre.startsWith('SC -')) {
            // Modelo SC (solo lectura)
            contSC++;
            const row = crearFilaSC(modelo, index);
            tablaSC.appendChild(row);
        } else {
            // Modelo convencional (editable)
            contConv++;
            const row = crearFilaConvencional(modelo, index);
            tablaConv.appendChild(row);
        }
    });
    
    // Actualizar contadores
    document.getElementById('countConvencionales').textContent = contConv;
    document.getElementById('countSC').textContent = contSC;
}

// Crear fila editable para modelo convencional
function crearFilaConvencional(modelo, index) {
    const tr = document.createElement('tr');
    
    const precioArs = modelo.precio_ars || 0;
    const precioUsd = modelo.precio_usd || 0;
    const cotizacion = modelo.cotizacion || 1000;
    const descuento = modelo.descuento || 0;
    const dadoBaja = modelo.dado_baja || 0;
    const familia = modelo.familia || 'OTROS';
    
    // Aplicar estilo si está dado de baja
    if (dadoBaja === 1) {
        tr.style.cssText = 'background-color: #fff5f5; opacity: 0.7;';
    }
    
    tr.innerHTML = `
        <td style="background: #f7fafc; font-weight: 600; color: #4a5568; font-size: 0.85em;">${familia}</td>
        <td><strong>${modelo.nombre}</strong></td>
        <td>
            <input type="number" 
                   class="form-input input-precio-ars" 
                   value="${precioArs}" 
                   data-index="${index}"
                   data-campo="precio_ars"
                   style="width: 100%; padding: 8px;">
        </td>
        <td>
            <input type="number" 
                   class="form-input input-precio-usd" 
                   value="${precioUsd}" 
                   data-index="${index}"
                   data-campo="precio_usd"
                   style="width: 100%; padding: 8px;">
        </td>
        <td>
            <input type="number" 
                   class="form-input input-cotizacion" 
                   value="${cotizacion}" 
                   data-index="${index}"
                   data-campo="cotizacion"
                   style="width: 100%; padding: 8px;">
        </td>
        <td>
            <input type="number" 
                   class="form-input" 
                   value="${descuento}" 
                   data-index="${index}"
                   data-campo="descuento"
                   style="width: 100%; padding: 8px;" 
                   min="0" 
                   max="100">
        </td>
        <td style="text-align: center;">
            <input type="checkbox" 
                   class="checkbox-baja"
                   ${dadoBaja === 1 ? 'checked' : ''}
                   data-index="${index}"
                   style="width: 20px; height: 20px; cursor: pointer;"
                   title="Marcar como dado de baja">
        </td>
    `;
    
    // Agregar event listeners específicos
    const inputPrecioUsd = tr.querySelector('.input-precio-usd');
    const inputCotizacion = tr.querySelector('.input-cotizacion');
    const inputPrecioArs = tr.querySelector('.input-precio-ars');
    
    // Cuando cambia el precio USD, calcular ARS automáticamente
    inputPrecioUsd.addEventListener('change', function() {
        const idx = parseInt(this.dataset.index);
        const valorUsd = parseFloat(this.value) || 0;
        const cotizacion = parseFloat(inputCotizacion.value) || 1000;
        
        // Calcular precio ARS = USD × Cotización
        const precioArs = valorUsd * cotizacion;
        
        // Actualizar el input de ARS
        inputPrecioArs.value = precioArs;
        
        // Guardar ambos valores
        preciosData.modelos[idx].precio_usd = valorUsd;
        preciosData.modelos[idx].precio_ars = precioArs;
        
        // Sincronizar con modelo SC si existe
        sincronizarModeloSC(idx);
    });
    
    // Cuando cambia la cotización, recalcular ARS si hay USD
    inputCotizacion.addEventListener('change', function() {
        const idx = parseInt(this.dataset.index);
        const cotizacion = parseFloat(this.value) || 1000;
        const valorUsd = parseFloat(inputPrecioUsd.value) || 0;
        
        // Si hay un precio USD, recalcular ARS
        if (valorUsd > 0) {
            const precioArs = valorUsd * cotizacion;
            inputPrecioArs.value = precioArs;
            preciosData.modelos[idx].precio_ars = precioArs;
        }
        
        preciosData.modelos[idx].cotizacion = cotizacion;
        sincronizarModeloSC(idx);
    });
    
    // Para precio ARS y descuento, solo actualizar sin calcular nada
    inputPrecioArs.addEventListener('change', function() {
        const idx = parseInt(this.dataset.index);
        const valor = parseFloat(this.value) || 0;
        preciosData.modelos[idx].precio_ars = valor;
        sincronizarModeloSC(idx);
    });
    
    tr.querySelectorAll('[data-campo="descuento"]').forEach(input => {
        input.addEventListener('change', function() {
            const idx = parseInt(this.dataset.index);
            const valor = parseFloat(this.value) || 0;
            preciosData.modelos[idx].descuento = valor;
            sincronizarModeloSC(idx);
        });
    });
    
    // Agregar event listener al checkbox
    const checkbox = tr.querySelector('.checkbox-baja');
    checkbox.addEventListener('change', function() {
        const idx = parseInt(this.dataset.index);
        toggleDadoBaja(idx, this.checked);
    });
    
    return tr;
}

// Crear fila de solo lectura para modelo SC
function crearFilaSC(modelo, index) {
    const tr = document.createElement('tr');
    
    // Buscar el modelo convencional equivalente usando el mapeo
    const nombreConv = SC_MAPPING[modelo.nombre] || modelo.nombre.replace('SC - ', '');
    const modeloConv = preciosData.modelos.find(m => m.nombre === nombreConv);
    
    // Usar los datos del modelo convencional si existe, si no usar los propios
    const datos = modeloConv || modelo;
    const dadoBaja = modelo.dado_baja || 0;
    const familia = modelo.familia || 'OTROS';
    
    // Aplicar estilo si está dado de baja
    if (dadoBaja === 1) {
        tr.style.cssText = 'background-color: #fff5f5; opacity: 0.7;';
    }
    
    tr.innerHTML = `
        <td style="background: #f7fafc; font-weight: 600; color: #4a5568; font-size: 0.85em;">${familia}</td>
        <td><strong>${modelo.nombre}</strong></td>
        <td style="background: #f7fafc; color: #2d3748;">
            $ ${formatearNumero(datos.precio_ars || 0)}
        </td>
        <td style="background: #f7fafc; color: #2d3748;">
            US$ ${formatearNumero(datos.precio_usd || 0)}
        </td>
        <td style="background: #f7fafc; color: #2d3748;">
            $ ${formatearNumero(datos.cotizacion || 1000)}
        </td>
        <td style="background: #f7fafc; color: #2d3748;">
            ${datos.descuento || 0}%
        </td>
        <td style="text-align: center; background: #f7fafc;">
            <input type="checkbox" 
                   class="checkbox-baja"
                   ${dadoBaja === 1 ? 'checked' : ''}
                   data-index="${index}"
                   style="width: 20px; height: 20px; cursor: pointer;"
                   title="Marcar como dado de baja">
        </td>
    `;
    
    // Agregar event listener al checkbox
    const checkbox = tr.querySelector('.checkbox-baja');
    checkbox.addEventListener('change', function() {
        const idx = parseInt(this.dataset.index);
        toggleDadoBaja(idx, this.checked);
    });
    
    return tr;
}

// Actualizar precio de un modelo
function actualizarPrecio(index, campo, valor) {
    preciosData.modelos[index][campo] = parseFloat(valor) || 0;
    sincronizarModeloSC(index);
}

// Sincronizar modelo SC con su equivalente convencional
function sincronizarModeloSC(index) {
    const modelo = preciosData.modelos[index];
    
    // Si es un modelo convencional, buscar todos los SC que dependen de él
    if (!modelo.nombre.startsWith('SC -')) {
        // Buscar todos los modelos SC que usan este convencional como referencia
        for (const [modeloSC, modeloConv] of Object.entries(SC_MAPPING)) {
            if (modeloConv === modelo.nombre) {
                const indexSC = preciosData.modelos.findIndex(m => m.nombre === modeloSC);
                if (indexSC !== -1) {
                    // Sincronizar todos los campos excepto el nombre
                    preciosData.modelos[indexSC].precio_ars = modelo.precio_ars;
                    preciosData.modelos[indexSC].precio_usd = modelo.precio_usd;
                    preciosData.modelos[indexSC].cotizacion = modelo.cotizacion;
                    preciosData.modelos[indexSC].descuento = modelo.descuento;
                }
            }
        }
    }
    
    // Re-renderizar para actualizar la vista del SC
    renderizarTablas();
}

// Toggle estado de dado de baja
function toggleDadoBaja(index, checked) {
    preciosData.modelos[index].dado_baja = checked ? 1 : 0;
    renderizarTablas();
}

// Guardar precios en el servidor
function guardarPrecios() {
    fetch('/api/precios', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(preciosData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarAlerta('Precios guardados exitosamente', 'success');
        }
    })
    .catch(error => {
        console.error('Error al guardar precios:', error);
        mostrarAlerta('Error al guardar los precios', 'error');
    });
}

// Abrir modal de gestión de modelos
function abrirModalGestionModelos() {
    const modal = document.getElementById('modalGestionModelos');
    const lista = document.getElementById('listaGestionModelos');
    
    lista.innerHTML = '';
    
    // Crear lista de checkboxes
    MODELOS_COMPLETOS.forEach(modelo => {
        const isHidden = preciosData.modelos_ocultos.includes(modelo);
        
        const div = document.createElement('div');
        div.className = 'modelo-checkbox-item';
        div.style.cssText = 'padding: 10px; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 10px;';
        
        div.innerHTML = `
            <input type="checkbox" 
                   id="check_${modelo.replace(/[^a-zA-Z0-9]/g, '_')}" 
                   ${isHidden ? 'checked' : ''}
                   style="width: 20px; height: 20px;">
            <label for="check_${modelo.replace(/[^a-zA-Z0-9]/g, '_')}" 
                   style="flex: 1; cursor: pointer;">
                ${modelo}
            </label>
        `;
        
        lista.appendChild(div);
    });
    
    modal.style.display = 'flex';
}

// Cerrar modal de gestión de modelos
function cerrarModalGestionModelos() {
    const modal = document.getElementById('modalGestionModelos');
    modal.style.display = 'none';
}

// Aplicar cambios de modelos visibles
function aplicarCambiosModelos() {
    preciosData.modelos_ocultos = [];
    
    MODELOS_COMPLETOS.forEach(modelo => {
        const checkbox = document.getElementById(`check_${modelo.replace(/[^a-zA-Z0-9]/g, '_')}`);
        if (checkbox && checkbox.checked) {
            preciosData.modelos_ocultos.push(modelo);
        }
    });
    
    cerrarModalGestionModelos();
    renderizarTablas();
    mostrarAlerta('Modelos actualizados correctamente', 'success');
}

// Exportar a Excel (simplificado)
function exportarExcel() {
    mostrarAlerta('Funcionalidad de exportación en desarrollo', 'info');
}

// Formatear números
function formatearNumero(num) {
    return new Intl.NumberFormat('es-AR').format(num);
}

// Mostrar alerta flotante
function mostrarAlerta(mensaje, tipo) {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    
    const colores = {
        'success': '#c6f6d5',
        'error': '#fed7d7',
        'info': '#bee3f8'
    };
    
    const iconos = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'info': 'fa-info-circle'
    };
    
    alert.className = 'alert';
    alert.style.cssText = `
        background: ${colores[tipo] || colores.info};
        padding: 15px 20px;
        border-radius: 5px;
        margin-bottom: 10px;
        animation: slideIn 0.3s ease;
    `;
    
    alert.innerHTML = `<i class="fas ${iconos[tipo]}"></i> ${mensaje}`;
    
    container.appendChild(alert);
    
    setTimeout(() => {
        alert.style.transition = 'opacity 0.5s';
        alert.style.opacity = '0';
        setTimeout(() => {
            container.removeChild(alert);
        }, 500);
    }, 3000);
}
