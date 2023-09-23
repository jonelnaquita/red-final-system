// Function to load a JavaScript file dynamically
function loadScript(url, callback) {
    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src = url;
    script.onload = callback;
    document.head.appendChild(script);
  }
  
  // Function to load all JavaScript files in the folder
  function loadMultipleJSFiles(folderPath, files) {
    files.forEach((file) => {
      const fullPath = folderPath + "/" + file;
      loadScript(fullPath);
    });
  }
  
  // Usage example
  const folderPath = "/js"; // Replace "js" with your actual folder path
  const jsFiles = [
    "ace.js",
    "alerts.js",
    "file3.js",
    // Add more file names as needed
  ];
  
  loadMultipleJSFiles(folderPath, jsFiles);
  