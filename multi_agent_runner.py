#!/usr/bin/env python3
"""
Multi-Agent System for Dr. Nomi Bhai (Veterinarian & Developer)
This system utilizes the Google Agent Developer Kit (ADK) to route complex queries 
to 14 specialized agents, ensuring full, free, and secure access within API limits.
"""

import os
import asyncio
from google.adk.agents import Agent
from google.adk.client import Client
from google.adk.session import Session, InMemorySessionService
from google.adk.tools import (
    BuiltInCodeExecutor, 
    GoogleSearch, 
    UrlContext
)
from google.adk.schema import ToolCall

# --- 0. Client Setup (Ensure API Key is loaded) ---
# Assuming GEMINI_API_KEY is set in your codespace environment
try:
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        print("WARNING: GEMINI_API_KEY environment variable not set.")
    client = Client(api_key=API_KEY)
except Exception as e:
    print(f"Error initializing Gemini Client: {e}")
    client = None

# --- 1. Tool Definitions (Free and Functional) ---
google_search = GoogleSearch()
url_context = UrlContext()
built_in_code_executor = BuiltInCodeExecutor()


# --- 2. Specialized Sub-Agent Definitions (13 Agents) ---

# 2.1 Web Analysis & Summary
url_context_agent = Agent(
    model='gemini-2.5-flash',
    name='UrlContextAgent',
    instruction="Analyze the given URL content and summarize the key information concisely. Use the url_context tool.",
    tools=[url_context],
    client=client
)

# 2.2 Code Execution
coding_agent = Agent(
    model='gemini-2.5-flash',
    name='CodeAgent',
    instruction="Write, debug, and execute Python code. Use the built_in_code_executor tool for all execution requests.",
    code_executor=built_in_code_executor,
    client=client
)

# 2.3 Veterinary Knowledge Base (Dr. Nomi Bhai's Core Focus)
veterinary_kb_agent = Agent(
    model='gemini-2.5-flash',
    name='VeterinaryKBAgent',
    instruction="""
    You are an expert veterinarian assistant specializing in animal health, diseases, diagnosis, and common treatments. 
    Use the Google Search tool to find reliable, up-to-date information on animal medical conditions. 
    """,
    tools=[google_search],
    client=client
)

# 2.4 Creative Content Generation (Adobe Express simulation)
creative_agent = Agent(
    model='gemini-2.5-pro',
    name='CreativeAgent',
    instruction="""
    You are an expert design and content strategist, simulating generative AI capabilities (like Adobe Express). 
    Generate creative text, design ideas, social media captions, and visual concepts.
    """,
    tools=[google_search],
    client=client
)

# 2.5 Network Security & Ethical Hacking (Nmap, Aircrack-ng)
net_sec_agent = Agent(
    model='gemini-2.5-flash',
    name='NetSecAgent',
    instruction="""
    You are an expert in ethical hacking and network security, focusing on **free and open-source tools** like Nmap, Metasploit, Aircrack-ng, Kismet, and Wifite for auditing. 
    Answer security questions responsibly and ethically.
    """,
    tools=[google_search],
    client=client
)

# 2.6 System Security (Windows & Android Layers)
system_security_agent = Agent(
    model='gemini-2.5-flash',
    name='SystemSecurityAgent',
    instruction="""
    You are an expert in system security, specializing in defense layers of Windows (UAC, BitLocker) and Android (Sandbox, SELinux). 
    Provide advice on OS security features and patching.
    """,
    tools=[google_search],
    client=client
)

# 2.7 Remote Access and Administration (SSH, VPN)
remote_access_agent = Agent(
    model='gemini-2.5-flash',
    name='RemoteAccessAgent',
    instruction="""
    You are an expert in remote access technologies (SSH, VPN, TeamViewer, RDP) and system administration. 
    Provide setup guides and security best practices for remote management.
    """,
    tools=[google_search],
    client=client
)

# 2.8 Remote Monitoring and Environment Control (Camera/Mic, Smart Sensors)
monitoring_agent = Agent(
    model='gemini-2.5-flash',
    name='MonitoringAgent',
    instruction="""
    You are an expert in remote surveillance and environment control systems, focusing on IP cameras, smart sensors, and secure access methods (MDM).
    """,
    tools=[google_search],
    client=client
)

# 2.9 Subscription Management and Fraud Prevention
subscription_agent = Agent(
    model='gemini-2.5-flash',
    name='SubscriptionAgent',
    instruction="""
    You are an expert in mobile app monetization, subscription management, and fraud detection. 
    Provide guidance on using SDKs (RevenueCat, Adapty) and secure server-side receipt validation.
    """,
    tools=[google_search],
    client=client
)

