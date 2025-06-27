/**
 * Hyper ADS - AI Processing Animation
 * Low computational impact client-side animation to visualize AI agent workflow
 */

class AgentAnimation {
    constructor() {
        // Agent workflow elements
        this.dataAnalystCard = document.getElementById('data-analyst');
        this.weatherAnalystCard = document.getElementById('weather-analyst');
        this.marketingStrategistCard = document.getElementById('marketing-strategist');
        
        this.connectionLines = document.querySelectorAll('.connection-line');
        this.dataPoints = document.querySelectorAll('.data-point');
        
        // Insight elements
        this.eventsInsightValue = document.querySelector('#events-insight .insight-value');
        this.weatherInsightValue = document.querySelector('#weather-insight .insight-value');
        this.strategyInsightValue = document.querySelector('#strategy-insight .insight-value');
        
        // Animation state
        this.isRunning = false;
        this.animationSpeed = 1;  // Normal speed multiplier
        this.weatherConditions = ['Sunny', 'Partly Cloudy', 'Rainy', 'Windy', 'Snowy', 'Clear Skies'];
        this.eventTypes = ['Concerts', 'Festivals', 'Sports', 'Conferences', 'Exhibitions', 'Local Fairs'];
        this.strategyTypes = ['Social Media', 'Local SEO', 'Event Sponsorship', 'Google Ads', 'Email Marketing'];
        
        // Text variations for agent status
        this.dataAnalystStatuses = [
            'Collecting local events data...',
            'Analyzing event attendance patterns...',
            'Identifying target demographics...',
            'Cross-referencing with historical data...',
            'Calculating traffic potential...'
        ];
        
        this.weatherAnalystStatuses = [
            'Waiting for data...',
            'Retrieving weather forecasts...',
            'Analyzing temperature trends...',
            'Evaluating impact on foot traffic...',
            'Correlating weather with consumer behavior...'
        ];
        
        this.marketingStrategistStatuses = [
            'Waiting for analysis...',
            'Reviewing collected insights...',
            'Formulating advertising strategy...',
            'Identifying optimal channels...',
            'Finalizing recommendations...'
        ];
    }
    
    // Start animation sequence
    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        
        // Reset UI
        this.reset();
        
