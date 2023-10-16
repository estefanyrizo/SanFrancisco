	const imgPreview = document.getElementById('img-preview')
	const imgUploader = document.getElementById('img-uploader')
	const imageUploadbar = document.getElementById('img-upload-bar');

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