// Variables globales
let archivoActual = null;
let datosOriginales = [];
let datosFiltrados = [];
let cambiosPendientes = [];

// Elementos del DOM
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileStatus = document.getElementById('fileStatus');
const fileName = document.getElementById('fileName');
const fileInfo = document.getElementById('fileInfo');
const btnProcesar = document.getElementById('btnProcesar');
const btnGuardar = document.getElementById('btnGuardar');
const btnDescargar = document.getElementById('btnDescargar');
const btnLimpiar = document.getElementById('btnLimpiar');
const spinner = document.getElementById('spinner');
const editSection = document.getElementById('editSection');
const searchOperacion = document.getElementById('searchOperacion');
const filterEjecutivo = document.getElementById('filterEjecutivo');
const filterEstado = document.getElementById('filterEstado');
const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');
const editableTableBody = document.getElementById('editableTableBody');
const recordCount = document.getElementById('recordCount');

// Setup Drag & Drop
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
});

// Manejar archivo seleccionado
function handleFile(file) {
    console.log(`📁 Archivo seleccionado: ${file.name}`);
    
    const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (extension !== '.xlsx' && extension !== '.xls') {
        showAlert('Por favor, selecciona un archivo Excel válido (.xlsx o .xls)', 'error');
        return;
    }
    
    archivoActual = file;
    fileName.textContent = file.name;
    fileInfo.textContent = `Tamaño: ${(file.size / 1024).toFixed(2)} KB`;
    fileStatus.style.display = 'block';
    btnProcesar.disabled = false;
    
    // Ocultar secciones previas
    editSection.style.display = 'none';
    btnGuardar.style.display = 'none';
    btnDescargar.style.display = 'none';
}

