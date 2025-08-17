"""
Economic Research AI Agent - Bank of Canada

Advanced AI agent for economic research, policy analysis, and 
document intelligence using LangChain and RAG capabilities.

Key Features:
- Economic research and analysis
- Policy document understanding
- Real-time data integration
- Multi-modal reasoning capabilities
- Bank of Canada domain expertise
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
import logging

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool, BaseTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import WebBaseLoader, PDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# Use DeepSeek as cost-effective alternative
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import OpenAI

import pandas as pd
import numpy as np
import requests
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EconomicQuery(BaseModel):
    """Economic research query model"""
    question: str = Field(description="The economic question or research topic")
    time_period: Optional[str] = Field(default=None, description="Time period for analysis")
    indicators: Optional[List[str]] = Field(default=None, description="Economic indicators to focus on")
    context: Optional[str] = Field(default=None, description="Additional context for the query")


class EconomicDataTool(BaseTool):
    """Tool for accessing real-time economic data"""
    
    name = "economic_data_fetcher"
    description = """
    Fetch real-time economic data from Bank of Canada and other sources.
    Input should be an indicator name like 'inflation', 'unemployment', 'gdp', etc.
    """
    
    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
    
    def _run(self, indicator: str) -> str:
        """Fetch economic data for specified indicator"""
        try:
            # Get latest data for the indicator
            response = requests.get(
                f"{self.api_base_url}/api/economic-data/indicators/{indicator}/latest",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return f"""
                Latest {indicator} data:
                - Value: {data.get('value', 'N/A')}
                - Date: {data.get('date', 'N/A')}
                - Quality Score: {data.get('quality_score', 'N/A')}
                - Year-over-year change: {data.get('year_over_year_change', 'N/A')}%
                """
            else:
                return f"Unable to fetch data for {indicator}. Status: {response.status_code}"
                
        except Exception as e:
            return f"Error fetching economic data: {str(e)}"
    
    async def _arun(self, indicator: str) -> str:
        """Async version of _run"""
        return self._run(indicator)


class ForecastTool(BaseTool):
    """Tool for generating economic forecasts"""
    
    name = "economic_forecaster"
    description = """
    Generate economic forecasts using ML models.
    Input should be an indicator name and forecast horizon like 'inflation,12' for 12-month inflation forecast.
    """
    
    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
    
    def _run(self, query: str) -> str:
        """Generate forecast for specified indicator"""
        try:
            parts = query.split(',')
            indicator = parts[0].strip()
            horizon = int(parts[1].strip()) if len(parts) > 1 else 12
            
            response = requests.post(
                f"{self.api_base_url}/api/predictions/forecast/{indicator}",
                json={
                    "horizon_days": horizon * 30,  # Convert months to days
                    "confidence_level": 0.95,
                    "scenario": "baseline"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                forecast = response.json()
                return f"""
                {indicator.title()} Forecast ({horizon} months):
                - Forecasted values: {forecast.get('forecasts', [])}
                - Confidence intervals: {forecast.get('confidence_intervals', [])}
                - Model used: {forecast.get('model_info', {}).get('model_name', 'Unknown')}
                - Forecast quality: {forecast.get('forecast_quality', {})}
                """
            else:
                return f"Unable to generate forecast for {indicator}. Status: {response.status_code}"
                
        except Exception as e:
            return f"Error generating forecast: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version of _run"""
        return self._run(query)


class PolicyAnalysisTool(BaseTool):
    """Tool for analyzing Bank of Canada policy documents"""
    
    name = "policy_analyzer"
    description = """
    Analyze Bank of Canada policy documents and statements.
    Input should be a policy topic or document type like 'monetary policy', 'financial stability', etc.
    """
    
    def __init__(self, vector_store):
        super().__init__()
        self.vector_store = vector_store
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(
                model="deepseek-chat",
                openai_api_base="https://api.deepseek.com/v1",
                temperature=0.1
            ),
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 5})
        )
    
    def _run(self, query: str) -> str:
        """Analyze policy documents related to query"""
        try:
            result = self.qa_chain.run(
                f"Analyze Bank of Canada policy regarding: {query}. "
                f"Provide insights on policy stance, recent changes, and implications."
            )
            return result
        except Exception as e:
            return f"Error analyzing policy: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version of _run"""
        return self._run(query)


