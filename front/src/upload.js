function enviarFormulario() {
    const file = document.getElementById('csvInput').files[0];
    const percentage = parseInt(document.getElementById('percentage').value);
  
    if (!file) {
      alert('Seleccioná un archivo CSV primero.');
      return;
    }
  
    // Armar array con los valores de los checkboxes
    const columns = [];
    for (let i = 1; i <= 5; i++) {
      const checked = document.getElementById(`chk${i}`).checked;
      columns.push(checked ? 1 : 0);
    }
  
    const formData = new FormData();
    formData.append('csvFile', file);
    formData.append('percentage', percentage);
    formData.append('columns', JSON.stringify(columns)); // mandamos como JSON string
  
    fetch('http://localhost:3000/upload-csv', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      alert('Formulario enviado correctamente');
      console.log(data);
    })
    .catch(err => {
      console.error('Error:', err);
      alert('Error al enviar el formulario');
    });
  }
  