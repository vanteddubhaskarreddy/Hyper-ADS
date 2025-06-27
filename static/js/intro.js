/**
 * Hyper ADS - Agent Introduction and Modal Functionality
 * Handles the intro modal that explains AI agents
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const modal = document.getElementById('agent-intro-modal');
    const closeBtn = document.querySelector('.close-modal');
    const startBtn = document.getElementById('start-experience');
    const reopenBtn = document.getElementById('reopen-intro');
    const floatingBtn = document.getElementById('show-agent-info');
    const privacyLink = document.getElementById('privacy-policy-link');
    const termsLink = document.getElementById('terms-service-link');
    const policyModal = document.getElementById('policy-modal');
    const policyContent = document.getElementById('policy-content');
    const policyClose = document.querySelector('#policy-modal .close-modal');
    
    // Show the modal on page load (with slight delay for better UX)
    setTimeout(() => {
        modal.style.display = 'block';
    }, 800);
    
    // Close modal when clicking the X button
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    // Close modal when clicking the Start button
    startBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    // Reopen modal from footer link
    reopenBtn.addEventListener('click', () => {
        modal.style.display = 'block';
    });
    
    // Reopen modal from floating button
    floatingBtn.addEventListener('click', () => {
        modal.style.display = 'block';
    });
    
    // Close when clicking outside the modal content
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
        if (event.target === policyModal) {
            policyModal.style.display = 'none';
        }
    });
    
    // Close on escape key
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
            }
            if (policyModal.style.display === 'block') {
                policyModal.style.display = 'none';
            }
        }
    });
    
    // Handle Privacy Policy click
    privacyLink.addEventListener('click', (event) => {
        event.preventDefault();
        policyContent.innerHTML = `
            <h2>Privacy Policy <i class="fas fa-shield-alt"></i></h2>
            <div class="friendly-policy">
                <p><strong>In human-friendly terms:</strong></p>
                <div class="policy-points">
                    <div class="policy-point">
                        <i class="fas fa-cookie-bite"></i>
                        <div>
                            <h4>Cookies & Data</h4>
                            <p>We collect just enough data to make your advertising recommendations awesome, not to stalk you around the internet. Our AI agents are nosy about local events and weather, not your personal life.</p>
                        </div>
                    </div>
                    
                    <div class="policy-point">
                        <i class="fas fa-envelope"></i>
                        <div>
                            <h4>Emails</h4>
                            <p>If you give us your email, we'll send you helpful recommendations for 7 days. After that, we'll stop. No spam, no "extended car warranties" - just useful marketing advice.</p>
                        </div>
                    </div>
                    
                    <div class="policy-point">
                        <i class="fas fa-user-secret"></i>
                        <div>
                            <h4>Your Secrets</h4>
                            <p>Your business details are kept between you, our AI agents, and the database. We don't sell your data or share it with third parties (our AI agents are very possessive).</p>
                        </div>
                    </div>
                </div>
                
                <div class="policy-fun-fact">
                    <i class="fas fa-lightbulb"></i>
                    <p>Fun fact: Our privacy policy is shorter than the ingredient list on a candy bar, and probably better for you too!</p>
                </div>
                
                <button class="primary-button close-policy">Got It!</button>
            </div>
        `;
        
        // Add event listener for the Got It button
        setTimeout(() => {
            document.querySelector('.close-policy').addEventListener('click', () => {
                policyModal.style.display = 'none';
            });
        }, 100);
        
        policyModal.style.display = 'block';
    });
    
    // Handle Terms of Service click
    termsLink.addEventListener('click', (event) => {
        event.preventDefault();
        policyContent.innerHTML = `
            <h2>Terms of Service <i class="fas fa-file-contract"></i></h2>
            <div class="friendly-policy">
                <p><strong>The important stuff, without the legalese:</strong></p>
                <div class="policy-points">
                    <div class="policy-point">
                        <i class="fas fa-magic"></i>
                        <div>
                            <h4>Not Actually Magic</h4>
                            <p>Our AI agents are smart, but they're not wizards. The recommendations are suggestions, not guarantees. Results may vary, and we can't promise you'll become a marketing legend overnight.</p>
                        </div>
                    </div>
                    
                    <div class="policy-point">
                        <i class="fas fa-handshake"></i>
                        <div>
                            <h4>Be Nice</h4>
                            <p>Please use our service for legitimate business purposes, not for planning world domination or selling questionable items. Our AI agents are impressionable!</p>
                        </div>
                    </div>
                    
                    <div class="policy-point">
                        <i class="fas fa-heart"></i>
                        <div>
                            <h4>Relationship Status</h4>
                            <p>Using Hyper ADS doesn't mean we're in a legally binding relationship, but we do hope it's the start of a beautiful friendship!</p>
                        </div>
                    </div>
                </div>
                
                <div class="policy-fun-fact">
                    <i class="fas fa-coffee"></i>
                    <p>Fun fact: This terms of service was written by humans fueled by coffee, not by lawyers fueled by billable hours.</p>
                </div>
                
                <button class="primary-button close-policy">I Agree!</button>
            </div>
        `;
        
        // Add event listener for the I Agree button
        setTimeout(() => {
            document.querySelector('.close-policy').addEventListener('click', () => {
                policyModal.style.display = 'none';
            });
        }, 100);
        
        policyModal.style.display = 'block';
    });
    
    // Close policy modal with X button
    if (policyClose) {
        policyClose.addEventListener('click', () => {
            policyModal.style.display = 'none';
        });
    }
});