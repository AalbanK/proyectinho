let jsonProductos = null;
let jsonCiudades = null;
let selectProducto = null;

async function obtenerContrato(idcontrato) {
    const response = await fetch(`/contratos/detalles/${idcontrato}`);
    if (!response.ok) {
        const message = `Ocurrió un error al intentar obtener el contrato: ${response.status}`;
        throw new Error(message);
    }
    const contrato = await response.json();
    return contrato;
}

// calcularSubtotales = (cantidad, precio, subtotal, subtotal_iva, porcentaje_iva) => {

//     cantidad = cantidad.value;
//     precio = precio.value;
//     porcentaje_iva = parseInt(porcentaje_iva);

//     // Verificar si solo tienen dígitos
//     let soloDigitos = /^\d+$/;
//     if (!cantidad.match(soloDigitos) || !precio.match(soloDigitos)) {            
//         subtotal.value = null;
//         subtotal_iva.value = null;
//         return;
//     }
//     // Convertir a Integer ambos
//     cantidad = parseInt(cantidad);        
//     precio = parseInt(precio);
//     if (cantidad <= 0 || precio <= 0) {
//         // para evitar calcular con valores negativos      
//         subtotal.value = null;
//         subtotal_iva.value = null;
//         return;        
//     }
    
//     let importesubtotal = cantidad * precio;
    
//     let importeiva = Math.round((porcentaje_iva * importesubtotal) / (porcentaje_iva + 100));
//     subtotal.value = importesubtotal;
//     subtotal_iva.value = importeiva;        
// }

// calcularTotal = (arraySubtotales) => {
//     let total = 0;
//     arraySubtotales.forEach(campo => {
//         total += (parseInt(campo.value) || 0); // el or es por si viene null o undefined o NaN (Not a Number): de ser así, pone 0
//     });
//     return total;
// };

crearElemento = (tipo, nombre, listaClases = [], textoContenido, tipoInput, requerido, deshabilitado) => {
    let elemento = document.createElement(tipo);

    if(listaClases.length > 0){
        elemento.classList.add(...listaClases); // el ... acá es como hacer un for por cada elemento del array. Buscar "operador spread"
    }

    if(nombre){
        elemento.name = nombre; // el atributo name es el que contiene el nombre del atributo en la bd
    }

    if(requerido){
        elemento.setAttribute("required", "required");
    }
    
    if(deshabilitado){
        elemento.setAttribute("readonly", "readonly");
        elemento.setAttribute("disabled", "disabled");
    }

    if(tipoInput){
        elemento.type = tipoInput;
    }

    /*if(tipo === "label"){
        labelInput.innerHTML = textoContenido;
    }*/

    if(textoContenido){
        if (!tipoInput){
            elemento.textContent = textoContenido;
        }
    }

    return elemento;
}

agregarOpcion = (elemento, valor, texto, campos = {}) => {
    let nuevaOpcion = document.createElement("option");
    nuevaOpcion.value = valor;
    nuevaOpcion.text = valor ? `${texto} (${valor})` : `${texto}`;
    if(campos){
        for (let clave in campos) {
            nuevaOpcion.setAttribute(`data-${clave}`, campos[clave]);
        }
    }
    elemento.add(nuevaOpcion);
}

