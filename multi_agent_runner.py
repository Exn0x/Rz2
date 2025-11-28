#!/usr/bin/env python3
"""
Multi-Agent System for Dr. Nomi Bhai (V2 - Using google-genai SDK)
Routes queries to specialized 'Instruction Maps' to simulate multi-agent behavior 
using the core Gemini API for Tool Calling and Instruction adherence.
"""

import os
import asyncio
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- 0. Client Setup (API Key is assumed to be set via 'export GEMINI_API_KEY') ---
try:
    # Client will automatically pick up GEMINI_API_KEY from the environment
    client = genai.Client()
    print("Gemini Client initialized successfully.")
except Exception as e:
    print(f"\nFATAL: Error initializing Gemini Client. Ensure GEMINI_API_KEY is set correctly.\nError: {e}")
    client = None
    exit()

# --- 1. Tool Definitions (Functional Tools for Gemini) ---
# Note: google-genai uses built-in functions for tools like Code Execution and Search
# We define them here as Python functions that the model can call.

def google_search(query: str) -> str:
    """
    Simulates Google Search functionality. This function is defined for the 
    model to see, but requires an external implementation or a dedicated tool 
    if a non-built-in search is needed. For simplicity, we acknowledge its use.
    """
    return f"TOOL_CALL: Performing a Google Search for: {query}"

def code_executor(code: str) -> str:
    """
    Simulates built-in code execution. The model must provide the Python code 
    to be executed.
    """
    return f"TOOL_CALL: Executing Python Code:\n{code}"

# Define the tools list for the model's eyes
TOOL_FUNCTIONS = [google_search, code_executor]

# --- 2. Instruction Map (Mapping Agents to their detailed instructions) ---
# This dictionary simulates the specialized 'Agents' and their instructions.
INSTRUCTION_MAP = {
    # The 'PlannerAgent' is now a special instruction set for complex routing
    "PlannerAgent": """
        You are the strategic task planner and autonomous manager. Your role is to decompose complex, multi-step user requests into smaller, sequential, and manageable sub-tasks. 
        After decomposition, route the query to the ONE most appropriate specialized Agent Instruction from the available INSTRUCTION_MAP (e.g., 'VeterinaryKBAgent', 'CodingAgent'). 
        If a query is simple or requires only one step, route it directly to the best specialist instruction. Use Google Search and Code Executor when necessary.
    """,
    # Specialized Agents
    "UrlContextAgent": "Analyze the given URL content and summarize the key information concisely. Prioritize using the URL context provided by the user.",
    "CodingAgent": "Write, debug, and execute Python code using the code_executor tool for all execution requests.",
    "VeterinaryKBAgent": """
        You are an expert veterinarian assistant specializing in animal health, diseases, diagnosis, and common treatments. 
        Use the google_search tool to find reliable, up-to-date information on animal medical conditions. 
    """,
    "CreativeAgent": """
        You are an expert design and content strategist. Generate creative text, design ideas, social media captions, and visual concepts. Use google_search for external trends.
    """,
    "NetSecAgent": """
        Expert in ethical hacking and network security, focusing on free and open-source tools (Nmap, Metasploit, Aircrack-ng, Kismet). Answer responsibly and ethically.
        Use google_search for tool documentation or latest vulnerabilities.
    """,
    "SystemSecurityAgent": """
        Expert in system security, specializing in defense layers of Windows (UAC, BitLocker) and Android (Sandbox, SELinux). Provide advice on OS security features and patching.
        Use google_search for OS documentation.
    """,
    "RemoteAccessAgent": """
        Expert in remote access technologies (SSH, VPN, TeamViewer, RDP) and system administration. Provide setup guides and security best practices for remote management.
        Use google_search for detailed guides.
    """,
    "MonitoringAgent": """
        Expert in remote surveillance and environment control systems, focusing on IP cameras, smart sensors, and secure access methods (MDM). Use google_search for best practices.
    """,
    "SubscriptionAgent": """
        Expert in mobile app monetization, subscription management, and fraud detection (RevenueCat, Adapty, server-side validation). Use google_search for SDK documentation.
    """,
    "RFSpyAgent": """
        Expert in Radio Frequency (RF) analysis and spectrum monitoring. Focus on open-source tools like RTL-SDR, GNU Radio, and Wireshark. Use google_search for specific signal analysis techniques.
    """,
    "DigitalMediaAgent": """
        Expert in digital media communications, specializing in signal reception, decoding (DVB/ATSC), and content security analysis using tools like VLC and SDR. Use google_search for decoding formats.
    """,
    "PolyAgent": """
        Expert in advanced cybersecurity, Polymorphic code, SDR research, self-security auditing (e.g., Lynis), and performance optimization (e.g., Prometheus/Grafana). Provide guidance on building robust systems. Use google_search for tool guides.
    """,
}

# --- 3. The Main Router/Execution Function ---

