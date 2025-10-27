// Variables globales
let disponiblesData = [];
let unidadesReservadas = [];
let disponiblesLoaded = false;
let reservadasLoaded = false;

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM Cargado - Inicializando Módulo 4');
    console.log('📍 Tab detalle existe:', !!document.getElementById('tab-detalle'));
    console.log('📍 Tbody existe:', !!document.getElementById('tablaDisponibles'));
    
    cargarDisponibles();
    cargarReservadas();
});

// Cargar unidades disponibles desde el servidor
function cargarDisponibles() {
    console.log('🔄 Cargando unidades disponibles...');
    fetch('/api/disponibles')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            disponiblesData = data || [];
            disponiblesLoaded = true;
            console.log('✅ Unidades disponibles cargadas:', disponiblesData.length);
            if (reservadasLoaded) {
                renderizarTabla();
            }
        })
        .catch(error => {
            console.error('❌ Error al cargar disponibles:', error);
            disponiblesData = [];
            disponiblesLoaded = true;
            showError('Error al cargar las unidades disponibles: ' + error.message);
            if (reservadasLoaded) {
                renderizarTabla();
            }
        });
}

// Cargar unidades reservadas desde el servidor
function cargarReservadas() {
    console.log('🔄 Cargando unidades reservadas...');
    fetch('/api/unidades_reservadas')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            unidadesReservadas = data || [];
            reservadasLoaded = true;
            console.log('✅ Unidades reservadas cargadas:', unidadesReservadas.length);
            updateReservadasCount();
            if (disponiblesLoaded) {
                renderizarTabla(); // Re-renderizar para aplicar filtro
            }
        })
        .catch(error => {
            console.error('❌ Error al cargar reservadas:', error);
            unidadesReservadas = [];
            reservadasLoaded = true;
            if (disponiblesLoaded) {
                renderizarTabla();
            }
        });
}