window.addEventListener('DOMContentLoaded', async function () {

    //cargar detalles de contrato
    const selectContrato = document.querySelector("#idContrato");
    selectContrato.addEventListener('change', async function (event) {
        let idcontrato = event.target.value; //  equivale al valor desde donde se está disparando el event
        clienteForm=document.getElementById('desc_cliente');
        proveedorForm=document.getElementById('desc_proveedor')
        prductoForm=document.querySelector('[name="producto"]');
        ciudadOForm=document.querySelector('[name="ciudad_O"]')
        ciudadDForm=document.querySelector('[name="ciudad_D"]')
        departamentoOForm=document.querySelector('[name="departamento_O"]')
        departamentoDForm=document.querySelector('[name="departamento_D"]')
        if (idcontrato && idcontrato != "undefined") {
            let jsonContrato = await obtenerContrato(idcontrato);
            console.log(jsonContrato)
            clienteForm.value= jsonContrato.desc_cliente;
            proveedorForm.value= jsonContrato.desc_proveedor;
            prductoForm.value= jsonContrato.desc_producto;
            prductoForm.dispatchEvent(new Event("change"));
            ciudadOForm.value= jsonContrato.desc_ciudad_origen;
            ciudadDForm.value= jsonContrato.desc_ciudad_destino;
            departamentoOForm.value= jsonContrato.desc_depto_origen;
            departamentoDForm.value= jsonContrato.desc_depto_destino;
            }
        else {
            clienteForm.value= "Primero seleccione un contrato";
            proveedorForm.value= "Primero seleccione un contrato";
            prductoForm.value= "Primero seleccione un contrato";
            ciudadOForm.value= "Primero seleccione un contrato";
            ciudadDForm.value= "Primero seleccione un contrato";
            departamentoOForm.value= "Primero seleccione un contrato";
            departamentoDForm.value= "Primero seleccione un contrato";
    
        }
        
    });
    selectContrato.dispatchEvent(new Event("change")); //para disparar el evento de cambio

    remisionForm = document.getElementById('remisionForm');
    /*remisionForm.addEventListener('submit', async function(event) {
        event.preventDefault();
       
        let remision = {};
        let formData = new FormData(event.target);
        
        for (let pair of formData.entries()) {
            if(pair[1]){ // solo si el value no es null, undefined o vacío
                remision[pair[0]] = pair[1]; // 0 para key (clave), 1 para value (valor)
            }
        }
    
        // Convertir el objeto a JSON
        let remisionJSON = JSON.stringify(remision);
        console.log(remisionJSON);
        
        divAlerta = crearElemento("div", "", ["alert"]);
        divAlerta.id = "respuesta_servidor";
        divAlerta.role = "alert"

        divRemision = document.getElementById("remision");
        parrafoMensaje = crearElemento("p");
       
        let opcionesRequest = {
            method: 'POST',
            headers: {'Accept': 'application/json', 'Content-Type': 'application/json' },
            body: remisionJSON
        };
        await fetch('/remisiones/nuevo', opcionesRequest)
        .then(response => {
            //console.log(response)
            if(document.getElementById(divAlerta.id)) divRemision.removeChild(document.getElementById(divAlerta.id));
            if (response.ok === true){
                divAlerta.classList.remove("alert-success", "alert-danger");
                divAlerta.classList.add("alert-success");
                if(divAlerta.firstElementChild){ // el primer elemento es el párrafo con el mensaje
                    divAlerta.removeChild(divAlerta.firstElementChild);
                }
                parrafoMensaje.textContent = 'La remision se ha insertado correctamente.';
                divAlerta.appendChild(parrafoMensaje);
                divRemision.prepend(divAlerta); // prepend para ponerlo como primer hijo del div
            }
            else {
                divAlerta.classList.remove("alert-success", "alert-danger")
                divAlerta.classList.add("alert-danger");
                if(divAlerta.firstElementChild){ // el primer elemento es el párrafo con el mensaje
                    divAlerta.removeChild(divAlerta.firstElementChild);
                }
                parrafoMensaje.textContent = 'Ocurrió un error al intentar guardar la remision. \nMensaje del servidor: ';
                if(response.status === 422 ){ //Unprocessable Entity. Suele devolver cuando falta algún parámetro o tiene valor inválido
                    response.json().then( (respuesta) =>{
                        console.log(respuesta)
                        if (respuesta.detail){
                            let mensaje_error;
                            try { //imprime object object :(
                                mensaje_error = JSON.parse(respuesta.detail);
                            } catch (e) {
                                mensaje_error = respuesta.detail;
                            }
                            console.log(mensaje_error)
                            parrafoMensaje.textContent += mensaje_error;
                        }
                    })
                }
                else if(response.status === 500){
                    response.json().then( (respuesta) =>{
                        if(respuesta.error){
                            let mensaje_error;
                            try {
                                mensaje_error = JSON.parse(respuesta.error);
                            } catch (e) {
                                mensaje_error = respuesta.error;
                            }
                            console.log(mensaje_error)
                            parrafoMensaje.textContent += mensaje_error;
                        }
                    })
                }
                divAlerta.appendChild(parrafoMensaje);
                divRemision.prepend(divAlerta); // prepend para ponerlo como primer hijo del div
            }
        })
        .then(data => console.log(data))
        .catch((error) => {
            console.error('Error:', error);
        });
    
   });*/
});