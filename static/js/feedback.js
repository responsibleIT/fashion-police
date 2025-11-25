// Feedback page JavaScript
async function submitFeedback(style) {
    try {
        const response = await fetch('/submit_feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ style: style })
        });

        if (response.ok) {
            const data = await response.json();
            
            // Show success message
            const successMsg = document.getElementById('success-message');
            successMsg.insertAdjacentText("afterBegin", `${style}`);
            successMsg.style.display = 'block';
            
            // Disable all buttons
            document.querySelectorAll('.style-button').forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.5';
                btn.style.cursor = 'not-allowed';
            });
            
            // Scroll to top to show success message
            setTimeout(() => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }, 100);
        } else {
            alert('Failed to save feedback');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
