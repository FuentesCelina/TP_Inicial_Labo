const express = require("express");

const cors = require("cors");
const fs = require('fs');
const csv = require('csv-parser');

const app = express();
const PORT = 3434;

app.use(cors()); // CORS

// Ruta para ejecutar el script Python
app.get("/generate", (req, res) => {
    parseCSV("./src/anomalos_detectados.csv")
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
