const path = require('path');
const{ spawn } = require('child_process');
const express = require("express");
const cors = require("cors");
const fs = require('fs');
const csv = require('csv-parser');


const app = express();
const PORT = 3434;


app.use(cors()); // CORS
const pythonScriptPath = path.join(__dirname, "src/main.py");


// Servir archivos estáticos desde "front/assets"
app.use("/assets", express.static(path.join(__dirname, "../front/assets")));


// Servir archivos estáticos desde "front/src"
app.use(express.static(path.join(__dirname, "../front/src")));


// Enviar "index.html" cuando alguien accede a la raíz "/"
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "../front/src", "index.html"));
});
//app.use('/', uploadRoute);


app.get("/ejecutar", (req, res) => {
  const pythonProcess = spawn("python", [pythonScriptPath]);


  pythonProcess.stdout.on("data", (data) => {
      console.log(`Salida de Python: ${data}`);
  });


  pythonProcess.stderr.on("data", (data) => {
      console.error(`Error: ${data}`);
  });


  pythonProcess.on("close", (code) => {
      console.log(`Python terminó con código ${code}`);
      res.json({mensaje:"El script ha finalizado. Ejecutando la función en HTML."});
      console.log(`ads`);
  });
});


// Ruta para ejecutar el script Python
app.get("/generate", (req, res) => {
    parseCSV("./empleados_mas_incumplidores.csv")
      .then((jsonData) =>
        {
          console.log("jsonData: ", jsonData);
          res.json(jsonData)}) // Dvolver JSON
      .catch((error) => res.status(500).json({ error: "Error parsing CSV" }));
  });


function parseCSV(filePath) {
    return new Promise((resolve, reject) => {
      const results = [];
 
      fs.createReadStream(filePath)
        .pipe(csv())
        .on('data', (data) => results.push(data))
        .on('end', () => resolve(results))
        .on('error', (error) => reject(error));
    });
  }


app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
});