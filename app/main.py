from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.core.graph import create_workflow

from app.utils.llms import LLMModel

app = FastAPI()

class QueryRequest(BaseModel):
    question: str


llm = LLMModel().get_model()


@app.get("/")
def read_root():
    return {"message": "Hello Vikas from research and report assistant project!"}


@app.post("/ask")
def ask_supervisor(request: QueryRequest):
    """Send user question to Supervisor Agent workflow"""
    question = request.question
    state = {"messages": [HumanMessage(content=question)]}
    
    
    workflow = create_workflow()
    result = workflow.invoke(state)

    final_response = result["messages"][-1].content
    
    return {"question": question, "answer": final_response}


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

