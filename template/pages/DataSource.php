<?php
    include 'static/component/header.php';
    include 'static/components/preloader.php'
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        /* Custom CSS to set active color for the buttons */
        .btn.active {
            background-color: #343a40;
            color: #ffffff;
        }

        .rounded-container {
          border-radius: 5px;
        }

        td.answers{
          width: 10%;
        }

    </style>
</head>
<body>
<div class="container-scroller">
    <?php include '../../static/components/navbar.php'; ?>
    <div class="container-fluid page-body-wrapper">
        <?php include 'static/components/sidebar.php'; ?>
        <div class="main-panel">
        <div class="content-wrapper">
          <div class="row">
          <div class="col grid-margin stretch-card">
              <div class="card">
                <div class="card-body">
                  <h2>FAQs</h2>
                  <p class="card-description">
                    Add and manage the FAQs used to train the chatbot.
                  </p>
                  <div class="my-2 d-flex justify-content-between align-items-center">
                    <div class="form-group border border-primary p-1">
                      <a class="btn btn-inverse-light btn-fw" onclick="setActiveButton(1)">Text</a>
                      <a class="btn btn-inverse-light btn-fw" onclick="setActiveButton(2)">FAQ</a>
                      <a class="btn btn-inverse-light btn-fw" onclick="setActiveButton(3)">Document</a>
                    </div>
                    <div class="form-group">
                      <div class="d-flex">
                          <div class="dropdown me-2">
                              <button class="btn btn-outline-dark dropdown-toggle" type="button" id="dropdownMenuButton2" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
                                  Bulk Action
                              </button>
                              <div class="dropdown-menu" aria-labelledby="dropdownMenuButton2">
                                  <a class="dropdown-item" href="#">Delete</a>
                              </div>
                          </div>
                          <button type="button" class="btn btn-outline-dark btn-fw me-2" onclick="toggleStatistics()">View Stats</button>
                          <a href="./AddDataSource.php" type="button" class="btn btn-danger">Add New</a>
                      </div>
                    </div>
                  </div>
                  <div class="row statistics d-none">
                    <div class="col-md-4 mb-4">
                        <div class="statistics-details d-flex flex-column align-items-center bg-inverse-success rounded-container p-4">
                            <div>
                                <p class="statistics-title">Total Sources</p>
                                <h3 class="rate-percentage">0</h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-4">
                        <div class="statistics-details d-flex flex-column align-items-center bg-inverse-info rounded-container p-4">
                            <div>
                                <p class="statistics-title">Processed</p>
                                <h3 class="rate-percentage">0</h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-4">
                        <div class="statistics-details d-flex flex-column align-items-center bg-inverse-danger rounded-container p-4">
                            <div>
                                <p class="statistics-title">Error</p>
                                <h3 class="rate-percentage">0</h3>
                            </div>
                        </div>
                    </div>
                  </div>
                  
                  <div class="table-responsive">
                  <table id="example" class="table">
  <thead>
    <tr>
      <th></th>
      <th>FAQ</th>
      <th>Action</th>
    </tr>
  </thead>
  <tbody>
        <tr>
          <!-- Inside the loop -->
          <td>
            <div class="form-check form-check-flat form-check-primary">
              <label class="form-check-label">
                <input type="checkbox" class="form-check-input" value="">
              </label>
            </div>
          </td>
          <td style="max-width: 400px">
            <div class="accordion accordion-filled" id="accordion" role="tablist">
              <div class="card">
                <div class="card-header" role="tab" id="heading">
                  <h6 class="mb-0">
                    <a data-bs-toggle="collapse" href="#collapse" aria-expanded="false" aria-controls="collapse" class="collapsed">
                    </a>
                  </h6>
                </div>
                <div id="collapse" class="collapse" role="tabpanel" aria-labelledby="heading" data-bs-parent="#accordion" style="">
                  <div class="card-body">
                    <p class="mb-0"></p>
                  </div>
                </div>
              </div>
            </div>
          </td>
          <td>
            <!-- Add align-middle class to vertically center the content -->
            <div class="btn-group" role="group" aria-label="Basic example" style="height: 30px;">
              <button type="button" class="btn btn-info">
                <i class="ti-wand"></i>
              </button>
              <button type="button" class="btn btn-danger" onclick="showSwal('warning-delete-data')">
                <i class="ti-trash"></i>
              </button>
            </div>
          </td>
        </tr>
  </tbody>
</table>

                  </div>

                </div>
              </div>
          </div>
          </div>
        </div>
        </div>
    </div>
    <?php include '/static/footer.php'; ?>
</div>


<?php include 'includes/popup.php'?>
</body>

<script>
  (function($){
    showSwal = function(type){
      if (type === 'warning-delete-data') {
      swal({
        title: 'Delete this data?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3f51b5',
        cancelButtonColor: '#ff4081',
        confirmButtonText: 'Great ',
        buttons: {
          cancel: {
            text: "Cancel",
            value: null,
            visible: true,
            className: "btn btn-danger",
            closeModal: true,
          },
          confirm: {
            text: "OK",
            value: true,
            visible: true,
            className: "btn btn-primary",
            closeModal: true
          }
        }
      }).then((willDelete) => {
        if (willDelete) {
          $.ajax({
            type: 'POST',
            url: 'delete_data.php',
            data: { rowToDelete: '<?php echo $rowCount; ?>' },
            success: function(response) {
              if (response === 'Success') {
                // Reload the page or update the accordion as needed
                location.reload(); // Reload the page
                // Alternatively, update the accordion content using JavaScript
              }
            }
          });
        }
      });
    }
    }
  })(jQuery)
</script>

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

    function toggleStatistics() {
        const statisticsDiv = document.querySelector('.statistics');
        statisticsDiv.classList.toggle('d-none');
    }
</script>

<script>
    window.location.href = "{{ redirect_url }}";
</script>

</html>