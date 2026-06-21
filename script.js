// ==========================================
// 🔑 USDA CONFIGURATION
// ==========================================
// Get your key here: https://fdc.nal.usda.gov/api-key-signup.html
const API_KEY = 'sSajQcq8PYn8fEtxqRHkJizKnixZ2ixsTlNXh69W'; // Replace with your real key if DEMO hits limits
const BASE_URL = 'https://api.nal.usda.gov/fdc/v1/foods/search';

// DOM Elements
const appContainer = document.getElementById('appContainer');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const resultsGrid = document.getElementById('resultsGrid');
const loader = document.getElementById('loader');

// Event Listeners
searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') performSearch();
});

async function performSearch() {
    const query = searchInput.value.trim();
    if (!query) return;

    // 1. Trigger Animation (Move Search Bar Up)
    appContainer.classList.add('active');
    
    // 2. Clear previous results & show loader
    resultsGrid.innerHTML = '';
    loader.style.display = 'block';

    // 3. API Call
    try {
        const response = await fetch(`${BASE_URL}?api_key=${API_KEY}&query=${encodeURIComponent(query)}&pageSize=12&dataType=Foundation,SR Legacy`);
        
        if (!response.ok) throw new Error('USDA API Error');
        
        const data = await response.json();
        renderResults(data.foods);

    } catch (error) {
        console.error(error);
        resultsGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; color: #888;">
                Error fetching data. <br>Please check your API Key or try again.
            </div>
        `;
    } finally {
        loader.style.display = 'none';
    }
}

function renderResults(foods) {
    if (!foods || foods.length === 0) {
        resultsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: #888;">No results found.</div>`;
        return;
    }

    const html = foods.map(food => {
        // USDA Nutrient IDs: 1008=Cals, 1003=Protein, 1004=Fat, 1005=Carbs
        const getNutrient = (id) => {
            const n = food.foodNutrients.find(x => x.nutrientId === id);
            return n ? Math.round(n.value) : 0;
        };

        const calories = getNutrient(1008);
        const protein = getNutrient(1003);
        const fat = getNutrient(1004);
        const carbs = getNutrient(1005);

        return `
            <article class="food-card">
                <div class="food-name">${food.description.toLowerCase()}</div>
                <div class="divider"></div>
                <div class="macros-list">
                    <div class="macro-item">
                        <span class="macro-label">Energy</span>
                        <span class="macro-value">${calories} kcal</span>
                    </div>
                    <div class="macro-item">
                        <span class="macro-label">Protein</span>
                        <span class="macro-value">${protein}g</span>
                    </div>
                    <div class="macro-item">
                        <span class="macro-label">Carbs</span>
                        <span class="macro-value">${carbs}g</span>
                    </div>
                    <div class="macro-item">
                        <span class="macro-label">Fat</span>
                        <span class="macro-value">${fat}g</span>
                    </div>
                </div>
            </article>
        `;
    }).join('');

    resultsGrid.innerHTML = html;
}