class EconomicResearchAgent:
    """
    Advanced AI agent for economic research and analysis
    """
    
    def __init__(self, api_base_url: str, deepseek_api_key: str):
        """Initialize the economic research agent"""
        self.api_base_url = api_base_url
        
        # Initialize LLM (using DeepSeek as cost-effective option)
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=deepseek_api_key,
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
        
        # Initialize vector store for document search
        self.vector_store = self._setup_vector_store()
        
        # Initialize tools
        self.tools = [
            EconomicDataTool(api_base_url),
            ForecastTool(api_base_url),
            PolicyAnalysisTool(self.vector_store),
            self._create_correlation_tool(),
            self._create_scenario_analysis_tool(),
            self._create_research_tool()
        ]
        
        # Create agent
        self.agent = self._create_agent()
        
        # Agent executor
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def _setup_vector_store(self) -> Chroma:
        """Setup vector store with Bank of Canada documents"""
        try:
            # Initialize embeddings
            embeddings = OpenAIEmbeddings()
            
            # Load Bank of Canada documents
            documents = self._load_bank_documents()
            
            # Create vector store
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory="./chroma_db"
            )
            
            return vector_store
            
        except Exception as e:
            logger.error(f"Error setting up vector store: {e}")
            # Return empty vector store as fallback
            return Chroma(embedding_function=OpenAIEmbeddings())
    
    def _load_bank_documents(self) -> List:
        """Load and process Bank of Canada documents"""
        documents = []
        
        # URLs of key Bank of Canada documents
        doc_urls = [
            "https://www.bankofcanada.ca/core-functions/monetary-policy/",
            "https://www.bankofcanada.ca/publications/policy-discussions/",
            "https://www.bankofcanada.ca/publications/annual-reports/",
        ]
        
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            for url in doc_urls:
                try:
                    loader = WebBaseLoader(url)
                    docs = loader.load()
                    split_docs = text_splitter.split_documents(docs)
                    documents.extend(split_docs)
                except Exception as e:
                    logger.warning(f"Failed to load document from {url}: {e}")
            
            logger.info(f"Loaded {len(documents)} document chunks")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return []
    
    def _create_correlation_tool(self) -> Tool:
        """Create tool for correlation analysis"""
        
        def correlation_analysis(query: str) -> str:
            try:
                # Parse query to extract indicators
                indicators = [i.strip() for i in query.split(',')]
                
                response = requests.get(
                    f"{self.api_base_url}/api/economic-data/correlations",
                    params={"indicators": indicators},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    matrix = data.get('correlation_matrix', {})
                    
                    result = f"Correlation Analysis for {', '.join(indicators)}:\n"
                    for pair, correlation in matrix.items():
                        result += f"- {pair}: {correlation:.3f}\n"
                    
                    return result
                else:
                    return f"Unable to calculate correlations. Status: {response.status_code}"
                    
            except Exception as e:
                return f"Error in correlation analysis: {str(e)}"
        
        return Tool(
            name="correlation_analyzer",
            description="Analyze correlations between economic indicators. Input should be comma-separated indicator names.",
            func=correlation_analysis
        )
    
    def _create_scenario_analysis_tool(self) -> Tool:
        """Create tool for scenario analysis"""
        
        def scenario_analysis(query: str) -> str:
            try:
                # Parse scenario query
                parts = query.split('|')
                model_name = parts[0].strip()
                scenarios = json.loads(parts[1]) if len(parts) > 1 else {"baseline": {}}
                
                response = requests.post(
                    f"{self.api_base_url}/api/predictions/models/{model_name}/scenario",
                    json=scenarios,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return f"""
                    Scenario Analysis Results:
                    - Model: {data.get('model_name', 'Unknown')}
                    - Scenarios: {list(data.get('scenarios', {}).keys())}
                    - Key insights: {data.get('insights', [])}
                    - Comparison: {data.get('comparison', {})}
                    """
                else:
                    return f"Unable to run scenario analysis. Status: {response.status_code}"
                    
            except Exception as e:
                return f"Error in scenario analysis: {str(e)}"
        
        return Tool(
            name="scenario_analyzer",
            description="Run scenario analysis using economic models. Input format: 'model_name|{scenario_config_json}'",
            func=scenario_analysis
        )
    
    def _create_research_tool(self) -> Tool:
        """Create tool for economic research"""
        
        def economic_research(query: str) -> str:
            try:
                # Use the LLM to generate research insights
                research_prompt = f"""
                As an expert economic researcher at the Bank of Canada, provide a comprehensive analysis of:
                {query}
                
                Consider:
                1. Current economic context
                2. Historical patterns and trends
                3. Policy implications
                4. International comparisons
                5. Risk factors and uncertainties
                
                Provide specific, actionable insights based on economic theory and empirical evidence.
                """
                
                response = self.llm.invoke([HumanMessage(content=research_prompt)])
                return response.content
                
            except Exception as e:
                return f"Error in economic research: {str(e)}"
        
        return Tool(
            name="economic_researcher",
            description="Conduct comprehensive economic research on a topic. Input should be a research question or topic.",
            func=economic_research
        )
    
    def _create_agent(self):
        """Create the agent with appropriate prompts"""
        
        system_prompt = """
        You are an advanced AI economic research assistant for the Bank of Canada. 
        
        Your expertise includes:
        - Monetary policy analysis
        - Economic forecasting and modeling
        - Financial stability assessment
        - International economic trends
        - Central banking operations
        
        Guidelines:
        1. Always provide accurate, evidence-based analysis
        2. Consider multiple perspectives and scenarios
        3. Highlight uncertainties and risks
        4. Reference relevant economic theory and data
        5. Tailor responses to central banking context
        6. Use Canadian economic context when relevant
        
        You have access to tools for:
        - Real-time economic data
        - Forecasting models
        - Policy document analysis
        - Correlation analysis
        - Scenario modeling
        - Economic research
        
        When responding:
        - Be concise but comprehensive
        - Provide actionable insights
        - Include relevant data and evidence
        - Suggest follow-up analysis if appropriate
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("assistant", "I'll analyze this economic question using my available tools and expertise. Let me gather the relevant data and insights."),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        return create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    async def research(self, query: EconomicQuery) -> Dict[str, Any]:
        """
        Conduct economic research based on the provided query
        """
        try:
            # Format the query for the agent
            formatted_query = f"""
            Economic Research Query: {query.question}
            Time Period: {query.time_period or 'Not specified'}
            Focus Indicators: {', '.join(query.indicators) if query.indicators else 'Not specified'}
            Additional Context: {query.context or 'None'}
            
            Please provide a comprehensive analysis including:
            1. Current status and recent trends
            2. Relevant economic data and forecasts
            3. Policy implications and considerations
            4. Risk factors and scenarios
            5. Recommendations for further analysis
            """
            
            # Execute agent
            result = await self.agent_executor.ainvoke({
                "input": formatted_query
            })
            
            return {
                "success": True,
                "query": query.question,
                "response": result["output"],
                "timestamp": datetime.now().isoformat(),
                "tools_used": self._extract_tools_used(result),
                "confidence": "high"  # Could be calculated based on data quality
            }
            
        except Exception as e:
            logger.error(f"Error in research: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_tools_used(self, result: Dict) -> List[str]:
        """Extract list of tools used in the research"""
        # This would extract tool usage from the agent result
        # Implementation depends on the specific agent framework
        return ["economic_data_fetcher", "policy_analyzer"]  # Placeholder
    
    async def chat(self, message: str) -> str:
        """
        Chat interface for interactive economic research
        """
        try:
            result = await self.agent_executor.ainvoke({
                "input": message
            })
            return result["output"]
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the conversation history"""
        return self.memory.chat_memory.messages
    
    def clear_history(self):
        """Clear the conversation history"""
        self.memory.clear()


# Example usage and testing
async def main():
    """Example usage of the Economic Research Agent"""
    
    # Initialize agent
    agent = EconomicResearchAgent(
        api_base_url="http://localhost:8000",
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY")
    )
    
    # Example research queries
    queries = [
        EconomicQuery(
            question="What is the current inflation outlook for Canada?",
            time_period="next 12 months",
            indicators=["inflation", "core_inflation"]
        ),
        EconomicQuery(
            question="How might rising interest rates affect housing markets?",
            indicators=["interest_rates", "housing_price_index"],
            context="Recent Bank of Canada rate decisions"
        ),
        EconomicQuery(
            question="What are the key risks to economic growth?",
            time_period="next 2 years"
        )
    ]
    
    # Conduct research
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Research Query: {query.question}")
        print(f"{'='*50}")
        
        result = await agent.research(query)
        
        if result["success"]:
            print(f"Response: {result['response']}")
            print(f"Tools Used: {result['tools_used']}")
        else:
            print(f"Error: {result['error']}")
    
    # Interactive chat example
    print(f"\n{'='*50}")
    print("Interactive Chat Session")
    print(f"{'='*50}")
    
    chat_queries = [
        "What's the relationship between unemployment and inflation in Canada?",
        "Should we be concerned about current economic indicators?",
        "What policy tools might be effective in the current environment?"
    ]
    
    for chat_query in chat_queries:
        print(f"\nHuman: {chat_query}")
        response = await agent.chat(chat_query)
        print(f"Agent: {response}")


if __name__ == "__main__":
    asyncio.run(main())
