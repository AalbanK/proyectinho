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

calcularNeto = (bruto, tara ) => { // recibe como parámetro los inputs del html
    bruto=bruto.value;
    tara=tara.value;

    let soloDigitos = /^\d+$/;
    if ((bruto && tara ) && bruto.match(soloDigitos) && tara.match(soloDigitos)) {
        // Convertir a Integer ambos
        bruto = parseInt(bruto);        
        tara = parseInt(tara);
        if (bruto <= 0 || tara <= 0) {
            // para evitar calcular con valores negativos      
            return null;        
        }
        if (bruto>tara) return bruto-tara
        else return null
    }
    else return null
}

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

    listenerCalculoOrigen = () => {
        document.getElementById('neto').value = calcularNeto(inputBruto, inputTara);
    }
    listenerCalculoDestino = () => {
        document.getElementById('netod').value = calcularNeto(inputBrutod, inputTarad);
    }

    const inputBruto = document.querySelector('input[name="bruto"]')
    const inputTara = document.querySelector('input[name="tara"]')
    const inputBrutod = document.querySelector('input[name="brutod"]')
    const inputTarad = document.querySelector('input[name="tarad"]')

    inputBruto.addEventListener('blur', listenerCalculoOrigen);
    inputTara.addEventListener('blur', listenerCalculoOrigen);
    inputBrutod.addEventListener('blur', listenerCalculoDestino);
    inputTarad.addEventListener('blur', listenerCalculoDestino);

});