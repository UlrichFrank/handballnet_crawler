// Debug Theme Function
export function debugTheme() {
  console.log('=== THEME DEBUG ===');
  
  const html = document.documentElement;
  console.log('1. HTML classes:', html.className);
  console.log('2. localStorage theme:', localStorage.getItem('theme'));
  
  // Try to add dark class
  console.log('3. Trying to add dark class...');
  html.classList.add('dark');
  console.log('4. After adding: HTML classes =', html.className);
  
  // Check if it works
  setTimeout(() => {
    const bodyBg = window.getComputedStyle(document.body).backgroundColor;
    console.log('5. Body background after 100ms:', bodyBg);
  }, 100);
  
  // Check CSS is loaded
  console.log('6. Checking CSS...');
  const sheets = document.styleSheets;
  console.log('   Stylesheets loaded:', sheets.length);
  for (let i = 0; i < Math.min(sheets.length, 3); i++) {
    try {
      console.log(`   Sheet ${i}:`, sheets[i].href || 'inline');
    } catch (e) {
      console.log(`   Sheet ${i}: (CORS restricted)`);
    }
  }
}

// Expose to window for console access
if (typeof window !== 'undefined') {
  (window as any).debugTheme = debugTheme;
}
