const inpFile = document.querySelector("#input-image");
inpFile.value = "";
const prevImage = document.querySelector("#preview-image");
const prevText = document.querySelector("#preview-text");

inpFile.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        prevText.style.display = "none";
        prevImage.style.display = "block";
        reader.addEventListener("load", function () {
            prevImage.setAttribute("src", this.result);
        });
        reader.readAsDataURL(file);
    }
});