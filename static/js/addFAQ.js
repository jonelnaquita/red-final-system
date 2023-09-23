
// Custom JavaScript function to set active button
function setActiveButton(buttonIndex) {
    const buttons = document.getElementsByClassName('btn');
    for (let i = 0; i < buttons.length; i++) {
        if (i + 1 === buttonIndex) {
            buttons[i].classList.add('active');
        } else {
            buttons[i].classList.remove('active');
        }
    }
}


ClassicEditor
    .create( document.querySelector( '#editor' ), {
        toolbar: {
            items: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'alignment', 'undo', 'redo']
        }
    })
    .catch( error => {
        console.error( error );
    });

ClassicEditor
    .create( document.querySelector( '#editor2' ), {
        toolbar: {
            items: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'alignment', 'undo', 'redo']
        }
    })
    .catch( error => {
        console.error( error );
    });


function showDiv(source) {
    const dataSources = document.querySelectorAll('.data-source');
    dataSources.forEach(sourceDiv => {
        sourceDiv.classList.remove('active');
    });

    const selectedDiv = document.getElementById(`${source}-data-source`);
    selectedDiv.classList.add('active');
}

function addMoreFaqInputs() {
    const faqInputs = document.querySelector('.faq-inputs');
    const faqData = faqInputs.cloneNode(true);
    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.classList.add('btn', 'btn-danger', 'btn-sm', 'mb-2');
    deleteButton.textContent = 'Delete';
    deleteButton.onclick = function() {
        faqData.remove();
    };
    faqData.appendChild(deleteButton);
    faqInputs.parentElement.insertBefore(faqData, document.querySelector('.add-more-btn'));
}

let fileInput = document.getElementById("file-input");
let fileList = document.getElementById("files-list");
let numOfFiles = document.getElementById("num-of-files");

fileInput.addEventListener("change", () => {
fileList.innerHTML = "";
numOfFiles.textContent = `${fileInput.files.length} Files Selected`;

for (i of fileInput.files) {
    let reader = new FileReader();
    let listItem = document.createElement("li");
    let fileName = i.name;
    let fileSize = (i.size / 1024).toFixed(1);
    listItem.innerHTML = `<p>${fileName}</p><p>${fileSize}KB</p>`;
    if (fileSize >= 1024) {
    fileSize = (fileSize / 1024).toFixed(1);
    listItem.innerHTML = `<p>${fileName}</p><p>${fileSize}MB</p>`;
    }
    fileList.appendChild(listItem);
}
});

document.getElementById('file-input').addEventListener('change', handleFileSelect);

function handleFileSelect(event) {
const files = event.target.files;
const fileCount = files.length;
const fileList = document.getElementById('files-list');
fileList.innerHTML = '';

if (fileCount > 5) {
    toastr.error('You can only upload 5 PDF files at a time!');
    return;
}

for (let i = 0; i < fileCount; i++) {
    const file = files[i];
    const fileType = file.type;
    if (fileType !== 'application/pdf') {
    toastr.error('Upload PDF files only!');
    return;
    }

    const listItem = document.createElement('li');
    listItem.textContent = file.name;
    fileList.appendChild(listItem);
}

document.getElementById('num-of-files').textContent = fileCount === 0 ? 'No Files Chosen' : `${fileCount} File(s) Chosen`;
}