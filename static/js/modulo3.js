// Elementos del DOM
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultContainer = document.getElementById('resultContainer');
const successAlert = document.getElementById('successAlert');
const errorAlert = document.getElementById('errorAlert');
const infoAlert = document.getElementById('infoAlert');
const errorMessage = document.getElementById('errorMessage');

// Inicialización
infoAlert.classList.add('show');

// Función simple para manejar pestañas (sin Bootstrap)
function initTabs() {
    document.querySelectorAll('.nav-link').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remover clase active de todos los botones y paneles
            document.querySelectorAll('.nav-link').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            // Agregar clase active al botón clickeado
            this.classList.add('active');
            
            // Mostrar el panel correspondiente
            const targetId = this.getAttribute('data-bs-target');
            const targetPane = document.querySelector(targetId);
            if (targetPane) {
                targetPane.classList.add('show', 'active');
            }
        });
    });
}

// Event Listeners para Drag & Drop
dropZone.addEventListener('click', () => {
    fileInput.click();
});

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
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// Función para manejar el archivo
function handleFile(file) {
    // Validar tipo de archivo
    const validTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                        'application/vnd.ms-excel'];
    const validExtensions = ['.xlsx', '.xls'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
        showError('Por favor, selecciona un archivo Excel válido (.xlsx o .xls)');
        return;
    }
    
    // Ocultar alertas
    hideAlerts();
    
    // Mostrar spinner
    loadingSpinner.classList.add('show');
    resultContainer.style.display = 'none';
    
    // Crear FormData y enviar archivo
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('Enviando archivo para procesamiento...');
    
    fetch('/procesar_excel', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Error al procesar el archivo');
            });
        }
        return response.json();
    })
    .then(data => {
        loadingSpinner.classList.remove('show');
        
        if (data.success) {
            // Guardar datos originales para filtrado
            saveOriginalData(data);
            
            // Mostrar resultados (ya vienen filtrados desde el backend)
            displayResults(data);
            successAlert.classList.add('show');
            
            // Actualizar contador de postergadas
            updatePostergadasCount();
            
            // Ocultar alerta de éxito después de 5 segundos
            setTimeout(() => {
                successAlert.classList.remove('show');
            }, 5000);
        } else {
            showError(data.error || 'Error al procesar el archivo');
        }
    })
    .catch(error => {
        loadingSpinner.classList.remove('show');
        showError(error.message);
    });
}

