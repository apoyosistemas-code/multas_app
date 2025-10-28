document.addEventListener("DOMContentLoaded", () => {
    const tabla = document.getElementById("tablaDatos");
    const resumen = document.getElementById("resumen");
    const btnRecargar = document.getElementById("btnRecargar");
    const btnBuscar = document.getElementById("btnBuscar");
    const buscarCAJ = document.getElementById("buscarCAJ");
    const btnAgregar = document.getElementById("btnAgregar");
    const nuevoNombre = document.getElementById("nuevoNombre");
    const nuevoCAJ = document.getElementById("nuevoCAJ");
    const btnBorrarAsamblea = document.getElementById("btnBorrarAsamblea");
    const selectAsamblea = document.getElementById("selectAsamblea");

    async function cargarAsambleasSelect() {
        const res = await fetch("/api/asambleas");
        const data = await res.json();
        selectAsamblea.innerHTML = "";
        data.forEach(a => {
            selectAsamblea.innerHTML += `<option value="${a.id}">${a.nombre} (${a.fecha.split('T')[0]})</option>`;
        });
    }

    async function cargarDatos(filtro = "") {
        try {
            let url = filtro ? `/buscar_caj/${filtro}` : "/api/datos";
            const res = await fetch(url);
            const data = await res.json();
            renderTabla(data);
            await cargarAsambleasSelect();
        } catch (error) {
            console.error("Error cargando datos:", error);
        }
    }

    function renderTabla(data) {
        const { asambleas, colegiaturas, asistencias } = data;
        tabla.innerHTML = "";

        // Encabezado
        let header = `<tr>
            <th class="border p-2 bg-gray-200">CAJ</th>`;
        asambleas.forEach(a => {
            header += `<th class="border p-2 bg-gray-200">${a.nombre}<br>${a.fecha.split('T')[0]}</th>`;
        });
        header += `
            <th class="border p-2 bg-gray-200">TOTAL MULTA (S/)</th>
            <th class="border p-2 bg-gray-200">ESTADO</th>
            <th class="border p-2 bg-gray-200">OBSERVACIONES</th>
        </tr>`;
        tabla.innerHTML = header;

        // Filas
        colegiaturas.forEach(c => {
            let fila = `<tr class="hover:bg-gray-100">
                <td class="border p-2 text-center">${c.id}</td>`;
            let total = 0;

            asambleas.forEach(a => {
                const asis = asistencias.find(s => s.colegiatura_id === c.id && s.asamblea_id === a.id);
                const presente = asis ? asis.presente === 1 : false;
                if (!presente) total += parseFloat(a.costo);

                fila += `
                    <td class="border p-2 text-center">
                        <input type="checkbox" ${presente ? "checked" : ""} 
                            data-caj="${c.id}" data-asamblea="${a.id}" class="chkAsistencia">
                    </td>`;
            });

            fila += `
                <td class="border p-2 text-center font-semibold text-red-600">${total.toFixed(2)}</td>
                <td class="border p-2 text-center">${c.estado || "No pagado"}</td>
                <td class="border p-2">
                    <input type="text" value="${c.observaciones || ""}" 
                        data-caj="${c.id}" class="inputObservacion w-full p-1 border rounded">
                </td>
            </tr>`;
            tabla.insertAdjacentHTML("beforeend", fila);
        });

        resumen.innerHTML = `
            <p>Total de asambleas: ${asambleas.length}</p>
            <p>Total de colegiados: ${colegiaturas.length}</p>
        `;
    }

    // Actualizar asistencia
    tabla.addEventListener("change", async e => {
        if (e.target.classList.contains("chkAsistencia")) {
            const caj = e.target.getAttribute("data-caj");
            const asamblea = e.target.getAttribute("data-asamblea");
            const presente = e.target.checked;
            await fetch(`/actualizar_asistencia/${caj}/${asamblea}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ presente })
            });
            cargarDatos(buscarCAJ.value);
        }

        if (e.target.classList.contains("inputObservacion")) {
            const caj = e.target.getAttribute("data-caj");
            const observacion = e.target.value;
            await fetch(`/actualizar_observacion/${caj}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ observacion })
            });
        }
    });

    // Buscar por número CAJ
    btnBuscar.addEventListener("click", () => {
        const valor = buscarCAJ.value.trim();
        if (valor) cargarDatos(valor);
    });

    // Recargar todo
    btnRecargar.addEventListener("click", () => cargarDatos());

    // Agregar nuevo colegiado
    btnAgregar.addEventListener("click", async () => {
        const nombre = nuevoNombre.value.trim();
        const caj = nuevoCAJ.value.trim();
        if (!nombre || !caj) {
            alert("Debes completar nombre y número CAJ");
            return;
        }

        await fetch("/agregar_colegiado", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre, caj })
        });

        nuevoNombre.value = "";
        nuevoCAJ.value = "";
        cargarDatos(); // 🔁 recargar tabla automáticamente
    });

    // Borrar asamblea
    btnBorrarAsamblea.addEventListener("click", async () => {
        const id = selectAsamblea.value;
        if (!id) return alert("Selecciona una asamblea para borrar.");

        if (!confirm("¿Seguro que deseas eliminar esta asamblea?")) return;

        await fetch(`/borrar_asamblea/${id}`, { method: "DELETE" });
        alert("Asamblea eliminada correctamente.");
        cargarDatos();
    });

    cargarDatos();
});