        // Start data analyst simulation
        this.simulateDataAnalyst()
            .then(() => this.simulateWeatherAnalyst())
            .then(() => this.simulateMarketingStrategist())
            .catch(error => console.error('Animation error:', error));
    }
    
    // Reset animation state
    reset() {
        // Reset progress bars
        document.querySelectorAll('.progress').forEach(bar => {
            bar.style.width = '0%';
        });
        
        // Reset agent cards
        document.querySelectorAll('.agent-card').forEach(card => {
            card.classList.remove('active');
        });
        
        // Reset data points
        document.querySelectorAll('.data-point').forEach(point => {
            point.classList.remove('active');
        });
        
        // Reset insights
        this.eventsInsightValue.textContent = '--';
        this.weatherInsightValue.textContent = '--';
        this.strategyInsightValue.textContent = '--';
    }
    
    // Simulate Data Analyst agent
    simulateDataAnalyst() {
        return new Promise(resolve => {
            // Activate data analyst card
            this.dataAnalystCard.classList.add('active');
            
            let progress = 0;
            let statusIndex = 0;
            const progressBar = this.dataAnalystCard.querySelector('.progress');
            const statusEl = this.dataAnalystCard.querySelector('.agent-status');
            
            // Update status text periodically
            const updateStatus = () => {
                statusEl.textContent = this.dataAnalystStatuses[statusIndex];
                statusIndex = (statusIndex + 1) % this.dataAnalystStatuses.length;
            };
            
            // Start with initial status
            updateStatus();
            
            // Status update interval
            const statusInterval = setInterval(updateStatus, 3000 / this.animationSpeed);
            
            // Progress update interval
            const interval = setInterval(() => {
                progress += 1;
                progressBar.style.width = `${progress}%`;
                
                // When 100% complete
                if (progress >= 100) {
                    clearInterval(interval);
                    clearInterval(statusInterval);
                    
                    // Show event insights
                    const eventCount = Math.floor(Math.random() * 15) + 5; // 5-20 events
                    const eventType = this.eventTypes[Math.floor(Math.random() * this.eventTypes.length)];
                    this.eventsInsightValue.textContent = `${eventCount} ${eventType}`;
                    
                    // Activate first data flow
                    setTimeout(() => {
                        this.dataPoints[0].classList.add('active');
                        setTimeout(() => resolve(), 1500 / this.animationSpeed);
                    }, 500 / this.animationSpeed);
                }
            }, 50 / this.animationSpeed);
        });
    }
    
    // Simulate Weather Analyst agent
    simulateWeatherAnalyst() {
        return new Promise(resolve => {
            // Activate weather analyst card
            this.weatherAnalystCard.classList.add('active');
            
            let progress = 0;
            let statusIndex = 0;
            const progressBar = this.weatherAnalystCard.querySelector('.progress');
            const statusEl = this.weatherAnalystCard.querySelector('.agent-status');
            
            // Update status text periodically
            const updateStatus = () => {
                statusEl.textContent = this.weatherAnalystStatuses[statusIndex];
                statusIndex = (statusIndex + 1) % this.weatherAnalystStatuses.length;
            };
            
            // Start with initial status
            updateStatus();
            
            // Status update interval
            const statusInterval = setInterval(updateStatus, 2800 / this.animationSpeed);
            
            // Progress update interval
            const interval = setInterval(() => {
                progress += 1.2;
                progressBar.style.width = `${Math.min(progress, 100)}%`;
                
                // When 100% complete
                if (progress >= 100) {
                    clearInterval(interval);
                    clearInterval(statusInterval);
                    
                    // Show weather insights
                    const weatherCondition = this.weatherConditions[Math.floor(Math.random() * this.weatherConditions.length)];
                    const temperature = Math.floor(Math.random() * 30) + 50; // 50-80°F
                    this.weatherInsightValue.textContent = `${weatherCondition}, ${temperature}°F`;
                    
                    // Activate second data flow
                    setTimeout(() => {
                        this.dataPoints[1].classList.add('active');
                        setTimeout(() => resolve(), 1500 / this.animationSpeed);
                    }, 500 / this.animationSpeed);
                }
            }, 40 / this.animationSpeed);
        });
    }
    
    // Simulate Marketing Strategist agent
    simulateMarketingStrategist() {
        return new Promise(resolve => {
            // Activate marketing strategist card
            this.marketingStrategistCard.classList.add('active');
            
            let progress = 0;
            let statusIndex = 0;
            const progressBar = this.marketingStrategistCard.querySelector('.progress');
            const statusEl = this.marketingStrategistCard.querySelector('.agent-status');
            
            // Update status text periodically
            const updateStatus = () => {
                statusEl.textContent = this.marketingStrategistStatuses[statusIndex];
                statusIndex = (statusIndex + 1) % this.marketingStrategistStatuses.length;
            };
            
            // Start with initial status
            updateStatus();
            
            // Status update interval
            const statusInterval = setInterval(updateStatus, 3200 / this.animationSpeed);
            
            // Progress update interval
            const interval = setInterval(() => {
                progress += 0.8;
                progressBar.style.width = `${Math.min(progress, 100)}%`;
                
                // When 100% complete
                if (progress >= 100) {
                    clearInterval(interval);
                    clearInterval(statusInterval);
                    
                    // Show strategy insights
                    const strategyType = this.strategyTypes[Math.floor(Math.random() * this.strategyTypes.length)];
                    this.strategyInsightValue.textContent = strategyType;
                    
                    // Complete animation
                    setTimeout(() => {
                        this.isRunning = false;
                        resolve();
                    }, 1000 / this.animationSpeed);
                }
            }, 60 / this.animationSpeed);
        });
    }
}

// Will be initialized by main.js
window.agentAnimation = new AgentAnimation();