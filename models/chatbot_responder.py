import re

class ChatbotResponder:
    def __init__(self):
        # Define keyword rules
        self.rules = [
            (r"\b(hi|hello|hey|greetings|good morning|good afternoon|namaste)\b", 
             "Hello! I am your SchemeAI Assistant. How can I help you find or apply for government schemes today?"),
            
            (r"\b(apply|how to apply|application)\b", 
             "To apply for a scheme:\n1. Browse schemes on the 'Schemes' page.\n2. Click on 'View Details' to read about the scheme.\n3. Click the 'Apply Now' button to go to the official government portal.\nMake sure you have all required documents ready!"),
            
            (r"\b(recommend|ai recommendation|find scheme|find my scheme|suggest|match)\b", 
             "You can get personalized scheme recommendations using our 'AI Recommendation' page! Simply fill out the multi-step questionnaire, and our machine learning model will match you with the best options."),
            
            (r"\b(eligibility|eligible|check eligibility|qualify)\b", 
             "You can check eligibility in two ways:\n1. Use the 'Eligibility Checker' page and select a scheme to see if you qualify.\n2. Fill out your profile in your Dashboard to see live eligibility indicators across schemes."),
            
            (r"\b(compare|comparison|difference)\b", 
             "Go to the 'Compare Schemes' page in the top menu, search and select up to three schemes, and view a detailed side-by-side comparison of benefits, limits, and links."),
            
            (r"\b(calculate|calculator|amount|pension amount|scholarship amount|subsidy)\b", 
             "Use our 'Benefits Calculator' page to estimate potential aids like scholarship amounts, monthly pension payouts, or farming subsidies with charts!"),
            
            (r"\b(document|aadhaar|pan|income certificate|caste certificate|domicile|passbook)\b", 
             "You can learn all about necessary application materials on our 'Required Documents' page. It details what each document is for, where to get it, and how long it stays valid."),
            
            (r"\b(register|login|signup|account|profile|dashboard)\b", 
             "Create an account on the 'Register' page to save your recommendations, bookmark schemes, track eligibility check history, and update your personal details on the User Dashboard."),
            
            (r"\b(admin|upload csv|dashboard admin|analytics)\b", 
             "Admins can login to the secure Admin Panel to create, modify, or delete schemes, upload CSV batch files, search users, and view registration/scheme analytics."),
            
            (r"\b(who are you|about|developer|team|website|project)\b", 
             "SchemeAI is a B.Tech final-year AI/ML project. It's a modern portal designed to bridge the gap between Indian citizens and government welfare schemes using intelligent eligibility ranking."),
            
            (r"\b(thank|thanks|great|cool|awesome|helpful)\b", 
             "You're welcome! Let me know if you need help with anything else. Good luck finding the right scheme!"),
        ]

    def get_response(self, user_query):
        if not user_query:
            return "Please type a question, and I'll do my best to help you!"
        
        query = user_query.lower().strip()
        
        for pattern, response in self.rules:
            if re.search(pattern, query):
                return response
                
        # Default response
        return "I'm sorry, I didn't quite catch that. I can assist you with how to apply, AI recommendations, documents required, calculators, and comparing schemes. Could you try rephrasing your question?"

chatbot = ChatbotResponder()

def respond_to_query(query):
    return chatbot.get_response(query)