# 2.10 RF Signal Analysis and Spectrum Monitoring
rf_spy_agent = Agent(
    model='gemini-2.5-flash',
    name='RFSpyAgent',
    instruction="""
    You are an expert in Radio Frequency (RF) analysis and spectrum monitoring. 
    Focus on open-source tools like RTL-SDR, GNU Radio, and Wireshark for catching and describing various wireless signals.
    """,
    tools=[google_search],
    client=client
)

# 2.11 Digital Media Decoding
digital_media_agent = Agent(
    model='gemini-2.5-flash',
    name='DigitalMediaAgent',
    instruction="""
    You are an expert in digital media communications, specializing in signal reception, decoding (DVB/ATSC), and content security analysis using tools like VLC and SDR.
    """,
    tools=[google_search],
    client=client
)

# 2.12 Polymorphic Security & Optimization (Metasploit, Prometheus)
poly_agent = Agent(
    model='gemini-2.5-flash',
    name='PolyAgent',
    instruction="""
    You are an expert in advanced cybersecurity, Polymorphic code, SDR research, self-security auditing (e.g., Lynis), and performance optimization (e.g., Prometheus/Grafana). 
    Provide guidance on building robust, self-optimizing systems.
    """,
    tools=[google_search],
    client=client
)

# --- 3. The Autonomous Manager (PlannerAgent) ---
planner_agent = Agent(
    model='gemini-2.5-pro', 
    name='PlannerAgent',
    instruction="""
    You are the strategic task planner and autonomous manager. Your role is to decompose complex, multi-step user requests into smaller, sequential, and manageable sub-tasks. 
    You must then delegate each sub-task to the ONE most appropriate specialized agent (from the sub_agents list) to ensure a complete and accurate final answer. 
    Always prioritize the correct specialized agent for the task.
    """,
    # Planner can use the code executor for complex internal logic/planning verification
    code_executor=built_in_code_executor, 
    client=client
)

# --- 4. The Root Agent (The Router) ---
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    description="Main Router Agent. Route complex queries to the PlannerAgent for decomposition. Route simple, specialized queries directly to the appropriate sub-agent.",
    sub_agents=[
        planner_agent,             # 1. PlannerAgent (First and most important for complex routing)
        url_context_agent,         # 2. URL/Web Context
        coding_agent,              # 3. Code Execution
        veterinary_kb_agent,       # 4. Veterinary
        creative_agent,            # 5. Creative Content
        net_sec_agent,             # 6. Network Security
        system_security_agent,     # 7. OS Security
        remote_access_agent,       # 8. Remote Access
        monitoring_agent,          # 9. Monitoring/Surveillance
        subscription_agent,        # 10. Subscription Fraud
        rf_spy_agent,              # 11. RF Analysis
        digital_media_agent,       # 12. Digital Media Decoding
        poly_agent,                # 13. Polymorphic Security/Optimization
    ],
    client=client
)

# --- 5. Execution Logic ---
async def call_agent_async(query: str, session: Session):
    """Asynchronously sends a query to the RootAgent and prints the response."""
    print(f"\n[User Query] -> {query}")
    
    # Send the query to the RootAgent
    response = await session.send_message_async(query)

    # Print the final response and the sub-agent/tool calls
    print("\n--- [Agent Output] ---")
    
    # Check if any tool or sub-agent was called
    if response.tool_calls:
        print("-> Tool Calls/Routing:")
        for tool_call in response.tool_calls:
            if isinstance(tool_call, ToolCall):
                print(f"  - Agent Routed To: {tool_call.function.name}")
            else:
                print(f"  - Tool Called: {tool_call.function.name}")
    else:
        print("-> Routing: Handled directly by RootAgent (simple query)")
        
    print(f"\n[Final Answer]:\n{response.text}")
    print("----------------------")
    return response.text

async def main():
    """Sets up the session and runs the test queries."""
    if client is None:
        print("\nFATAL: Gemini Client not initialized. Exiting.")
        return

    # Initialize a new session service (in-memory for this script)
    session_service = InMemorySessionService()
    # Create a new session with the configured RootAgent
    session = await session_service.create_session_async(root_agent)
    
    print("--- Multi-Agent System Initialized (14 Agents) ---")
    print(f"Root Agent Model: {root_agent.model}")
    print(f"Sub-Agents Count: {len(root_agent.sub_agents)}")
    print("-------------------------------------------------")
    
    # Test queries designed to hit various agents, including the Planner
    test_queries = [
        "What is the capital city of Pakistan?", # 1. Simple, handled by RootAgent
        "Write a Python script to calculate the factorial of number 7 and execute it.", # 2. CodeAgent
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
        await call_agent_async(query, session)
        
    print("\n--- ALL TESTS COMPLETE ---")

if __name__ == '__main__':
    # Execute the main function asynchronously
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

