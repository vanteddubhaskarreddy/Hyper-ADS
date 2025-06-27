document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recommender-form');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const recommendationsContent = document.getElementById('recommendations-content');
    const channelsContainer = document.getElementById('channels-container');
    const errorMessage = document.getElementById('error-message');
    const savePdfButton = document.getElementById('save-pdf');
    const emailResultsButton = document.getElementById('email-results');
    const useLocationButton = document.getElementById('use-location');
    const locationStatus = document.getElementById('location-status');
    
    // Initialize the agent animation
    const animation = window.agentAnimation;
    
    // Initialize lat/long fields with default values if postal code is 66213
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');
    const postalCodeInput = document.getElementById('postal-code');
    
    if (postalCodeInput.value === '66213') {
        // Default coordinates for 66213 (Overland Park, KS)
        latitudeInput.value = '38.9041260';
        longitudeInput.value = '-94.6898814';
    }
    
    // Use browser geolocation
    useLocationButton.addEventListener('click', () => {
        locationStatus.textContent = 'Getting your location...';
        
        if (!navigator.geolocation) {
            locationStatus.textContent = 'Geolocation is not supported by your browser';
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                // Format to exactly 4 decimal places
                const latitude = formatCoordinate(position.coords.latitude);
                const longitude = formatCoordinate(position.coords.longitude);
                
                latitudeInput.value = latitude;
                longitudeInput.value = longitude;
                
                // Clear postal code (we now have precise coordinates)
                postalCodeInput.value = '';
                
                locationStatus.textContent = `Location set to ${latitude}, ${longitude}`;
                
                // Add success styling
                locationStatus.style.color = 'var(--success)';
                setTimeout(() => {
                    locationStatus.style.color = 'var(--light-text)';
                }, 3000);
            },
            (error) => {
                let message;
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        message = 'Location permission denied';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message = 'Location information unavailable';
                        break;
                    case error.TIMEOUT:
                        message = 'Location request timed out';
                        break;
                    default:
                        message = 'Unknown error occurred';
                }
                locationStatus.textContent = message;
                locationStatus.style.color = 'var(--error)';
            }
        );
    });
    
    // Form submission handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form values
        const businessName = document.getElementById('business-name').value.trim();
        const businessType = document.getElementById('business-type').value.trim();
        const businessEmail = document.getElementById('business-email').value.trim();
        const postalCode = postalCodeInput.value.trim();
        
        // Format coordinates to exactly 4 decimal places
        let latitude = null;
        let longitude = null;
        
        if (latitudeInput.value) {
            latitude = formatCoordinate(latitudeInput.value);
        }
        
        if (longitudeInput.value) {
            longitude = formatCoordinate(longitudeInput.value);
        }
        
        // Form validation
        if (!businessName || businessName.length > 100) {
            alert('Please enter a valid business name (max 100 characters)');
            return;
        }
        
        if (!businessType || businessType.length > 100) {
            alert('Please enter a valid business type (max 100 characters)');
            return;
        }
        
        if (businessEmail && businessEmail.length > 100) {
            alert('Email address is too long (max 100 characters)');
            return;
        }
        
        if (postalCode && postalCode.length > 20) {
            alert('Postal code is too long (max 20 characters)');
            return;
        }
        
        // Validate coordinates
        if (!latitude || !longitude) {
            alert('Please enter both latitude and longitude values');
            return;
        }
        
        // Hide any previous results/errors
        results.classList.add('hidden');
        errorMessage.classList.add('hidden');
        loading.classList.remove('hidden');
        
        // Start the agent animation
        animation.start();
        
        // Prepare data for API with formatted coordinates
        const requestData = {
            business_name: businessName,
            business_type: businessType,
            business_email: businessEmail,
            business_postal_code: postalCode,
            business_latitude: parseFloat(latitude),
            business_longitude: parseFloat(longitude)
        };
        
        try {
            // Call the API
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            // Check for HTTP errors
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || `Server error: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("API Response:", data); // Debug: Log full response
            
            // Hide loading indicator
            loading.classList.add('hidden');
            
            // Render results - check all possible result structures
            let recommendation = "";
            if (data.recommendations && data.recommendations.overview) {
                // Main structure from main_sse.py
                recommendation = data.recommendations.overview;
            } else if (data.recommendation) {
                // Alternative structure
                recommendation = data.recommendation;
            } else if (typeof data === 'string') {
                // Plain string response
                recommendation = data;
            } else {
                // Fallback: stringify the object
                recommendation = JSON.stringify(data, null, 2);
            }
            
            recommendationsContent.innerHTML = formatRecommendation(recommendation);
            
            // Render channel recommendations
            const channelsContainer = document.getElementById('channels-container');
            if (channelsContainer) {
                // Render channel recommendations
                let channels = [];
                if (data.recommendations && data.recommendations.channels) {
                    channels = data.recommendations.channels;
                } else if (data.channels) {
                    channels = data.channels;
                }
                renderChannels(channels || []);
            }
            
            // Show results
            results.classList.remove('hidden');
            
            // Scroll to results
            results.scrollIntoView({ behavior: 'smooth' });
            
            // Store recommendation ID for email function
            window.currentRecommendationId = data.user_id || null;
            
            // Track successful submission
            trackEvent('recommendation_generated', {
                business_type: businessType
            });
        } catch (error) {
            console.error('Error:', error);
            loading.classList.add('hidden');
            document.querySelector('#error-message p').textContent = error.message || 'An error occurred while generating recommendations.';
            errorMessage.classList.remove('hidden');
            
            // Track error
            trackEvent('recommendation_error', {
                error_message: error.message
            });
        }
    });
    
    // Format recommendation text with Markdown-like syntax
    function formatRecommendation(text) {
        if (!text) return '';
        
        // Replace line breaks with paragraphs
        text = text.replace(/\n\n/g, '</p><p>');
        
        // Bold text between asterisks
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text between single asterisks
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Headers (if any)
        text = text.replace(/^# (.*$)/gm, '<h2>$1</h2>');
        text = text.replace(/^## (.*$)/gm, '<h3>$1</h3>');
        
        return `<p>${text}</p>`;
    }

    // Add this function to format coordinates to exactly 4 decimal places
    function formatCoordinate(value) {
        // Convert to number and handle validation
        let numValue = parseFloat(value);
        
        if (isNaN(numValue)) {
            return null;
        }
        
        // Format to exactly 4 decimal places
        let formatted = numValue.toFixed(4);
        return formatted;
    }
    
    // Render channel recommendations
    function renderChannels(channels) {
        // Check if the channel container exists
        if (!channelsContainer) {
            console.log('Channels section is removed from HTML');
            return;
        }

        channelsContainer.innerHTML = '';
        
        channels.forEach((channel, index) => {
            const channelCard = document.createElement('div');
            channelCard.className = 'channel-card';
            channelCard.style.animationDelay = `${0.1 * index}s`;
            
            channelCard.innerHTML = `
                <h4>${channel.name}</h4>
                <p>${channel.description}</p>
                <div class="channel-budget">Budget allocation: $${channel.budget}</div>
            `;
            
            channelsContainer.appendChild(channelCard);
        });
        
        // If no channels, show a message
        if (channels.length === 0) {
            channelsContainer.innerHTML = '<p class="no-channels">No specific channels recommended.</p>';
        }
    }
    
    // PDF generation
    savePdfButton.addEventListener('click', () => {
        window.print();
        
        // Track PDF saving
        trackEvent('pdf_saved');
    });
    
    // Email results again
    // Inside the email-results click handler:

    emailResultsButton.addEventListener('click', async () => {
        const businessEmail = document.getElementById('business-email').value;
        
        if (!businessEmail) {
            alert('Please enter your email address in the form above to receive 7 days of daily recommendations.');
            document.getElementById('business-email').focus();
            return;
        }
        
        try {
            const response = await fetch('/api/email-results', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: businessEmail,
                    recommendation_id: window.currentRecommendationId || null
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            alert('Recommendations sent! You will receive fresh marketing strategies every morning for the next 7 days.');
            
            // Track email sending
            trackEvent('results_emailed');
        } catch (error) {
            console.error('Error sending email:', error);
            alert('Sorry, we encountered an error sending the email.');
        }
    });
    
    // Simple analytics tracking function
    function trackEvent(eventName, properties = {}) {
        console.log(`[Analytics] ${eventName}`, properties);
        
        // Send to server for tracking
        fetch('/api/track-event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event: eventName,
                properties
            })
        }).catch(err => console.error('Analytics error:', err));
    }
});