document.addEventListener('DOMContentLoaded', function() {
  const analyzeBtn = document.getElementById('analyzeBtn');
  const loadingIndicator = document.getElementById('loadingIndicator');
  const results = document.getElementById('results');

  function getScoreColorClass(score) {
    if (score >= 85) return 'score-green';
    if (score >= 70) return 'score-yellow';
    if (score >= 65) return 'score-orange';
    return 'score-red';
  }


  function displayResults(data) {
    // Set cumulative score and color
    const scoreCircle = document.querySelector('.score-circle');
    const scoreValue = scoreCircle.querySelector('.score-value');
    const cumulativeScore = data.cumulative_score;
    const cumulativeColorClass = getScoreColorClass(cumulativeScore);

    scoreCircle.style.setProperty('--score', cumulativeScore);
    scoreValue.textContent = cumulativeScore;
    // Remove old color classes and add the new one
    scoreCircle.classList.remove('score-green', 'score-yellow', 'score-orange', 'score-red');
    scoreCircle.classList.add(cumulativeColorClass);


    // Display ratings
    const ratingsContent = document.getElementById('ratingsContent');
    ratingsContent.innerHTML = '';
    
    data.ratings.forEach(rating => {
      const ratingElement = document.createElement('div');
      const ratingScore = rating.score;
      const ratingColorClass = getScoreColorClass(ratingScore);

      ratingElement.className = `rating-item ${ratingColorClass}`; // Add color class to the item
      ratingElement.innerHTML = `
        <div class="rating-header">
          <span class="rating-name">${rating["Rating Name"]}</span>
          <span class="rating-score">${ratingScore}%</span>
        </div>
        <div class="rating-bar">
          <div class="rating-progress" style="width: ${ratingScore}%"></div>
        </div>
      `;
      // Apply the color variable directly to the progress bar for immediate effect
      const progressBar = ratingElement.querySelector('.rating-progress');
      progressBar.style.setProperty('--current-score-color', `var(--${ratingColorClass.replace('score-','')}-color, var(--primary-color))`);

      ratingsContent.appendChild(ratingElement);
    });

    // Display false claims
    const falseClaimsContent = document.getElementById('falseClaimsContent');
    if (data.false_claims) {
      falseClaimsContent.querySelector('p').textContent = data.false_claims;
      falseClaimsContent.classList.remove('hidden');
    } else {
      falseClaimsContent.classList.add('hidden');
    }

    // Display references
    const referencesContent = document.getElementById('referencesContent');
    referencesContent.innerHTML = '';
    data.references.forEach(ref => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = ref;
      a.target = '_blank';
      a.textContent = ref;
      li.appendChild(a);
      referencesContent.appendChild(li);
    });

    // Show results
    loadingIndicator.classList.add('hidden');
    results.classList.remove('hidden');
  }

  function handleError(error) {
    loadingIndicator.textContent = 'Error analyzing page: ' + error.message;
    loadingIndicator.style.color = 'var(--danger-color)';
    console.error('Error:', error);
  }

  function resetUI() {
    loadingIndicator.textContent = 'Analyzing claims...';
    loadingIndicator.style.color = 'var(--text-color)';
    results.classList.add('hidden');
    loadingIndicator.classList.remove('hidden');
  }

  analyzeBtn.addEventListener('click', function() {
    resetUI();
    
    // Get the current tab's URL
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      const currentUrl = tabs[0].url;
      
      fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pageURL: currentUrl
        })
      })
      .then(response => {
        console.log(response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Backend Response:', data);
        displayResults(data);
      })
      .catch(error => handleError(error));
    });
  });
});
