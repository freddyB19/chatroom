
const socket = io(`${window.location.host}/chat`)
const room = document.querySelector("#chatroom").dataset.room
const consola = document.querySelector("#allMessages")
const input_mensaje = document.querySelector("#input-message")
const username = document.querySelector("#username").dataset.username //.textContent
const tipo_mensaje = {
	emisor: 'repaly',
	receptor: 'sender',
}

socket.on('connect', () => {
	socket.emit('join', {room: room, username: username})
})

socket.on('conectando', ({historial}) => {

	if(historial.length){

		const historial_mensajes = historial.map((msg) => {
			const mensaje = document.createElement("li")
			mensaje.className = (username == msg.username) 
				? tipo_mensaje.emisor 
				: tipo_mensaje.receptor

			mensaje.innerHTML = `
				<p>${msg.mensaje}</p>
				<span class="time">${msg.tiempo}</span>
			`
			return mensaje
		})

		consola.replaceChildren()
		consola.append(...historial_mensajes)
	} 

})

socket.on('notificacion', ({pin}) => {

	document.querySelector(
		"#notificacion-mensaje"
	).textContent = pin.mensaje

	document.querySelector(
		'#notificacion-usuarios-totales'
	).textContent = pin.usuarios
	
	setTimeout((dom) => {
		dom.textContent = ""
	}, 
	3000, 
	document.querySelector("#notificacion-mensaje"))

})

socket.on('typing', ({pin}) => {
	
	if(username != pin.username){
		if(!document.querySelector(`#user-${pin.username}`)){
			const userTyping = document.createElement('p')
			userTyping.textContent = pin.mensaje
			userTyping.setAttribute('id', `user-${pin.username}`)
			document.querySelector("#typing").replaceChildren()
			document.querySelector("#typing").appendChild(userTyping)
		}

	}

	
})

socket.on('stopped_typing', ({pin}) => {
	if(document.querySelector(`#user-${pin.username}`)){
		document.querySelector("#typing").removeChild(
			document.querySelector(`#user-${pin.username}`)
		)
	}
	
})

socket.on('mensaje', (msg) => {

	const mensaje = document.createElement('li')
	mensaje.className = (username == msg.username) 
		? tipo_mensaje.emisor 
		: tipo_mensaje.receptor
	mensaje.innerHTML = `
		<p>${msg.mensaje}</p>
		<span class="time">${msg.tiempo}</span>
	`
	consola.appendChild(mensaje)
})


input_mensaje.addEventListener('input', (event) => {
	if(event.target.value.length > 0)
		socket.emit('typing', {room: room, username: username, typing: true})
})

input_mensaje.addEventListener('blur', (event) => {
	setTimeout((data) => {
		socket.emit('stopped_typing', data)
	}, 800, {room: room, username: username, typing: false})

})


document.querySelector("#form-chat").addEventListener("submit", (event) => {
	event.preventDefault()

	socket.emit('chat_mensaje', {mensaje: input_mensaje.value, room: room, username: username})
	input_mensaje.value = ""


	input_mensaje.blur()
})


document.querySelector(".salir").addEventListener('click', (event) => {
	socket.emit('leave', {room: room, username: username})

	window.location.replace(window.location.origin);
})