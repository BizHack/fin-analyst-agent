// Main JavaScript for TrainingUp.ai application

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabLinks = document.querySelectorAll('.nav-link');
    const tickerForm = document.getElementById('tickerForm');
    const tabContentDiv = document.getElementById('tabContent');
    
    // Handle tab clicks
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active tab
            tabLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Update hidden input in the form
            const tabType = this.getAttribute('data-tab-type');
            if (tickerForm) {
                const tabTypeInput = tickerForm.querySelector('input[name="tab_type"]');
                if (tabTypeInput) {
                    tabTypeInput.value = tabType;
                }
            }
        });
    });
    
    // Handle ticker search form submission
    if (tickerForm) {
        tickerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading state
            if (tabContentDiv) {
                tabContentDiv.innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
            }
            
            const formData = new FormData(this);
            
            fetch('/analyze_ticker', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(html => {
                if (tabContentDiv) {
                    tabContentDiv.innerHTML = html;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (tabContentDiv) {
                    tabContentDiv.innerHTML = `<div class="alert alert-danger">Error loading data: ${error.message}</div>`;
                }
            });
        });
    }
    
    // Handle "Analyze New Event" button
    const analyzeEventBtn = document.getElementById('analyzeEventBtn');
    if (analyzeEventBtn) {
        analyzeEventBtn.addEventListener('click', function() {
            // Randomly choose event type
            const eventTypes = ['social_post', 'politician_trade', 'market_move'];
            const randomEvent = eventTypes[Math.floor(Math.random() * eventTypes.length)];
            
            // Create form data
            const formData = new FormData();
            formData.append('event_type', randomEvent);
            
            // Show processing notification
            const alertsContainer = document.getElementById('alertsContainer');
            if (alertsContainer) {
                const loadingAlert = document.createElement('div');
                loadingAlert.className = 'alert alert-info';
                loadingAlert.innerHTML = '<div class="spinner-border spinner-border-sm me-2" role="status"></div> Analyzing new market event...';
                alertsContainer.prepend(loadingAlert);
                
                // Call API to simulate new event
                fetch('/simulate_event', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    // Remove loading alert
                    loadingAlert.remove();
                    
                    // Display the result
                    const resultAlert = document.createElement('div');
                    resultAlert.className = 'alert alert-success alert-dismissible fade show';
                    resultAlert.innerHTML = `
                        <strong>${data.event}</strong>
                        <p>${data.analysis}</p>
                        <p><em>Impact: ${data.impact}</em></p>
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    alertsContainer.prepend(resultAlert);
                    
                    // Auto dismiss after 10 seconds
                    setTimeout(() => {
                        if (resultAlert) {
                            const bsAlert = new bootstrap.Alert(resultAlert);
                            bsAlert.close();
                        }
                    }, 10000);
                })
                .catch(error => {
                    // Remove loading alert
                    loadingAlert.remove();
                    
                    // Show error
                    const errorAlert = document.createElement('div');
                    errorAlert.className = 'alert alert-danger alert-dismissible fade show';
                    errorAlert.innerHTML = `
                        <strong>Error analyzing event</strong>
                        <p>${error.message}</p>
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    alertsContainer.prepend(errorAlert);
                });
            }
        });
    }
    
    // Auto-refresh market data every 60 seconds
    function refreshMarketData() {
        const marketDataContainer = document.getElementById('marketMovements');
        if (marketDataContainer) {
            fetch('/analyze_ticker', {
                method: 'POST',
                body: new FormData(document.createElement('form'))
            })
            .then(response => response.text())
            .then(html => {
                // Extract just the market data section and update
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                const newMarketData = tempDiv.querySelector('#marketMovements');
                if (newMarketData) {
                    marketDataContainer.innerHTML = newMarketData.innerHTML;
                }
            })
            .catch(error => console.error('Error refreshing market data:', error));
        }
    }
    
    // Set up interval for refreshing (commented out for now to avoid unnecessary API calls in demo)
    // const refreshInterval = setInterval(refreshMarketData, 60000);
    
    // Load initial tab content if no content is present
    if (tabContentDiv && tabContentDiv.children.length === 0 && tickerForm) {
        tickerForm.dispatchEvent(new Event('submit'));
    }
});
