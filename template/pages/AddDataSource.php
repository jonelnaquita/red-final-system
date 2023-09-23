<?php
    include 'components/header.php';
    include 'components/preloader.php'
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>

    <style>
        /* Custom CSS to set active color for the buttons */
        .btn.active {
            background-color: #CE1E2D;
            color: #ffffff;
        }

        .btn-danger{
            background-color: #CE1E2D;
            color: #ffffff;
        }

        .ck-editor__editable {
            min-height: 200px; /* Set your desired height here */
        }

        .add-more-btn{
          width: 100%;
        }

        .mdi-no-padding {
          margin: 0; /* Remove the default margin */
        }

        .data-source {
        display: none; /* Initially hide all data source divs */
        }

        .data-source.active {
            display: block; /* Show the active data source div */
        }

        .container-file-upload {
          background-color: #ffffff;
          width: 100%;
          position: relative;
          margin: 3.12em auto;
          padding: 3.12em 1.25em;
          border-radius: 0.43em;
          border: 2px solid #CE1E2D; /* Replace #007bff with your desired border color */
          padding: 20px;
          border-style: dashed
        }
        
        input[type="file"] {
          display: none;
        }

        .file-input-lbl {
          display: block;
          position: relative;
          font-size: 1.12em;
          font-weight: 500;
          text-align: center;
          padding: 1.12em 0;
          margin: auto;
          border-style: dashed;
          border-radius: 0.31em;
          cursor: pointer;
        }

        #num-of-files {
          font-weight: 400;
          text-align: center;
          margin: 1.25em 0 1.87em 0;
        }

        ul {
          list-style-type: none;
        }
        .container-file-upload li {
          font-weight: 500;
          background-color: #eff5ff;
          color: #025bee;
          margin-bottom: 1em;
          padding: 1.1em 1em;
          border-radius: 0.3em;
          display: flex;
          justify-content: space-between;
        }



    </style>
      <script src="https://cdn.ckeditor.com/ckeditor5/39.0.0/classic/ckeditor.js"></script>
</head>
<body>
<div class="container-scroller">
    <?php include 'components/navbar.php'; ?>
    <div class="container-fluid page-body-wrapper">
        <?php include 'components/sidebar.php'; ?>
        <div class="main-panel">
        <div class="content-wrapper">
          <div class="row">
          <div class="col grid-margin stretch-card">
              <div class="card">
                <div class="card-body">
                  <h2>NEW DATA SOURCES</h2>
                  <p class="card-description">
                    Data sources, such as a text and documents, are used to train the chatbot. To add a new data source, select a type from below.
                  </p>
                  <div class="my-2 d-flex justify-content-between align-items-center">
                    <div class="form-group">
                      <a class="btn btn-outline-danger btn-fw me-2 active" onclick="setActiveButton(1); showDiv('text')"><i class="mdi mdi-format-list-bulleted me-2"></i>Text</a>
                      <a class="btn btn-outline-danger btn-fw me-2" onclick="setActiveButton(2); showDiv('faq')"><i class="mdi mdi-help-circle-outline me-2"></i>FAQ</a>
                      <a class="btn btn-outline-danger btn-fw me-2" onclick="setActiveButton(3); showDiv('documents')"><i class="mdi mdi-file-document me-2"></i>Documents</a>
                    </div>
                  </div>

                  <!-- Text Input Data Source -->
                  <div id="text-data-source" class="data-source active">
                    <p class="card-description">
                      Enter the text that you want to train the chatbot on. Ideally, this would be the information you want the chatbot to learn, which may not be available via other sources such as your website
                    </p>
                    <form action="" method="post">
                      <textarea name="textarea" id="editor" rows="100"></textarea>
                      <button type="button" class="btn btn-danger mt-2">Submit</button>
                    </form>
                  </div>


                  <!-- FAQ Input Data Source -->
                  <div id="faq-data-source" class="data-source">
                    <p class="card-description">
                        Enter the frequently asked questions and answers you want the chatbot to learn.
                    </p>
                    <form action="" method="post">
                        <div class="faq-inputs">
                            <div class="form-group">
                                <label for="exampleInputPassword1"><b>Question:</b></label>
                                <input type="password" name="questions[]" class="form-control" placeholder="Enter the Question">
                            </div>
                            <div class="form-group">
                                <label for="editor2"><b>Answer:</b></label>
                                <textarea name="textarea[]" id="editor2" rows="100"></textarea>
                            </div>
                        </div>
                        <button type="button" class="btn btn-inverse-success btn-fw add-more-btn btn-sm" onclick="addMoreFaqInputs()">
                            <i class="mdi mdi-plus me-2"></i>Add More
                        </button>
                        <button type="button" class="btn btn-danger mt-2">Submit</button>
                    </form>
                </div>

                  <!-- Documents upload Data Source -->
                  <div id="documents-data-source" class="data-source">
                    <!-- Content for the "Documents" button goes here -->
                    <p class="card-description">
                        Upload and train the chatbot on your documents.
                    </p>
                    <li class="card-description">Supported files: PDF (more coming soon)</li>
                    <li class="card-description">Max. 5 files at a time</li>
                    <li class="card-description">File size: 1 MB per file</li>

                    <div class="container-file-upload">
                      <input type="file" id="file-input" multiple accept=".pdf"/>
                      <label for="file-input" class="file-input-lbl btn-inverse-success btn-fw">
                        <i class="fa-solid fa-arrow-up-from-bracket"></i>
                        &nbsp; Choose Files To Upload
                      </label>
                      <div id="num-of-files">No Files Chosen</div>
                      <ul id="files-list"></ul>
                    </div>
                  </div>
                  
                </div>
              </div>
          </div>
          </div>
        </div>
        </div>
    </div>
    <?php include 'components/footer.php'; ?>
</div>
</body>
<script>
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
</script>

<script>
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
</script>

<script>
    function showDiv(source) {
        const dataSources = document.querySelectorAll('.data-source');
        dataSources.forEach(sourceDiv => {
            sourceDiv.classList.remove('active');
        });

        const selectedDiv = document.getElementById(`${source}-data-source`);
        selectedDiv.classList.add('active');
    }
</script>

<script>
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
</script>

<script>
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

</script>

<script>
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
</script>


</html>