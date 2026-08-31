"""Medical agent tools — educational mock APIs."""

from __future__ import annotations

from typing import Any, Callable

from medical_assistant.src.rag.pipeline import medical_rag_query

# Mock educational databases (NOT real medical data)
SYMPTOM_DB = {
    "fever": "Educational: Fever is elevated body temperature, often a sign the immune system is fighting infection. Common causes include viral infections. Seek medical care if fever is very high or persistent.",
    "headache": "Educational: Headaches can be tension-type, migraine, or secondary to other conditions. Rest, hydration, and stress reduction help mild cases. See a doctor for severe or sudden headaches.",
    "cough": "Educational: Coughs clear airways. Acute coughs often follow colds. Chronic cough may need evaluation. See a doctor if cough includes blood or breathing difficulty.",
    "fatigue": "Educational: Fatigue is extreme tiredness. Causes include poor sleep, stress, anemia, or illness. Persistent fatigue warrants medical evaluation.",
}

MEDICATION_DB = {
    "paracetamol": "Educational: Paracetamol (acetaminophen) is a common pain reliever and fever reducer. Follow dosage on packaging. Overdose can harm the liver.",
    "ibuprofen": "Educational: Ibuprofen is an NSAID used for pain, fever, and inflammation. Take with food. Not suitable for everyone — ask a pharmacist or doctor.",
    "amoxicillin": "Educational: Amoxicillin is an antibiotic for bacterial infections. Must be prescribed by a doctor. Never use leftover antibiotics without medical advice.",
    "aspirin": "Educational: Aspirin reduces pain, fever, and inflammation. Low-dose aspirin is used for heart disease prevention in some patients — only under medical supervision.",
}

SPECIALISTS = {
    "cardiology": ["Dr. Heart Care Clinic", "City Cardiology Center"],
    "dermatology": ["Skin Health Clinic", "Dermatology Associates"],
    "pediatrics": ["Children's Wellness Center", "Family Pediatrics"],
    "general": ["Community Health Center", "Primary Care Clinic"],
}


def bmi_calculator(weight_kg: float, height_m: float) -> str:
    """Calculate BMI and give educational category."""
    if height_m <= 0 or weight_kg <= 0:
        return "Error: weight and height must be positive numbers."
    bmi = round(weight_kg / (height_m ** 2), 1)
    if bmi < 18.5:
        category = "underweight"
    elif bmi < 25:
        category = "normal weight"
    elif bmi < 30:
        category = "overweight"
    else:
        category = "obese"
    return (
        f"BMI: {bmi} ({category}). "
        "Educational only — BMI is a screening tool, not a diagnosis. Consult a healthcare provider."
    )


def symptom_lookup(symptoms: str) -> str:
    """Look up educational info about symptoms (mock database)."""
    key = symptoms.lower().strip()
    for symptom, info in SYMPTOM_DB.items():
        if symptom in key:
            return f"{info} [Not a diagnosis — see a doctor for personal health concerns.]"
    return (
        f"No educational entry for '{symptoms}'. "
        "This tool uses a small mock database for learning. Always consult a real doctor."
    )


def medication_info(drug_name: str) -> str:
    """Look up educational medication information (mock database)."""
    key = drug_name.lower().strip()
    for drug, info in MEDICATION_DB.items():
        if drug in key:
            return f"{info} [Educational only — never self-medicate without professional advice.]"
    return f"No educational entry for '{drug_name}'. Consult a pharmacist or doctor for real medication information."


def find_specialist(specialty: str, city: str = "your area") -> str:
    """Find mock specialist listings for learning purposes."""
    key = specialty.lower().strip()
    for spec, clinics in SPECIALISTS.items():
        if spec in key or key in spec:
            return (
                f"Educational mock results for {specialty} in {city}:\n"
                + "\n".join(f"  - {c}" for c in clinics)
                + "\n[Mock data for learning — not real appointments.]"
            )
    return f"No mock listings for '{specialty}'. Try: cardiology, dermatology, pediatrics, general."


def search_medical_kb(query: str) -> str:
    """Search the medical knowledge base using RAG."""
    result = medical_rag_query(query, top_k=2)
    if not result["chunks"]:
        return "No medical documents found. Ingest docs first."
    return result["answer"]


TOOLS: dict[str, Callable[..., str]] = {
    "bmi_calculator": bmi_calculator,
    "symptom_lookup": symptom_lookup,
    "medication_info": medication_info,
    "find_specialist": find_specialist,
    "search_medical_kb": search_medical_kb,
}

TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "bmi_calculator",
            "description": "Calculate BMI from weight (kg) and height (meters). Educational only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weight_kg": {"type": "number", "description": "Weight in kilograms"},
                    "height_m": {"type": "number", "description": "Height in meters"},
                },
                "required": ["weight_kg", "height_m"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "symptom_lookup",
            "description": "Look up educational information about a symptom (mock database).",
            "parameters": {
                "type": "object",
                "properties": {
                    "symptoms": {"type": "string", "description": "Symptom to look up, e.g. fever, headache"}
                },
                "required": ["symptoms"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "medication_info",
            "description": "Look up educational information about a medication (mock database).",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string", "description": "Medication name, e.g. paracetamol"}
                },
                "required": ["drug_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_specialist",
            "description": "Find mock specialist listings for learning (not real appointments).",
            "parameters": {
                "type": "object",
                "properties": {
                    "specialty": {"type": "string", "description": "Medical specialty, e.g. cardiology"},
                    "city": {"type": "string", "description": "City name", "default": "your area"},
                },
                "required": ["specialty"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_medical_kb",
            "description": "Search the medical education knowledge base for health topics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Medical education search query"}
                },
                "required": ["query"],
            },
        },
    },
]


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    if name not in TOOLS:
        return f"Unknown tool: {name}"
    try:
        return TOOLS[name](**arguments)
    except (TypeError, ValueError) as exc:
        return f"Invalid arguments for {name}: {exc}"
