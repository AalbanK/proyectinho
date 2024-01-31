let jsonCiudades = null;
let selectDepto = null;

agregarOpcion = (elemento, valor, texto) => {
    let nuevaOpcion = document.createElement("option");
    nuevaOpcion.value = valor;
    nuevaOpcion.text = texto;
    elemento.add(nuevaOpcion);
}

fetchCargarDepartamentos = () => {
    selectDepto = document.querySelector("#id_departamento");
    selectDepto.length = 0; //para vaciar el select, por si acaso
    agregarOpcion(selectDepto, '', 'Seleccione un Departamento...');
        fetch('/departamentos/todos')
        .then((response) => response.json())
        .then((deptos) => {
            for (let depto of deptos) {
                agregarOpcion(selectDepto, depto.iddepartamento, depto.descripcion)
            }
        })
        .catch(error => {
            console.error(error)
            agregarOpcion(selectDepto, 0, 'Sin Datos');
        });
    };

    async function obtenerCiudades() {
        const response = await fetch('/ciudades/todos');
        if (!response.ok) {
            const message = `Ocurrió un error al intentar obtener las ciudades: ${response.status}`;
            throw new Error(message);
        }
        const ciudades = await response.json();
        return ciudades;
    }

    window.addEventListener('DOMContentLoaded', fetchCargarDepartamentos);
    window.addEventListener('DOMContentLoaded', async () => {
        await obtenerCiudades()
        .then(ciudades => {jsonCiudades = ciudades })
        .catch(error => {
            console.error(error);
            jsonCiudades = {};
        });
        const selectCiudad = document.querySelector("#id_ciudad");

        selectDepto.addEventListener('change', function (event) {

            let idDepto = event.target.value;

            if (idDepto && idDepto != "undefined") {
                selectCiudad.length = 0; // vaciar antes de volver a cargar!

                jsonCiudades.map(function (ciu) {
                    if (ciu.iddepartamento == idDepto) {
                        agregarOpcion(selectCiudad, ciu.idciudad, `${ciu.descripcion}`);
                    }
                });
            }
    });
});