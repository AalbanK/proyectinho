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


fetchCargarProductos = async () => {
    selectProducto = crearElemento("select", "productos[]", ["form-control"], "", "", true, true);
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

            // Convertir el objeto a JSON
        let facturaJSON = JSON.stringify(factura);
        console.log(facturaJSON);
        
        divAlerta = crearElemento("div", "", ["alert"]);
        divAlerta.id = "respuesta_servidor";
        divAlerta.role = "alert"

        divFacturaVenta = document.getElementById("factura_venta");
        parrafoMensaje = crearElemento("p");

        let opcionesRequest = {
            method: 'POST',
            headers: {'Accept': 'application/json', 'Content-Type': 'application/json' },
            body: facturaJSON
        };
        await fetch('/ventas/nuevo', opcionesRequest)
            .then(response => {
                //console.log(response)
                if(document.getElementById(divAlerta.id)) divFacturaVenta.removeChild(document.getElementById(divAlerta.id));
                if (response.ok === true){
                    divAlerta.classList.remove("alert-success", "alert-danger");
                    divAlerta.classList.add("alert-success");
                    if(divAlerta.firstElementChild){ // el primer elemento es el párrafo con el mensaje
                        divAlerta.removeChild(divAlerta.firstElementChild);
                    }
                    parrafoMensaje.textContent = 'La factura se ha insertado correctamente.';
                    divAlerta.appendChild(parrafoMensaje);
                    divFacturaVenta.prepend(divAlerta); // prepend para ponerlo como primer hijo del div
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
                    divFacturaVenta.prepend(divAlerta); // prepend para ponerlo como primer hijo del div
                }
            })
            .then(data => console.log(data))
            .catch((error) => {
                console.error('Error:', error);
            });
       };

);