# Enhanced Deep Research Agent System
# A multi-agent workflow for automated research, analysis, and reporting

# =============================================================================
# IMPORTS AND SETUP
# =============================================================================
from agents import Agent, WebSearchTool, trace, Runner, gen_trace_id, function_tool
from agents.model_settings import ModelSettings
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Dict, List, Optional
from IPython.display import display, Markdown
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# =============================================================================
# ENHANCED PYDANTIC MODELS
# =============================================================================
class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")
    priority: int = Field(default=1, description="Search priority (1=high, 2=medium, 3=low)")

class WebSearchPlan(BaseModel):
    searches: List[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")
    estimated_time: str = Field(description="Estimated time to complete all searches")

class SearchResult(BaseModel):
    query: str = Field(description="The search query used")
    summary: str = Field(description="Summary of search results")
    sources_count: int = Field(description="Number of sources found")
    relevance_score: float = Field(description="Relevance score (0-1)")

class ReportData(BaseModel):
    title: str = Field(description="Report title")
    executive_summary: str = Field(description="Executive summary (2-3 sentences)")
    detailed_report: str = Field(description="The detailed report in markdown format")
    key_findings: List[str] = Field(description="List of key findings")
    recommendations: List[str] = Field(description="Actionable recommendations")
    follow_up_questions: List[str] = Field(description="Suggested topics to research further")
    sources: List[str] = Field(description="List of sources used")
    generated_at: str = Field(description="Timestamp when report was generated")

# =============================================================================
# ENHANCED SEARCH AGENT
# =============================================================================
SEARCH_INSTRUCTIONS = """You are an expert research assistant specializing in technology career analysis. 
Given a search term, you search the web and produce a comprehensive summary focused on:

- Current and projected demand for professionals in AI, Cybersecurity, and Blockchain
- Job market odds and employment prospects for each domain individually and in combination
- Salary ranges, job roles, and growth trends in these fields
- Industry insights, market data, and career statistics

Your summary should:
- Be 2-3 paragraphs and under 400 words
- Include specific salary data, job growth percentages, and market statistics
- Focus on current trends (2024-2025) and future projections
- Identify the most credible and recent sources
- Write clearly for career professionals and job seekers
- Emphasize practical career insights and market opportunities"""

search_agent = Agent(
    name="Tech Career Research Specialist",
    instructions=SEARCH_INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="medium")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)

# =============================================================================
# ENHANCED PLANNER AGENT
# =============================================================================
class ResearchConfig:
    MAX_SEARCHES = 5
    MIN_SEARCHES = 3
    SEARCH_TIMEOUT = 30  # seconds

PLANNER_INSTRUCTIONS = f"""You are a strategic research planner specializing in technology career analysis. 
Given a research query about AI, Cybersecurity, and Blockchain careers, create an optimal search strategy that will provide comprehensive coverage of:

- Current and projected demand for professionals in these fields
- Job market odds and employment prospects
- Salary ranges, job roles, and growth trends
- Industry insights and career statistics

Your plan should:
- Generate {ResearchConfig.MIN_SEARCHES}-{ResearchConfig.MAX_SEARCHES} targeted search queries
- Prioritize searches by importance (1=critical, 2=important, 3=supplementary)
- Include searches for current market data, salary information, and growth projections
- Cover both individual domains and combined skill sets
- Focus on recent data (2024-2025) and future trends
- Estimate the time needed to complete all searches"""

planner_agent = Agent(
    name="Career Market Research Planner",
    instructions=PLANNER_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)

