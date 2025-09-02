// Theme testing utility
// Run this in the browser console to test all themes

const themes = ['night', 'morning', 'afternoon', 'sunset', 'minimalist', 'business'];
let currentIndex = 0;

function testNextTheme() {
  if (currentIndex >= themes.length) {
    console.log('✅ All themes tested!');
    return;
  }
  
  const theme = themes[currentIndex];
  console.log(`🎨 Testing theme: ${theme}`);
  
  // Remove all skin classes
  document.body.className = document.body.className.replace(/\bskin-\w+\b/g, '');
  
  // Add new skin class
  document.body.classList.add(`skin-${theme}`);
  
  // Log any issues
  setTimeout(() => {
    const issues = [];
    
    // Check for unreadable text
    const elements = document.querySelectorAll('*');
    elements.forEach(el => {
      const style = window.getComputedStyle(el);
      const color = style.color;
      const bgColor = style.backgroundColor;
      
      // Check if text is too light on light background
      if (theme === 'minimalist' || theme === 'business') {
        if (color.includes('255, 255, 255') && bgColor.includes('255, 255, 255')) {
          issues.push(`White text on white background: ${el.className}`);
        }
      }
    });
    
    if (issues.length > 0) {
      console.warn(`⚠️ Issues in ${theme}:`, issues);
    } else {
      console.log(`✅ ${theme} looks good!`);
    }
    
    currentIndex++;
    setTimeout(testNextTheme, 2000);
  }, 1000);
}

// Start testing
console.log('🚀 Starting theme test...');
testNextTheme();