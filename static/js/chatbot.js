document.addEventListener('DOMContentLoaded', function () {
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector("#send-btn");
    const chatbox = document.querySelector(".chatbox");

    let step = 0;  // Keeps track of which question to ask
    let userInputs = {};  // Stores user inputs for season, soil type, region, and area

    const questions = [
        "What season are you planting in? (e.g., jan-mar, apr-jun, jul-sep, oct-dec)",
        "What is the soil type? (e.g., red-soil, black-soil, laterite-soil, alluvial-soil, saline-soils)",
        "Which region are you in? (e.g., Vellore, Coimbatore,Tuticorin etc.)",
        "How many acres are you planting(1-3)?"
    ];

    const askNextQuestion = () => {
        if (step < questions.length) {
            createChatLi(questions[step], 'incoming');
            step++;
        } else {
            fetchCropsRecommendation();
        }
    };

    const createChatLi = (message, className) => {
        const chatLi = document.createElement('li');
        chatLi.classList.add('chat', className);
        chatLi.innerHTML = `<p>${message}</p>`;
        chatbox.appendChild(chatLi);
        chatbox.scrollTop = chatbox.scrollHeight;  // Scroll to the bottom
    };

    const fetchCropsRecommendation = () => {
        fetch('/get_crop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userInputs),
        })
        .then(response => response.json())
        .then(data => {
            const crop = data.crop;
            createChatLi(`Based on your inputs, a suitable crop would be: ${crop}`, 'incoming');
        })
        .catch(error => {
            console.error('Error:', error);
            createChatLi("Sorry, something went wrong.", 'incoming');
        });
    };

    sendChatBtn.addEventListener('click', () => {
        const message = chatInput.value.trim().toLowerCase();
        if (message) {
            createChatLi(message, 'outgoing');
            chatInput.value = '';  // Clear the input field

            if (message === "exit") {
                createChatLi("Thank you! The conversation has been ended.", 'incoming');
                step = questions.length;  // Stop asking questions
                return;
            }

            if (step === 1) userInputs.season = message;
            else if (step === 2) userInputs.soilType = message;
            else if (step === 3) userInputs.region = message;
            else if (step === 4) userInputs.acres = message;

            askNextQuestion();
        }
    });

    // Start the conversation by asking the first question
    askNextQuestion();
});
