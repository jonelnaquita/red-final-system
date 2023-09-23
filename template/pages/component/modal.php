<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        .modal {
        display: none;
        transition: opacity 0.3s ease;
        }

        .modal.fade.show {
        display: block;
        opacity: 1;
        }

        .modal.fade {
        opacity: 0;
        }

        /* Center the modal */
        .modal-dialog-centered {
        display: flex;
        align-items: center;
        min-height: 100vh;
        }

        /* Add some background and box-shadow to the modal content */
        .modal-content {
        background-color: #fff;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        }

        /* Style the modal header */
        .modal-header {
        border-bottom: 1px solid #f0f0f0;
        }

        /* Style the modal title */
        .modal-title {
        font-size: 18px;
        font-weight: bold;
        margin: 0;
        }

        /* Style the modal body */
        .modal-body {
        padding: 20px;
        }

        /* Style the modal footer */
        .modal-footer {
        border-top: 1px solid #f0f0f0;
        padding: 10px 20px;
        }

        /* Center the button in the footer */
        .modal-footer .btn {
        display: block;
        margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="card-body">
            <h4 class="card-title">Small Modal</h4>
            <p class="card-description">Small modal with max-width set to 300px</p>
            <div class="text-center">
            <button type="button" class="btn-sm btn btn-primary" id="showModalButton">Small modal <i class="ti-arrow-circle-right ms-1"></i></button>
            </div>
        </div>
    </div>

    <div class="modal fade" id="smallModal" tabindex="-1" aria-labelledby="smallModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-sm">
            <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="smallModalLabel">Modal title</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <p>Modal body text goes here.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-success btn-sm m-2">Submit</button>
                <button type="button" class="btn btn-light btn-sm m-2" data-bs-dismiss="modal">Cancel</button>
            </div>
            </div>
        </div>
    </div>
</body>

<script>
  // Get the modal element
  const smallModal = document.getElementById('smallModal');

  // Get the button that opens the modal
  const showModalButton = document.getElementById('showModalButton');

  // Function to show the modal
  function showModal() {
    smallModal.classList.add('show', 'fade');
    document.body.classList.add('modal-open');
    const backdrop = document.createElement('div');
    backdrop.classList.add('modal-backdrop', 'fade', 'show');
    document.body.appendChild(backdrop);
  }

  // Function to hide the modal
  function hideModal() {
    smallModal.classList.remove('show', 'fade');
    document.body.classList.remove('modal-open');
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
      document.body.removeChild(backdrop);
    }
  }

  // Add click event listener to the button to show the modal
  showModalButton.addEventListener('click', showModal);

  // Add click event listener to the close button to hide the modal
  const closeButton = smallModal.querySelector('.btn-close');
  closeButton.addEventListener('click', hideModal);

  // Add click event listener to the backdrop to hide the modal when clicked outside the modal
  smallModal.addEventListener('click', function (event) {
    if (event.target === smallModal) {
      hideModal();
    }
  });
</script>
</html>