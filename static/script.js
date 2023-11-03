

// -------------------- Animacion y relleno de la subida de la imagen ----------------------------------------------

const imgPreview = document.getElementById('img-preview');
const imgUploader = document.getElementById('img-uploader');
const imageUploadbar = document.getElementById('img-upload-bar');

if (imgUploader) {
	imgUploader.addEventListener('change', async (event) => {
		const file = event.target.files[0];
		const formData = new FormData()
		formData.append('file', file)

		const res = await axios.post("/imagen", formData, {
			headers: {
				'content-type': 'multipart/form-data'
			},
			onUploadProgress(event) {
				let progress = Math.round((event.loaded * 100.0) / event.total);

				imageUploadbar.setAttribute('value', progress);
			}
		});

		imgPreview.src = URL.createObjectURL(imgUploader.files[0]);
		console.log(res);
	});
}
//----------------------------------------------------------------------------------------------------------------



//------------------ Seccion encargada de la funcion asincrona de la busqueda del ganado -------------------------

const buscadorganado = document.getElementById('buscarganadoinput');

/*Hace una copia temporal de los datos antes de realizar la busqueda, para no tener que volver a consultar si la 
busqueda no es necesaria o se cancela la introduccion del parametro a buscar*/
const datosiniciales = document.getElementsByClassName("ganado-list")[0].firstElementChild.outerHTML;

buscadorganado.addEventListener("input", function () {

	fetch("/buscarganado?q=" + buscadorganado.value)
		.then((response) => response.text())
		.then((html) => {
			let da = datosiniciales;
			if (buscadorganado.value != '') {
				document.getElementById("ganado-items").innerHTML = html;
			}
			else {
				document.getElementsByClassName("ganado-list")[0].innerHTML = datosiniciales;
			}
		})
		.catch((error) => {
			console.warn(error);
		});
});
//-----------------------------------------------------------------------------------------------------------------

function actualizarInfo(id) {
	swal.fire({
	  "title": "¿Estas seguro?",
	  "text": "Estas a punto de actualizar informacion que luego no podras recuperar!",
	  "icon": "warning",
	  "showCancelButton": true,
	  "cancelButtonText": "No, cancelar",
	  "confirmButtonText": "Si, eliminar",
	  "confirmButtonColor": "#dc3545",
	  "reverseButtons": true,
	})
	  .then(function (result) {
		if (result.isConfirmed) {
		  window.location.href="editar?id="+id
		  swal.fire({
			"title": "Exito",
			"text": "Hemos actualizado los datos",
			"icon": "success"
		  })
		} else {
		  swal.fire({
			"text": "Tus datos estan a salvo",
			"icon": "success",

		  });
		}
	  });
  }

