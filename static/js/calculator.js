/* ==========================================================================
   SchemeAI - Benefits Calculator Systems (dynamic math and Chart.js)
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // Initialize Chart instances dictionary to prevent memory leakage
    window.calcCharts = {};

    // 1. Setup Calculator Selectors
    const calcTypeSelect = document.getElementById("calc-type");
    const calcSections = document.querySelectorAll(".calc-section");

    calcTypeSelect?.addEventListener("change", (e) => {
        const selected = e.target.value;
        calcSections.forEach(section => {
            if (section.id === `${selected}-calc`) {
                section.style.display = "block";
            } else {
                section.style.display = "none";
            }
        });
        // Clear previous calculations
        document.querySelectorAll(".calc-result-box").forEach(box => box.style.display = "none");
    });

    // 2. Scholarship Calculator
    const scholForm = document.getElementById("scholarship-form");
    scholForm?.addEventListener("submit", (e) => {
        e.preventDefault();
        calculateScholarship();
    });

    // 3. Pension Calculator
    const pensionForm = document.getElementById("pension-form");
    pensionForm?.addEventListener("submit", (e) => {
        e.preventDefault();
        calculatePension();
    });

    // 4. Subsidy Calculator
    const subsidyForm = document.getElementById("subsidy-form");
    subsidyForm?.addEventListener("submit", (e) => {
        e.preventDefault();
        calculateSubsidy();
    });

    // 5. Loan Calculator
    const loanForm = document.getElementById("loan-form");
    loanForm?.addEventListener("submit", (e) => {
        e.preventDefault();
        calculateLoan();
    });

    // 6. Housing Calculator
    const housingForm = document.getElementById("housing-form");
    housingForm?.addEventListener("submit", (e) => {
        e.preventDefault();
        calculateHousing();
    });
});

// Helper to destroy previous chart of same type
function refreshChart(chartId, config) {
    if (window.calcCharts[chartId]) {
        window.calcCharts[chartId].destroy();
    }
    const ctx = document.getElementById(chartId).getContext('2d');
    window.calcCharts[chartId] = new Chart(ctx, config);
}

// Calculations Logic
function calculateScholarship() {
    const income = parseFloat(document.getElementById("schol-income").value);
    const edu = document.getElementById("schol-edu").value;
    const cat = document.getElementById("schol-cat").value;

    let baseSchol = 0;
    let allowances = 0;

    // Logic based on education level
    if (edu === "Postgraduate") {
        baseSchol = 25000;
        allowances = 8000;
    } else if (edu === "Graduate") {
        baseSchol = 18000;
        allowances = 5000;
    } else if (edu === "12th Pass") {
        baseSchol = 12000;
        allowances = 3000;
    } else if (edu === "10th Pass") {
        baseSchol = 8000;
        allowances = 2000;
    } else {
        baseSchol = 4000;
        allowances = 1000;
    }

    // Reservation benefits
    if (cat === "SC" || cat === "ST") {
        baseSchol *= 1.3;
        allowances *= 1.2;
    } else if (cat === "OBC") {
        baseSchol *= 1.15;
    }

    // Income penalty
    if (income > 250000) {
        // ineligible
        showToast("Income exceeds scholarship limits! Under government rules, scholarships are capped under ₹2.5 Lakhs.", "warning");
        baseSchol = 0;
        allowances = 0;
    }

    const total = baseSchol + allowances;

    document.getElementById("schol-result-total").innerText = `₹${total.toFixed(0)}`;
    document.getElementById("schol-result-base").innerText = `₹${baseSchol.toFixed(0)}`;
    document.getElementById("schol-result-allowance").innerText = `₹${allowances.toFixed(0)}`;
    document.getElementById("scholarship-result").style.display = "block";

    if (total > 0) {
        refreshChart("scholChart", {
            type: 'bar',
            data: {
                labels: ['Base Reimbursement', 'Maintenance Allowance', 'Total Aid'],
                datasets: [{
                    label: 'Scholarship Breakdown (₹)',
                    data: [baseSchol, allowances, total],
                    backgroundColor: ['#4A90E2', '#FFD6E7', '#2E8B57'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });
    }
}

function calculatePension() {
    const age = parseInt(document.getElementById("pension-age").value);
    const contr = parseFloat(document.getElementById("pension-contribution").value);

    // APY guaranteed return ranges from ₹1000 to ₹5000 depending on investment size
    // Calculate total duration till age 60
    const yearsToContribute = 60 - age;
    const months = yearsToContribute * 12;
    const totalContributed = contr * months;

    // Model exponential interest matching APY scales
    let pensionEstimate = 1000;
    if (contr >= 250) pensionEstimate = 5000;
    else if (contr >= 200) pensionEstimate = 4000;
    else if (contr >= 150) pensionEstimate = 3000;
    else if (contr >= 100) pensionEstimate = 2000;

    // Apply scaling factor based on entry age (older entries need larger pools)
    const totalMaturityPool = totalContributed * (3.5 - (age / 35.0));

    document.getElementById("pension-result-monthly").innerText = `₹${pensionEstimate} / month`;
    document.getElementById("pension-result-contrib").innerText = `₹${totalContributed.toFixed(0)}`;
    document.getElementById("pension-result-pool").innerText = `₹${totalMaturityPool.toFixed(0)}`;
    document.getElementById("pension-result").style.display = "block";

    refreshChart("pensionChart", {
        type: 'pie',
        data: {
            labels: ['Total Contribution Paid', 'Estimated Accrued Interest'],
            datasets: [{
                data: [totalContributed, Math.max(0, totalMaturityPool - totalContributed)],
                backgroundColor: ['#FFD6E7', '#4A90E2']
            }]
        },
        options: { responsive: true }
    });
}

function calculateSubsidy() {
    const cost = parseFloat(document.getElementById("subsidy-cost").value);
    const sector = document.getElementById("subsidy-sector").value;
    const cat = document.getElementById("subsidy-cat").value;

    let subsidyPercent = 0.20; // baseline 20%
    if (sector === "Agriculture") subsidyPercent = 0.50; // 50% for agri
    else if (sector === "Housing") subsidyPercent = 0.35; // 35% for houses

    if (cat === "SC" || cat === "ST") {
        subsidyPercent += 0.10; // extra 10%
    } else if (cat === "OBC") {
        subsidyPercent += 0.05;
    }

    // Limit maximum subsidy payouts
    let maxSubsidy = 150000;
    if (sector === "Housing") maxSubsidy = 267000;
    if (sector === "Business") maxSubsidy = 300000;

    let subsidyAmount = cost * subsidyPercent;
    if (subsidyAmount > maxSubsidy) {
        subsidyAmount = maxSubsidy;
    }

    const applicantAmount = cost - subsidyAmount;

    document.getElementById("subsidy-result-amount").innerText = `₹${subsidyAmount.toFixed(0)}`;
    document.getElementById("subsidy-result-percent").innerText = `${(subsidyAmount / cost * 100).toFixed(1)}%`;
    document.getElementById("subsidy-result-own").innerText = `₹${applicantAmount.toFixed(0)}`;
    document.getElementById("subsidy-result").style.display = "block";

    refreshChart("subsidyChart", {
        type: 'doughnut',
        data: {
            labels: ['Government Subsidy', 'Self Finance Required'],
            datasets: [{
                data: [subsidyAmount, applicantAmount],
                backgroundColor: ['#2E8B57', '#4A90E2']
            }]
        },
        options: { responsive: true }
    });
}

function calculateLoan() {
    const income = parseFloat(document.getElementById("loan-income").value);
    const emi = parseFloat(document.getElementById("loan-emi").value) || 0.0;
    const tenure = parseInt(document.getElementById("loan-tenure").value); // in years
    const rate = parseFloat(document.getElementById("loan-rate").value) / 12 / 100; // monthly rate

    // Standard FOIR (Fixed Obligation to Income Ratio) calculation (around 50%)
    const maxEMI = (income * 0.50) - emi;

    let eligibleLoan = 0;
    let monthlyInstallment = 0;

    if (maxEMI > 0) {
        const totalMonths = tenure * 12;
        // PV = PMT * [1 - (1+r)^-n] / r
        eligibleLoan = maxEMI * (1 - Math.pow(1 + rate, -totalMonths)) / rate;
        monthlyInstallment = maxEMI;
    }

    if (eligibleLoan < 0) eligibleLoan = 0;

    document.getElementById("loan-result-eligible").innerText = `₹${eligibleLoan.toFixed(0)}`;
    document.getElementById("loan-result-emi").innerText = `₹${monthlyInstallment.toFixed(0)}`;
    document.getElementById("loan-result").style.display = "block";

    if (eligibleLoan > 0) {
        const totalInterest = (monthlyInstallment * tenure * 12) - eligibleLoan;
        refreshChart("loanChart", {
            type: 'bar',
            data: {
                labels: ['Principal Loan Amount', 'Interest Payable'],
                datasets: [{
                    label: 'Financial Distribution (₹)',
                    data: [eligibleLoan, totalInterest],
                    backgroundColor: ['#4A90E2', '#E74C3C'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });
    }
}

function calculateHousing() {
    const income = parseFloat(document.getElementById("house-income").value);
    const location = document.getElementById("house-location").value;
    const bpl = document.getElementById("house-bpl").value;

    let eligible = "Not Eligible";
    let grant = 0;

    if (bpl === "Yes" || income <= 300000) {
        eligible = "Eligible (EWS Category)";
        grant = location === "Rural" ? 120000 : 150000;
        // toilet allowance
        grant += 12000;
    } else if (income <= 600000) {
        eligible = "Eligible (LIG Category)";
        grant = 100000; // Credit Linked Subsidy Scheme standard
    } else if (income <= 1800000) {
        eligible = "Eligible (MIG Category)";
        grant = 80000; // Subsidy discount
    }

    document.getElementById("house-result-status").innerText = eligible;
    document.getElementById("house-result-grant").innerText = `₹${grant.toFixed(0)}`;
    document.getElementById("house-result").style.display = "block";

    if (grant > 0) {
        refreshChart("housingChart", {
            type: 'doughnut',
            data: {
                labels: ['Welfare Housing Grant', 'Applicant Loan Portion'],
                datasets: [{
                    data: [grant, Math.max(0, 1000000 - grant)],
                    backgroundColor: ['#2E8B57', '#F4B400']
                }]
            },
            options: { responsive: true }
        });
    }
}
