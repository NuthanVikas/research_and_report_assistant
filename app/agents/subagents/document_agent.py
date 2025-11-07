from app.utils.llms import LLMModel
from app.core.agent_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os

llm = LLMModel().get_model()

def document_agent(state: AgentState) -> Command[str]:
    """Formats professional reports"""
    content = state["messages"][-1].content
    print("\nDocument Agent Active")

    prompt = f"""
    Format the following content into a professional report with these sections:
    
    # Title
    ## Abstract
    ## Key Findings
    ## Recommendations
    ## Conclusion

    Content:
    {content}

    Your task is to convert the summarized information to PDF or doc format.
    """
    

    result = llm.invoke([HumanMessage(content=prompt)])
    formatted_content = result.content
    
    #PDF file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/health_report_{timestamp}.pdf"
    
    #reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    
    #Generate PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    #Split content into paragraphs and add to PDF
    for line in formatted_content.split('\n'):
        if line.strip():
            if line.startswith('#'):
                #Heading
                para = Paragraph(line.replace('#', '').strip(), styles['Heading1'])
            else:
                #Normal text
                para = Paragraph(line, styles['BodyText'])
            story.append(para)
            story.append(Spacer(1, 12))
    
    doc.build(story)
    
    # Return message with file path
    response_message = f"[REPORT]\n\nReport generated successfully!\n\nFile saved at: {filename}\n\nContent:\n{formatted_content}"
    
    return Command(
        goto="report_agent",
        update={"messages": [AIMessage(content=response_message)]}
    )
