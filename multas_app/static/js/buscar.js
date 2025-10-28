document.addEventListener("DOMContentLoaded", () => {
  const btnBuscar = document.getElementById("buscar");
  const inputMatricula = document.getElementById("matricula");
  const resultadoDiv = document.getElementById("resultado");
  const detalleBody = document.getElementById("detalle");
  const mensaje = document.getElementById("mensaje");
  const totalSpan = document.getElementById("total");
  const unitariaSpan = document.getElementById("unitaria");
  const cajSpan = document.getElementById("cajVal");
  const nombreSpan = document.getElementById("nombreVal");
  const estadoSpan = document.getElementById("estadoVal");
  const obsSpan = document.getElementById("obsVal");

  async function buscar() {
    const matricula = inputMatricula.value.trim();
    if (!matricula) {
      mensaje.textContent = "Por favor, ingrese un número CAJ.";
      return;
    }

    mensaje.textContent = "Buscando...";
    resultadoDiv.classList.add("hidden");
    detalleBody.innerHTML = "";

    try {
      const res = await fetch("/buscar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ matricula })
      });

      const data = await res.json();

      if (!data.existe) {
        mensaje.textContent = data.mensaje || "No se encontró el CAJ.";
        unitariaSpan.textContent = `S/ ${data.unidad_multa ? data.unidad_multa.toFixed(2) : '0.00'}`;
        totalSpan.textContent = `S/ ${data.multa_total ? data.multa_total.toFixed(2) : '0.00'}`;
        cajSpan.textContent = "";
        nombreSpan.textContent = "";
        estadoSpan.textContent = "";
        obsSpan.textContent = "";
        resultadoDiv.classList.remove("hidden");
        return;
      }

      // Mostrar resultados
      mensaje.textContent = "";
      resultadoDiv.classList.remove("hidden");
      detalleBody.innerHTML = "";

      cajSpan.textContent = data.caj;
      nombreSpan.textContent = data.matricula;
      estadoSpan.textContent = data.estado || "";
      obsSpan.textContent = data.observaciones || "";

      data.detalles.forEach((d, i) => {
        const asistio = d.presente ? "✅" : "❌";
        const multa = d.presente ? "-" : `S/ ${d.costo.toFixed(2)}`;
        detalleBody.innerHTML += `
          <tr class="border-b">
            <td class="p-2 text-center">${i + 1}</td>
            <td class="p-2 text-center">${d.asamblea_nombre} — ${new Date(d.fecha).toLocaleDateString()}</td>
            <td class="p-2 text-center">${asistio}</td>
            <td class="p-2 text-center">${multa}</td>
          </tr>
        `;
      });

      unitariaSpan.textContent = `S/ ${data.unidad_multa.toFixed(2)}`;
      totalSpan.textContent = `S/ ${data.multa_total.toFixed(2)}`;
    } catch (err) {
      mensaje.textContent = "Error al conectar con el servidor.";
      console.error(err);
    }
  }

  btnBuscar.addEventListener("click", buscar);
  inputMatricula.addEventListener("keypress", e => {
    if (e.key === "Enter") buscar();
  });
});
