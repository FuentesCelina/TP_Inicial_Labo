# Isolation Forest Script

Este proyecto incluye un script en Python, un servidor en Node.js y un frontend en HTML con Bootstrap.

## Requisitos previos

Asegúrate de tener instalado lo siguiente:
- [ Node.js 18 LTS ] (https://nodejs.org/) y npm(incluído en Node).
- [ Python 3 ]  (https://www.python.org/)

## Instalación y ejecución

### 1. Clonar el repositorio
```sh
git clone https://github.com/FuentesCelina/TP_Inicial_Labo.git
```

### 2. Levantar servidor backend (Node.js)
```sh
cd repo/back
npm install
node server.js
```

### 3. Frontend (HTML + Bootstrap)
Abrir el archivo `front/src/index.html` en tu navegador.

## Estructura del proyecto
```
/TP_Inicial_Labo
│── front/
│   ├── assets/
│   ├── src/
│       ├── index.html
│       ├── script.css
│       ├── ...(otros archivos de estilos)
│── back/
│   ├── server.js
│   ├── package.json
│   ├── src/
│       ├── main.py (script .py principal)
│       ├── ... .csv/.py (otros scripts/csv generados)
│── README.md
│── .gitignore
```

## Notas
- Asegúrate de que el puertos utilizado no esté en uso. Por default el puerto es el 3434. En cuyo caso se puede configurar desde una línea del archivo 'server.js':
> const PORT = 3434;


---
¡Listo! 🚀