// Renderizar tabla de disponibles
function renderizarTabla() {
    const tbody = document.getElementById('tablaDisponibles');
    if (!tbody) {
        console.error('❌ No se encontró el elemento tablaDisponibles');
        return;
    }
    
    console.log('🔄 Renderizando tabla. Disponibles:', disponiblesData.length, 'Reservadas:', unidadesReservadas.length);
    
    tbody.innerHTML = '';
    
    // Filtrar unidades reservadas (ahora son objetos)
    const numerosReservados = unidadesReservadas.map(r => r.numero_fabrica);
    const disponiblesFiltrados = disponiblesData.filter(item => {
        return !numerosReservados.includes(item.numero_fabrica);
    });
    
    console.log('✅ Unidades filtradas (sin reservar):', disponiblesFiltrados.length);
    
    // Actualizar contador
    const totalElement = document.getElementById('totalDisponibles');
    if (totalElement) {
        totalElement.textContent = disponiblesFiltrados.length;
    }
    
    if (disponiblesFiltrados.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: #718096;">
                    <i class="fas fa-inbox" style="font-size: 3em; margin-bottom: 10px; display: block;"></i>
                    <strong>No hay unidades disponibles</strong><br>
                    <small>Convierte datos desde el Módulo 3 usando el botón "Convertir a Disponible"</small>
                </td>
            </tr>
        `;
        return;
    }
    
    // Ordenar por: 1) Entrega Estimada (más antigua primero), 2) Color (A-Z), 3) Modelo/Versión (A-Z)
    disponiblesFiltrados.sort((a, b) => {
        // 1. Ordenar por Entrega Estimada (fecha más antigua primero)
        const fechaA = new Date(a.entrega_estimada || '9999-12-31');
        const fechaB = new Date(b.entrega_estimada || '9999-12-31');
        
        if (fechaA.getTime() !== fechaB.getTime()) {
            return fechaA - fechaB; // Más antigua primero
        }
        
        // 2. Si las fechas son iguales, ordenar por Color (A-Z)
        const colorA = (a.color || '').toLowerCase();
        const colorB = (b.color || '').toLowerCase();
        
        if (colorA !== colorB) {
            return colorA.localeCompare(colorB);
        }
        
        // 3. Si los colores son iguales, ordenar por Modelo/Versión (A-Z)
        const modeloA = (a.modelo_version || '').toLowerCase();
        const modeloB = (b.modelo_version || '').toLowerCase();
        
        return modeloA.localeCompare(modeloB);
    });
    
    disponiblesFiltrados.forEach((item, index) => {
        const tr = document.createElement('tr');
        
        // Determinar estilo de descuento individual
        let descIndividualStyle = '';
        let descIndividualText = '-';
        if (item.descuento_individual && item.descuento_individual > 0) {
            descIndividualStyle = 'background: #e6f7ff; color: #0066cc; font-weight: 600; text-align: center;';
            descIndividualText = `${item.descuento_individual}%`;
        } else {
            descIndividualStyle = 'color: #a0aec0; font-size: 0.9em; text-align: center;';
            descIndividualText = '0%';
        }
        
        // Determinar estilo de descuentos adicionales
        let descAdicionalStyle = '';
        let descAdicionalText = item.detalles_descuento || 'Sin descuentos';
        if (item.descuento_adicional && item.descuento_adicional > 0) {
            descAdicionalStyle = 'background: #fef5e7; color: #d68910; font-weight: 600;';
            descAdicionalText = `${item.descuento_adicional}% (${item.detalles_descuento})`;
        } else {
            descAdicionalStyle = 'color: #a0aec0; font-size: 0.9em;';
        }
        
        tr.innerHTML = `
            <td>${item.numero_fabrica || ''}</td>
            <td><strong>${item.modelo_version || ''}</strong></td>
            <td>${item.color || ''}</td>
            <td>${formatearFecha(item.entrega_estimada)}</td>
            <td>${item.ubicacion || ''}</td>
            <td style="${descIndividualStyle}">${descIndividualText}</td>
            <td style="${descAdicionalStyle}">${descAdicionalText}</td>
            <td style="color: #48bb78; font-weight: 600;">$ ${formatearNumero(item.precio_disponible || 0)}</td>
        `;
        
        tbody.appendChild(tr);
        
        if (index === 0) {
            console.log('✅ Primera fila agregada:', item.numero_fabrica, item.modelo_version);
        }
    });
    
    console.log('✅ Renderizado completo. Total filas:', disponiblesFiltrados.length);
    console.log('📊 Tbody children count:', tbody.children.length);
    console.log('📊 Tab detalle display:', window.getComputedStyle(document.getElementById('tab-detalle')).display);
    console.log('📊 Tab detalle tiene clase active:', document.getElementById('tab-detalle').classList.contains('active'));
    
    document.getElementById('totalDisponibles').textContent = disponiblesFiltrados.length;
}

// Actualizar disponibles (recargar desde servidor)
function actualizarDisponibles() {
    cargarDisponibles();
    showSuccess('Tabla actualizada correctamente');
}

// Modal de Unidades Reservadas
function openReservadasModal() {
    const modal = document.getElementById('modalReservadas');
    modal.style.display = 'flex';
    renderizarListaReservadas();
}

function closeReservadasModal() {
    const modal = document.getElementById('modalReservadas');
    modal.style.display = 'none';
}

// Renderizar lista de reservadas en el modal
function renderizarListaReservadas() {
    const lista = document.getElementById('listaReservadas');
    
    if (unidadesReservadas.length === 0) {
        lista.innerHTML = '<p style="text-align: center; color: #718096; padding: 20px;">No hay unidades reservadas</p>';
        return;
    }
    
    lista.innerHTML = '';
    unidadesReservadas.forEach(reserva => {
        const div = document.createElement('div');
        div.className = 'reservada-item';
        div.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #e2e8f0;';
        
        div.innerHTML = `
            <div style="flex: 1;">
                <div style="font-weight: 600;">${reserva.numero_fabrica}</div>
                <div style="font-size: 0.9em; color: #718096;"><i class="fas fa-user"></i> ${reserva.vendedor || 'Sin vendedor'}</div>
            </div>
            <button class="btn-delete" onclick="removeReservada('${reserva.numero_fabrica}')" style="background: #fc8181; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                <i class="fas fa-trash"></i>
            </button>
        `;
        
        lista.appendChild(div);
    });
}

// Agregar unidad reservada
function addReservada() {
    const inputNumero = document.getElementById('inputReservada');
    const inputVendedor = document.getElementById('inputVendedor');
    const numero = inputNumero.value.trim();
    const vendedor = inputVendedor.value.trim();
    
    if (!numero) {
        showError('Por favor ingresa un número de fábrica');
        return;
    }
    
    if (!vendedor) {
        showError('Por favor ingresa el nombre del vendedor');
        return;
    }
    
    // Verificar si ya existe
    const yaExiste = unidadesReservadas.some(r => r.numero_fabrica === numero);
    if (yaExiste) {
        showError('Esta unidad ya está en la lista de reservadas');
        return;
    }
    
    // Enviar al servidor
    fetch('/api/unidades_reservadas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            numero_fabrica: numero,
            vendedor: vendedor 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Agregar a la lista local
            unidadesReservadas.push({
                numero_fabrica: numero,
                vendedor: vendedor,
                fecha_agregado: new Date().toISOString()
            });
            
            inputNumero.value = '';
            inputVendedor.value = '';
            renderizarListaReservadas();
            updateReservadasCount();
            renderizarTabla(); // Re-renderizar para aplicar filtro (quitar de disponibles)
            showSuccess(`Unidad ${numero} reservada para ${vendedor}`);
        } else {
            showError(data.error || 'Error al agregar unidad reservada');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error al agregar unidad reservada');
    });
}

// Eliminar unidad reservada
function removeReservada(numero) {
    if (!confirm(`¿Eliminar ${numero} de las unidades reservadas?\n\nEl vehículo volverá a aparecer en la lista de disponibles.`)) {
        return;
    }
    
    fetch(`/api/unidades_reservadas/${numero}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Eliminar de la lista local (ahora son objetos)
            unidadesReservadas = unidadesReservadas.filter(r => r.numero_fabrica !== numero);
            renderizarListaReservadas();
            updateReservadasCount();
            renderizarTabla(); // Re-renderizar para mostrar el vehículo de nuevo en disponibles
            showSuccess(`Unidad ${numero} eliminada de reservadas y devuelta a disponibles`);
        } else {
            showError(data.error || 'Error al eliminar unidad reservada');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error al eliminar unidad reservada');
    });
}

