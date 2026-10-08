const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const uploadButton = document.getElementById("upload-button");
const uploadError = document.getElementById("upload-error");

const documentsContainer = document.getElementById("documents-container");
const refreshDocumentsButton = document.getElementById(
    "refresh-documents-button"
);

const askForm = document.getElementById("ask-form");
const questionInput = document.getElementById("question-input");
const askButton = document.getElementById("ask-button");
const askError = document.getElementById("ask-error");

const answerSection = document.getElementById("answer-section");
const answerContainer = document.getElementById("answer-container");

const sourcesSection = document.getElementById("sources-section");
const sourcesContainer = document.getElementById("sources-container");


let pollingTimers = new Map();
let currentEventSource = null;


function showError(element, message) {
    element.textContent = message;
    element.classList.remove("hidden");
}


function hideError(element) {
    element.textContent = "";
    element.classList.add("hidden");
}


function escapeHtml(value) {
    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


function formatDate(dateString) {
    return new Date(dateString).toLocaleString("uk-UA");
}


function getStatusLabel(status) {
    const labels = {
        processing: "Обробляється...",
        ready: "Готовий",
        failed: "Помилка",
    };

    return labels[status] || status;
}


function getStatusClass(status) {
    return `status-${status}`;
}


async function loadDocuments() {
    try {
        const response = await fetch("/api/documents");

        if (!response.ok) {
            throw new Error(
                "Не вдалося отримати список документів."
            );
        }

        const documents = await response.json();

        renderDocuments(documents);
        updatePolling(documents);
    } catch (error) {
        documentsContainer.innerHTML = `
            <p class="error">
                ${escapeHtml(error.message)}
            </p>
        `;
    }
}


function renderDocuments(documents) {
    if (documents.length === 0) {
        documentsContainer.innerHTML = `
            <p class="empty-state">
                Документів ще немає.
            </p>
        `;

        return;
    }

    const list = document.createElement("div");
    list.className = "document-list";

    for (const doc of documents) {
        const item = document.createElement("div");
        item.className = "document-item";

        item.innerHTML = `
            <div class="document-info">
                <div class="document-name">
                    ${escapeHtml(doc.filename)}
                </div>

                <div class="document-meta">
                    Chunks: ${doc.chunks_count}
                    <br>
                    Додано: ${formatDate(doc.created_at)}
                </div>

                <div class="status ${getStatusClass(doc.status)}">
                    ${getStatusLabel(doc.status)}
                    ${doc.status === "failed" && doc.error
                        ? `<br><small>Причина: ${doc.error}</small>`
                        : ""}
                </div>
            </div>

            <button
                type="button"
                class="delete-button"
            >
                Видалити
            </button>
        `;

        const deleteButton = item.querySelector(".delete-button");

        deleteButton.addEventListener("click", () => {
            deleteDocument(doc.id);
        });

        list.appendChild(item);
    }

    documentsContainer.innerHTML = "";
    documentsContainer.appendChild(list);
}


function updatePolling(documents) {
    const processingIds = new Set(
        documents
            .filter((doc) => doc.status === "processing")
            .map((doc) => doc.id)
    );

    for (const doc of documents) {
        if (doc.status !== "processing") {
            stopPolling(doc.id);
            continue;
        }

        if (pollingTimers.has(doc.id)) {
            continue;
        }

        const timer = setInterval(() => {
            checkDocumentStatus(doc.id);
        }, 2000);

        pollingTimers.set(doc.id, timer);
    }

    for (const documentId of pollingTimers.keys()) {
        if (!processingIds.has(documentId)) {
            stopPolling(documentId);
        }
    }
}


function stopPolling(documentId) {
    const timer = pollingTimers.get(documentId);

    if (timer) {
        clearInterval(timer);
        pollingTimers.delete(documentId);
    }
}


async function checkDocumentStatus(documentId) {
    try {
        const response = await fetch(
            `/api/documents/${documentId}`
        );

        if (!response.ok) {
            stopPolling(documentId);
            return;
        }

        const doc = await response.json();

        if (document.status !== "processing") {
            stopPolling(documentId);
            await loadDocuments();
        }
    } catch (error) {
        stopPolling(documentId);
    }
}


async function uploadDocument(event) {
    event.preventDefault();

    hideError(uploadError);

    const file = fileInput.files[0];

    if (!file) {
        showError(
            uploadError,
            "Оберіть файл."
        );

        return;
    }

    const formData = new FormData();

    formData.append("file", file);

    uploadButton.disabled = true;
    uploadButton.textContent = "Завантаження...";

    try {
        const response = await fetch(
            "/api/documents",
            {
                method: "POST",
                body: formData,
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Не вдалося завантажити документ."
            );
        }

        fileInput.value = "";

        await loadDocuments();
    } catch (error) {
        showError(
            uploadError,
            error.message
        );
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "Завантажити";
    }
}


async function deleteDocument(documentId) {
    const confirmed = window.confirm(
        "Ви впевнені, що хочете видалити цей документ?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(
            `/api/documents/${documentId}`,
            {
                method: "DELETE",
            }
        );

        if (!response.ok) {
            let message = "Не вдалося видалити документ.";

            try {
                const data = await response.json();

                if (data.detail) {
                    message = data.detail;
                }
            } catch (error) {
                // Response does not contain JSON.
            }

            throw new Error(message);
        }

        stopPolling(documentId);

        await loadDocuments();
    } catch (error) {
        window.alert(error.message);
    }
}


