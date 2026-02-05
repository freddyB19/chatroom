
const URL_CHATROOM = `${window.location.host}/chat`
const CHATROOM_ID = "#chatroom";
const LIST_MESSAGES_ID = "#allMessages";
const INPUT_MESSAGE_ID = "#input-message";
const USERNAME_ID = "#username";
const CONTENT_CHAT = '.chat-body'
const TYPING_INDICATOR_ID = "#typingIndicator"
const SEND_BUTTON_MESSAGE = "#button-send-message"


const socket = io(URL_CHATROOM);

const chatBody = document.querySelector(CONTENT_CHAT);
const consola = document.querySelector(LIST_MESSAGES_ID);
const input_mensaje = document.querySelector(INPUT_MESSAGE_ID);
const send_button = document.querySelector(SEND_BUTTON_MESSAGE);
const typingIndicator = document.querySelector(TYPING_INDICATOR_ID);

const room = document.querySelector(CHATROOM_ID).dataset.room;
const username = document.querySelector(CHATROOM_ID).dataset.username;


function scrollToBottom() {
    chatBody.scrollTop = chatBody.scrollHeight;
}

const tipo_mensaje = {emisor: 'right', receptor: 'left'};
const tipo_mensaje_group = {receptor: 'received'};


const Message = ({message, type}) => {
	const MAX_LEN_MESSAGE = 50;

	const content_message = document.createElement("div");
	const length_message = message.length;
	content_message.className = `
		message-bubble message-${type} ${length_message >= MAX_LEN_MESSAGE ? 'message-long': ''}
	`;
	content_message.textContent = message;
	return content_message;
}

const MessageReceived = ({message_received, username}) => {
	const content_message = document.createElement("div");
	const content_avatar = document.createElement("div");

	const message = Message({type: tipo_mensaje.receptor, message: message_received})
		
	content_message.className = `message-group ${tipo_mensaje_group.receptor}`;
	content_avatar.className = 'avatar-container';
	content_avatar.setAttribute("uk-tooltip", username);
	content_avatar.innerHTML = `
		<svg class="user-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
        </svg>
	`
	content_message.append(...[content_avatar, message]);

	return content_message;
}

const InsertMessage = ({message, content}) => {
	content.insertBefore(message, typingIndicator);
}

const InsertMessageHistory = ({list_messages, content}) => {
	list_messages.push(typingIndicator);
	content.replaceChildren()
	content.append(...list_messages)
}

const CreateGroupMessage = ({data}) => {
	return (username == data.username) 
		? Message({message: data.mensaje, type: tipo_mensaje.emisor})
		: MessageReceived({message_received: data.mensaje, username: data.username})
}


socket.on('connect', () => {
	socket.emit('join', {room: room, username: username})
})


socket.on('conectando', ({historial}) => {
	if(historial.length){
		const historial_mensajes = historial.map((data) => CreateGroupMessage({data}));
		InsertMessageHistory({
			list_messages: historial_mensajes,
			content: consola
		})
	}
})

socket.on('notificacion', ({pin}) => {
	const notification_message = document.querySelector('#notification-message');
	notification_message.textContent = pin.mensaje;
	setTimeout((dom) => {
			dom.textContent = ""
		}, 
		3000, 
		notification_message
	);
	
	const list_users = pin.usuarios;

	const content_users = document.querySelector("#notification-users");
	const content_id_users = document.querySelector("#id-users");

	const list = document.createElement("ul");
	list.innerHTML = `${
			list_users.map(user => `<li>${user}</li>`).join('')
	}`;

	content_id_users.setAttribute("uk-tooltip", list.innerHTML);

	const list_of_three_users = list_users.slice(0, 3);
	const users = list_of_three_users.map((user, index) => {
		const span = document.createElement("span");
		span.classList.add("uk-badge");
		span.textContent = user[0].toLocaleUpperCase();
		return span;
	});
	
	const TOTAL_MAX_USERS = 3;

	if (list_users.length > TOTAL_MAX_USERS){
		const span = document.createElement("span");
		span.classList.add("uk-badge");
		span.textContent = "3+";
		users.push(span);
	}
	
	content_users.replaceChildren()
	content_users.append(...users);
})

socket.on('typing', ({pin}) => {
	if(username != pin.username){
	    if (!typingIndicator.classList.contains('is-active')) {
            typingIndicator.classList.add('is-active');
            scrollToBottom();
        }
	}
})

socket.on('stopped_typing', ({pin}) => {
	if(username != pin.username){
		if (typingIndicator.classList.contains('is-active'))
			typingIndicator.classList.remove('is-active');
	}

})

socket.on('mensaje', (msg) => {
	typingIndicator.classList.remove('is-active');
	InsertMessage({message: CreateGroupMessage({data: msg}), content: consola});
	scrollToBottom();
})

input_mensaje.addEventListener('input', (event) => {
	let input_value = event.target.value;

	let message = input_value.trim() !== "";
	
	send_button.disabled = !message;

	if(input_value.length > 0)
		socket.emit('typing', {room: room, username: username, typing: true});
})

input_mensaje.addEventListener('blur', (event) => {
	setTimeout((data) => {
		socket.emit('stopped_typing', data)
	}, 800, {room: room, username: username, typing: false})
})

document.querySelector("#form-chat").addEventListener("submit", (event) => {
	event.preventDefault();
	
	socket.emit('chat_mensaje', {mensaje: input_mensaje.value, room: room, username: username})
	input_mensaje.value = ""
	send_button.disabled = true;

	input_mensaje.blur()
})


document.querySelector(".salir").addEventListener('click', (event) => {
	socket.emit('leave', {room: room, username: username})
	window.location.replace(window.location.origin);
})
