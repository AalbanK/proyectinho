let jsonProductos = null;
let jsonCiudades = null;
let selectProducto = null;

calcularSubtotales = (cantidad, precio, subtotal, subtotal_iva, porcentaje_iva) => {

    cantidad = cantidad.value;
    precio = precio.value;
    porcentaje_iva = parseInt(porcentaje_iva);

    // Verificar si solo tienen dígitos
    let soloDigitos = /^\d+$/;
    if (!cantidad.match(soloDigitos) || !precio.match(soloDigitos)) {            
        subtotal.value = null;
        subtotal_iva.value = null;
        return;
    }
    // Convertir a Integer ambos
    cantidad = parseInt(cantidad);        
    precio = parseInt(precio);
    if (cantidad <= 0 || precio <= 0) {
        // para evitar calcular con valores negativos      
        subtotal.value = null;
        subtotal_iva.value = null;
        return;        
    }
    
    let importesubtotal = cantidad * precio;
    
    let importeiva = Math.round((porcentaje_iva * importesubtotal) / (porcentaje_iva + 100));
    subtotal.value = importesubtotal;
    subtotal_iva.value = importeiva;        
}

calcularTotal = (arraySubtotales) => {
    let total = 0;
    arraySubtotales.forEach(campo => {
        total += (parseInt(campo.value) || 0); // el or es por si viene null o undefined o NaN (Not a Number): de ser así, pone 0
    });
    return total;
};

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


fetchCargarProductos = async () => {
    selectProducto = crearElemento("select", "productos[]", ["form-control"], "", "", true);
    selectProducto.length = 0; //para vaciar el select, por si acaso
    agregarOpcion(selectProducto, '', 'Seleccione un Producto...');
    await fetch('/productos/todos')
    .then((response) => response.json())
    .then((productos) => {
        for (let producto of productos) {
            agregarOpcion(selectProducto, producto.idproducto, producto.descripcion, {"iva": producto.porcentaje_iva})
        }

    })
    .catch(error => {
        console.error(error)
        agregarOpcion(selectProducto, 0, 'Sin Datos');
    });
};