// Función para mostrar resultados
function displayResults(data) {
    if (!data.tabs || data.tabs.length === 0) {
        showError('No se encontraron datos para mostrar');
        return;
    }
    
    // Crear pestañas de navegación (sin ícono)
    let tabsHtml = '<ul class="nav nav-tabs mb-3" id="myTab" role="tablist" style="justify-content: flex-start;">';
    data.tabs.forEach((tab, index) => {
        const activeClass = index === 0 ? 'active' : '';
        tabsHtml += `
            <li class="nav-item" role="presentation">
                <button class="nav-link ${activeClass}" id="${tab.id}-tab" 
                        data-bs-toggle="tab" data-bs-target="#${tab.id}" 
                        type="button" role="tab" aria-controls="${tab.id}" 
                        aria-selected="${index === 0}">
                    ${tab.name} 
                    <span class="badge bg-primary ms-2">${tab.count}</span>
                </button>
            </li>
        `;
    });
    tabsHtml += '</ul>';
    
    // Agregar botones de filtro debajo de las pestañas
    tabsHtml += `
        <div class="filter-controls mb-3">
            <button class="btn btn-warning" id="filterEmptyOperation" onclick="toggleFilterEmptyOperation()">
                <i class="fas fa-filter"></i> Filtrar: Operación Vacía
            </button>
            <button class="btn btn-warning" id="filterEmptyCliente" onclick="toggleFilterEmptyCliente()">
                <i class="fas fa-filter"></i> Filtrar: Cliente Vacío
            </button>
            <button class="btn btn-secondary" id="clearFilter" onclick="clearFilter()" style="display: none;">
                <i class="fas fa-times"></i> Mostrar Todos
            </button>
            <button class="btn btn-success" id="convertirDisponible" onclick="convertirADisponible()">
                <i class="fas fa-check-circle"></i> Convertir a Disponible
            </button>
        </div>
    `;
    
    // Crear contenido de las pestañas
    let tabContentHtml = '<div class="tab-content" id="myTabContent">';
    data.tabs.forEach((tab, index) => {
        const activeClass = index === 0 ? 'show active' : '';
        
        // Crear tabla HTML para cada pestaña
        let tableHtml = '<div class="table-responsive"><table class="table table-striped table-hover">';
        
        // Encabezados (sin íconos)
        tableHtml += '<thead class="table-dark"><tr>';
        tab.columns.forEach(column => {
            tableHtml += `<th>${column}</th>`;
        });
        tableHtml += '</tr></thead>';
        
        // Filas de datos
        tableHtml += '<tbody>';
        tab.rows.forEach(row => {
            tableHtml += '<tr>';
            row.forEach(cell => {
                // Formatear fechas si es necesario
                let cellValue = cell !== null ? cell : '';
                if (cellValue && typeof cellValue === 'string' && cellValue.includes('T')) {
                    // Posible fecha en formato ISO
                    const date = new Date(cellValue);
                    if (!isNaN(date.getTime())) {
                        cellValue = date.toLocaleDateString('es-AR');
                    }
                }
                tableHtml += `<td>${cellValue}</td>`;
            });
            tableHtml += '</tr>';
        });
        tableHtml += '</tbody></table></div>';
        
        tabContentHtml += `
            <div class="tab-pane fade ${activeClass}" id="${tab.id}" 
                 role="tabpanel" aria-labelledby="${tab.id}-tab">
                ${tableHtml}
            </div>
        `;
    });
    tabContentHtml += '</div>';
    
    // Insertar pestañas y contenido en el contenedor
    const resultContainer = document.getElementById('resultContainer');
    const cardBody = resultContainer.querySelector('.card-body');
    
    cardBody.innerHTML = `
        <div class="alert alert-info mb-3">
            <i class="fas fa-info-circle me-2"></i>
            <strong>Total de registros procesados:</strong> ${data.total_rows}
        </div>
        ${tabsHtml}
        ${tabContentHtml}
    `;
    
    // Mostrar contenedor de resultados
    resultContainer.style.display = 'block';
    
    // Inicializar funcionalidad de pestañas
    initTabs();
    
    // Scroll suave hacia los resultados
    resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Función para mostrar error
function showError(message) {
    hideAlerts();
    errorMessage.textContent = message;
    errorAlert.classList.add('show');
    
    // Ocultar alerta de error después de 8 segundos
    setTimeout(() => {
        errorAlert.classList.remove('show');
    }, 8000);
}

// Función para ocultar todas las alertas
function hideAlerts() {
    infoAlert.classList.remove('show');
    successAlert.classList.remove('show');
    errorAlert.classList.remove('show');
}

// Variable global para almacenar los datos originales
let originalData = null;
let unidadesPostergadas = [];

// Cargar unidades postergadas desde el servidor (base de datos)
(function initPostergadas() {
    console.log('🔄 Iniciando carga de unidades postergadas...');
    fetch('/api/unidades_postergadas')
        .then(response => {
            console.log('📡 Respuesta recibida:', response.status);
            return response.json();
        })
        .then(data => {
            unidadesPostergadas = data;
            console.log('✅ Unidades postergadas cargadas desde BD:', unidadesPostergadas);
            console.log('📊 Total de unidades postergadas:', unidadesPostergadas.length);
            updatePostergadasCount();
        })
        .catch(error => {
            console.error('❌ Error al cargar unidades postergadas:', error);
        });
})();

// Cargar unidades postergadas desde el servidor
function loadUnidadesPostergadas() {
    return fetch('/api/unidades_postergadas')
        .then(response => response.json())
        .then(data => {
            unidadesPostergadas = data;
            return unidadesPostergadas;
        });
}

// Guardar unidades postergadas en el servidor (ya no se usa localStorage)
function saveUnidadesPostergadas() {
    // Ya no es necesario, se guarda automáticamente en cada operación
}

// Función para guardar datos originales
function saveOriginalData(data) {
    originalData = JSON.parse(JSON.stringify(data)); // Deep copy
    
    // Cargar unidades postergadas
    loadUnidadesPostergadas();
}

// Función para filtrar filas donde "Operación" está vacía
function toggleFilterEmptyOperation() {
    if (!originalData) return;
    
    const filteredData = {
        success: true,
        tabs: [],
        total_rows: 0
    };
    
    originalData.tabs.forEach(tab => {
        // Encontrar el índice de la columna "Operación"
        const operacionIndex = tab.columns.indexOf('Operación');
        
        if (operacionIndex !== -1) {
            // Filtrar solo las filas donde Operación está vacía o es null
            const filteredRows = tab.rows.filter(row => {
                const operacionValue = row[operacionIndex];
                return operacionValue === null || operacionValue === '' || operacionValue === undefined;
            });
            
            if (filteredRows.length > 0) {
                filteredData.tabs.push({
                    id: tab.id,
                    name: tab.name,
                    count: filteredRows.length,
                    columns: tab.columns,
                    rows: filteredRows
                });
                filteredData.total_rows += filteredRows.length;
            }
        }
    });
    
    // Mostrar datos filtrados
    displayResults(filteredData);
    
    // Cambiar visibilidad de botones
    document.getElementById('filterEmptyOperation').style.display = 'none';
    document.getElementById('filterEmptyCliente').style.display = 'none';
    document.getElementById('clearFilter').style.display = 'inline-block';
}

// Función para filtrar filas donde "Cliente" está vacía
function toggleFilterEmptyCliente() {
    if (!originalData) return;
    
    const filteredData = {
        success: true,
        tabs: [],
        total_rows: 0
    };
    
    originalData.tabs.forEach(tab => {
        // Encontrar el índice de la columna "Cliente"
        const clienteIndex = tab.columns.indexOf('Cliente');
        
        if (clienteIndex !== -1) {
            // Filtrar solo las filas donde Cliente está vacía o es null
            const filteredRows = tab.rows.filter(row => {
                const clienteValue = row[clienteIndex];
                return clienteValue === null || clienteValue === '' || clienteValue === undefined;
            });
            
            if (filteredRows.length > 0) {
                filteredData.tabs.push({
                    id: tab.id,
                    name: tab.name,
                    count: filteredRows.length,
                    columns: tab.columns,
                    rows: filteredRows
                });
                filteredData.total_rows += filteredRows.length;
            }
        }
    });
    
    // Mostrar datos filtrados
    displayResults(filteredData);
    
    // Cambiar visibilidad de botones
    document.getElementById('filterEmptyOperation').style.display = 'none';
    document.getElementById('filterEmptyCliente').style.display = 'none';
    document.getElementById('clearFilter').style.display = 'inline-block';
}

// Función para limpiar el filtro y mostrar todos los datos
function clearFilter() {
    if (!originalData) return;
    
    // Mostrar datos originales
    displayResults(originalData);
    
    // Cambiar visibilidad de botones
    document.getElementById('filterEmptyOperation').style.display = 'inline-block';
    document.getElementById('filterEmptyCliente').style.display = 'inline-block';
    document.getElementById('clearFilter').style.display = 'none';
}

// ==================== SISTEMA DE UNIDADES POSTERGADAS ====================

// Función para aplicar filtro de unidades postergadas
function applyPostergadasFilter(data) {
    console.log('Aplicando filtro de postergadas. Total unidades bloqueadas:', unidadesPostergadas.length);
    console.log('Unidades bloqueadas:', unidadesPostergadas);
    
    if (unidadesPostergadas.length === 0) {
        console.log('No hay unidades postergadas, retornando datos sin filtrar');
        return data;
    }
    
    const filteredData = {
        success: true,
        tabs: [],
        total_rows: 0
    };
    
    data.tabs.forEach(tab => {
        // Encontrar el índice de la columna "Nº Fábrica"
        const fabricaIndex = tab.columns.indexOf('Nº Fábrica');
        console.log(`Tab: ${tab.name}, Índice de Nº Fábrica: ${fabricaIndex}`);
        
        if (fabricaIndex !== -1) {
            const totalRows = tab.rows.length;
            
            // Filtrar excluyendo las unidades postergadas
            const filteredRows = tab.rows.filter(row => {
                const fabricaValue = String(row[fabricaIndex] || '').trim();
                const isBlocked = unidadesPostergadas.includes(fabricaValue);
                
                if (isBlocked) {
                    console.log(`Filtrando unidad: ${fabricaValue}`);
                }
                
                return !isBlocked;
            });
            
            console.log(`${tab.name}: ${totalRows} filas originales, ${filteredRows.length} después del filtro`);
            
            if (filteredRows.length > 0 || tab.rows.length === 0) {
                filteredData.tabs.push({
                    id: tab.id,
                    name: tab.name,
                    count: filteredRows.length,
                    columns: tab.columns,
                    rows: filteredRows
                });
                filteredData.total_rows += filteredRows.length;
            }
        }
    });
    
    console.log('Datos filtrados totales:', filteredData.total_rows);
    return filteredData;
}

// Función para abrir el modal de Unidades Postergadas
function openPostergadasModal() {
    // Crear modal si no existe
    let modal = document.getElementById('postergadasModal');
    if (!modal) {
        modal = createPostergadasModal();
        document.body.appendChild(modal);
    }
    
    // Actualizar lista
    updatePostergadasList();
    
    // Mostrar modal
    modal.style.display = 'flex';
}

// Función para cerrar el modal
function closePostergadasModal() {
    const modal = document.getElementById('postergadasModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Función para crear el modal HTML
function createPostergadasModal() {
    const modal = document.createElement('div');
    modal.id = 'postergadasModal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-ban"></i> Unidades Postergadas</h3>
                <button class="modal-close" onclick="closePostergadasModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <p style="color: #718096; margin-bottom: 20px;">
                    Agrega números de fábrica para ocultarlos de todas las listas. 
                    Estas unidades no se mostrarán en ninguna pestaña.
                </p>
                
                <div class="input-group">
                    <input type="text" 
                           id="postergadaInput" 
                           placeholder="Ingresa Nº de Fábrica (ej: YAC123456)"
                           class="form-input"
                           onkeypress="if(event.key === 'Enter') addPostergada()">
                    <button class="btn btn-primary" onclick="addPostergada()">
                        <i class="fas fa-plus"></i> Agregar
                    </button>
                </div>
                
                <div id="postergadasList" class="postergadas-list">
                    <!-- Lista se genera dinámicamente -->
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closePostergadasModal()">
                    Cerrar
                </button>
            </div>
        </div>
    `;
    return modal;
}

// Función para agregar una unidad postergada
function addPostergada() {
    const input = document.getElementById('postergadaInput');
    const valor = input.value.trim();
    
    if (!valor) {
        alert('Por favor ingresa un número de fábrica');
        return;
    }
    
    if (unidadesPostergadas.includes(valor)) {
        alert('Este número de fábrica ya está en la lista');
        return;
    }
    
    // Guardar en la base de datos
    fetch('/api/unidades_postergadas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ numero_fabrica: valor })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Agregar a la lista local
            unidadesPostergadas.push(valor);
            
            console.log('Unidad agregada a postergadas:', valor);
            console.log('Lista completa de postergadas:', unidadesPostergadas);
            
            // Limpiar input
            input.value = '';
            
            // Actualizar lista visual
            updatePostergadasList();
            
            // Actualizar contador en el botón
            updatePostergadasCount();
            
            // Mostrar mensaje informativo
            showInfoMessage(`Unidad "${valor}" agregada. Recarga el archivo Excel para aplicar los cambios.`);
        } else {
            alert('Error: ' + (data.error || 'No se pudo agregar la unidad'));
        }
    })
    .catch(error => {
        console.error('Error al agregar unidad postergada:', error);
        alert('Error al agregar la unidad postergada');
    });
}

// Función para eliminar una unidad postergada
function removePostergada(valor) {
    fetch(`/api/unidades_postergadas/${encodeURIComponent(valor)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Eliminar de la lista local
            const index = unidadesPostergadas.indexOf(valor);
            if (index > -1) {
                unidadesPostergadas.splice(index, 1);
            }
            
            // Actualizar lista visual
            updatePostergadasList();
            
            // Actualizar contador en el botón
            updatePostergadasCount();
            
            // Mostrar mensaje informativo
            showInfoMessage(`Unidad "${valor}" eliminada. Recarga el archivo Excel para ver los cambios.`);
        } else {
            alert('Error: ' + (data.error || 'No se pudo eliminar la unidad'));
        }
    })
    .catch(error => {
        console.error('Error al eliminar unidad postergada:', error);
        alert('Error al eliminar la unidad postergada');
    });
}

// Función para mostrar mensaje informativo
function showInfoMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-info';
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '10000';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.transition = 'opacity 0.5s';
        alertDiv.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(alertDiv);
        }, 500);
    }, 3000);
}

