document.addEventListener("DOMContentLoaded", () => {

    const chatInput = document.getElementById("chatInput");
    const sendButton = document.getElementById("sendMessage");
    const chatMessages = document.getElementById("chatMessages");



    /* =========================================
       ENVIAR MENSAJE
    ========================================= */

    function sendMessage() {

        const text = chatInput.value.trim();

        if (!text) {
            return;
        }


        const message = document.createElement("div");

        message.className = "message message-user";


        message.innerHTML = `

            <div class="message-body">

                <span class="message-author">
                    Tú
                </span>

                <div class="message-bubble">
                    ${escapeHtml(text)}
                </div>

            </div>

        `;


        chatMessages.appendChild(message);


        chatInput.value = "";


        chatInput.style.height = "auto";


        scrollToBottom();


        /*
         * Más adelante aquí conectaremos
         * con el backend de Python.
         */

        setTimeout(() => {

            addGoraMessage(
                "Te escucho 🐾 Cuéntame un poquito más."
            );

        }, 700);

    }



    /* =========================================
       RESPUESTA GORA
    ========================================= */

    function addGoraMessage(text) {

        const message = document.createElement("div");

        message.className = "message message-gora";


        message.innerHTML = `

            <div class="message-avatar">
                🐱
            </div>

            <div class="message-body">

                <span class="message-author">
                    Gora
                </span>

                <div class="message-bubble">
                    ${escapeHtml(text)}
                </div>

            </div>

        `;


        chatMessages.appendChild(message);


        scrollToBottom();

    }



    /* =========================================
       ENTER
    ========================================= */

    chatInput.addEventListener("keydown", (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    });



    /* =========================================
       BOTÓN ENVIAR
    ========================================= */

    sendButton.addEventListener(
        "click",
        sendMessage
    );



    /* =========================================
       AUTO RESIZE TEXTAREA
    ========================================= */

    chatInput.addEventListener("input", () => {

        chatInput.style.height = "auto";

        chatInput.style.height =
            Math.min(
                chatInput.scrollHeight,
                110
            ) + "px";

    });



    /* =========================================
       SCROLL
    ========================================= */

    function scrollToBottom() {

        chatMessages.scrollTop =
            chatMessages.scrollHeight;

    }



    /* =========================================
       EMOCIONES
    ========================================= */

    const emotionButtons =
        document.querySelectorAll(
            ".emotion-buttons button"
        );


    emotionButtons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const emotion =
                    button.dataset.emotion;


                console.log(
                    "Emoción seleccionada:",
                    emotion
                );

            }
        );

    });



    /* =========================================
       CÁMARA
    ========================================= */

    const cameraButton =
        document.getElementById(
            "cameraButton"
        );


    if (cameraButton) {

        cameraButton.addEventListener(
            "click",
            () => {

                console.log(
                    "Abrir detección facial"
                );

            }
        );

    }



    /* =========================================
       SEGURIDAD HTML
    ========================================= */

    function escapeHtml(value) {

        const div =
            document.createElement("div");

        div.textContent = value;

        return div.innerHTML;

    }

});