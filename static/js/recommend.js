/* ==========================================================================
   SchemeAI - AI Recommendation Questionnaire Wizard
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    let currentStep = 1;
    const totalSteps = 3;

    const form = document.getElementById("recommendation-wizard-form");
    const nextBtns = document.querySelectorAll(".next-step");
    const prevBtns = document.querySelectorAll(".prev-step");
    const stepDots = document.querySelectorAll(".step-dot");
    const formSteps = document.querySelectorAll(".form-step");
    const resultsContainer = document.getElementById("recommendation-results");
    const formContainer = document.getElementById("wizard-form-container");

    // Initialize dots
    updateStepsUI();

    nextBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            if (validateStep(currentStep)) {
                if (currentStep < totalSteps) {
                    currentStep++;
                    updateStepsUI();
                }
            }
        });
    });

    prevBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            if (currentStep > 1) {
                currentStep--;
                updateStepsUI();
            }
        });
    });

    form?.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        if (!validateStep(currentStep)) return;

        // Show spinner / loader state
        formContainer.style.display = "none";
        resultsContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h4 class="mt-4">Analyzing Your Profile...</h4>
                <p class="text-secondary">Our machine learning model is checking your criteria eligibility scores.</p>
            </div>
        `;
        resultsContainer.style.display = "block";

        const formData = new FormData(form);
        const jsonData = {};
        formData.forEach((value, key) => {
            jsonData[key] = value;
        });

        try {
            const response = await fetch("/api/recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(jsonData)
            });
            const data = await response.json();

            if (response.ok) {
                renderRecommendations(data.recommendations, jsonData);
            } else {
                showToast(data.message || "Failed to process recommendation.", "danger");
                formContainer.style.display = "block";
                resultsContainer.style.display = "none";
            }
        } catch (error) {
            console.error("Recommendation submission error:", error);
            showToast("Failed to connect to recommendation server.", "danger");
            formContainer.style.display = "block";
            resultsContainer.style.display = "none";
        }
    });

    function updateStepsUI() {
        formSteps.forEach((step, idx) => {
            if (idx + 1 === currentStep) {
                step.classList.add("active");
            } else {
                step.classList.remove("active");
            }
        });

        stepDots.forEach((dot, idx) => {
            const stepNum = idx + 1;
            dot.classList.remove("active", "completed");
            if (stepNum === currentStep) {
                dot.classList.add("active");
            } else if (stepNum < currentStep) {
                dot.classList.add("completed");
                dot.innerHTML = '<i class="fas fa-check"></i>';
            } else {
                dot.innerText = stepNum;
            }
        });
    }

    function validateStep(step) {
        let valid = true;
        const currentStepEl = document.querySelector(`.form-step[data-step="${step}"]`);
        const requiredInputs = currentStepEl.querySelectorAll("[required]");

        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                valid = false;
                input.classList.add("is-invalid");
                // Listen to clear error on input
                input.addEventListener("input", () => {
                    input.classList.remove("is-invalid");
                }, { once: true });
            } else {
                input.classList.remove("is-invalid");
            }
        });

        if (!valid) {
            showToast("Please fill in all mandatory fields before proceeding.", "warning");
        }
        return valid;
    }

    function renderRecommendations(recs, userData) {
        if (!recs || recs.length === 0) {
            resultsContainer.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                    <h3>No Schemes Found</h3>
                    <p class="text-secondary">Based on our rules and ML threshold, we couldn't match any schemes directly to your profile inputs.</p>
                    <button class="btn btn-primary-custom mt-3" onclick="window.location.reload()">Try Again</button>
                </div>
            `;
            return;
        }

        let html = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h3>Your Personalized Scheme Recommendations</h3>
                <div>
                    <button class="btn btn-outline-custom me-2" id="download-pdf-report"><i class="fas fa-file-pdf me-2"></i>Download PDF</button>
                    <button class="btn btn-primary-custom" onclick="window.location.reload()"><i class="fas fa-redo me-2"></i>New Test</button>
                </div>
            </div>
            
            <div id="pdf-report-content">
                <div class="card card-custom mb-4 bg-light border-0">
                    <h5>Profile Summary Evaluated:</h5>
                    <div class="row text-secondary g-2 mt-2">
                        <div class="col-md-3"><strong>Name:</strong> ${userData.name}</div>
                        <div class="col-md-3"><strong>Age:</strong> ${userData.age} Yrs</div>
                        <div class="col-md-3"><strong>Gender:</strong> ${userData.gender}</div>
                        <div class="col-md-3"><strong>Annual Income:</strong> ₹${userData.income}</div>
                        <div class="col-md-3"><strong>Occupation:</strong> ${userData.occupation}</div>
                        <div class="col-md-3"><strong>State:</strong> ${userData.state}</div>
                        <div class="col-md-3"><strong>Disability:</strong> ${userData.disability_status}</div>
                        <div class="col-md-3"><strong>BPL Status:</strong> ${userData.bpl_status}</div>
                    </div>
                </div>
                
                <div class="row g-4">
        `;

        recs.forEach(rec => {
            const confColor = rec.confidence >= 80 ? 'text-success' : (rec.confidence >= 50 ? 'text-warning' : 'text-danger');
            
            html += `
                <div class="col-12">
                    <div class="card card-custom">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-3">
                                <div>
                                    <span class="badge bg-primary mb-2">${rec.category}</span>
                                    <h4 class="card-title">${rec.name}</h4>
                                    <p class="text-muted small mb-0">${rec.department}</p>
                                </div>
                                <div class="text-end">
                                    <div class="h5 mb-0 ${confColor} font-weight-bold">${rec.confidence}%</div>
                                    <small class="text-secondary">AI Confidence Score</small>
                                </div>
                            </div>
                            
                            <p class="card-text">${rec.description}</p>
                            
                            <div class="row mt-4 mb-4 g-3">
                                <div class="col-md-6">
                                    <div class="p-3 bg-light rounded" style="height:100%">
                                        <strong><i class="fas fa-check-circle text-success me-2"></i>Eligible Benefits:</strong>
                                        <p class="mt-2 mb-0 text-secondary">${rec.benefits}</p>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="p-3 bg-light rounded" style="height:100%">
                                        <strong><i class="fas fa-file-alt text-primary me-2"></i>Required Documents:</strong>
                                        <p class="mt-2 mb-0 text-secondary">${rec.required_documents}</p>
                                    </div>
                                </div>
                            </div>

                            <div class="alert alert-info border-0 bg-light-blue text-dark py-2 mb-4">
                                <strong><i class="fas fa-lightbulb text-warning me-2"></i>AI Match Reason:</strong> ${rec.reason}
                            </div>

                            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mt-4 pt-3 border-top">
                                <button class="btn btn-outline-custom bookmark-btn" data-scheme-id="${rec.id}">
                                    <i class="far fa-bookmark me-2"></i>Bookmark
                                </button>
                                <a href="${rec.official_link}" target="_blank" class="btn btn-primary-custom">
                                    <i class="fas fa-external-link-alt me-2"></i>Apply Via Official Portal
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        resultsContainer.innerHTML = html;

        // Bind event listeners to new elements in container
        // 1. Bookmarks setup inside recommendations list
        setupBookmarks();

        // 2. PDF Download
        document.getElementById("download-pdf-report")?.addEventListener("click", () => {
            downloadPDFReport();
        });
    }

    function downloadPDFReport() {
        const element = document.getElementById("pdf-report-content");
        if (!element) return;
        
        // Use html2pdf if loaded, otherwise fallback to window.print()
        if (window.html2pdf) {
            const opt = {
                margin:       10,
                filename:     'SchemeAI-Recommendation-Report.pdf',
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2 },
                jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(element).save();
        } else {
            // Temporary styles to only print report content
            const originalContent = document.body.innerHTML;
            const printContent = element.innerHTML;
            
            document.body.innerHTML = `
                <div style="padding: 30px; font-family: 'Poppins', sans-serif;">
                    <h2 style="color:#4A90E2; border-bottom: 2px solid #4A90E2; padding-bottom: 10px; margin-bottom: 20px;">SchemeAI Recommendation Report</h2>
                    ${printContent}
                </div>
            `;
            window.print();
            document.body.innerHTML = originalContent;
            window.location.reload(); // reload to rebind JS events
        }
    }
});