// Función para actualizar la lista visual de postergadas
function updatePostergadasList() {
    const listContainer = document.getElementById('postergadasList');
    if (!listContainer) return;
    
    if (unidadesPostergadas.length === 0) {
        listContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No hay unidades postergadas</p>
            </div>
        `;
        return;
    }
    
    let html = '<ul class="postergadas-items">';
    unidadesPostergadas.forEach(valor => {
        html += `
            <li class="postergada-item">
                <span><i class="fas fa-ban"></i> ${valor}</span>
                <button class="btn-remove" onclick="removePostergada('${valor}')" title="Eliminar">
                    <i class="fas fa-trash"></i>
                </button>
            </li>
        `;
    });
    html += '</ul>';
    
    listContainer.innerHTML = html;
}

// Función para actualizar el contador en el botón
function updatePostergadasCount() {
    const countSpan = document.getElementById('postergadasCount');
    if (countSpan) {
        countSpan.textContent = unidadesPostergadas.length;
    }
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Cargar unidades postergadas desde el servidor
    loadUnidadesPostergadas().then(() => {
        updatePostergadasCount();
    });
});

// Función para convertir datos filtrados a módulo Disponible
function convertirADisponible() {
    // Verificar si hay datos cargados
    if (!originalData || !originalData.tabs) {
        alert('⚠️ No hay datos para convertir. Por favor, carga un archivo Excel primero.');
        return;
    }
    
    // Buscar la pestaña de Ventas Convencionales (YAC)
    const ventasConvencionalesTab = originalData.tabs.find(tab => tab.id === 'ventas-convencionales');
    
    if (!ventasConvencionalesTab) {
        alert('⚠️ No se encontró la pestaña de Ventas Convencionales (YAC).');
        return;
    }
    
    // Encontrar el índice de la columna "Cliente"
    const clienteIndex = ventasConvencionalesTab.columns.indexOf('Cliente');
    
    if (clienteIndex === -1) {
        alert('⚠️ No se encontró la columna "Cliente" en los datos.');
        return;
    }
    
    // Filtrar solo las filas donde Cliente está vacío
    const filasFiltradas = ventasConvencionalesTab.rows.filter(row => {
        const clienteValue = row[clienteIndex];
        return clienteValue === null || clienteValue === '' || clienteValue === undefined;
    });
    
    if (filasFiltradas.length === 0) {
        alert('⚠️ No hay vehículos con cliente vacío para convertir a Disponible.');
        return;
    }
    
    // Preparar datos para enviar al backend
    // Las columnas del Excel son:
    // 0: Nº Fábrica, 1: Nº Chasis, 2: Modelo/Versión, 3: Color, 
    // 4: Fecha Finanzas, 5: Despacho Estimado, 6: Entrega Estimada,
    // 7: Fecha Recepción, 8: Ubicación, 9: Días Stock, 10: Precio p/ Disponible,
    // 11: Cód. Cliente, 12: Cliente, 13: Vendedor, 14: Operación
    const disponibles = filasFiltradas.map(row => {
        return {
            numero_fabrica: row[0] || '',
            numero_chasis: row[1] || '',
            modelo_version: row[2] || '',
            color: row[3] || '',
            fecha_finanzas: row[4] || '',
            despacho_estimado: row[5] || '',
            entrega_estimada: row[6] || '',
            fecha_recepcion: row[7] || '',
            ubicacion: row[8] || '',
            dias_stock: row[9] || '',
            precio_disponible: row[10] || '',
            cod_cliente: row[11] || '',
            cliente: row[12] || '',
            vendedor: row[13] || '',
            operacion: row[14] || ''
        };
    });
    
    // Confirmar con el usuario
    const confirmar = confirm(
        `¿Deseas convertir ${disponibles.length} vehículo(s) de Ventas Convencionales con cliente vacío al módulo Disponible?\n\n` +
        `Esta acción reemplazará todos los datos actuales en el módulo Disponible.`
    );
    
    if (!confirmar) {
        return;
    }
    
    // Mostrar spinner de carga
    const btnConvertir = document.getElementById('convertirDisponible');
    const textoOriginal = btnConvertir.innerHTML;
    btnConvertir.disabled = true;
    btnConvertir.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Convirtiendo...';
    
    // Enviar datos al backend
    fetch('/api/disponibles', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(disponibles)
    })
    .then(response => response.json())
    .then(data => {
        btnConvertir.disabled = false;
        btnConvertir.innerHTML = textoOriginal;
        
        if (data.success) {
            // Mostrar mensaje de éxito
            const mensaje = `✅ ${disponibles.length} vehículo(s) convertido(s) exitosamente al módulo Disponible.`;
            showSuccessMessage(mensaje);
            
            // Preguntar si desea ir al módulo 4
            setTimeout(() => {
                const irAModulo4 = confirm(
                    `Los vehículos han sido transferidos al módulo Disponible.\n\n` +
                    `¿Deseas ir ahora al módulo Disponible para verlos?`
                );
                
                if (irAModulo4) {
                    window.location.href = '/modulo4';
                }
            }, 1000);
        } else {
            alert('❌ Error al convertir a Disponible: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        btnConvertir.disabled = false;
        btnConvertir.innerHTML = textoOriginal;
        console.error('Error al convertir a Disponible:', error);
        alert('❌ Error al convertir a Disponible: ' + error.message);
    });
}

// Función para mostrar mensaje de éxito
function showSuccessMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success';
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '10000';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.transition = 'opacity 0.5s';
        alertDiv.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(alertDiv);
        }, 500);
    }, 3000);
}

// Función para exportar seguimiento a Excel
function exportarSeguimientoAExcel() {
    // Verificar que haya datos para exportar
    const tablas = document.querySelectorAll('.tab-pane table');
    if (tablas.length === 0) {
        showError('No hay datos para exportar');
        return;
    }
    
    // Crear un nuevo libro de Excel
    const wb = XLSX.utils.book_new();
    
    // Procesar cada pestaña (zona)
    document.querySelectorAll('.tab-pane').forEach((tabPane, index) => {
        const tabla = tabPane.querySelector('table');
        if (!tabla) return;
        
        // Obtener el nombre de la zona desde el título
        const titulo = tabPane.querySelector('h4');
        let nombreHoja = titulo ? titulo.textContent.trim() : `Zona ${index + 1}`;
        
        // Limpiar nombre de hoja (Excel tiene restricciones)
        nombreHoja = nombreHoja
            .replace(/[\\\/\?\*\[\]]/g, '') // Eliminar caracteres no permitidos
            .substring(0, 31); // Máximo 31 caracteres
        
        // Extraer datos de la tabla
        const datos = [];
        const headers = [];
        
        // Obtener headers
        const headerCells = tabla.querySelectorAll('thead th');
        headerCells.forEach(th => {
            headers.push(th.textContent.trim());
        });
        
        // Obtener filas de datos
        const rows = tabla.querySelectorAll('tbody tr');
        rows.forEach(tr => {
            const fila = {};
            const cells = tr.querySelectorAll('td');
            cells.forEach((td, i) => {
                if (headers[i]) {
                    fila[headers[i]] = td.textContent.trim();
                }
            });
            datos.push(fila);
        });
        
        // Crear hoja de Excel
        const ws = XLSX.utils.json_to_sheet(datos);
        
        // Ajustar ancho de columnas
        const colWidths = headers.map(header => {
            let maxWidth = header.length;
            datos.forEach(row => {
                const cellValue = row[header] ? row[header].toString() : '';
                maxWidth = Math.max(maxWidth, cellValue.length);
            });
            return { wch: Math.min(maxWidth + 2, 50) }; // Máximo 50 caracteres
        });
        ws['!cols'] = colWidths;
        
        // Agregar hoja al libro
        XLSX.utils.book_append_sheet(wb, ws, nombreHoja);
    });
    
    // Descargar archivo
    const fecha = new Date().toISOString().split('T')[0];
    XLSX.writeFile(wb, `seguimiento_unidades_${fecha}.xlsx`);
    
    showSuccessAlert('Archivo exportado correctamente');
}
