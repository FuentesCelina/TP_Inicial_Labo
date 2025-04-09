const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const router = express.Router();

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

    generateTxtFile(percentage, columns);

    res.status(200).json({
      message: 'Archivo y datos recibidos correctamente',
      fileName: file.originalname,
      percentage,
      columns
    });

  } catch (error) {
    console.error('Error al procesar la solicitud:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
});

function generateTxtFile(percentage, columns){
     // Crear archivo datos.txt en ../
     const outputPath = path.join(__dirname, '../../datos.txt');
     const content = `${percentage}\n${columns.join('\n')}`;
     fs.writeFileSync(outputPath, content);
     console.log('Archivo de salida generado en:', outputPath);
}

module.exports = router;