crearFila = (crearBotonEliminar) => {
    let divPadre = crearElemento("div", "fila", []);
    let elementoLinea = document.createElement("hr");
    divPadre.appendChild(elementoLinea);

    //un div form-row que contiene varios div de clase col. Cada uno de esos divs tiene un input o un select
    let elementoDiv = crearElemento("div", "", ["form-row", "mb-2", "fila_detalle"]);
    let colAutoDiv = crearElemento("div", "", ["form-group", "col-12", "col-md-4", "col-lg-3", "d-flex", "flex-column", "justify-content-end"]);
    let labelProducto = crearElemento("label", "", [], "Producto");
    let selProducto = selectProducto.cloneNode(true); // clonar el nodo porque no es nuevo (como los demás)
    colAutoDiv.appendChild(labelProducto);
    colAutoDiv.appendChild(selProducto);
    elementoDiv.appendChild(colAutoDiv);

    colAutoDiv = crearElemento("div", "", ["form-group", "col-12", "col-sm-4", "col-md-2", "col-lg-2", "d-flex", "flex-column", "justify-content-end"]);
    let labelCantidad = crearElemento("label", "", [], "Cantidad (en Kg)");
    let campoCantidad = crearElemento("input", "cantidad[]", ["form-control"], "", "number", true);
    colAutoDiv.appendChild(labelCantidad);
    colAutoDiv.appendChild(campoCantidad);
    elementoDiv.appendChild(colAutoDiv);

    colAutoDiv = crearElemento("div", "", ["form-group", "col-12", "col-sm-4", "col-md-3", "col-lg-2", "d-flex", "flex-column", "justify-content-end"]);
    let labelPrecio = crearElemento("label", "", [], "Precio (en Gs)");
    let campoPrecio = crearElemento("input", "precio[]", ["form-control"], "", "number", true);
    colAutoDiv.appendChild(labelPrecio);
    colAutoDiv.appendChild(campoPrecio);
    elementoDiv.appendChild(colAutoDiv);

    colAutoDiv = crearElemento("div", "", ["form-group", "col-12", "col-sm-4","col-md-3", "col-lg-1", "d-flex", "flex-column", "justify-content-end"]);
    let labelPorcentajeIVA = crearElemento("label", "", [], "% IVA");
    let campoPorcentajeIVA = crearElemento("input", "porcentaje_iva[]", ["form-control"], "", "number", true, true);
    colAutoDiv.appendChild(labelPorcentajeIVA);
    colAutoDiv.appendChild(campoPorcentajeIVA);
    elementoDiv.appendChild(colAutoDiv);

    selProducto.addEventListener("change", () => {
        campoPorcentajeIVA.value = selProducto.options[selProducto.selectedIndex].getAttribute('data-iva');
        calcularSubtotales(campoCantidad, 
            campoPrecio, 
            campoSubtotal,
            campoSubtotal_iva,
            campoPorcentajeIVA.value);
        document.getElementById('total').value = calcularTotal(document.getElementsByName('subtotal[]'));
    });

    colAutoDiv = crearElemento("div", "", ["form-group", "col-12", "col-sm-6", "col-md-6", "col-lg-2", "d-flex", "flex-column", "justify-content-end"]);
    let labelSubtotal = crearElemento("label", "", [], "Subtotal");
    let campoSubtotal = crearElemento("input", "subtotal[]", ["form-control"], "", "number", true, true);
    colAutoDiv.appendChild(labelSubtotal);
    colAutoDiv.appendChild(campoSubtotal);
    elementoDiv.appendChild(colAutoDiv);

    colAutoDiv = crearElemento("div", "", ["form-group", "col", "d-flex", "flex-column", "justify-content-end"]);
    let labelSubtotal_iva = crearElemento("label", "", [], "Subtotal IVA");
    let campoSubtotal_iva = crearElemento("input", "subtotal_iva[]", ["form-control"], "", "number", true, true);
    colAutoDiv.appendChild(labelSubtotal_iva);
    colAutoDiv.appendChild(campoSubtotal_iva);
    elementoDiv.appendChild(colAutoDiv);

    listenerCalculo = () => {
        calcularSubtotales(campoCantidad, 
            campoPrecio, 
            campoSubtotal,
            campoSubtotal_iva,
            campoPorcentajeIVA.value);
        document.getElementById('total').value = calcularTotal(document.getElementsByName('subtotal[]'));
    }
    
    campoCantidad.addEventListener('blur', listenerCalculo);
    campoPrecio.addEventListener('blur', listenerCalculo);

    if(!!crearBotonEliminar){ //!! convierte a boolean
        colAutoDiv = crearElemento("div", "", ["form-group","col-auto", "d-flex", "flex-column", "justify-content-end"]);
        let botonEliminar = crearElemento("button", "", ["btn", "btn-danger","ml-2"], "X");
        
        eliminarFila = () => {
            let elementoHR = elementoDiv.parentNode.querySelector('hr'); // Se asume que hay un hr arriba
            console.log(elementoHR)
            if(elementoHR) {
                elementoHR.parentNode.removeChild(elementoHR);
            }
            elementoDiv.remove();
            document.getElementById('total').value = calcularTotal(document.getElementsByName('subtotal[]'));
        }
        botonEliminar.addEventListener("click", eliminarFila);
        
        colAutoDiv.appendChild(botonEliminar);
    }

    elementoDiv.appendChild(colAutoDiv);

    divPadre.appendChild(elementoDiv);    
    return divPadre;
 
}

