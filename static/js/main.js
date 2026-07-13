/* ==========================================================================
   SchemeAI - Main Interactive JS (Theme, Voice, Translate, Chatbot)
   ========================================================================== */

// Language Translations Dictionary
const translations = {
    en: {
        logo: "SchemeAI",
        tagline: "Find the Right Government Scheme in Seconds with AI",
        home: "Home",
        about: "About",
        schemes: "Schemes",
        aiRec: "AI Recommendation",
        eligibility: "Eligibility Checker",
        compare: "Compare Schemes",
        calc: "Benefits Calculator",
        docs: "Required Documents",
        dashboard: "Dashboard",
        faq: "FAQ",
        contact: "Contact",
        login: "Login",
        register: "Register",
        logout: "Logout",
        searchPlaceholder: "Search Government Schemes...",
        findBtn: "Find My Scheme",
        heroHead: "Find the Right Government Scheme in Seconds with AI",
        heroDesc: "Empowering citizens with personalized machine learning recommendations for central and state welfare benefits.",
        howItWorks: "How It Works",
        step1: "Enter Details",
        step1Desc: "Provide your age, income, and occupation profile.",
        step2: "AI Analysis",
        step2Desc: "Our model reviews and predicts eligibility scores.",
        step3: "Get Schemes",
        step3Desc: "Instantly view relevant, ranked government schemes.",
        step4: "Apply Online",
        step4Desc: "Direct links to official application portals.",
        popularSchemes: "Popular Welfare Schemes",
        statsSchemes: "Total Schemes",
        statsUsers: "Users Helped",
        statsCat: "Categories",
        statsStates: "States Covered",
        chatbotGreeting: "Hi! How can I assist you with schemes today?",
    },
    hi: {
        logo: "योजनाAI",
        tagline: "एआई के साथ सेकंडों में सही सरकारी योजना खोजें",
        home: "मुख्य पृष्ठ",
        about: "हमारे बारे में",
        schemes: "योजनाएं",
        aiRec: "एआई सिफारिश",
        eligibility: "पात्रता जाँचकर्ता",
        compare: "योजनाओं की तुलना",
        calc: "लाभ कैलकुलेटर",
        docs: "आवश्यक दस्तावेज",
        dashboard: "डैशबोर्ड",
        faq: "अक्सर पूछे जाने वाले प्रश्न",
        contact: "संपर्क करें",
        login: "लॉगिन",
        register: "पंजीकरण",
        logout: "लॉगआउट",
        searchPlaceholder: "सरकारी योजनाएं खोजें...",
        findBtn: "मेरी योजना खोजें",
        heroHead: "एआई के साथ सेकंडों में सही सरकारी योजना खोजें",
        heroDesc: "नागरिकों को केंद्रीय और राज्य कल्याणकारी लाभों के लिए व्यक्तिगत मशीन लर्निंग सिफारिशों के साथ सशक्त बनाना।",
        howItWorks: "यह कैसे काम करता है",
        step1: "विवरण दर्ज करें",
        step1Desc: "अपनी आयु, आय और व्यवसाय प्रोफ़ाइल प्रदान करें।",
        step2: "एआई विश्लेषण",
        step2Desc: "हमारा मॉडल पात्रता स्कोर की समीक्षा और भविष्यवाणी करता है।",
        step3: "योजनाएं प्राप्त करें",
        step3Desc: "तुरंत प्रासंगिक, रैंक की गई सरकारी योजनाएं देखें।",
        step4: "ऑनलाइन आवेदन",
        step4Desc: "आधिकारिक आवेदन पोर्टलों के लिए सीधे लिंक।",
        popularSchemes: "लोकप्रिय कल्याणकारी योजनाएं",
        statsSchemes: "कुल योजनाएं",
        statsUsers: "मदद की गई उपयोगकर्ता",
        statsCat: "श्रेणियां",
        statsStates: "कवर किए गए राज्य",
        chatbotGreeting: "नमस्ते! आज मैं योजनाओं के संबंध में आपकी क्या सहायता कर सकता हूँ?",
    },
    mr: {
        logo: "योजनाAI",
        tagline: "एआय च्या मदतीने सेकंदात योग्य सरकारी योजना शोधा",
        home: "मुख्यपृष्ठ",
        about: "आमच्याबद्दल",
        schemes: "योजना",
        aiRec: "एआय शिफारस",
        eligibility: "पात्रता तपासक",
        compare: "योजनांची तुलना",
        calc: "लाभ कॅल्क्युलेटर",
        docs: "आवश्यक कागदपत्रे",
        dashboard: "डॅशबोर्ड",
        faq: "वारंवार विचारले जाणारे प्रश्न",
        contact: "संपर्क",
        login: "लॉगिन",
        register: "नोंदणी",
        logout: "लॉगआउट",
        searchPlaceholder: "सरकारी योजना शोधा...",
        findBtn: "माझी योजना शोधा",
        heroHead: "एआय च्या मदतीने सेकंदात योग्य सरकारी योजना शोधा",
        heroDesc: "नागरिकांना केंद्रीय आणि राज्य कल्याणकारी फायद्यांसाठी वैयक्तिकृत मशीन लर्निंग शिफारसींसह सक्षम करणे.",
        howItWorks: "हे कसे कार्य करते",
        step1: "माहिती भरा",
        step1Desc: "तुमचे वय, उत्पन्न आणि व्यवसाय प्रोफाइल प्रदान करा.",
        step2: "एआय विश्लेषण",
        step2Desc: "आमचे मॉडेल पात्रता गुण आणि शिफारसींचे पुनरावलोकन करते.",
        step3: "योजना मिळवा",
        step3Desc: "संबंधित, श्रेणीबद्ध सरकारी योजना त्वरित पहा.",
        step4: "ऑनलाईन अर्ज करा",
        step4Desc: "अधिकृत अर्ज पोर्टलचे थेट दुवे.",
        popularSchemes: "लोकप्रिय कल्याणकारी योजना",
        statsSchemes: "एकूण योजना",
        statsUsers: "मदत केलेले वापरकर्ते",
        statsCat: "श्रेण्या",
        statsStates: "कव्हर केलेले राज्य",
        chatbotGreeting: "नमस्कार! आज मी तुम्हाला योजना शोधण्यात कशी मदत करू?",
    }
};

