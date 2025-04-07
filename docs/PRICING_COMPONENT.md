# Ultra Pricing Component

This document explains how to view and test the new pricing component with the feather icon.

## Current Setup

We've set up a dedicated test page that shows the pricing component in isolation. This helps ensure the component works correctly before integrating it into the main application.

## Viewing the Test Page

1. The development server is running on http://localhost:3000
2. Open this URL in your browser to see the pricing display test page
3. You should see three examples of the pricing component:
   - Basic: Shows pricing for a single, low-cost model
   - Standard: Shows pricing for two models
   - Premium: Shows pricing for multiple models including premium options with the feather icon

## Features of the Pricing Component

- **Dynamic Cost Calculation**: Automatically calculates costs based on selected models
- **Feather Icon**: Shows a gold feather icon for premium model selections
- **Animation**: The feather icon animates when premium models are selected
- **Token Estimates**: Shows estimated costs based on input and output tokens
- **Responsive Design**: Works well on all screen sizes

## Returning to the Main Application

Once you've verified the pricing component works correctly, you can return to the main application by:

1. Stop the current development server (Ctrl+C)
2. Edit the `index.html` file to change back to the main application:
   ```html
   <script type="module" src="/src/main.jsx"></script>
   ```
3. Restart the development server with `npm run dev`

## Troubleshooting

If you encounter any issues:

1. Check the browser console for errors
2. Verify that all required packages are installed
3. Clear your browser cache or try a private/incognito window 