document.addEventListener('DOMContentLoaded', function() {
  const analyzeBtn = document.getElementById('analyzeBtn');
  const loadingIndicator = document.getElementById('loadingIndicator');
  const results = document.getElementById('results');
  const analysisContent = document.getElementById('analysisContent');
  
  analyzeBtn.addEventListener('click', function() {
    // Get the current tab's URL
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      const url = tabs[0].url;
      
      // Show loading indicator
      loadingIndicator.classList.remove('hidden');
      results.classList.add('hidden');
      
      // Send request to backend
      fetch('http://localhost:8000/analyze-sustainability', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ pageURL: url })
      })
      .then(response => response.json())
      .then(data => {
        // Hide loading indicator
        loadingIndicator.classList.add('hidden');
        
        // Display results
        analysisContent.innerHTML = data.analysis.replace(/\n/g, '<br>');
        results.classList.remove('hidden');
      })
      .catch(error => {
        loadingIndicator.classList.add('hidden');
        analysisContent.innerHTML = 'Error: ' + error.message;
        results.classList.remove('hidden');
      });
    });
  });
});
