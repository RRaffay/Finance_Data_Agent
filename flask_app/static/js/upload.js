document.getElementById("upload-form").addEventListener("submit", function (event) {
    event.preventDefault();

    if (typeof marked.parse === 'undefined' && typeof marked === 'undefined') {
        console.error("Marked.js is not loaded correctly");
        return;
    } else {
        console.log("Marked.js is loaded correctly");
    }

    var formData = new FormData();
    formData.append("file", document.getElementById("file").files[0]);
    formData.append("objective", document.getElementById("objective").value);

    var uploadSpinner = document.querySelector("#upload-form .loading-spinner");
    uploadSpinner.style.display = "block";

    fetch("/upload", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            // Use marked.parse or marked depending on the version
            var analysisHTML;
            if (typeof marked.parse !== 'undefined') {
                analysisHTML = marked.parse(data.analysis);
            } else {
                analysisHTML = marked(data.analysis);
            }

            document.getElementById("analysis").innerHTML = analysisHTML;
            uploadSpinner.style.display = "none";

            document.getElementById("analysis-section").style.display = "block";
            document.getElementById("chat-box").style.display = "flex";
            document.getElementById("upload-form").style.display = "none";

            window.treeData = data.tree;
        })
        .catch((error) => {
            console.error("Error:", error);
            uploadSpinner.style.display = "none";
        });
});

document.getElementById("example-button").addEventListener("click", function () {
    var uploadSpinner = document.querySelector("#upload-form .loading-spinner");
    uploadSpinner.style.display = "block";

    fetch("/example")
        .then((response) => response.json())
        .then((data) => {
            var analysisHTML;
            if (typeof marked.parse !== 'undefined') {
                analysisHTML = marked.parse(data.analysis);
            } else {
                analysisHTML = marked(data.analysis);
            }

            document.getElementById("analysis").innerHTML = analysisHTML;
            uploadSpinner.style.display = "none";

            document.getElementById("analysis-section").style.display = "block";
            document.getElementById("chat-box").style.display = "flex";
            document.getElementById("upload-form").style.display = "none";

            window.treeData = data.tree;
        })
        .catch((error) => {
            console.error("Error:", error);
            uploadSpinner.style.display = "none";
        });
});

function toggleAnalysis() {
    var analysisSection = $("#analysis");
    var button = $("#toggle-analysis-btn");
    analysisSection.collapse("toggle");
    if (button.attr("aria-expanded") === "true") {
        button.text("Show Analysis");
        button.attr("aria-expanded", "false");
    } else {
        button.text("Hide Analysis");
        button.attr("aria-expanded", "true");
    }
}