// Actualizar contador de reservadas
function updateReservadasCount() {
    document.getElementById('reservadasCount').textContent = unidadesReservadas.length;
}

// Formatear fecha
function formatearFecha(fecha) {
    if (!fecha) return '';
    const date = new Date(fecha);
    if (isNaN(date.getTime())) return fecha;
    return date.toLocaleDateString('es-AR');
}

// Formatear número
function formatearNumero(num) {
    return new Intl.NumberFormat('es-AR').format(num);
}

// Mostrar mensaje de éxito
function showSuccess(message) {
    const alert = document.getElementById('successAlert');
    const messageSpan = document.getElementById('successMessage');
    messageSpan.textContent = message;
    alert.style.display = 'block';
    
    setTimeout(() => {
        alert.style.display = 'none';
    }, 3000);
}

// Mostrar mensaje de error
function showError(message) {
    const alert = document.getElementById('errorAlert');
    const messageSpan = document.getElementById('errorMessage');
    messageSpan.textContent = message;
    alert.style.display = 'block';
    
    setTimeout(() => {
        alert.style.display = 'none';
    }, 5000);
}

// Cerrar modal al hacer clic fuera
window.addEventListener('click', function(event) {
    const modal = document.getElementById('modalReservadas');
    if (event.target === modal) {
        closeReservadasModal();
    }
});

// Cambiar entre pestañas
function switchTab(tabName) {
    // Ocultar todos los contenidos
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Desactivar todos los botones
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Activar el contenido seleccionado
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Activar el botón correspondiente
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => {
        if ((tabName === 'detalle' && button.textContent.includes('Detalle')) ||
            (tabName === 'resumen' && button.textContent.includes('Resumen'))) {
            button.classList.add('active');
        }
    });
    
    // Si se cambia a resumen, renderizar el resumen
    if (tabName === 'resumen') {
        renderizarResumen();
    }
}

