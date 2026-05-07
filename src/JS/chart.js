document.addEventListener("DOMContentLoaded", async () => {
    const dataScript = document.getElementById("impact-data");
    const canvas = document.getElementById("graph");

    if (!dataScript || !canvas) {
        return;
    }

    const impactData = JSON.parse(dataScript.textContent || "{}");
    console.log(impactData);

    const loadChartLibrary = () => {
        if (window.Chart) {
            return Promise.resolve(window.Chart);
        }

        return new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = "../node_modules/chart.js/dist/chart.umd.min.js";
            script.onload = () => resolve(window.Chart);
            script.onerror = () => reject(new Error("Failed to load Chart.js"));
            document.head.appendChild(script);
        });
    };

    const Chart = await loadChartLibrary();
    const labels = Object.keys(impactData).map((fileName) => fileName.replace(/\.toml$/i, ""));
    const revenueLoss = Object.values(impactData).map((item) => item.estimated_revenue_loss_eur ?? 0);

    const context = canvas.getContext("2d");

    if (!context) {
        return;
    }

    if (window.impactChart) {
        window.impactChart.destroy();
    }

    window.impactChart = new Chart(context, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Estimated Revenue Loss (EUR)",
                    data: revenueLoss,
                    backgroundColor: "rgba(245, 158, 11, 0.75)",
                    borderColor: "rgba(245, 158, 11, 1)",
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: "Estimated Revenue Loss by Incident",
                },
                legend: {
                    position: "top",
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const value = Number(context.raw || 0);
                            return ` ${context.dataset.label}: €${value.toLocaleString()}`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 0,
                    },
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "EUR",
                    },
                    ticks: {
                        callback: (value) => `€${Number(value).toLocaleString()}`,
                    },
                },
            },
        },
    });
});