// State Variables
let currentLanguage = localStorage.getItem("language") || "en";
let currentTheme = localStorage.getItem("theme") || "light";

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Theme & Language Selector
    applyTheme(currentTheme);
    applyLanguage(currentLanguage);

    const themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
        themeToggle.checked = currentTheme === "dark";
        themeToggle.addEventListener("change", (e) => {
            currentTheme = e.target.checked ? "dark" : "light";
            applyTheme(currentTheme);
        });
    }

    const langSelector = document.getElementById("language-select");
    if (langSelector) {
        langSelector.value = currentLanguage;
        langSelector.addEventListener("change", (e) => {
            currentLanguage = e.target.value;
            applyLanguage(currentLanguage);
        });
    }

    // 2. Sticky Navbar & Scroll Events
    const navbar = document.querySelector(".navbar-custom");
    const backToTopBtn = document.getElementById("back-to-top");

    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            navbar?.classList.add("scrolled");
        } else {
            navbar?.classList.remove("scrolled");
        }

        if (window.scrollY > 300) {
            backToTopBtn?.classList.add("visible");
        } else {
            backToTopBtn?.classList.remove("visible");
        }
    });

    backToTopBtn?.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    // 3. Voice Search Integration
    setupVoiceSearch();

    // 4. Chatbot Widget Events
    setupChatbot();
    
    // 5. Setup Bookmarks
    setupBookmarks();
});

// Theme Application Function
function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
}

// Language Application Function
function applyLanguage(lang) {
    localStorage.setItem("language", lang);
    const elementsToTranslate = document.querySelectorAll("[data-translate]");
    
    elementsToTranslate.forEach(element => {
        const key = element.getAttribute("data-translate");
        if (translations[lang] && translations[lang][key]) {
            if (element.tagName === "INPUT" && element.type === "text") {
                element.placeholder = translations[lang][key];
            } else {
                element.innerText = translations[lang][key];
            }
        }
    });
}

