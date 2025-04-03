document.addEventListener("DOMContentLoaded", function () {
    const ejecutarBtn = document.querySelector(".btn-primary");
    
    ejecutarBtn.addEventListener("click", function () {
        ejecutarBtn.style.display = "none";
        
        // Loader
        const loader = document.createElement("div");
        loader.className = "spinner-border text-primary mt-3";
        loader.setAttribute("role", "status");
        loader.innerHTML = '<span class="visually-hidden">Loading...</span>';
        
        // Sumar loader
        ejecutarBtn.parentNode.appendChild(loader);

    });
});

function fetchCSVData() {
    fetch("http://localhost:3434/generate")
      .then((response) => response.json())
      .then((data) => {
        populateTable(data)})
      .catch((error) => console.error("Error fetching data:", error));
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
        <td>${row.fecha || "N/A"}</td>
        <td>${row.dia_semana || "N/A"}</td>
        <td>${row.asistencia || "N/A"}</td>
        <td>${row.hora_entrada || "N/A"}</td>
        <td>${row.hora_salida || "N/A"}</td>
        <td>${row.tipo_ausencia || "N/A"}</td>
        <td>${row.min_entrada || "N/A"}</td>
        <td>${row.min_salida || "N/A"}</td>
        <td>${row.anomalia || "N/A"}</td>
      `;
  
      tableBody.appendChild(tr);
    });
  }
  