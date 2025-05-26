#!/bin/bash

# Browser Cache Cleaner for UltrAI MVP Testing
# Specifically targets localStorage and cache for the MVP testing

echo "🧹 Clearing browser cache for UltrAI MVP testing..."

# Chrome - most likely browser
if [ -d "$HOME/Library/Application Support/Google/Chrome" ]; then
    echo "📍 Found Chrome - clearing cache..."
    
    # Kill Chrome processes if running
    pkill -x "Google Chrome" 2>/dev/null || true
    sleep 2
    
    # Clear Chrome cache and storage
    rm -rf "$HOME/Library/Application Support/Google/Chrome/Default/Local Storage"
    rm -rf "$HOME/Library/Application Support/Google/Chrome/Default/Session Storage" 
    rm -rf "$HOME/Library/Application Support/Google/Chrome/Default/GPUCache"
    rm -rf "$HOME/Library/Caches/Google/Chrome"
    
    echo "✅ Chrome cache cleared"
fi

# Safari
if [ -d "$HOME/Library/Safari" ]; then
    echo "📍 Found Safari - clearing cache..."
    
    # Kill Safari processes if running  
    pkill -x "Safari" 2>/dev/null || true
    sleep 2
    
    # Clear Safari cache and storage
    rm -rf "$HOME/Library/Safari/LocalStorage"
    rm -rf "$HOME/Library/Safari/Databases"
    rm -rf "$HOME/Library/Caches/com.apple.Safari"
    
    echo "✅ Safari cache cleared"
fi

# Firefox
if [ -d "$HOME/Library/Application Support/Firefox" ]; then
    echo "📍 Found Firefox - clearing cache..."
    
    # Kill Firefox processes if running
    pkill -x "firefox" 2>/dev/null || true
    sleep 2
    
    # Clear Firefox cache (more complex, but this hits the main areas)
    rm -rf "$HOME/Library/Caches/Firefox"
    find "$HOME/Library/Application Support/Firefox/Profiles" -name "storage" -type d -exec rm -rf {} + 2>/dev/null || true
    
    echo "✅ Firefox cache cleared"
fi

# Edge
if [ -d "$HOME/Library/Application Support/Microsoft Edge" ]; then
    echo "📍 Found Edge - clearing cache..."
    
    # Kill Edge processes if running
    pkill -x "Microsoft Edge" 2>/dev/null || true
    sleep 2
    
    # Clear Edge cache and storage
    rm -rf "$HOME/Library/Application Support/Microsoft Edge/Default/Local Storage"
    rm -rf "$HOME/Library/Application Support/Microsoft Edge/Default/Session Storage"
    rm -rf "$HOME/Library/Caches/com.microsoft.edgemac"
    
    echo "✅ Edge cache cleared"
fi

echo ""
echo "🎯 Cache clearing complete!"
echo ""
echo "Next steps:"
echo "1. Open your browser"
echo "2. Go to your frontend URL"
echo "3. Hard refresh (Cmd+Shift+R or Cmd+F5)"
echo "4. Test step 4 for model loading"
echo ""
echo "If you still have issues, try opening in incognito/private mode first."