// Voice Search Implementation
function setupVoiceSearch() {
    const voiceBtns = document.querySelectorAll(".voice-search-btn");
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        voiceBtns.forEach(btn => btn.style.display = "none");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = currentLanguage === "hi" ? "hi-IN" : (currentLanguage === "mr" ? "mr-IN" : "en-IN");
    recognition.interimResults = false;

    voiceBtns.forEach(btn => {
        const targetInputId = btn.getAttribute("data-target");
        const targetInput = document.getElementById(targetInputId);

        if (!targetInput) return;

        btn.addEventListener("click", () => {
            btn.classList.add("listening");
            btn.innerHTML = '<i class="fas fa-microphone-alt"></i>';
            showToast("Listening...", "info");
            recognition.start();
        });

        recognition.onresult = (event) => {
            const resultText = event.results[0][0].transcript;
            targetInput.value = resultText;
            btn.classList.remove("listening");
            btn.innerHTML = '<i class="fas fa-microphone"></i>';
            showToast(`Searching for: "${resultText}"`, "success");
            // Auto submit form if wrapped inside one
            const parentForm = targetInput.closest("form");
            if (parentForm) parentForm.submit();
        };

        recognition.onerror = (e) => {
            console.error("Speech Recognition Error:", e);
            btn.classList.remove("listening");
            btn.innerHTML = '<i class="fas fa-microphone"></i>';
            showToast("Speech recognition failed. Try typing.", "warning");
        };

        recognition.onend = () => {
            btn.classList.remove("listening");
            btn.innerHTML = '<i class="fas fa-microphone"></i>';
        };
    });
}

// Chatbot UI Setup
function setupChatbot() {
    const toggler = document.getElementById("chatbot-toggle");
    const container = document.getElementById("chatbot-container");
    const closeBtn = document.getElementById("chatbot-close");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("chat-send");
    const chatBody = document.getElementById("chat-body");

    if (!toggler || !container || !chatInput || !sendBtn || !chatBody) return;

    toggler.addEventListener("click", () => {
        container.classList.toggle("active");
        if (container.classList.contains("active")) {
            chatInput.focus();
        }
    });

    closeBtn?.addEventListener("click", () => {
        container.classList.remove("active");
    });

    const handleChat = async () => {
        const query = chatInput.value.trim();
        if (!query) return;

        // Append user bubble
        appendChatBubble(query, "user");
        chatInput.value = "";

        // Append typing spinner indicator
        const typingId = "typing-" + Date.now();
        const typingBubble = document.createElement("div");
        typingBubble.id = typingId;
        typingBubble.classList.add("chat-bubble", "bot");
        typingBubble.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Typist...';
        chatBody.appendChild(typingBubble);
        chatBody.scrollTop = chatBody.scrollHeight;

        try {
            const response = await fetch("/api/chatbot", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query })
            });
            const data = await response.json();
            
            // Remove spinner and replace with real content
            const spinner = document.getElementById(typingId);
            if (spinner) spinner.remove();

            appendChatBubble(data.reply, "bot");
        } catch (error) {
            console.error("Chatbot response error:", error);
            const spinner = document.getElementById(typingId);
            if (spinner) spinner.remove();
            appendChatBubble("I am experiencing network difficulties. Please try again later.", "bot");
        }
    };

    sendBtn.addEventListener("click", handleChat);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleChat();
    });
}

function appendChatBubble(text, sender) {
    const chatBody = document.getElementById("chat-body");
    const bubble = document.createElement("div");
    bubble.classList.add("chat-bubble", sender);
    bubble.innerText = text;
    chatBody.appendChild(bubble);
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Bookmarks Utility
function setupBookmarks() {
    const bookmarkBtns = document.querySelectorAll(".bookmark-btn");
    
    bookmarkBtns.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const schemeId = btn.getAttribute("data-scheme-id");
            if (!schemeId) return;

            try {
                const response = await fetch(`/api/bookmark/${schemeId}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" }
                });
                const data = await response.json();

                if (response.status === 401) {
                    showToast("Please login to bookmark schemes.", "warning");
                    return;
                }

                if (data.status === "added") {
                    btn.classList.add("active");
                    btn.innerHTML = '<i class="fas fa-bookmark text-primary"></i>';
                    showToast(data.message, "success");
                } else if (data.status === "removed") {
                    btn.classList.remove("active");
                    btn.innerHTML = '<i class="far fa-bookmark"></i>';
                    showToast(data.message, "info");
                }
            } catch (err) {
                console.error("Bookmark operation error:", err);
                showToast("Could not modify bookmarks. Try again.", "danger");
            }
        });
    });
}

// Global Toast Notification Utility
function showToast(message, type = "primary") {
    let container = document.getElementById("toast-container-custom");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container-custom";
        container.classList.add("toast-container-custom");
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.classList.add("toast-custom", type);
    
    let iconClass = "fa-info-circle";
    if (type === "success") iconClass = "fa-check-circle";
    if (type === "warning") iconClass = "fa-exclamation-triangle";
    if (type === "danger") iconClass = "fa-times-circle";

    toast.innerHTML = `
        <i class="fas ${iconClass} text-${type}"></i>
        <div>${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = "slideIn 0.3s ease reverse forwards";
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
window.showToast = showToast;
