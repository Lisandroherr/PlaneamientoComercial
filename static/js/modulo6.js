// Variables globales
let datosRecaudacion = null;

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    cargarRecaudacion();
});

// Cargar datos de recaudación
function cargarRecaudacion() {
    console.log('🔄 Cargando datos de recaudación...');
    
    fetch('/api/recaudacion')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                datosRecaudacion = data;
                console.log('✅ Datos de recaudación cargados:', data);
                actualizarDashboard();
            } else {
                showError('Error al cargar los datos de recaudación');
            }
        })
        .catch(error => {
            console.error('❌ Error al cargar recaudación:', error);
            showError('Error al cargar los datos de recaudación');
        });
}

// Actualizar dashboard con los datos
function actualizarDashboard() {
    if (!datosRecaudacion) return;
    
    // Actualizar tarjetas de resumen
    document.getElementById('totalGeneral').textContent = formatearMoneda(datosRecaudacion.total_general);
    document.getElementById('cantidadTotal').textContent = datosRecaudacion.cantidad_total;
    
    document.getElementById('totalStock').textContent = formatearMoneda(datosRecaudacion.en_stock.total);
    document.getElementById('cantidadStock').textContent = datosRecaudacion.en_stock.cantidad;
    
    document.getElementById('totalNoStock').textContent = formatearMoneda(datosRecaudacion.no_stock.total);
    document.getElementById('cantidadNoStock').textContent = datosRecaudacion.no_stock.cantidad;
    
    // Actualizar contadores de tabs
    document.getElementById('tabStockCount').textContent = datosRecaudacion.en_stock.cantidad;
    document.getElementById('tabNoStockCount').textContent = datosRecaudacion.no_stock.cantidad;
    
    // Renderizar tablas
    renderizarTablaStock();
    renderizarTablaNoStock();
}

// Renderizar tabla de En Stock
function renderizarTablaStock() {
    const tbody = document.getElementById('tablaStock');
    tbody.innerHTML = '';
    
    if (datosRecaudacion.en_stock.unidades.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; padding: 40px; color: #718096;">
                    <i class="fas fa-inbox" style="font-size: 3em; margin-bottom: 10px; display: block;"></i>
                    <strong>No hay unidades en stock</strong>
                </td>
            </tr>
        `;
        return;
    }
    
    datosRecaudacion.en_stock.unidades.forEach(unidad => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${unidad.numero_fabrica}</td>
            <td><strong>${unidad.modelo_version || ''}</strong></td>
            <td><span style="color: #48bb78;"><i class="fas fa-warehouse"></i> ${unidad.ubicacion || ''}</span></td>
            <td style="color: #48bb78; font-weight: 600; font-size: 1.1em;">$ ${formatearNumero(unidad.precio)}</td>
        `;
        tbody.appendChild(tr);
    });
    
    // Agregar fila de total
    const trTotal = document.createElement('tr');
    trTotal.style.background = '#f7fafc';
    trTotal.style.fontWeight = 'bold';
    trTotal.innerHTML = `
        <td colspan="3" style="text-align: right; padding: 15px;"><strong>TOTAL EN STOCK:</strong></td>
        <td style="color: #48bb78; font-weight: 700; font-size: 1.2em;">$ ${formatearNumero(datosRecaudacion.en_stock.total)}</td>
    `;
    tbody.appendChild(trTotal);
}

// Renderizar tabla de No Stock
function renderizarTablaNoStock() {
    const tbody = document.getElementById('tablaNoStock');
    tbody.innerHTML = '';
    
    if (datosRecaudacion.no_stock.unidades.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; padding: 40px; color: #718096;">
                    <i class="fas fa-inbox" style="font-size: 3em; margin-bottom: 10px; display: block;"></i>
                    <strong>No hay unidades fuera de stock</strong>
                </td>
            </tr>
        `;
        return;
    }
    
    datosRecaudacion.no_stock.unidades.forEach(unidad => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${unidad.numero_fabrica}</td>
            <td><strong>${unidad.modelo_version || ''}</strong></td>
            <td><span style="color: #f56565;"><i class="fas fa-truck"></i> ${unidad.ubicacion || ''}</span></td>
            <td style="color: #f56565; font-weight: 600; font-size: 1.1em;">$ ${formatearNumero(unidad.precio)}</td>
        `;
        tbody.appendChild(tr);
    });
    
    // Agregar fila de total
    const trTotal = document.createElement('tr');
    trTotal.style.background = '#f7fafc';
    trTotal.style.fontWeight = 'bold';
    trTotal.innerHTML = `
        <td colspan="3" style="text-align: right; padding: 15px;"><strong>TOTAL NO STOCK:</strong></td>
        <td style="color: #f56565; font-weight: 700; font-size: 1.2em;">$ ${formatearNumero(datosRecaudacion.no_stock.total)}</td>
    `;
    tbody.appendChild(trTotal);
}

// Cambiar entre tabs
function mostrarTab(tipo) {
    // Ocultar todas las tabs
    document.getElementById('tab-stock').style.display = 'none';
    document.getElementById('tab-nostock').style.display = 'none';
    
    // Remover clase active de todos los botones
    document.getElementById('tab-stock-btn').classList.remove('active');
    document.getElementById('tab-nostock-btn').classList.remove('active');
    
    // Mostrar la tab seleccionada
    if (tipo === 'stock') {
        document.getElementById('tab-stock').style.display = 'block';
        document.getElementById('tab-stock-btn').classList.add('active');
    } else {
        document.getElementById('tab-nostock').style.display = 'block';
        document.getElementById('tab-nostock-btn').classList.add('active');
    }
}

// Actualizar datos (recargar)
function actualizarRecaudacion() {
    cargarRecaudacion();
    showSuccess('Datos actualizados correctamente');
}

// Formatear número con separadores de miles
function formatearNumero(numero) {
    return new Intl.NumberFormat('es-AR').format(Math.round(numero));
}

// Formatear moneda
function formatearMoneda(valor) {
    return '$ ' + formatearNumero(valor);
}

// Mostrar mensaje de éxito
function showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success';
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '10000';
    alertDiv.style.minWidth = '300px';
    alertDiv.style.background = '#48bb78';
    alertDiv.style.color = 'white';
    alertDiv.style.padding = '15px 20px';
    alertDiv.style.borderRadius = '8px';
    alertDiv.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
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

// Mostrar mensaje de error
function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-error';
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '10000';
    alertDiv.style.minWidth = '300px';
    alertDiv.style.background = '#f56565';
    alertDiv.style.color = 'white';
    alertDiv.style.padding = '15px 20px';
    alertDiv.style.borderRadius = '8px';
    alertDiv.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
    alertDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.transition = 'opacity 0.5s';
        alertDiv.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(alertDiv);
        }, 500);
    }, 5000);
}
