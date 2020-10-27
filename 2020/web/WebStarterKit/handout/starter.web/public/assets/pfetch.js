async function pfetch(input, init) {
	const response = await fetch(input, init);

	progress = (init || {}).progress || ((p) => {});

	const reader = response.body.getReader();
	let bytesReceived = 0;
	let value = new Uint8Array();
	while (true) {
		const result = await reader.read();
		if (result.done) {
			break;
		}
		bytesReceived += result.value.length;
		let new_value = new Uint8Array(value.length + result.value.length);
		new_value.set(value, 0);
		new_value.set(result.value, value.length);
		value = new_value;
		progress(bytesReceived);
	}
	const text = new TextDecoder("utf-8").decode(value);

	return text;
}
