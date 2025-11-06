// Módulo 2: Preventa del mes siguiente
let dataPreventa = [];
let isEditMode = false;

// Cargar preventa al iniciar
document.addEventListener('DOMContentLoaded', () => {
    cargarPreventa();
    
    // Event listeners para botones
    document.getElementById('btn-pegar').addEventListener('click', activarModoPegar);
    document.getElementById('btn-editar').addEventListener('click', activarModoEdicion);
    document.getElementById('btn-guardar').addEventListener('click', guardarPreventa);
    document.getElementById('btn-cancelar').addEventListener('click', cancelarEdicion);
    document.getElementById('btn-convertir').addEventListener('click', convertirADisponible);
    document.getElementById('btn-limpiar').addEventListener('click', limpiarTabla);
});

// Cargar preventa desde la base de datos
async function cargarPreventa() {
    try {
        const response = await fetch('/api/preventa');
        if (response.ok) {
            dataPreventa = await response.json();
            renderizarTabla();
            mostrarMensaje('Preventa cargada correctamente', 'success');
        }
    } catch (error) {
        console.error('Error al cargar preventa:', error);
        mostrarMensaje('Error al cargar preventa', 'error');
    }
}

// Renderizar tabla
function renderizarTabla() {
    const tbody = document.getElementById('tabla-preventa-body');
    tbody.innerHTML = '';
    
    if (dataPreventa.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2rem; color: #999;">
                    No hay datos de preventa. Use el botón "Pegar desde Excel" para cargar datos.
                </td>
            </tr>
        `;
        return;
    }
    
    dataPreventa.forEach((item, index) => {
        const row = document.createElement('tr');
        
        // Columnas editables
        row.innerHTML = `
            <td>
                <input type="text" 
                    class="form-control form-control-sm" 
                    value="${item.modelo_version || ''}"
                    data-index="${index}"
                    data-field="modelo_version"
                    ${!isEditMode ? 'disabled' : ''}>
            </td>
            <td>
                <input type="text" 
                    class="form-control form-control-sm" 
                    value="${item.operacion || ''}"
                    data-index="${index}"
                    data-field="operacion"
                    ${!isEditMode ? 'disabled' : ''}>
            </td>
            <td>
                <input type="text" 
                    class="form-control form-control-sm vendedor-input" 
                    value="${item.vendedor || ''}"
                    data-index="${index}"
                    data-field="vendedor"
                    ${!isEditMode ? 'disabled' : ''}>
            </td>
            <td>
                <input type="text" 
                    class="form-control form-control-sm" 
                    value="${item.color || ''}"
                    data-index="${index}"
                    data-field="color"
                    ${!isEditMode ? 'disabled' : ''}>
            </td>
            <td style="text-align: center;">
                <input type="checkbox" 
                    ${item.informado ? 'checked' : ''}
                    data-index="${index}"
                    data-field="informado"
                    ${!isEditMode ? 'disabled' : ''}>
            </td>
            <td style="text-align: center;">
                <input type="checkbox" 
                    ${item.cancelado ? 'checked' : ''}
                    data-index="${index}"
                    data-field="cancelado"
                    ${!isEditMode ? 'disabled' : ''}>
            </td>
            <td style="text-align: center;">
                <input type="checkbox" 
                    ${item.asignado ? 'checked' : ''}
                    data-index="${index}"
                    data-field="asignado"
                    ${!isEditMode ? 'disabled' : ''}>
            </td>
            <td style="text-align: center;">
                <button class="btn btn-sm btn-danger" onclick="eliminarFila(${index})" ${!isEditMode ? 'disabled' : ''}>
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
        
        // Event listeners para inputs
        const inputs = row.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const idx = parseInt(e.target.dataset.index);
                const field = e.target.dataset.field;
                
                if (e.target.type === 'checkbox') {
                    dataPreventa[idx][field] = e.target.checked;
                } else {
                    dataPreventa[idx][field] = e.target.value;
                }
            });
        });
    });
    
    actualizarContadores();
}

// Activar modo pegar (textarea para pegar desde Excel)
function activarModoPegar() {
    const overlay = document.createElement('div');
    overlay.className = 'paste-overlay';
    overlay.innerHTML = `
        <div class="paste-container">
            <h4>Pegar datos desde Excel</h4>
            <p>Copie las filas de Excel (sin encabezados) y péguelas aquí:</p>
            <textarea id="paste-area" rows="10" placeholder="Pegue aquí... (Modelo/Versión, Operación, Vendedor, Color)"></textarea>
            <div style="margin-top: 1rem;">
                <button class="btn btn-primary" onclick="procesarDatosPegados()">Procesar</button>
                <button class="btn btn-secondary" onclick="cerrarModalPegar()">Cancelar</button>
            </div>
            <small style="color: #666; display: block; margin-top: 1rem;">
                Formato esperado: Modelo/Versión [TAB] Operación [TAB] Vendedor [TAB] Color<br>
                Las columnas Informado, Cancelado y Asignado se dejarán sin marcar por defecto.
            </small>
        </div>
    `;
    document.body.appendChild(overlay);
    document.getElementById('paste-area').focus();
}