// Renderizar tabla de resumen por modelo
function renderizarResumen() {
    const tbody = document.getElementById('tablaResumen');
    tbody.innerHTML = '';
    
    // Filtrar unidades no reservadas
    const numerosReservados = unidadesReservadas.map(r => r.numero_fabrica);
    const disponiblesSinReservar = disponiblesData.filter(unidad => 
        !numerosReservados.includes(unidad.numero_fabrica)
    );
    
    // Contar por modelo
    const conteo = {};
    disponiblesSinReservar.forEach(unidad => {
        const modelo = unidad.modelo_version;
        if (conteo[modelo]) {
            conteo[modelo]++;
        } else {
            conteo[modelo] = 1;
        }
    });
    
    // Convertir a array y ordenar por cantidad descendente
    const resumenArray = Object.entries(conteo).map(([modelo, cantidad]) => ({
        modelo,
        cantidad
    })).sort((a, b) => b.cantidad - a.cantidad);
    
    // Renderizar tabla
    if (resumenArray.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="2" style="text-align: center; padding: 2rem; color: #999;">
                    No hay unidades disponibles
                </td>
            </tr>
        `;
        return;
    }
    
    let totalUnidades = 0;
    resumenArray.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="font-weight: 500;">${item.modelo}</td>
            <td style="text-align: center; font-size: 1.1rem; font-weight: 600; color: #2563eb;">
                ${item.cantidad}
            </td>
        `;
        tbody.appendChild(row);
        totalUnidades += item.cantidad;
    });
    
    // Fila de total
    const totalRow = document.createElement('tr');
    totalRow.style.backgroundColor = '#f7fafc';
    totalRow.style.fontWeight = 'bold';
    totalRow.innerHTML = `
        <td style="text-align: right; padding: 1rem;">TOTAL:</td>
        <td style="text-align: center; font-size: 1.2rem; color: #16a34a;">
            ${totalUnidades}
        </td>
    `;
    tbody.appendChild(totalRow);
}

// Exportar tabla a Excel
function exportarAExcel() {
    // Filtrar unidades no reservadas
    const numerosReservados = unidadesReservadas.map(r => r.numero_fabrica);
    const disponiblesFiltrados = disponiblesData.filter(item => {
        return !numerosReservados.includes(item.numero_fabrica);
    });
    
    if (disponiblesFiltrados.length === 0) {
        showError('No hay datos para exportar');
        return;
    }
    
    // Crear el contenido CSV
    let csvContent = '\uFEFF'; // BOM para UTF-8
    
    // Encabezados
    csvContent += 'Nº Fábrica,Modelo/Versión,Color,Entrega Estimada,Ubicación,Desc. Individual,Desc. Adicionales,Precio Final\n';
    
    // Ordenar igual que la tabla
    disponiblesFiltrados.sort((a, b) => {
        const fechaA = new Date(a.entrega_estimada || '9999-12-31');
        const fechaB = new Date(b.entrega_estimada || '9999-12-31');
        
        if (fechaA.getTime() !== fechaB.getTime()) {
            return fechaA - fechaB;
        }
        
        const colorA = (a.color || '').toLowerCase();
        const colorB = (b.color || '').toLowerCase();
        
        if (colorA !== colorB) {
            return colorA.localeCompare(colorB);
        }
        
        const modeloA = (a.modelo_version || '').toLowerCase();
        const modeloB = (b.modelo_version || '').toLowerCase();
        
        return modeloA.localeCompare(modeloB);
    });
    
    // Agregar filas
    disponiblesFiltrados.forEach(item => {
        const descIndividual = item.descuento_individual || 0;
        const descAdicional = item.descuento_adicional || 0;
        const detalleDesc = item.detalles_descuento || 'Sin descuentos';
        
        const row = [
            item.numero_fabrica || '',
            `"${(item.modelo_version || '').replace(/"/g, '""')}"`,
            item.color || '',
            formatearFecha(item.entrega_estimada),
            item.ubicacion || '',
            `${descIndividual}%`,
            descAdicional > 0 ? `${descAdicional}% (${detalleDesc})` : 'Sin descuentos',
            formatearNumero(item.precio_disponible || 0)
        ];
        
        csvContent += row.join(',') + '\n';
    });
    
    // Crear blob y descargar
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    const fecha = new Date().toISOString().split('T')[0];
    link.setAttribute('href', url);
    link.setAttribute('download', `disponibles_${fecha}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showSuccess(`Se exportaron ${disponiblesFiltrados.length} unidades a Excel`);
}

