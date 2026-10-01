// ==================================================
// EduGenie Frontend JavaScript
// ==================================================


// --------------------------------------------------
// Feature selection
// --------------------------------------------------

function selectFeature(feature) {

    const sections = [
        "chatSection",
        "summarySection",
        "quizSection",
        "notesSection"
    ];

    sections.forEach(function(section) {

        document
            .getElementById(section)
            .classList.add("hidden");

    });


    const tabs = [
        "chatTab",
        "summaryTab",
        "quizTab",
        "notesTab"
    ];

    tabs.forEach(function(tab) {

        document
            .getElementById(tab)
            .classList.remove("active");

    });


    document
        .getElementById(feature + "Section")
        .classList.remove("hidden");


    document
        .getElementById(feature + "Tab")
        .classList.add("active");


    hideResult();
}


// --------------------------------------------------
// Loading
// --------------------------------------------------

function showLoading() {

    document
        .getElementById("loading")
        .classList.remove("hidden");

}


function hideLoading() {

    document
        .getElementById("loading")
        .classList.add("hidden");

}


// --------------------------------------------------
// Result
// --------------------------------------------------

function showResult(text) {

    document
        .getElementById("resultSection")
        .classList.remove("hidden");

    document
        .getElementById("resultText")
        .textContent = text;

}


function hideResult() {

    document
        .getElementById("resultSection")
        .classList.add("hidden");

}


// --------------------------------------------------
// Generic API request
// --------------------------------------------------

async function sendRequest(url, data) {

    showLoading();

    try {

        const response = await fetch(url, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(data)

        });


        const result = await response.json();


        if (!response.ok || !result.success) {

            throw new Error(
                result.message ||
                "Something went wrong."
            );

        }


        showResult(result.answer);


    } catch (error) {

        showResult(
            "Error: " + error.message
        );

    } finally {

        hideLoading();

    }

}


// --------------------------------------------------
// Ask Question
// --------------------------------------------------

function askQuestion() {

    const question =
        document
            .getElementById("questionInput")
            .value
            .trim();


    if (!question) {

        alert("Please enter a question.");

        return;
    }


    sendRequest(
        "/chat",
        {
            question: question
        }
    );

}


// --------------------------------------------------
// Generate Summary
// --------------------------------------------------

function generateSummary() {

    const text =
        document
            .getElementById("summaryInput")
            .value
            .trim();


    if (!text) {

        alert("Please enter study material.");

        return;
    }


    sendRequest(
        "/summary",
        {
            text: text
        }
    );

}


// --------------------------------------------------
// Generate Quiz
// --------------------------------------------------

function generateQuiz() {

    const topic =
        document
            .getElementById("quizInput")
            .value
            .trim();


    if (!topic) {

        alert("Please enter a topic.");

        return;
    }


    sendRequest(
        "/quiz",
        {
            topic: topic
        }
    );

}


// --------------------------------------------------
// Generate Notes
// --------------------------------------------------

function generateNotes() {

    const topic =
        document
            .getElementById("notesInput")
            .value
            .trim();


    if (!topic) {

        alert("Please enter a topic.");

        return;
    }


    sendRequest(
        "/notes",
        {
            topic: topic
        }
    );

}


// --------------------------------------------------
// Copy result
// --------------------------------------------------

function copyResult() {

    const text =
        document
            .getElementById("resultText")
            .innerText;


    navigator.clipboard.writeText(text)
        .then(function() {

            alert("Response copied!");

        })
        .catch(function() {

            alert("Unable to copy response.");

        });

}


// --------------------------------------------------
// Load History
// --------------------------------------------------

async function loadHistory() {

    const historySection =
        document
            .getElementById("historySection");


    historySection
        .classList
        .remove("hidden");


    const historyList =
        document
            .getElementById("historyList");


    historyList.innerHTML =
        "<p>Loading history...</p>";


    try {

        const response =
            await fetch("/history");


        const result =
            await response.json();


        if (!result.success) {

            throw new Error(
                "Unable to load history."
            );

        }


        if (result.history.length === 0) {

            historyList.innerHTML =
                "<p>No learning history yet.</p>";

            return;
        }


        historyList.innerHTML = "";


        result.history.forEach(function(item) {

            const div =
                document.createElement("div");


            div.className =
                "history-item";


            div.innerHTML = `

                <div class="history-question">
                    ${escapeHTML(item.question)}
                </div>

                <div class="history-answer">
                    ${escapeHTML(item.answer)}
                </div>

                <span class="history-feature">
                    ${escapeHTML(item.feature)}
                </span>

            `;


            historyList.appendChild(div);

        });


    } catch (error) {

        historyList.innerHTML =
            "<p>Unable to load history.</p>";

    }

}


// --------------------------------------------------
// Delete History
// --------------------------------------------------

async function deleteHistory() {

    const confirmDelete =
        confirm(
            "Are you sure you want to delete all history?"
        );


    if (!confirmDelete) {

        return;

    }


    try {

        const response =
            await fetch(
                "/history/delete",
                {
                    method: "DELETE"
                }
            );


        const result =
            await response.json();


        if (result.success) {

            loadHistory();

        } else {

            alert("Unable to delete history.");

        }


    } catch (error) {

        alert("Something went wrong.");

    }

}


// --------------------------------------------------
// Basic HTML escaping
// --------------------------------------------------

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}