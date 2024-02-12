let fechaHoy = new Date()
let fechaHoyCadena = fechaHoy.toISOString().substr(0, 10) // formato: yyyy-mm-dd
let quinceDiasEnMilisegundos = 1000 * 60 * 60 * 24 * 15; // milisegundos * (1 segundo) * (1 minuto) * (1 día) * (15 días)
let resta = fechaHoy.getTime() - quinceDiasEnMilisegundos; //getTime devuelve milisegundos de esa fecha
let fechaHaceDosSemanas = new Date(resta);
let fechaHaceDosSemanasCadena = fechaHaceDosSemanas.toISOString().substr(0, 10)

let tablaStock, tablaDT =  null;
let datos = [];
let urlEspanholDT =  '/static/vendor/datatables/es-ES.json';
const urlInformeStock = '/informes/stock';
const titulo_reporte = 'Movimientos de Stock'

inicializarDataTable = (tabla, datos, columnas, urlIdioma, parametros, titulo_reporte) => {
  if ( $.fn.DataTable.isDataTable(tabla) ) { 
    tabla.DataTable().destroy(); //destruir el datatable si ya existe
  }
  return tabla.DataTable({
    data: datos,
    dataSrc: '',
    columns: columnas,
    language: {
        url: urlIdioma
    },
    dom: 'Bfrtip',
    buttons: [
      {
        extend: 'excel', // extensión del plugin
        text: 'Excel', // texto del botón
        filename: `${titulo_reporte} - ${fechaHoy.toISOString()}`, // título con fecha + hora actuales
        title: titulo_reporte,
        messageTop: function () { // va entre el título y la tabla
            // por cada clave (key) de "parametros", reemplaza los guiones bajos de las claves por espacios, además de colocar el texto en formato "clave: valor"
            // ej.: "'Tipo_Movimiento':'Todos'" pasa a ser "Tipo Movimiento: Todos"
          let paramsString = Object.keys(parametros).map(function(key) {
            return key.replace('_', ' ') + ': ' + parametros[key];
          }).join('\n');
          return paramsString;
        }
      },
      {
        extend: 'pdf', // extensión del plugin
        text: 'PDF', //texto del botón
        title: titulo_reporte,
        filename: `${titulo_reporte} - ${fechaHoy.toISOString()}`, // título con fecha + hora actuales
        messageTop: function () { // va entre el título y la tabla
            // por cada clave (key) de "parametros", reemplaza los guiones bajos de las claves por espacios, además de colocar el texto en formato "clave: valor"
            // ej.: "'Tipo_Movimiento':'Todos'" pasa a ser "Tipo Movimiento: Todos"
          let paramsString = Object.keys(parametros).map(function(key) {
            return key.replace('_', ' ') + ': ' + parametros[key];
          }).join('\n');
          return paramsString;
        }
      }
   ]
  });
}

toggleFechas = (elemento) => {
  let rangoFechas = elemento;
  switch(rangoFechas){
    case "esQuince": {
      $('#inputDesde').val(fechaHaceDosSemanasCadena);
      $('#inputHasta').val(fechaHoyCadena);
      $('#inputDesde').prop( "disabled", true );
      $('#inputHasta').prop( "disabled", true );
      break;
    }
    case "esPersonalizado": {
      $('#inputDesde').val(fechaHoyCadena);
      $('#inputHasta').val(fechaHoyCadena);
      $('#inputDesde').prop( "disabled", false );
      $('#inputHasta').prop( "disabled", false );
      break;
    }
  }   
}

$(document).ready(function(){

    tablaStock = $("#movimientos_stock");
    document.querySelectorAll('[name=gridRadios]').forEach((radio) => radio.addEventListener('click', (event) => toggleFechas(event.target.value)));
    toggleFechas(document.querySelector('[name=gridRadios]:checked').value);

    document.querySelector('#parametros_stock').addEventListener('submit', function(e) {
        e.preventDefault(); // evita el comportamiento por defecto al hacer submit al formulario
        let fechaDesde = document.querySelector('#inputDesde').value;
        let fechaHasta = document.querySelector('#inputHasta').value;
        let producto = document.querySelector('#inputProducto');
        let tipoMov = document.querySelector('#inputTipoMov');

        datos = []; // se limpia el contenido de datos

        // parámetros a pasar al request.
        parametros = {
            fecha_desde: fechaDesde,
            fecha_hasta: fechaHasta,
            producto: producto.value,
            tipo_movimiento: tipoMov.value
        }

        parametros_dt = {}; // los parámetros a pasar al datatable (para la impresión del reporte). Los parámetros acá están basados en la variable "parametros"
        parametros_dt.Desde = parametros.fecha_desde ? parametros.fecha_desde : '-'; // coloca un guión si no se pasó el parámetro
        parametros_dt.Hasta = parametros.fecha_hasta ? parametros.fecha_hasta : '-'; // coloca un guión si no se pasó el parámetro 
        parametros_dt.Producto = parametros.producto ? (producto.options[producto.selectedIndex].text) : 'Todos' // Muestra el texto "Todos" si no se pasó el parámetro, caso contrario muestra el texto de la opción seleccionada en el select
        parametros_dt.Tipo_Movimiento = parametros.tipo_movimiento ? (tipoMov.options[tipoMov.selectedIndex].text) : 'Todos' // Muestra el texto "Todos" si no se pasó el parámetro, caso contrario muestra el texto de la opción seleccionada en el select

        fetch(urlInformeStock, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(parametros) // se convierten los parámetros a JSON, en este caso
        })
        .then(response => response.json())
        .then(json => {
            datos = json;
            console.log(datos);
            columnas = [
                { title: "Producto", data: "descripcion" },
                { title: "Tipo de Movimiento", data: "tipo_movimiento" },
                { title: "Cantidad", data: "cantidad" },
                { title: "Fecha", data: "fecha" }
            ]
            inicializarDataTable(tablaStock, datos, columnas, urlEspanholDT, parametros_dt, titulo_reporte)
                })
        .catch(error => {
            datos = [];
            let errorMessage = "Falló el request: " + error;
            
        });
    });
});
