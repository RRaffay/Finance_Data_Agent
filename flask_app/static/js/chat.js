function askQuestion() {
    var question = document.getElementById("question").value;
    var questionSpinner = document.querySelector("#chat-box .loading-spinner");
    questionSpinner.style.display = "block";

    fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: question }),
    })
        .then((response) => response.json())
        .then((data) => {
            var responsesDiv = document.getElementById("responses");

            // Display user's question
            var questionElement = document.createElement("div");
            questionElement.className = "alert alert-primary chat-message";
            questionElement.innerText = question;
            responsesDiv.appendChild(questionElement);

            // Display AI response
            var responseElement = document.createElement("div");
            responseElement.className = "alert alert-secondary chat-message mathjax";

            // Use marked.parse or marked depending on the version
            var responseHTML;
            if (typeof marked.parse !== 'undefined') {
                responseHTML = marked.parse(data.response);
            } else {
                responseHTML = marked(data.response);
            }

            responseElement.innerHTML = responseHTML;
            responsesDiv.appendChild(responseElement);

            // Hide the spinner
            questionSpinner.style.display = "none";

            // Clear the input field
            document.getElementById("question").value = "";

            // Scroll to the bottom of the chat container
            scrollToBottom();

        })
        .catch((error) => {
            console.error("Error:", error);
            questionSpinner.style.display = "none";
        });
}

function scrollToBottom() {
    var responsesDiv = document.getElementById("responses");
    responsesDiv.scrollTop = responsesDiv.scrollHeight;
}

function restartAnalysis() {
    location.reload();
}
