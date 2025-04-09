document.addEventListener("DOMContentLoaded", function () {
  const ejecutarBtn = document.getElementById("runButton");

  ejecutarBtn.addEventListener("click", function (event) {
    event.preventDefault();
    ejecutarMain();
      ejecutarBtn.style.display = "none";

      // Loader
      const loader = document.createElement("div");
      loader.className = "spinner-border text-primary mt-3";
      loader.setAttribute("role", "status");
      loader.innerHTML = '<span class="visually-hidden">Loading...</span>';

      // Agregar el loader al DOM
      ejecutarBtn.parentNode.appendChild(loader);

      setTimeout(() => {
          // Eliminar el loader después de 3 segundos
          loader.remove();
      }, 3000);

      var boton = document.getElementById("button_csv");
      boton.style.display = "inline";
  });
});

function ejecutarMain() {
  fetch("http://localhost:3434/ejecutar")
            .then(response => response.json()) // Convertir la respuesta en JSON
            .then(data => {
                console.log(data);
                document.getElementById("resultado").innerText = data.mensaje; // Mostrar mensaje en HTML
                alert("El script ha terminado. Ahora ejecutamos esta función.");
                fetchCSVData();
            })
            .catch(error => console.error("Error:", error));
}

function fetchData(action) {
    fetch("http://localhost:3434/generate")
      .then((response) => response.json())
      .then(action)
      .catch((error) => console.error("Error fetching data:", error));
  }

  function fetchCSVData() {
    fetchData(populateTable);
  }
  
  function descargar_csv() {
    fetchData(convertir_csv);
  }
  
  function populateTable(data) {
    const table = document.getElementById("tableData");
    const tableBody = document.getElementById("table-body");
    
    tableBody.innerHTML = "";
  
    if (data.length > 0) {
      table.style.display = "table"; // Mostrar la tabla solo si hay datos
    } else {
      table.style.display = "none"; // Ocultar la tabla si no hay datos
    }
  
    data.forEach((row) => {
      console.log("Row Data:", row); // debug
  
      const tr = document.createElement("tr");
  
      tr.innerHTML = `
        <td>${row.empleado_id || "N/A"}</td>
        <td>${row.faltas_acumuladas || "N/A"}</td>
        <td>${row.faltas_seguidas || "N/A"}</td>
        <td>${row.falta_lunes_viernes || "N/A"}</td>
        <td>${row.llegada_tarde || "N/A"}</td>
        <td>${row.retiro_temprano || "N/A"}</td>
        <td>${row.anomaly_score || "N/A"}</td>
      `;
  
      tableBody.appendChild(tr);
    });
  }

function convertir_csv(data) {
  const csvData = jsonToCSV(data);

  const blob = new Blob([csvData], { type: 'text/csv' });

  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'datos.csv';

  link.click();
}

function jsonToCSV(jsonData) {
  if (!jsonData || jsonData.length === 0) return '';

  // Extraer las cabeceras de las columnas (las claves del primer objeto del JSON)
  const headers = Object.keys(jsonData[0]);

  // Crear una fila de encabezado (cabeceras)
  const csvRows = [];
  csvRows.push(headers.join(','));  // Unir las cabeceras con comas

  // Crear filas de datos
  jsonData.forEach(row => {
    const values = headers.map(header => {
      let value = row[header] || ''; // Si no hay valor, poner una cadena vacía
      value = value.toString().replace(/"/g, '""'); // Escapar comillas dobles (para que Excel las lea correctamente)
      return `"${value}"`; // Asegurarse de envolver los valores con comillas dobles
    });
    csvRows.push(values.join(',')); // Unir los valores con comas y agregar la fila
  });

  return csvRows.join('\n'); // Unir todas las filas con saltos de línea
}