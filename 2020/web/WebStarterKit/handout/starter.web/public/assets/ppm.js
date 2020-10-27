async function loadPPM(href, init) {
	const text = await pfetch(href, init);

	let lines = text.split(/\s/g).filter((v) => v.length > 0);
	if (lines.length < 4) {
		throw Error("Invalid PPM");
	}
	let format = lines[0];
	let width = lines[1];
	let height = lines[2];
	let depth = lines[3];
	if (lines.length < 4 + (width * height)) {
		throw Error("Invalid PPM");
	}
	// Sharing is caring
	// https://stackoverflow.com/a/22826906/214063
	let buffer = new Uint8ClampedArray(width * height * 4);
	for (var y = 0; y < height; y++) {
		for (var x = 0; x < width; x++) {
			var bpos = (y * width + x) * 4;
			var ipos = (y * width + x) * 3 + 4;
			buffer[bpos  ] = lines[ipos  ] / depth * 255;
			buffer[bpos+1] = lines[ipos+1] / depth * 255;
			buffer[bpos+2] = lines[ipos+2] / depth * 255;
			buffer[bpos+3] = 255;
		}
	}
	// create off-screen canvas element
	var canvas = document.createElement('canvas');
	var ctx = canvas.getContext('2d');

	canvas.width = width;
	canvas.height = height;

	// create imageData object
	var idata = ctx.createImageData(width, height);

	// set our buffer as source
	idata.data.set(buffer);

	// update canvas with new data
	ctx.putImageData(idata, 0, 0);

	// set the img.src to the canvas data url
	return canvas.toDataURL();
}