// Procesar datos pegados
window.procesarDatosPegados = function() {
    const textarea = document.getElementById('paste-area');
    const text = textarea.value.trim();
    
    if (!text) {
        alert('Por favor pegue los datos primero');
        return;
    }
    
    const lines = text.split('\n');
    const newData = [];
    
    lines.forEach(line => {
        if (line.trim() === '') return;
        
        // Separar por tabulaciones (copiar desde Excel)
        const cols = line.split('\t');
        
        if (cols.length >= 4) {
            newData.push({
                modelo_version: cols[0].trim(),
                operacion: cols[1].trim(),
                vendedor: cols[2].trim(),
                color: cols[3].trim(),
                informado: false,
                cancelado: false,
                asignado: false
            });
        }
    });
    
    if (newData.length > 0) {
        dataPreventa = newData;
        isEditMode = true;
        renderizarTabla();
        cerrarModalPegar();
        mostrarMensaje(`${newData.length} filas cargadas desde Excel`, 'success');
        mostrarBotonesEdicion();
    } else {
        alert('No se pudo procesar los datos. Verifique el formato.');
    }
};

// Cerrar modal pegar
window.cerrarModalPegar = function() {
    const overlay = document.querySelector('.paste-overlay');
    if (overlay) {
        overlay.remove();
    }
};

// Activar modo edición (sin pegar desde Excel)
function activarModoEdicion() {
    if (dataPreventa.length === 0) {
        mostrarMensaje('No hay datos para editar. Use "Pegar desde Excel" primero.', 'error');
        return;
    }
    
    isEditMode = true;
    renderizarTabla();
    mostrarBotonesEdicion();
    mostrarMensaje('Modo edición activado', 'success');
}

// Guardar preventa
async function guardarPreventa() {
    if (dataPreventa.length === 0) {
        mostrarMensaje('No hay datos para guardar', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/preventa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataPreventa)
        });
        
        const result = await response.json();
        
        if (result.success) {
            isEditMode = false;
            renderizarTabla();
            ocultarBotonesEdicion();
            mostrarMensaje(`✅ ${result.count} registros guardados. ${result.message}`, 'success');
        } else {
            mostrarMensaje('Error al guardar: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error al guardar:', error);
        mostrarMensaje('Error al guardar preventa', 'error');
    }
}

// Cancelar edición
function cancelarEdicion() {
    isEditMode = false;
    cargarPreventa();
    ocultarBotonesEdicion();
}

// Convertir a disponible (solo unidades sin vendedor)
async function convertirADisponible() {
    const sinVendedor = dataPreventa.filter(item => !item.vendedor || item.vendedor.trim() === '');
    
    if (sinVendedor.length === 0) {
        mostrarMensaje('No hay unidades sin vendedor para convertir', 'error');
        return;
    }
    
    if (!confirm(`¿Desea convertir ${sinVendedor.length} unidades de preventa (sin vendedor) a disponible?\n\nLas unidades con vendedor asignado NO se agregarán.`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/preventa/convertir_disponible', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            mostrarMensaje(result.message, 'success');
        } else {
            mostrarMensaje('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error al convertir:', error);
        mostrarMensaje('Error al convertir a disponible', 'error');
    }
}

// Limpiar tabla
async function limpiarTabla() {
    if (dataPreventa.length === 0) {
        mostrarMensaje('La tabla ya está vacía', 'error');
        return;
    }
    
    if (confirm('¿Está seguro de eliminar TODOS los datos de preventa?\n\nEsto también eliminará las unidades de preventa del módulo Disponible.')) {
        try {
            // Guardar tabla vacía (esto limpiará automáticamente el disponible)
            const response = await fetch('/api/preventa', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([])  // Array vacío
            });
            
            const result = await response.json();
            
            if (result.success) {
                dataPreventa = [];
                isEditMode = false;
                renderizarTabla();
                ocultarBotonesEdicion();
                mostrarMensaje('✅ Bitácora limpiada y unidades eliminadas del disponible', 'success');
            } else {
                mostrarMensaje('Error al limpiar: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error al limpiar:', error);
            mostrarMensaje('Error al limpiar la tabla', 'error');
        }
    }
}

// Eliminar fila individual
window.eliminarFila = function(index) {
    if (confirm('¿Eliminar esta fila?')) {
        dataPreventa.splice(index, 1);
        renderizarTabla();
    }
};

// Mostrar/ocultar botones de edición
function mostrarBotonesEdicion() {
    document.getElementById('btn-guardar').style.display = 'inline-block';
    document.getElementById('btn-cancelar').style.display = 'inline-block';
    document.getElementById('btn-pegar').disabled = true;
    document.getElementById('btn-editar').disabled = true;
}

function ocultarBotonesEdicion() {
    document.getElementById('btn-guardar').style.display = 'none';
    document.getElementById('btn-cancelar').style.display = 'none';
    document.getElementById('btn-pegar').disabled = false;
    document.getElementById('btn-editar').disabled = false;
}

// Actualizar contadores
function actualizarContadores() {
    const total = dataPreventa.length;
    const conVendedor = dataPreventa.filter(item => item.vendedor && item.vendedor.trim() !== '').length;
    const sinVendedor = total - conVendedor;
    
    document.getElementById('total-preventa').textContent = total;
    document.getElementById('total-vendedor').textContent = conVendedor;
    document.getElementById('total-sin-vendedor').textContent = sinVendedor;
}

// Mostrar mensajes
function mostrarMensaje(texto, tipo) {
    const alertContainer = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${tipo === 'success' ? 'success' : 'danger'}`;
    alert.textContent = texto;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 3000);
}
