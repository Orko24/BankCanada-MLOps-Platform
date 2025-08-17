"""
AI Agent Service with Dynamic API Key Support

This service creates AI agents on-demand using user-provided API keys
instead of requiring environment variables.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class EconomicResearchService:
    """Economic research service with dynamic API key support"""
    
    def __init__(self, api_key: str):
        """Initialize with user-provided API key"""
        self.api_key = api_key
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the AI agent with the provided API key"""
        try:
            from langchain_community.chat_models import ChatOpenAI
            from langchain.agents import AgentExecutor, create_openai_tools_agent
            from langchain.memory import ConversationBufferWindowMemory
            from langchain.prompts import ChatPromptTemplate
            from langchain.tools import Tool
            
            # Initialize LLM with DeepSeek
            self.llm = ChatOpenAI(
                model="deepseek-chat",
                openai_api_key=self.api_key,
                openai_api_base="https://api.deepseek.com/v1",
                temperature=0.1,
                max_tokens=4000
            )
            
            # Initialize memory
            self.memory = ConversationBufferWindowMemory(
                k=10,
                memory_key="chat_history",
                return_messages=True
            )
            
            # Create tools
            tools = self._create_tools()
            
            # Create agent
            system_prompt = """
            You are an advanced AI economic research assistant for the Bank of Canada.
            
            Your expertise includes:
            - Monetary policy analysis
            - Economic forecasting and modeling
            - Financial stability assessment
            - International economic trends
            - Central banking operations
            
            Guidelines:
            1. Provide accurate, evidence-based analysis
            2. Consider multiple perspectives and scenarios
            3. Highlight uncertainties and risks
            4. Reference relevant economic theory and data
            5. Tailor responses to central banking context
            6. Use Canadian economic context when relevant
            
            When responding:
            - Be concise but comprehensive
            - Provide actionable insights
            - Include relevant data and evidence
            - Suggest follow-up analysis if appropriate
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
                ("assistant", "I'll analyze this economic question using my expertise and available tools."),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            self.agent = create_openai_tools_agent(
                llm=self.llm,
                tools=tools,
                prompt=prompt
            )
            
            self.agent_executor = AgentExecutor.from_agent_and_tools(
                agent=self.agent,
                tools=tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )
            
            logger.info("AI agent initialized successfully with DeepSeek")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI agent: {e}")
            raise
    
    def _create_tools(self) -> List:
        """Create tools for the AI agent"""
        tools = []
        
        # Economic data tool
        def get_economic_data(indicator: str) -> str:
            """Get latest economic data for specified indicator"""
            try:
                import requests
                # Simple Bank of Canada API call
                url = f"https://www.bankofcanada.ca/valet/observations/{indicator}/json"
                params = {'recent': 5}
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    observations = data.get('observations', [])
                    if observations:
                        latest = observations[0]
                        return f"Latest {indicator}: {latest.get('v', 'N/A')} (Date: {latest.get('d', 'N/A')})"
                
                return f"Unable to fetch data for {indicator}"
                
            except Exception as e:
                return f"Error fetching {indicator}: {str(e)}"
        
        tools.append(Tool(
            name="economic_data_fetcher",
            description="Fetch real-time economic data from Bank of Canada. Input should be an indicator code like 'CPIXCORE', 'GDP', etc.",
            func=get_economic_data
        ))
        
        # Economic analysis tool
        def analyze_trends(query: str) -> str:
            """Analyze economic trends and provide insights"""
            try:
                # This would integrate with your ML models
                # For now, provide structured analysis framework
                analysis = f"""
                Economic Analysis for: {query}
                
                Key Considerations:
                1. Current Economic Context: Review recent indicators and trends
                2. Historical Patterns: Compare with historical data and cycles
                3. Policy Implications: Consider monetary policy impacts
                4. Risk Factors: Identify potential risks and uncertainties
                5. International Context: Consider global economic conditions
                
                Recommendation: Conduct detailed analysis using available economic data and models.
                """
                return analysis
                
            except Exception as e:
                return f"Analysis error: {str(e)}"
        
        tools.append(Tool(
            name="trend_analyzer",
            description="Analyze economic trends and provide structured insights. Input should be an economic topic or question.",
            func=analyze_trends
        ))
        
        # Policy research tool
        def research_policy(topic: str) -> str:
            """Research monetary policy topics"""
            try:
                policy_analysis = f"""
                Policy Research: {topic}
                
                Bank of Canada Perspective:
                - Current Policy Stance: Review recent policy decisions and communications
                - Historical Context: Consider previous policy responses to similar conditions
                - International Comparison: Compare with other central banks
                - Economic Impact: Assess potential effects on key indicators
                - Communication Strategy: Consider public messaging and guidance
                
                Key Resources:
                - Monetary Policy Reports
                - Governor speeches and testimonies
                - Financial System Reviews
                - Staff analytical notes
                """
                return policy_analysis
                
            except Exception as e:
                return f"Policy research error: {str(e)}"
        
        tools.append(Tool(
            name="policy_researcher",
            description="Research monetary policy topics and Bank of Canada positions. Input should be a policy topic or question.",
            func=research_policy
        ))
        
        return tools
    
    async def research(self, question: str, context: Optional[str] = None, indicators: Optional[List[str]] = None) -> Dict[str, Any]:
        """Conduct economic research"""
        try:
            # Format the research query
            formatted_query = f"""
            Economic Research Query: {question}
            Additional Context: {context or 'Not specified'}
            Focus Indicators: {', '.join(indicators) if indicators else 'Not specified'}
            
            Please provide a comprehensive analysis including:
            1. Current status and recent trends
            2. Relevant economic data and evidence
            3. Policy implications and considerations
            4. Risk factors and scenarios
            5. Recommendations for further analysis
            """
            
            # Execute research
            result = await asyncio.to_thread(
                self.agent_executor.invoke,
                {"input": formatted_query}
            )
            
            return {
                "success": True,
                "question": question,
                "response": result["output"],
                "timestamp": datetime.now().isoformat(),
                "confidence": "high"
            }
            
        except Exception as e:
            logger.error(f"Research error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def chat(self, message: str) -> str:
        """Chat with the economic research agent using direct API call"""
        try:
            import httpx
            
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an expert economic research assistant for the Bank of Canada. Provide insightful analysis on Canadian economic indicators, monetary policy, and financial markets. Be precise, data-driven, and professional in your responses."
                    },
                    {
                        "role": "user", 
                        "content": message
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.1,
                "stream": False
            }
            
            # Make the API call
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('choices') and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                    else:
                        return "No response generated"
                else:
                    logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                    return f"I apologize, but I encountered an API error: {response.status_code}"
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def get_conversation_history(self) -> List:
        """Get conversation history"""
        return self.memory.chat_memory.messages if self.memory else []
    
    def clear_history(self):
        """Clear conversation history"""
        if self.memory:
            self.memory.clear()