window.addEventListener('DOMContentLoaded', async function () {
    await fetchCargarProductos();
    divDetalles = document.getElementById('detalles');
    divDetalles.appendChild(crearFila(false));
    botonAgregarFila = document.getElementById('btnAgregarDetalle');
    botonAgregarFila.addEventListener("click", () => {
        divDetalles.appendChild(crearFila(true));
    });
    
    facturaForm = document.getElementById('facturaForm');
    facturaForm.addEventListener('submit', async function(event) {
        event.preventDefault();
       
        let factura = {};
        let formData = new FormData(event.target);
        for (let pair of formData.entries()) {
            if(pair[0].substring(pair[0].length - 2) !== '[]') { // solo agregar si la clave no termina en "[]", ya que lo que es de array se agrega más abajo en "detalles"
                if(pair[1]){ // solo si el value no es null, undefined o vacío
                    factura[pair[0]] = pair[1]; // 0 para key (clave), 1 para value (valor)
                }
            }
        }

        let lineasDetalles = facturaForm.querySelectorAll('.fila_detalle');
        let formDatas = [];
        lineasDetalles.forEach(div => {
            let fd = new FormData();
            let detalle = {};
            let campos = div.querySelectorAll('input, select');

            campos.forEach(campo => {
                // con el name "productos[] se hace una excepción porque se deben generar dos claves: uno para el idproducto y el otro para la descripción
                if(campo.name === 'productos[]'){
                    fd.append('idproducto', campo.value);
                    fd.append('descripcion_producto', campo.options[campo.selectedIndex].textContent);
                }
                else {
                        fd.append(campo.name.substring(0, campo.name.length - 2), campo.value);
                }
            });

            for (let pair of fd.entries()) {
                // la clave pasa a ser el name del campo, sin los "[]". Ej.: si el name es "cantidad[]", entonces la clave es "cantidad"
                detalle[pair[0]] = pair[1]; // 0 para key (clave), 1 para value (valor)
            }
            formDatas.push(detalle);
        });          
        
        factura.detalles = formDatas;
    
        // Convertir el objeto a JSON
        let facturaJSON = JSON.stringify(factura);
        // console.log(facturaJSON);
        
        divAlerta = crearElemento("div", "", ["alert"]);
        divAlerta.id = "respuesta_servidor";
        divAlerta.role = "alert"

        divFacturaCompra = document.getElementById("factura_compra");
        parrafoMensaje = crearElemento("p");

        let opcionesRequest = {
            method: 'POST',
            headers: {'Accept': 'application/json', 'Content-Type': 'application/json' },
            body: facturaJSON
        };
        await fetch('/compras/nuevo', opcionesRequest)
            .then(response => {
                //console.log(response)
                if(document.getElementById(divAlerta.id)) divFacturaCompra.removeChild(document.getElementById(divAlerta.id));
                if (response.ok === true){
                    divAlerta.classList.remove("alert-success", "alert-danger");
                    divAlerta.classList.add("alert-success");
                    if(divAlerta.firstElementChild){ // el primer elemento es el párrafo con el mensaje
                        divAlerta.removeChild(divAlerta.firstElementChild);
                    }
                    parrafoMensaje.textContent = 'La factura se ha insertado correctamente.';
                    divAlerta.appendChild(parrafoMensaje);
                    divFacturaCompra.prepend(divAlerta); // prepend para ponerlo como primer hijo del div
                }
                else {
                    divAlerta.classList.remove("alert-success", "alert-danger")
                    divAlerta.classList.add("alert-danger");
                    if(divAlerta.firstElementChild){ // el primer elemento es el párrafo con el mensaje
                        divAlerta.removeChild(divAlerta.firstElementChild);
                    }
                    parrafoMensaje.textContent = 'Ocurrió un error al intentar guardar la factura. \nMensaje del servidor: ';
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
                    divFacturaCompra.prepend(divAlerta); // prepend para ponerlo como primer hijo del div
                }
            })
            .then(data => console.log(data))
            .catch((error) => {
                console.error('Error:', error);
            });
        
       });
});