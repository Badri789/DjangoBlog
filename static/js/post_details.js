// ფუნქცია უზრუნველყოფს დინამიური reply form-ების დაგენერირებასა
// და მათზე ვალიდაციების ფუნქციების მიბმას.
function onCommentReply(parentId, rootId, action, csrftoken) {

    const replySection = document.querySelector(".write-reply-" + rootId);
    if (replySection.innerHTML.trim().length !== 0) {
        replySection.innerHTML = "";
    }

    replySection.innerHTML += `
        <form id="reply-form-${parentId}" class="w-100 d-inline-flex flex-column" method="post" action="${action}">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
            <label class="form-label" for="reply-text-${parentId}">Add Reply</label>
            <textarea id="reply-text-${parentId}" class="form-control" name="${parentId}-body" cols="40" 
                rows="3" required="" placeholder="Enter reply..."></textarea>
            <input type="hidden" name="parent_comment" value="${parentId}">
            <input type="hidden" name="root_comment" value="${rootId}">
            <div class="w-75 mt-3 d-inline-flex justify-content-start">
                <span id="reply-counter-${parentId}" class="btn me-3 mt-1" style="cursor: default;">0</span>
                <button id="reply-btn-${parentId}" class="btn btn-outline-primary w-25 mt-1" type="submit" 
                name="save_reply">Add Reply</button>
            </div>
        </form>
    `;

    const textArea = document.querySelector(`#reply-text-${parentId}`);
    textArea.focus();

    document.querySelector(`#reply-form-${parentId}`).addEventListener('submit',
        (e) => onCommentSubmit(e, `#reply-text-${parentId}`,
            `.write-reply-${rootId}`, "submit-reply"));

    validateCommentText(`#reply-text-${parentId}`,
        `#reply-counter-${parentId}`, `#reply-btn-${parentId}`);

}

// ფუნქცია უზრუნველყოფს დინამიური edit form-ების დაგენერირებასა
// და მათზე ვალიდაციების ფუნქციების მიბმას.
function onCommentEdit(editBtn, commentId, action, csrftoken) {

    const contentBodyWrapper = document.querySelector(`#body-wrapper-${commentId}`);
    const oldContent = contentBodyWrapper.innerHTML;
    const oldText = contentBodyWrapper.firstElementChild.innerHTML;


    const closeButton = document.createElement("button");
    closeButton.classList.add("btn", "btn-outline-danger")
    closeButton.innerHTML = `<i class="bi bi-x"></i>`;

    editBtn.parentNode.replaceChild(closeButton, editBtn);

    closeButton.addEventListener("click", () => {
        contentBodyWrapper.innerHTML = oldContent;
        closeButton.parentNode.replaceChild(editBtn, closeButton);
    });

    contentBodyWrapper.innerHTML = "";

    contentBodyWrapper.innerHTML += `
          <form id="edit-form-${commentId}" class="w-100 d-inline-flex flex-column" method="post" action="${action}">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
            <label class="form-label" for="edit-text-${commentId}">Edit Comment</label>
            <textarea id="edit-text-${commentId}" class="form-control" name="${commentId}-body" cols="40"
                rows="3" required="" placeholder="Edit comment...">${oldText}</textarea>
            <div class="w-75 mt-3 d-inline-flex justify-content-start">
                <span id="edit-counter-${commentId}" class="btn me-3 mt-1" style="cursor: default;">0</span>
                <button id="edit-btn-${commentId}" class="btn btn-outline-primary w-25 mt-1" type="submit">
                    Save
                </button>
            </div>
        </form>
    `;

    document.querySelector(`#edit-form-${commentId}`).addEventListener("submit",
        (e) => onCommentSubmit(e, `#edit-text-${commentId}`,
            `#body-wrapper-${commentId}`, "edit-comment"));

    validateCommentText(`#edit-text-${commentId}`,
        `#edit-counter-${commentId}`, `#edit-btn-${commentId}`);

}


function validateCommentText(commentTextId, commentTextCounterId, commentSubmitBtnId) {

    const commentText = document.querySelector(commentTextId);
    const commentTextCounter = document.querySelector(commentTextCounterId);
    const commentSubmitBtn = document.querySelector(commentSubmitBtnId);

    const MIN_CHARS = 15;
    const initialLength = commentText.value.length;
    commentTextCounter.textContent = initialLength;
    commentSubmitBtn.disabled = initialLength < MIN_CHARS;
    commentTextCounter.classList.add(initialLength < MIN_CHARS ? "btn-danger" : "btn-success");

    commentText.addEventListener("input", () => {
        let count = commentText.value.length;
        commentTextCounter.textContent = count;
        if (count >= MIN_CHARS) {
            commentTextCounter.classList.remove("btn-danger");
            commentTextCounter.classList.add("btn-success");
            commentSubmitBtn.disabled = false;
        } else {
            commentTextCounter.classList.remove("btn-success");
            commentTextCounter.classList.add("btn-danger");
            commentSubmitBtn.disabled = true;
        }
    });
}

function onCommentSubmit(event, validationField, scrollTo, actionType) {
    const commentText = document.querySelector(validationField);
    if (commentText.value.length < 15) {
        event.preventDefault();
        swal("Form Validation Error!", "", "error");
    } else {
        localStorage.setItem("scroll-to", scrollTo);
        localStorage.setItem("action-type", actionType);
    }
}

document.querySelector(`#form-root`).addEventListener('submit',
    (e) => onCommentSubmit(e, "#id_root-body",
        ".root-comments-div", "submit-root"));


window.onload = function focusOnAdded() {
    const scrollTo = localStorage.getItem("scroll-to");
    const actionType = localStorage.getItem("action-type");
    if (scrollTo != null && actionType != null) {
        switch (actionType) {
            case "submit-root":
                document.querySelector(scrollTo).lastElementChild
                    .scrollIntoView({behavior: 'instant', block: 'center'});
                break;
            case "submit-reply":
                document.querySelector(scrollTo).previousElementSibling.lastElementChild
                    .scrollIntoView({behavior: 'instant', block: 'center'});
                break;
            case "edit-comment":
                document.querySelector(scrollTo).parentElement.scrollIntoView({behavior: 'instant', block: 'center'});
                break;
            case "rate-post":
            case "notification":
                document.querySelector(scrollTo).scrollIntoView({behavior: 'instant', block: 'center'});
        }
        localStorage.removeItem("scroll-to");
        localStorage.removeItem("action-type");
    }
}


validateCommentText("#id_root-body", "#root-text-counter",
    "#root-btn-submit");

document.querySelector("#rating-form").addEventListener("submit", () => {
    localStorage.setItem("scroll-to", "#rating-form");
    localStorage.setItem("action-type", "rate-post");
});
