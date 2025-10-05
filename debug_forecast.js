// Script de diagnóstico para el problema de Forecast
console.log('🔍 DIAGNÓSTICO DE FORECAST');
console.log('========================');

// Verificar si el componente AnalysisModal existe
console.log('1. Verificando AnalysisModal...');
const analysisModal = document.querySelector('.analysis-modal');
if (analysisModal) {
    console.log('✅ AnalysisModal encontrado');
} else {
    console.log('❌ AnalysisModal NO encontrado');
}

// Verificar si la pestaña Forecast existe
console.log('2. Verificando pestaña Forecast...');
const forecastTab = document.querySelector('[data-tab="forecast"]');
if (forecastTab) {
    console.log('✅ Pestaña Forecast encontrada');
} else {
    console.log('❌ Pestaña Forecast NO encontrada');
}

// Verificar si el contenido de Forecast se está renderizando
console.log('3. Verificando contenido de Forecast...');
const forecastSection = document.querySelector('.forecast-section');
if (forecastSection) {
    console.log('✅ Sección Forecast encontrada');
    console.log('Contenido:', forecastSection.innerHTML.substring(0, 100) + '...');
} else {
    console.log('❌ Sección Forecast NO encontrada');
}

// Verificar navegación de pestañas
console.log('4. Verificando navegación...');
const tabButtons = document.querySelectorAll('.tab-button');
console.log('Pestañas encontradas:', tabButtons.length);
tabButtons.forEach((tab, index) => {
    console.log(`Pestaña ${index}:`, tab.textContent.trim());
});

// Verificar estado de React
console.log('5. Verificando estado de React...');
if (window.React) {
    console.log('✅ React cargado');
} else {
    console.log('❌ React NO cargado');
}

console.log('========================');
console.log('🎯 INSTRUCCIONES:');
console.log('1. Abre la consola del navegador (F12)');
console.log('2. Ejecuta este script');
console.log('3. Revisa los resultados');
console.log('4. Si hay errores, compártelos');
