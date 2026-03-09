from fastapi import APIRouter

from src.util.genai import try_gemini_inference
import json
from src.models.api import WeeklySummaryRequest, WeeklySummaryResponse, DailyHabitAiInferenceRequest, DailyHabitAiInferenceResponse


genai_router = APIRouter(prefix="/genai", tags=["genai"])

@genai_router.get("/health")
async def genai_health_check():
    try:
        gem_inf = try_gemini_inference("Hello, world! explains how AI works in brief.")
        return {"status": "genai router is healthy", "sample_response": gem_inf}
    except Exception as e:
        return {"status": "genai router is unhealthy", "error": str(e)}
    # return {"status": "genai router is healthy"}

@genai_router.post(
        "/weekly-summary", 
        response_model=WeeklySummaryResponse
)

async def genai_weekly_summary(user_input: WeeklySummaryRequest): 
    # hobby = user_input.get("hobbyName")
    # description = user_input.get("hobbyDescription")
    # feedback = user_input.get("hobbyFeedback")
    hobby =  user_input.hobbyName
    description = user_input.hobbyDescription
    feedback = user_input.hobbyFeedback
    try:
        # lets write a weekly summarizing prompt that will return a json response back to user after gemini inference
        prompt = f"""
        You are an expert AI assistant that provides weekly summaries of hobbies.
        Given the following hobby description, provide a weekly summary of the hobby.
        Return the summary in JSON format with the following properties:
        - summary: Provide a weekly summary of the hobby. use a short and concise manner
        Hobby Description: {description}WeeklySummaryRequest
        Hobby Name: {hobby}
        Feedback: {feedback}
        """

        raw_text = try_gemini_inference(prompt)

        # Remove the code block markers
        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1
        json_string = raw_text[start:end]

        # Parse it
        try:
            data = json.loads(json_string)
            print(data, data["summary"])
            return {"response": data}
            # return {"summary": data["summary"]}
        except json.JSONDecodeError as e:
            print("JSON Error:", e)

    except Exception as e:
        return {"status": "genai router is unhealthy", "error": str(e)}


@genai_router.post("/inference", response_model=DailyHabitAiInferenceResponse)
async def genai_inference(
    # user_input: dict[str, str]
    user_input: DailyHabitAiInferenceRequest
):
    # hobby = user_input.get("hobby")
    # description = user_input.get("description")
    # feedback = user_input.get("feedback")
    hobby = user_input.hobby
    description = user_input.description
    feedback = user_input.feedback
    try:
        print(user_input)
        
        # lets write a prompt for giving feedback that are actionable to improve provided hobby, return data should be in json format and maintain a strict propr: values format
        prompt = f"""
        You are an expert AI assistant that provides actionable feedback to improve hobbies.
        Given the following hobby description, provide specific and actionable feedback to help improve it.
        Return the feedback in JSON format with the following properties:
        - strengths: List the strengths of the hobby.
        - areas_for_improvement: List specific areas where the hobby can be improved.
        - actionable_steps: Provide clear and actionable steps to enhance the hobby.
        - actions_legacy: provide specific actions of about 2 to 6 taken from actionable_steps and repurpose it in an array with each object containing an id, title, time with am/pm time format, and a completed boolean value in them
        - examples: Provide examples of how to use the hobby effectively.
        - actions: Provide a clear and concise instruction as its in example of how to use the hobby effectively RATHER THAN HOW IT SHOULD HAVE BEEN. about 2 to 6 taken from actionable_steps and repurpose it in an array with each object containing an id, title, time with am/pm time format, and a completed boolean value in them. it would be on daily basis.
        Hobby Description: {description}
        Hobby Name: {hobby}
        Feedback: {feedback}
        """

        raw_text = try_gemini_inference(prompt)

        # Remove the code block markers
        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1
        json_string = raw_text[start:end]

        # Parse it
        try:
            data = json.loads(json_string)
            print(data["strengths"])
            return {"response": data}
        except json.JSONDecodeError as e:
            print("JSON Error:", e)


    except Exception as e:
        return {"error": str(e)}