document.addEventListener('DOMContentLoaded', async () => {
    // DOM Elements
    const lastUpdatedEl = document.getElementById('last-updated');
    const currentCpiEl = document.getElementById('current-cpi');
    const cpiChangeEl = document.getElementById('cpi-change');
    const momInflationEl = document.getElementById('mom-inflation');
    const momChangeEl = document.getElementById('mom-change');
    const yoyInflationEl = document.getElementById('yoy-inflation');
    const daysTrackedEl = document.getElementById('days-tracked');
    const categoryGridEl = document.getElementById('category-grid');
    const timeBtns = document.querySelectorAll('.time-btn');

    let fullHistory = [];
    let chartInstance = null;

    // Fetch Data
    try {
        // Fetching directly from the live GitHub repository so the webpage works anywhere!
        const response = await fetch('https://raw.githubusercontent.com/thomasriveros/robust-cpi-bolivia/main/fidalga_tracker_results.json');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();

        if (!data.history || data.history.length === 0) {
            throw new Error("No history data found.");
        }

        fullHistory = data.history.map(item => ({
            ...item,
            dateObj: new Date(item.date)
        }));

        initializeDashboard(fullHistory);

    } catch (error) {
        console.error("Error loading data:", error);
        lastUpdatedEl.innerHTML = `Error: ${error.message}<br><small>Make sure python server is running at project root</small>`;
        lastUpdatedEl.style.color = "var(--danger)";
        lastUpdatedEl.style.background = "rgba(239, 68, 68, 0.1)";
        lastUpdatedEl.style.height = "auto";
    }

    function initializeDashboard(history) {
        // 1. Summary Metrics
        const latest = history[history.length - 1];
        const prevDay = history.length > 1 ? history[history.length - 2] : latest;
        const lastMonth = history.length > 30 ? history[history.length - 31] : history[0]; // approx
        const lastYear = history.length > 365 ? history[history.length - 366] : history[0];

        // Last Updated
        lastUpdatedEl.textContent = `Updated: ${latest.date}`;

        // Current CPI
        const currentVal = latest.cpi;
        currentCpiEl.textContent = currentVal.toFixed(2);

        // Daily Change
        const dayChange = ((currentVal - prevDay.cpi) / prevDay.cpi) * 100;
        renderChange(cpiChangeEl, dayChange, "daily");

        // MoM Inflation
        const momVal = ((currentVal - lastMonth.cpi) / lastMonth.cpi) * 100;
        momInflationEl.textContent = `${momVal.toFixed(2)}%`;
        momChangeEl.textContent = "Last 30 days";

        // YoY Inflation (Estimated if < 1 year data)
        const yoyVal = ((currentVal - lastYear.cpi) / lastYear.cpi) * 100;
        yoyInflationEl.textContent = `${yoyVal.toFixed(2)}%`;

        // Days Tracked
        daysTrackedEl.textContent = history.length;

        // 2. Chart
        initChart(history);

        // 3. Category Breakdown
        renderCategories(latest, prevDay);

        // 4. Event Listeners
        timeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // remove active class
                timeBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const range = btn.dataset.range;
                filterChart(range);
            });
        });
    }

    function renderChange(el, value, label) {
        const sign = value > 0 ? "+" : "";
        el.textContent = `${sign}${value.toFixed(2)}% ${label}`;
        el.className = "metric-change"; // reset
        if (value > 0) el.classList.add('change-positive');
        if (value < 0) el.classList.add('change-negative');
    }

    function initChart(data) {
        const ctx = document.getElementById('mainChart').getContext('2d');

        // Prepare Data
        const labels = data.map(d => d.date);
        const values = data.map(d => d.cpi);

        // Gradient Fill
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(79, 70, 229, 0.5)'); // Accent color high opacity
        gradient.addColorStop(1, 'rgba(79, 70, 229, 0.0)');

        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'CPI',
                    data: values,
                    borderColor: '#4f46e5',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    pointRadius: 0, // hide points by default for clean look
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.1 // slight curve
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 17, 26, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#a0a4b0',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: false,
                        callbacks: {
                            label: function (context) {
                                return `CPI: ${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            displayFormats: {
                                month: 'MMM yyyy'
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#a0a4b0'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#a0a4b0'
                        }
                    }
                }
            }
        });
    }

    function filterChart(range) {
        if (!chartInstance) return;

        const now = new Date();
        let cutoff = new Date(fullHistory[0].dateObj); // default to start

        if (range === '1y') {
            cutoff.setFullYear(now.getFullYear() - 1);
        } else if (range === '6m') {
            cutoff.setMonth(now.getMonth() - 6);
        } else if (range === '3m') {
            cutoff.setMonth(now.getMonth() - 3);
        }

        const filteredData = fullHistory.filter(d => d.dateObj >= cutoff);

        chartInstance.data.labels = filteredData.map(d => d.date);
        chartInstance.data.datasets[0].data = filteredData.map(d => d.cpi);
        chartInstance.update();
    }

    function renderCategories(latest, prev) {
        categoryGridEl.innerHTML = '';

        const subIndices = latest.sub_indices;
        const prevIndices = prev.sub_indices;

        // Sort by value (impact) or name? Let's sort by inflation (value desc)
        const sortedCats = Object.entries(subIndices).sort((a, b) => b[1] - a[1]);

        sortedCats.forEach(([catName, val]) => {
            const prevVal = prevIndices[catName] || val;
            const change = ((val - prevVal) / prevVal) * 100;

            const card = document.createElement('div');
            card.className = 'category-item';

            const sign = change > 0 ? "+" : "";
            const colorClass = change > 0 ? "change-positive" : (change < 0 ? "change-negative" : "");

            card.innerHTML = `
                <div class="cat-name">${catName}</div>
                <div class="cat-val">${val.toFixed(2)}</div>
                <div class="cat-change ${colorClass}">${sign}${change.toFixed(2)}%</div>
            `;

            categoryGridEl.appendChild(card);
        });
    }
});