# =============================================================================
# ENHANCED EMAIL FUNCTION TOOL
# =============================================================================
@function_tool
def send_research_email(subject: str, html_body: str, recipient_email: str = None) -> Dict[str, str]:
    """ Send a formatted research report via email """
    try:
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        
        # Use environment variables or defaults
        from_email = Email(os.environ.get('FROM_EMAIL', 'research@example.com'))
        to_email = To(recipient_email or os.environ.get('TO_EMAIL', 'recipient@example.com'))
        
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_email, subject, content)
        
        response = sg.client.mail.send.post(request_body=mail.get())
        
        if response.status_code in [200, 201, 202]:
            return {"status": "success", "message": "Email sent successfully"}
        else:
            return {"status": "error", "message": f"Email failed with status {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        return {"status": "error", "message": str(e)}

# =============================================================================
# ENHANCED EMAIL AGENT - OgaAgent
# =============================================================================
EMAIL_INSTRUCTIONS = """You are a professional email composer specializing in technology career research reports. 
Given a detailed research report about AI, Cybersecurity, and Blockchain career prospects, create a well-formatted HTML email that:
- Has a compelling subject line highlighting key career insights or salary information
- Includes an executive summary focusing on job market odds and demand
- Formats the report with proper HTML structure (headings, lists, emphasis)
- Uses professional styling with clear sections for salary data, job roles, and growth trends
- Includes a clear call-to-action for career planning or skill development
- Maintains the technical accuracy of market data and statistics
- Emphasizes practical career advice and market opportunities"""

OgaAgent = Agent(
    name="OgaAgent",
    instructions=EMAIL_INSTRUCTIONS,
    tools=[send_research_email],
    model="gpt-4o-mini",
)

# =============================================================================
# ENHANCED WRITER AGENT
# =============================================================================
WRITER_INSTRUCTIONS = """You are a senior technology career analyst and report writer. Your task is to create 
comprehensive, professional research reports focused on AI, Cybersecurity, and Blockchain career prospects. Given a research query and search results, you should:

1. Create a compelling title that captures the career market insights
2. Write an executive summary (2-3 sentences) highlighting key job market findings and salary insights
3. Structure the report with clear sections covering:
   - Current and projected demand for professionals
   - Job market odds and employment prospects for each domain
   - Salary ranges, job roles, and growth trends
   - Combined skill set advantages
4. Synthesize information from multiple sources into coherent career insights
5. Include specific salary data, job growth percentages, and market statistics
6. Provide actionable career recommendations based on market demand
7. Suggest skill development priorities and career paths
8. List all sources used with emphasis on recent market data

The report should be:
- 1000-2000 words in length
- Written for career professionals and job seekers
- Well-structured with clear headings for each career domain
- Data-driven with specific salary ranges and growth statistics
- Actionable with clear career planning recommendations"""

writer_agent = Agent(
    name="Technology Career Analyst",
    #Two lines were removed for privacy reasons. 
    output_type=ReportData,
)

# =============================================================================
# ENHANCED SEARCH EXECUTION FUNCTIONS
# =============================================================================
async def plan_research_strategy(query: str) -> WebSearchPlan:
    """ Create an optimal search strategy for the research query """
    logger.info("�� Planning research strategy...")
    
    try:
        result = await Runner.run(planner_agent, f"Research Query: {query}")
        search_plan = result.final_output
        
        # Validate search plan
        if len(search_plan.searches) < ResearchConfig.MIN_SEARCHES:
            logger.warning(f"Only {len(search_plan.searches)} searches planned, minimum is {ResearchConfig.MIN_SEARCHES}")
        
        #Six lines of codes were removed for privacy reasons.

async def execute_searches(search_plan: WebSearchPlan) -> List[SearchResult]:
    """ Execute all planned searches with error handling and progress tracking """
    logger.info("�� Executing searches...")
    
    # Sort searches by priority
    sorted_searches = sorted(search_plan.searches, key=lambda x: x.priority)
    
    search_tasks = []
    for i, search_item in enumerate(sorted_searches, 1):
        logger.info(f"  📋 Search {i}/{len(sorted_searches)}: {search_item.query}")
        task = asyncio.create_task(execute_single_search(search_item))
        search_tasks.append(task)
    
    try:
        # Execute searches with timeout
        results = await asyncio.wait_for(
            asyncio.gather(*search_tasks, return_exceptions=True),
            timeout=ResearchConfig.SEARCH_TIMEOUT * len(search_tasks)
        )
        
        # Filter out exceptions and create SearchResult objects
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Search {i+1} failed: {str(result)}")
            else:
                valid_results.append(result)
        
        logger.info(f"✅ Completed {len(valid_results)}/{len(search_tasks)} searches successfully")
        return valid_results
        
    except asyncio.TimeoutError:
        logger.error("⏰ Search execution timed out")
        raise

async def execute_single_search(search_item: WebSearchItem) -> SearchResult:
    """ Execute a single search and return structured results """
    try:
        search_input = f"Search Query: {search_item.query}\nReason: {search_item.reason}\nPriority: {search_item.priority}"
        result = await Runner.run(search_agent, search_input)
        
        return SearchResult(
            query=search_item.query,
            summary=result.final_output,
            sources_count=1,  # WebSearchTool doesn't provide source count
            relevance_score=0.8  # Default relevance score
        )
        
    except Exception as e:
        logger.error(f"Search failed for '{search_item.query}': {str(e)}")
        raise

# =============================================================================
# ENHANCED REPORT GENERATION
# =============================================================================
async def generate_comprehensive_report(query: str, search_results: List[SearchResult]) -> ReportData:
    """ Generate a comprehensive research report from search results """
    logger.info("�� Generating comprehensive report...")
    
    try:
        # Prepare input for writer agent
        search_summaries = [f"Query: {r.query}\nSummary: {r.summary}" for r in search_results]
        writer_input = f"""
Original Research Query: {query}

Search Results:
{chr(10).join(search_summaries)}

Please create a comprehensive career market research report based on this information, focusing on job demand, salary ranges, and career prospects.
"""
        
       #Hey, I removed 11 lines of codes for privacy reasons.
async def send_research_report(report: ReportData, recipient_email: str = None) -> Dict[str, str]:
    """ Send the research report via email using OgaAgent """
    logger.info("📧 Sending research report via OgaAgent...")
    
    try:
        # Create email content
        email_content = f"""
        <h1>{report.title}</h1>
        <h2>Executive Summary</h2>
        <p>{report.executive_summary}</p>
        <h2>Key Findings</h2>
        <ul>{"".join([f"<li>{finding}</li>" for finding in report.key_findings])}</ul>
        <h2>Detailed Report</h2>
        {report.detailed_report}
        <h2>Career Recommendations</h2>
        <ul>{"".join([f"<li>{rec}</li>" for rec in report.recommendations])}</ul>
        <hr>
        <p><small>Report generated on {report.generated_at}</small></p>
        """
        
        subject = f"Career Market Report: {report.title}"
        result = await Runner.run(OgaAgent, email_content)
        
        logger.info("✅ Report sent successfully via OgaAgent")
        return {"status": "success", "message": "Report sent via email"}
        
    except Exception as e:
        logger.error(f"❌ Email sending failed: {str(e)}")
        return {"status": "error", "message": str(e)}

# =============================================================================
# MAIN ENHANCED WORKFLOW
# =============================================================================
async def run_enhanced_research(query: str, send_email: bool = True, recipient_email: str = None) -> ReportData:
    """ Complete enhanced research workflow with error handling and progress tracking """
    
    logger.info(f"🚀 Starting enhanced research for: {query[:100]}...")
    
    #Hello, 20 lines were removed for privacy reasons.
    except Exception as e:
        logger.error(f"❌ Research workflow failed: {str(e)}")
        raise

# =============================================================================
# EXAMPLE USAGE AND TESTING
# =============================================================================
async def main():
    """ Example usage of the enhanced research system """
    
    # Updated research query focusing on career prospects
    query = """
    What is the current and projected demand for professionals in AI, Cybersecurity, and Blockchain?
    
    What are the odds of securing a job in each domain individually and in combination?
    
    What are the salary ranges, job roles, and growth trends in these fields?
    
    Include analysis of:
    - Current market demand and future projections
    - Employment prospects and job market odds
    - Salary ranges and compensation trends
    - Key job roles and career paths
    - Growth trends and industry outlook
    - Combined skill set advantages
    """
    
    try:
        # Run enhanced research
        report = await run_enhanced_research(
            query=query,
            send_email=True,  # Set to False to skip email
            recipient_email="your-email@example.com"  # Replace with actual email
        )
        
        # Display results
        print(f"\n📊 Career Market Report: {report.title}")
        print(f"📝 Executive Summary: {report.executive_summary}")
        print(f"🔍 Key Findings: {len(report.key_findings)} findings")
        print(f"💡 Career Recommendations: {len(report.recommendations)} recommendations")
        
        return report
        
    except Exception as e:
        logger.error(f"Research failed: {str(e)}")
        return None

# Run if executed directly
if __name__ == "__main__":
    asyncio.run(main())
