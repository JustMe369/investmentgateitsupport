// Matrix Animation
function initMatrix() {
    const canvas = document.getElementById('matrix');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Set canvas to full window size
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    resizeCanvas();
    
    // Characters - taken from the original Matrix
    const matrix = '01';
    const characters = matrix.split('');
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    
    // Set the width of each column to be 1 character
    const drops = [];
    for (let i = 0; i < columns; i++) {
        drops[i] = Math.random() * -100; // Start drops at random positions above the viewport
    }
    
    // Set the font of the canvas
    ctx.font = `${fontSize}px monospace`;
    
    // Drawing the characters
    function draw() {
        // Semi-transparent black background for the trail effect
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Set the color and drawing style for the characters
        ctx.fillStyle = '#0f0'; // Green text
        
        // Loop over each drop
        for (let i = 0; i < drops.length; i++) {
            // Pick a random character
            const text = characters[Math.floor(Math.random() * characters.length)];
            
            // Draw the character
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            
            // Reset the drop to the top after it has reached the bottom
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            
            // Move the drop down
            drops[i]++;
        }
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        const newWidth = window.innerWidth;
        const newHeight = window.innerHeight;
        
        // Only resize if dimensions actually changed
        if (canvas.width !== newWidth || canvas.height !== newHeight) {
            const oldDropsLength = drops.length;
            resizeCanvas();
            
            // Adjust drops array for new width
            const newColumns = Math.floor(canvas.width / fontSize);
            
            // Add or remove drops based on width change
            if (newColumns > oldDropsLength) {
                // Add new drops
                for (let i = oldDropsLength; i < newColumns; i++) {
                    drops[i] = Math.random() * -100;
                }
            } else {
                // Remove extra drops
                drops.length = newColumns;
            }
        }
    });
    
    // Animation loop
    setInterval(draw, 33);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initMatrix);
