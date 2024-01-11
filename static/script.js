

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

buscadorganado.addEventListener("keypress", function(event){
	if (event.key === "Enter"){
		event.preventDefault();
	}
});

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

//Eliminar ganado

function eliminarBovino(id, chapa, nombre) {
	swal({
		title: "¿Estas seguro?",
		text: "Estas a punto de eliminar los datos del bovino: " + nombre + " con chapa " + chapa,
		icon: "warning",
		buttons: ["Cancelar", true],
		dangerMode: true,
	})
	.then((willDelete) => {
		if (willDelete) {
		window.location.href="/infonovillo/" + id + "/borrar"
		} else {
		  swal("Tus datos están a salvo");
		}
	  });
}
//Matar ganado

function matarBovino(id) {
	swal({
		title: "¿Estas seguro?",
		text: "¿Estas seguro que deseas marcar este bovino como fallecido?",
		icon: "warning",
		buttons: ["Cancelar", true],
		dangerMode: true,
	})
	.then((willDelete) => {
		if (willDelete) {
			window.location.href="/infonovillo/" + id + "/muerto"
		}
	  });
}

// Eliminar compra

function eliminarCompra(id) {
	swal({
		title: "¿Estas seguro?",
		text: "Estas a punto de eliminar los datos de esta compra",
		icon: "warning",
		buttons: ["Cancelar", true],
		dangerMode: true,
	})
	.then((willDelete) => {
		if (willDelete) {
		window.location.href="/eliminarcompra//" + id
		} else {
		  swal("Tus datos están a salvo");
		}
	  });
}