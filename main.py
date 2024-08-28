import llm
import database
from openai import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from dotenv import load_dotenv


load_dotenv()

BACKEND_SERVER = os.getenv("SERVER_URL")
app = FastAPI(servers=[{"url":BACKEND_SERVER}])

class PostHumanQueryPayload(BaseModel):
    human_query: str
    
class PostHumanQueryResponse(BaseModel):
    result: list
    
@app.post(
    "/human_query",
    name="Human Query",
    operation_id="post_human_query",
    description="Gets a natural language query, internally transforms it to a SQL query, queries the database, and returns the result.",
)
async def human_query(payload: PostHumanQueryPayload) ->dict[str,str]:
    #paylod.human_query = "Cual es el total de ingresos y egresos?"
    
    # Transform human query to sql query
    sql_query = await llm.human_query_to_sql(payload.human_query)
    
    # Verify format SQL query
    if not sql_query:
        return {"error":"SQL query generation failed"}
    result_dict = json.loads(sql_query)
    
    # Make SQL query
    result = await database.query(result_dict["sql_query"])
    
    # Transform query result to human-friendly response
    answer = await llm.build_answer(result,payload.human_query)
    if not answer:
        return {"error":"Response generation failed "}
    
    return {"answer":answer}