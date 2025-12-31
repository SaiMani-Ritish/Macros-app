# Macro Explorer
### Using USDA API

A modern, minimalist web application that allows users to search for nutritional information using the official USDA FoodData Central API. 

The interface features a fluid "search-first" design: the search bar starts at the center of the screen and animates to the top upon interaction, revealing a grid of nutritional cards.

Built with pure HTML, CSS, and Vanilla JavaScript. No framework installation required.

## 📂 Project Structure

```text
/usda-macro-explorer
  ├── index.html      # The main HTML structure
  ├── style.css       # Styling and animations
  ├── script.js       # API logic and DOM manipulation
  └── README.md       # This file

```

##  How to Run

1. **Download the files:** Ensure `index.html`, `style.css`, and `script.js` are in the same folder.
2. **Get an API Key:**
* Go to the [USDA API Key Signup](https://fdc.nal.usda.gov/api-key-signup.html).
* Fill out the form to get your free API key immediately.


3. **Configure the App:**
* Open `script.js` in any text editor (Notepad, VS Code, etc.).
* Find the line at the top: `const API_KEY = 'DEMO_KEY';`
* Replace `'DEMO_KEY'` with the key you received in your email.


4. **Launch:**
* Double-click `index.html` to open it in your browser.



## Configuration

### Switching Data Types

By default, the app filters for "Foundation" and "SR Legacy" foods to ensure high-quality raw ingredient data. You can change this in `script.js` inside the `fetch` URL:

```javascript
// Current:
&dataType=Foundation,SR Legacy

// For Branded Foods (packaged goods):
&dataType=Branded

```

## Customization

You can change the color scheme, by opening `style.css` and modifying the CSS variables at the top:

```css
:root {
    --bg: #000000;       /* Background color */
    --card-bg: #111111;  /* Card background */
    --text-main: #ffffff; /* Main text color */
    --accent: #ffffff;    /* Accent color */
}

```

## License

This project is open source and available for personal or educational use.
