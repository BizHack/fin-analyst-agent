/**
 * main.js - Main JavaScript file for finHackers
 */

// Wait for the DOM to be loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the UI components
    initializeUI();
    
    // Setup refresh timer for market data
    setupRefreshTimer();
    
    // Initialize event listeners
    setupEventListeners();
});

/**
 * Initialize UI components
 */
function initializeUI() {
    console.log('Initializing UI components');
    
    // Initialize tabs if present
    const tabButtons = document.querySelectorAll('.tab-button');
    if (tabButtons.length > 0) {
        initializeTabs(tabButtons);
    }
    
    // Initialize stock selector if present
    const stockSelect = document.getElementById('stock-select');
    if (stockSelect) {
        initializeStockSelector(stockSelect);
    }
}

/**
 * Initialize tabs functionality
 * @param {NodeList} tabButtons - List of tab button elements
 */
function initializeTabs(tabButtons) {
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Hide all tab panels
            tabPanels.forEach(panel => {
                panel.classList.add('hidden');
                panel.classList.remove('active');
            });
            
            // Show the corresponding panel
            const tabId = button.getAttribute('data-tab');
            const activePanel = document.getElementById(`${tabId}-tab`);
            if (activePanel) {
                activePanel.classList.remove('hidden');
                activePanel.classList.add('active');
            }
        });
    });
}

/**
 * Initialize stock selector functionality
 * @param {HTMLElement} stockSelect - Stock select dropdown element
 */
function initializeStockSelector(stockSelect) {
    stockSelect.addEventListener('change', () => {
        const selectedStock = stockSelect.value;
        const tickerSymbols = document.querySelectorAll('.ticker-symbol');
        
        // Update ticker symbols in the content
        tickerSymbols.forEach(el => {
            el.textContent = selectedStock;
        });
        
        // Load new data for the selected stock via AJAX
        loadStockData(selectedStock);
        
        // Refresh the current tab
        const activeTab = document.querySelector('.tab-button.active');
        if (activeTab) {
            activeTab.click();
        }
    });
}

/**
 * Load stock data via AJAX
 * @param {string} ticker - Stock ticker symbol
 */
function loadStockData(ticker) {
    console.log(`Loading data for ${ticker}...`);
    
    // Get the active tab to determine what kind of data to load
    const activeTab = document.querySelector('.tab-button.active');
    if (!activeTab) return;
    
    const tabType = activeTab.getAttribute('data-tab');
    
    // Create form data
    const formData = new FormData();
    formData.append('ticker', ticker);
    formData.append('tab_type', tabType);
    
    // Send AJAX request to the backend
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
        // Update the current tab panel with new content
        const activePanel = document.getElementById(`${tabType}-tab`);
        if (activePanel) {
            activePanel.innerHTML = html;
        }
    })
    .catch(error => {
        console.error('Error loading stock data:', error);
    });
}

/**
 * Setup timer to refresh market data periodically
 */
function setupRefreshTimer() {
    // Refresh market data every 60 seconds
    setInterval(refreshMarketData, 60000);
}

/**
 * Refresh market data via AJAX
 */
function refreshMarketData() {
    console.log('Refreshing market data...');
    
    fetch('/market_data')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Update the market pulse section with new data
        updateMarketPulse(data);
    })
    .catch(error => {
        console.error('Error refreshing market data:', error);
    });
}

/**
 * Update the market pulse section with new data
 * @param {Object} data - Market data object
 */
function updateMarketPulse(data) {
    // Update SPY
    const spyPrice = document.getElementById('spy-price');
    const spyChange = document.getElementById('spy-change');
    if (spyPrice && spyChange) {
        spyPrice.textContent = `$${data.spy.price}`;
        spyChange.textContent = `${data.spy.change}%`;
        spyChange.className = data.spy.change_direction === 'up' 
            ? 'text-xs text-green-400' 
            : 'text-xs text-red-400';
        
        const spyIcon = spyChange.querySelector('i');
        if (spyIcon) {
            spyIcon.className = data.spy.change_direction === 'up' 
                ? 'fas fa-caret-up mr-1' 
                : 'fas fa-caret-down mr-1';
        }
    }
    
    // Update Bitcoin
    const btcPrice = document.getElementById('btc-price');
    const btcChange = document.getElementById('btc-change');
    if (btcPrice && btcChange) {
        btcPrice.textContent = `$${data.bitcoin.price}`;
        btcChange.textContent = `${data.bitcoin.change}%`;
        btcChange.className = data.bitcoin.change_direction === 'up' 
            ? 'text-xs text-green-400' 
            : 'text-xs text-red-400';
        
        const btcIcon = btcChange.querySelector('i');
        if (btcIcon) {
            btcIcon.className = data.bitcoin.change_direction === 'up' 
                ? 'fas fa-caret-up mr-1' 
                : 'fas fa-caret-down mr-1';
        }
    }
    
    // Update Gold
    const goldPrice = document.getElementById('gold-price');
    const goldChange = document.getElementById('gold-change');
    if (goldPrice && goldChange) {
        goldPrice.textContent = `$${data.gold.price}`;
        goldChange.textContent = `${data.gold.change}%`;
        goldChange.className = data.gold.change_direction === 'up' 
            ? 'text-xs text-green-400' 
            : 'text-xs text-red-400';
        
        const goldIcon = goldChange.querySelector('i');
        if (goldIcon) {
            goldIcon.className = data.gold.change_direction === 'up' 
                ? 'fas fa-caret-up mr-1' 
                : 'fas fa-caret-down mr-1';
        }
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Add any additional event listeners here
    
    // Example: Listen for simulate event button clicks
    const simulateEventButton = document.getElementById('simulate-event');
    if (simulateEventButton) {
        simulateEventButton.addEventListener('click', simulateMarketEvent);
    }
}

/**
 * Simulate a market event
 */
function simulateMarketEvent() {
    console.log('Simulating market event...');
    
    // Get the event type
    const eventType = document.getElementById('event-type').value;
    
    // Create form data
    const formData = new FormData();
    formData.append('event_type', eventType);
    
    // Send AJAX request to the backend
    fetch('/simulate_event', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Display the event results
        displayEventResults(data);
    })
    .catch(error => {
        console.error('Error simulating event:', error);
    });
}

/**
 * Display event results
 * @param {Object} data - Event results data
 */
function displayEventResults(data) {
    const resultsContainer = document.getElementById('event-results');
    if (!resultsContainer) return;
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    // Create result elements
    const eventDiv = document.createElement('div');
    eventDiv.className = 'p-4 bg-slate-100 rounded-lg mt-4 animate-fade-in';
    
    const eventTitle = document.createElement('h4');
    eventTitle.className = 'font-semibold text-midnight mb-2';
    eventTitle.textContent = data.event;
    
    const eventAnalysis = document.createElement('p');
    eventAnalysis.className = 'text-sm text-gray-700 mb-2';
    eventAnalysis.textContent = data.analysis;
    
    const eventImpact = document.createElement('p');
    eventImpact.className = 'text-sm font-medium text-teal';
    eventImpact.textContent = `Impact: ${data.impact}`;
    
    // Append elements to container
    eventDiv.appendChild(eventTitle);
    eventDiv.appendChild(eventAnalysis);
    eventDiv.appendChild(eventImpact);
    resultsContainer.appendChild(eventDiv);
}