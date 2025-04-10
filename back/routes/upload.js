const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const router = express.Router();
const { spawn } = require('child_process');


// Configuración de multer (memoria, sin guardar archivos en disco)
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
      cb(null, 'uploads/'); // Carpeta donde se guarda el archivo
    },
    filename: function (req, file, cb) {
      const uniqueName = 'asistencia_empleados.csv';
      cb(null, uniqueName);
    }
  });
const upload = multer({ storage });

router.post('/upload-csv', upload.single('csvFile'), (req, res) => {
    console.log('Archivo guardado en:', req.file?.path);

  try {
    const file = req.file;
    const percentage = parseInt(req.body.percentage);
    const columns = JSON.parse(req.body.columns);

    console.log('Archivo recibido:', file.originalname);
    console.log('Porcentaje:', percentage);
    console.log('Columnas:', columns);

    if (!file || !percentage || !Array.isArray(columns)) {
      return res.status(400).json({ message: 'Faltan datos en la solicitud' });
    }

     // Primero se ejecuta esta función interna
    generateTxtFile(percentage, columns);

     // Ahora ejecutamos el script de Python
     const pythonScriptPath = path.join(__dirname, "../src/main.py");
     const pythonProcess = spawn('python', [pythonScriptPath]);
 
     pythonProcess.stdout.on('data', (data) => {
       console.log(`Salida de Python: ${data}`);
     });
 
     pythonProcess.stderr.on('data', (data) => {
       console.error(`Error del script Python: ${data}`);
     });
 
     pythonProcess.on('close', (code) => {
       console.log(`Python terminó con código ${code}`);
 
       // Respondemos cuando todo haya terminado
       res.status(200).json({
         message: 'Archivo procesado y script ejecutado correctamente',
         fileName: file.originalname,
         percentage,
         columns
       });
    });

  } catch (error) {
    console.error('Error al procesar la solicitud:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
});

function generateTxtFile(percentage, columns){
     // Crear archivo datos.txt en ../
     const outputPath = path.join(__dirname, '../uploads/datos.txt');
     const content = `${percentage}\n${columns.join('\n')}`;
     fs.writeFileSync(outputPath, content);
     console.log('Archivo de salida generado en:', outputPath);
}

module.exports = router;