function renderSources(sources) {
    sourcesContainer.innerHTML = "";

    if (!sources || sources.length === 0) {
        sourcesSection.classList.add("hidden");
        return;
    }

    for (const source of sources) {
        const item = document.createElement("div");

        item.className = "source-item";

        const page = source.page ?? "—";
        const score = Number(source.score).toFixed(3);

        item.innerHTML = `
            <div class="source-meta">
                File: ${escapeHtml(source.filename)}
                <br>
                Document ID: ${escapeHtml(source.document_id)}
                <br>
                Page: ${page}
                <br>
                Score: ${score}
            </div>

            <div class="source-snippet">
                ${escapeHtml(source.snippet)}
            </div>
        `;

        sourcesContainer.appendChild(item);
    }

    sourcesSection.classList.remove("hidden");
}


function startStreaming(question) {
    if (currentEventSource) {
        currentEventSource.close();
        currentEventSource = null;
    }

    const url =
        `/api/ask/stream?question=${encodeURIComponent(question)}`;

    const eventSource = new EventSource(url);

    currentEventSource = eventSource;

    answerSection.classList.remove("hidden");
    sourcesSection.classList.add("hidden");

    answerContainer.textContent = "";

    eventSource.addEventListener("sources", (event) => {
        try {
            const sources = JSON.parse(event.data);

            renderSources(sources);
        } catch (error) {
            showError(
                askError,
                "Не вдалося прочитати джерела."
            );
        }
    });

    eventSource.addEventListener("token", (event) => {
        try {
            const data = JSON.parse(event.data);

            answerContainer.textContent += data.token;
        } catch (error) {
            showError(
                askError,
                "Не вдалося прочитати відповідь."
            );
        }
    });

    eventSource.addEventListener("done", (event) => {
        try {
            const data = JSON.parse(event.data);

            if (data.answer) {
                answerContainer.textContent = data.answer;
            }
        } catch (error) {
            showError(
                askError,
                "Не вдалося завершити відповідь."
            );
        } finally {
            eventSource.close();

            if (currentEventSource === eventSource) {
                currentEventSource = null;
            }

            askButton.disabled = false;
            askButton.textContent = "Запитати";
        }
    });

    eventSource.onerror = () => {
        eventSource.close();

        if (currentEventSource === eventSource) {
            currentEventSource = null;
        }

        askButton.disabled = false;
        askButton.textContent = "Запитати";

        showError(
            askError,
            "Сталася помилка під час отримання відповіді."
        );
    };
}


function askQuestion(event) {
    event.preventDefault();

    hideError(askError);

    const question = questionInput.value.trim();

    if (question.length < 3) {
        showError(
            askError,
            "Питання повинно містити щонайменше 3 символи."
        );

        return;
    }

    if (currentEventSource) {
        currentEventSource.close();
        currentEventSource = null;
    }

    askButton.disabled = true;
    askButton.textContent = "Думаю...";

    answerSection.classList.remove("hidden");
    sourcesSection.classList.add("hidden");

    answerContainer.textContent = "";

    startStreaming(question);
}


uploadForm.addEventListener(
    "submit",
    uploadDocument
);

refreshDocumentsButton.addEventListener(
    "click",
    loadDocuments
);

askForm.addEventListener(
    "submit",
    askQuestion
);


loadDocuments();
