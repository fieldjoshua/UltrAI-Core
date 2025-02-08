async def main():
    # Initialize your model clients
    llama_client = LlamaClient()
    chatgpt_client = ChatGPTClient()
    gemini_client = GeminiClient()
    
    orchestrator = TriLLMOrchestrator(
        llama_client,
        chatgpt_client,
        gemini_client
    )
    
    result = await orchestrator.process_responses(
        "Your prompt here"
    )
    
    if result["status"] == "success":
        print("Final Synthesis:", result["final_synthesis"])
        print("Metrics:", result["metrics"])
    else:
        print("Error:", result["error"]) 