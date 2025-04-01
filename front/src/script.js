document.addEventListener("DOMContentLoaded", function () {
    const ejecutarBtn = document.querySelector(".btn-primary");
    
    ejecutarBtn.addEventListener("click", function () {
        ejecutarBtn.style.display = "none";
        
        // Loader
        const loader = document.createElement("div");
        loader.className = "spinner-border text-primary mt-3";
        loader.setAttribute("role", "status");
        loader.innerHTML = '<span class="visually-hidden">Loading...</span>';
        
        // Insert loader into the DOM
        ejecutarBtn.parentNode.appendChild(loader);
        
        // After timeout, replace loader with "Reporte generado!"
        setTimeout(() => {
            loader.remove();
            const message = document.createElement("p");
            message.className = "mt-1 text-success-emphasis fw-bold";
            message.textContent = "📄 Reporte generado!";
            ejecutarBtn.parentNode.appendChild(message);
        }, 3000);
    });
});

function runPython() {
    
}