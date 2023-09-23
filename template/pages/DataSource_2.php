<?php
    include '../components/header.php';
    include '../components/preloader.php'
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

    </style>
</head>
<body>
<div class="container-scroller">
    <?php include '../components/navbar.php'; ?>
    <div class="container-fluid page-body-wrapper">
        <?php include '../components/sidebar.php'; ?>
        <div class="main-panel">
        <div class="content-wrapper">
          <div class="row">
          <div class="col grid-margin stretch-card">
              <div class="card">
                <div class="card-body">
                  <h2>DATA SOURCES</h2>
                  <p class="card-description">
                    Add and manage the data sources used to train the chatbot.
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
                    <table class="table">
                      <thead>
                        <tr>
                          <th></th>
                          <th>File</th>
                          <th>Characters</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>
                            <div class="form-check form-check-flat form-check-primary">
                              <label class="form-check-label">
                                <input type="checkbox" class="form-check-input">
                              </label>
                            </div>
                          </td>
                          <td>faq.pdf</td>
                          <td>54,782</td>
                          <td><label class="badge badge-danger">Pending</label></td>
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
    <?php include '../components/footer.php'; ?>
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

    function toggleStatistics() {
        const statisticsDiv = document.querySelector('.statistics');
        statisticsDiv.classList.toggle('d-none');
    }
</script>
</html>