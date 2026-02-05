
const URL_LIVING_ROOM = `${window.location.host}/sala-espera`;
const CHANNEL_LIVINGROOM_ID = "#channel-livingroom";
const USERNAME_ID = "#username";
const NAME_CHANNEL_ID = "#nameChatroom";
const FORM_BUTTON_ID = "#form-button";


const socket = io(URL_LIVING_ROOM);
const ROOM = document.querySelector(CHANNEL_LIVINGROOM_ID).dataset.room;

const usernameInput = document.querySelector(USERNAME_ID);
const chatroomInput = document.querySelector(NAME_CHANNEL_ID);
const formButton = document.querySelector(FORM_BUTTON_ID);

const validForm = () => {
  const username = usernameInput.value.trim() !== "";
  const chatroom = chatroomInput.value.trim() !== "";

  formButton.disabled = !(username && chatroom);
}

const addListChannels = ({channels, mount_channels}) => {
	if(!Array.isArray(channels))
		throw new Error(`No es un array de elementos: ${channels}`);

	mount_channels.replaceChildren();
	mount_channels.append(...channels);
}

const addChannel = ({channel, mount_channels}) => {
	mount_channels.replaceChildren()
	mount_channels.append(channel);
}


const showCreatedChannels = ({channels, livingroom = null}) => {
	if (!livingroom)
			throw new Error(`Error: el valor de 'livingroom' enviado es: ${livingroom}`);

	const created_channels = channels.map((channel) => {
		const elemento = document.createElement('li');
		elemento.innerHTML =`
			# ${channel.room} <span class="badge">${channel.total_usuarios}</span>
		`;

		return elemento;
	});

	created_channels.unshift(livingroom);

	return created_channels;
}

socket.on('connect', () => {
	socket.emit('join', {room: ROOM})
})

socket.on('disconnect', () => {})

socket.on("sala_espera", ({rooms, total}) => {
	const channel_list = document.querySelector('#channel-list');
	const members = document.querySelectorAll(".total-members");
	const channel_livingroom = document.querySelector("#channel-livingroom")?.parentElement;
	
	members.forEach(mount => mount.textContent = total);

	if (rooms.length){
		const created_channels = showCreatedChannels({channels: rooms, livingroom: channel_livingroom});

		addListChannels({
			channels: created_channels, 
			mount_channels: channel_list
		})
	
	} else {
		addChannel({
			channel: channel_livingroom, 
			mount_channels: channel_list
		})
	}
});

usernameInput.addEventListener('input', validForm);
chatroomInput.addEventListener('input', validForm);


document.addEventListener('DOMContentLoaded', () => {
    // Seleccionamos los elementos
    const menuBtn = document.querySelector('#menuBtn');
    const closeBtn = document.querySelector('#closeBtn');
    const sidebar = document.querySelector('#sidebar');
    const overlay = document.querySelector('#overlay');

    // Función para abrir/cerrar
    const toggleMenu = () => {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    };

    // Verificamos que los elementos existan antes de asignar el evento
    if (menuBtn && sidebar && overlay) {
        menuBtn.addEventListener('click', toggleMenu);
        
        if (closeBtn) closeBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', toggleMenu);
      
    } else {
        console.error("Error: No se encontraron los IDs necesarios en el HTML.");
    }
});

function closeAlert() {
    document.getElementById('alertOverlay').style.display = 'none';
}