// Procesar archivo
btnProcesar.addEventListener('click', async () => {
    if (!archivoActual) {
        showAlert('Por favor, selecciona un archivo primero', 'warning');
        return;
    }
    
    console.log('🔄 Iniciando procesamiento...');
    
    spinner.classList.add('show');
    btnProcesar.disabled = true;
    
    const formData = new FormData();
    formData.append('file', archivoActual);
    
    try {
        const response = await fetch('/api/modulo7/procesar', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ Procesamiento exitoso:', data);
            
            // Guardar datos
            datosOriginales = data.datos_filtrados || [];
            datosFiltrados = [...datosOriginales];
            archivoActual = { filepath: data.filepath, filename: data.filename };
            
            // Poblar filtros dropdown
            poblarFiltros();
            
            // Renderizar tabla
            renderizarTabla();
            
            editSection.style.display = 'block';
            btnGuardar.style.display = 'inline-flex';
            btnDescargar.style.display = 'inline-flex';
            
            showAlert(`Archivo procesado correctamente. ${data.filas_filtradas} registros disponibles para edición.`, 'success');
        } else {
            showAlert(`Error al procesar: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showAlert(`Error al procesar el archivo: ${error.message}`, 'error');
    } finally {
        spinner.classList.remove('show');
        btnProcesar.disabled = false;
    }
});

// Renderizar tabla editable
function renderizarTabla() {
    editableTableBody.innerHTML = '';
    
    if (datosFiltrados.length === 0) {
        editableTableBody.innerHTML = `
            <tr>
                <td colspan="8" style="padding: 30px; text-align: center; color: #718096;">
                    <i class="fas fa-inbox" style="font-size: 3em; opacity: 0.3; display: block; margin-bottom: 10px;"></i>
                    No hay registros para mostrar
                </td>
            </tr>
        `;
        recordCount.textContent = '0 registros';
        return;
    }
    
    datosFiltrados.forEach((fila, index) => {
        const tr = document.createElement('tr');
        tr.dataset.rowIdx = fila.row_idx;
        tr.dataset.index = index;
        
        tr.innerHTML = `
            <td style="padding: 10px; font-weight: 600; color: #2D2D2D;">
                ${fila.operacion || ''}
            </td>
            <td style="padding: 10px;">
                <input type="text" 
                       class="campo-editable" 
                       data-campo="ejecutivo" 
                       data-row-idx="${fila.row_idx}"
                       value="${fila.ejecutivo || ''}"
                       placeholder="Ejecutivo">
            </td>
            <td style="padding: 10px;">
                <input type="text" 
                       class="campo-editable" 
                       data-campo="estado" 
                       data-row-idx="${fila.row_idx}"
                       value="${fila.estado || ''}"
                       placeholder="Estado">
            </td>
            <td style="padding: 10px;">
                <input type="text" 
                       class="campo-editable" 
                       data-campo="estado_seg_op" 
                       data-row-idx="${fila.row_idx}"
                       value="${fila.estado_seg_op || ''}"
                       placeholder="Estado Seg Op">
            </td>
            <td style="padding: 10px;">
                <input type="text" 
                       class="campo-editable" 
                       data-campo="ef_cancelad" 
                       data-row-idx="${fila.row_idx}"
                       value="${fila.ef_cancelad || ''}"
                       placeholder="EF Cancelad">
            </td>
            <td style="padding: 10px;">
                <input type="text" 
                       class="campo-editable" 
                       data-campo="usado_comp" 
                       data-row-idx="${fila.row_idx}"
                       value="${fila.usado_comp || ''}"
                       placeholder="Usado Comp">
            </td>
            <td style="padding: 10px;">
                <input type="text" 
                       class="campo-editable" 
                       data-campo="cred_liq" 
                       data-row-idx="${fila.row_idx}"
                       value="${fila.cred_liq || ''}"
                       placeholder="Cred Liq">
            </td>
            <td style="padding: 10px; background: #f7fafc;">
                <span style="color: #4a5568; font-size: 0.9em; display: block; padding: 8px;" 
                      title="${fila.observaciones || 'Sin observaciones'}">
                    ${fila.observaciones || '-'}
                </span>
            </td>
        `;
        
        editableTableBody.appendChild(tr);
    });
    
    recordCount.textContent = `${datosFiltrados.length} registro(s) disponible(s) para edición`;
    
    // Agregar eventos de cambio
    agregarEventosEdicion();
}

// Agregar eventos a campos editables
function agregarEventosEdicion() {
    const inputs = document.querySelectorAll('.campo-editable');
    
    inputs.forEach(input => {
        input.addEventListener('input', (e) => {
            const campo = e.target.dataset.campo;
            const rowIdx = parseInt(e.target.dataset.rowIdx);
            const valor = e.target.value;
            
            // Marcar como modificado
            e.target.classList.add('modified');
            
            // Registrar cambio
            const cambioExistente = cambiosPendientes.findIndex(
                c => c.row_idx === rowIdx && c.campo === campo
            );
            
            if (cambioExistente !== -1) {
                cambiosPendientes[cambioExistente].valor = valor;
            } else {
                cambiosPendientes.push({ row_idx: rowIdx, campo, valor });
            }
            
            console.log(`✏️ Cambio registrado: Fila ${rowIdx}, Campo ${campo} = "${valor}"`);
        });
    });
}

// Función para poblar filtros dropdown
function poblarFiltros() {
    // Obtener valores únicos de ejecutivos
    const ejecutivos = [...new Set(datosOriginales.map(f => f.ejecutivo).filter(e => e))].sort();
    filterEjecutivo.innerHTML = '<option value="">Todos</option>';
    ejecutivos.forEach(ejecutivo => {
        const option = document.createElement('option');
        option.value = ejecutivo;
        option.textContent = ejecutivo;
        filterEjecutivo.appendChild(option);
    });
    
    // Obtener valores únicos de estados (filtrar números de teléfono)
    const estados = [...new Set(datosOriginales.map(f => f.estado).filter(e => {
        if (!e) return false;
        const esTexto = String(e);
        
        // Contar dígitos - si tiene más de 5 dígitos, probablemente es teléfono
        const cantidadDigitos = (esTexto.match(/\d/g) || []).length;
        if (cantidadDigitos > 5) return false;
        
        // Filtrar valores muy largos
        if (esTexto.length > 50) return false;
        
        // Filtrar si contiene patrones típicos de teléfono
        if (/[\d\-\/]{5,}/.test(esTexto)) return false;
        
        return true;
    }))].sort();
    
    filterEstado.innerHTML = '<option value="">Todos</option>';
    estados.forEach(estado => {
        const option = document.createElement('option');
        option.value = estado;
        option.textContent = estado;
        filterEstado.appendChild(option);
    });
}

// Función para aplicar todos los filtros
function aplicarFiltros() {
    const operacion = searchOperacion.value.toLowerCase();
    const ejecutivo = filterEjecutivo.value;
    const estado = filterEstado.value;
    
    datosFiltrados = datosOriginales.filter(fila => {
        let cumple = true;
        
        // Filtro por operación
        if (operacion && fila.operacion) {
            cumple = cumple && fila.operacion.toString().toLowerCase().includes(operacion);
        }
        
        // Filtro por ejecutivo
        if (ejecutivo) {
            cumple = cumple && fila.ejecutivo === ejecutivo;
        }
        
        // Filtro por estado
        if (estado) {
            cumple = cumple && fila.estado === estado;
        }
        
        return cumple;
    });
    
    renderizarTabla();
}

// Event listeners para filtros
searchOperacion.addEventListener('input', aplicarFiltros);
filterEjecutivo.addEventListener('change', aplicarFiltros);
filterEstado.addEventListener('change', aplicarFiltros);

// Limpiar filtros
btnLimpiarFiltros.addEventListener('click', () => {
    searchOperacion.value = '';
    filterEjecutivo.value = '';
    filterEstado.value = '';
    datosFiltrados = [...datosOriginales];
    renderizarTabla();
});

// Guardar cambios
btnGuardar.addEventListener('click', async () => {
    if (cambiosPendientes.length === 0) {
        showAlert('No hay cambios para guardar', 'warning');
        return;
    }
    
    console.log(`💾 Guardando ${cambiosPendientes.length} cambios...`);
    
    spinner.classList.add('show');
    btnGuardar.disabled = true;
    
    try {
        const response = await fetch('/api/modulo7/actualizar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filepath: archivoActual.filepath,
                cambios: cambiosPendientes
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log(`✅ ${data.cambios_aplicados} cambios guardados`);
            showAlert(`${data.cambios_aplicados} cambios guardados correctamente`, 'success');
            
            // Limpiar cambios pendientes
            cambiosPendientes = [];
            
            // Remover clase modified
            document.querySelectorAll('.modified').forEach(el => {
                el.classList.remove('modified');
            });
        } else {
            showAlert(`Error al guardar: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showAlert(`Error al guardar cambios: ${error.message}`, 'error');
    } finally {
        spinner.classList.remove('show');
        btnGuardar.disabled = false;
    }
});

// Descargar archivo
btnDescargar.addEventListener('click', () => {
    if (!archivoActual || !archivoActual.filename) {
        showAlert('No hay archivo procesado para descargar', 'warning');
        return;
    }
    
    console.log('📥 Descargando archivo...');
    
    const url = `/api/modulo7/descargar/${archivoActual.filename}`;
    window.location.href = url;
    
    showAlert('Descarga iniciada', 'success');
});

// Limpiar todo
btnLimpiar.addEventListener('click', () => {
    if (confirm('¿Estás seguro de que deseas limpiar todos los datos?')) {
        archivoActual = null;
        datosOriginales = [];
        datosFiltrados = [];
        cambiosPendientes = [];
        
        fileInput.value = '';
        fileStatus.style.display = 'none';
        editSection.style.display = 'none';
        btnProcesar.disabled = true;
        btnGuardar.style.display = 'none';
        btnDescargar.style.display = 'none';
        searchOperacion.value = '';
        filterEjecutivo.value = '';
        filterEstado.value = '';
        
        showAlert('Datos limpiados correctamente', 'info');
    }
});

// Función para mostrar alertas
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    
    const colors = {
        success: '#48bb78',
        error: '#f56565',
        warning: '#ed8936',
        info: '#4299e1'
    };
    
    const alert = document.createElement('div');
    alert.style.cssText = `
        padding: 15px 20px;
        margin-bottom: 20px;
        border-radius: 8px;
        background: ${colors[type]}15;
        border-left: 4px solid ${colors[type]};
        display: flex;
        align-items: center;
        gap: 12px;
        animation: slideIn 0.3s ease;
    `;
    
    alert.innerHTML = `
        <i class="fas fa-${icons[type]}" style="color: ${colors[type]}; font-size: 1.3em;"></i>
        <span style="flex: 1; color: #2D2D2D; font-weight: 500;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; color: #718096; cursor: pointer; font-size: 1.2em; padding: 0; width: 24px; height: 24px;">×</button>
    `;
    
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// Animaciones CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(-100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
