document.addEventListener("DOMContentLoaded", function () {
    const ejecutarBtn = document.querySelector(".btn-primary");
    
    ejecutarBtn.addEventListener("click", function () {
        ejecutarBtn.style.display = "none";
        
        // Loader
        const loader = document.createElement("div");
        loader.className = "spinner-border text-primary mt-3";
        loader.setAttribute("role", "status");
        loader.innerHTML = '<span class="visually-hidden">Loading...</span>';
        
        // Agregar loader al DOM
        ejecutarBtn.parentNode.appendChild(loader);
        
        // Ocultar loader por timeout
        setTimeout(() => {
            loader.remove();
            ejecutarBtn.style.display = "inline-block";
        }, 3000);
    });
});
