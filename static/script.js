	const imgPreview = document.getElementById('img-preview')
	const imgUploader = document.getElementById('img-uploader')
	const imageUploadbar = document.getElementById('img-upload-bar');
	const url = document.getElementById('url')

	const CLOUDINARY_URL = 'https://api.cloudinary.com/v1_1/estefany/image/upload';
	const cloudinary_code = 'rsuy9xjm';

	console.log(imgUploader)

	imgUploader.addEventListener('change', async (event) => {
		const file = event.target.files[0];
		withcredentials:false;
		const formData = new FormData()
		formData.append('file', file)
		formData.append('upload_preset', cloudinary_code)

		const res = await axios.post(CLOUDINARY_URL, formData, {
			headers: {
				'content-type': 'multipart/form-data'
			},

			onUploadProgress(event) {
				let progress = Math.round((event.loaded * 100.0) / event.total);
		
				imageUploadbar.setAttribute('value', progress);
			}

		});

		imgPreview.src = res.data.secure_url;
		url.value = imgPreview.src

	});