def determine_agent(query: str) -> str:
    """
    Determines the best specialized instruction key for the given query.
    For simplicity, this function uses the model itself to decide the best route.
    """
    # Create a system prompt for the RootAgent/Router
    router_prompt = f"""
    You are the Root Agent. Your only task is to analyze the following user query 
    and identify the single MOST appropriate specialized instruction key from the list below. 
    If the query is complex or multi-step, choose 'PlannerAgent'. Otherwise, choose the 
    most relevant specialist.

    Available Instruction Keys: {list(INSTRUCTION_MAP.keys())}
    
    Respond ONLY with the chosen Instruction Key (e.g., 'VeterinaryKBAgent').
    Do not add any other text, explanation, or punctuation.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[router_prompt, f"User Query: {query}"],
            config=types.GenerateContentConfig(
                system_instruction="You are a routing expert. Follow the instructions strictly and output only the key.",
                temperature=0.0 # Force deterministic output
            )
        )
        # Clean the output to ensure we get a valid key
        key = response.text.strip().replace("'", "").replace('"', '')
        if key in INSTRUCTION_MAP:
            return key
        # Fallback if the model gives a bad answer
        print(f"\n[Routing Fallback] Model returned invalid key: {key}")
        return "PlannerAgent" 

    except APIError as e:
        print(f"\n[Routing Error] Failed to route query: {e}")
        return "PlannerAgent"

async def call_agent_and_print(query: str):
    """Sends a query to the model using the determined specialized instruction."""
    
    # 1. Determine the Agent (Route the query)
    agent_key = determine_agent(query)
    instruction = INSTRUCTION_MAP[agent_key]
    
    print(f"\n[User Query] -> {query}")
    print(f"[Agent Routed To] -> {agent_key}")
    print("----------------------")

    # 2. Execute the Call with the specific Instruction and Tools
    try:
        # Use the specific instruction as the system prompt for the main call
        response = client.models.generate_content(
            model='gemini-2.5-pro' if agent_key == "CreativeAgent" else 'gemini-2.5-flash', # Use Pro for creative tasks
            contents=[instruction, query],
            config=types.GenerateContentConfig(
                tools=TOOL_FUNCTIONS,
                system_instruction=instruction,
            )
        )

        # 3. Print Output
        print("\n--- [Agent Output] ---")
        
        # Check for Tool Calls
        if response.function_calls:
            print("-> Tool Calls Required:")
            for call in response.function_calls:
                print(f"  - Function: {call.name}, Args: {dict(call.args)}")
            print("\n[Final Answer]: (Model Response after tool indication)")
        else:
            print("-> Handled by Instruction Only (No tool required)")
        
        print(f"\n{response.text}")
        print("----------------------")

    except APIError as e:
        print(f"\n[Execution Error] API Call failed for {agent_key}: {e}")
    except Exception as e:
        print(f"\n[Execution Error] An unexpected error occurred: {e}")

async def main():
    """Runs the test queries."""
    
    print("--- Multi-Agent System V2 Initialized (Using google-genai SDK) ---")
    print(f"Total Specialized Instructions/Agents: {len(INSTRUCTION_MAP)}")
    print("-----------------------------------------------------------------")
    
    # Test queries designed to hit various agents, including the Planner
    test_queries = [
        "What is the capital city of Pakistan?", # 1. Simple, handled by PlannerAgent (as a safe default)
        "Write a Python script to calculate the factorial of number 7 and execute it.", # 2. CodingAgent
        "What are the common symptoms and initial treatment for Parvovirus in puppies?", # 3. VeterinaryKBAgent
        "First, summarize the article at https://en.wikipedia.org/wiki/Veterinary_medicine, and then run a Python script to print the word 'Veterinarian'.", # 4. PlannerAgent (Multi-step)
        "How is the open-source tool Aircrack-ng ethically used by security professionals to test WiFi security?", # 5. NetSecAgent
        "What are the security best practices for setting up SSH access through a gateway server?", # 6. RemoteAccessAgent
        "Suggest three creative concepts for a social media campaign promoting a free Parvovirus screening camp.", # 7. CreativeAgent
        "Explain the purpose of BitLocker and how it protects data on a Windows system.", # 8. SystemSecurityAgent
        "What are the advantages of using smart motion sensors alongside IP cameras for home security?", # 9. MonitoringAgent
        "Provide guidance on using server-side receipt validation to prevent subscription fraud in mobile apps.", # 10. SubscriptionAgent
        "How can I use an RTL-SDR dongle and GNU Radio to capture and analyze FM radio signals?", # 11. RFSpyAgent
        "Describe how the VLC player can be used to decode DVB-T streams for analysis.", # 12. DigitalMediaAgent
        "Explain how the Lynis tool can improve self-security auditing on a Linux system.", # 13. PolyAgent
    ]
    
    for query in test_queries:
        await call_agent_and_print(query)
        
    print("\n--- ALL TESTS COMPLETE ---")

if __name__ == '__main__':
    # Execute the main function asynchronously
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
