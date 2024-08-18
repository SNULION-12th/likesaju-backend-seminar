from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from langchain_community.llms import HuggingFaceHub
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

from django.conf import settings

### 1안: PydanticOutputParser를 사용하여 response를 자동 파싱하는 방법 (응답 형식이 일관되지 않게 나와서 지금은 사용 불가, 하지만 프롬프팅을 잘 하면 사용 가능할 듯...)

# from langchain.output_parsers import PydanticOutputParser
# from pydantic import BaseModel, Field, field_validator
# from typing import List, Optional
# from pydantic import BaseModel

# class FortuneItem(BaseModel):
#     headline: Optional[str]
#     content: str

# class FortuneTypes(BaseModel):
#     generalFortune: List[FortuneItem]
#     healthFortune: List[FortuneItem]
#     loveFortune: List[FortuneItem]
#     careerFortune: List[FortuneItem]
#     wealthFortune: List[FortuneItem]


# class ChatView(APIView):
#     def post(self, request):
#         model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
#         data = request.data['data']
#         huggingface_key = settings.HUGGINGFACEHUB_API_KEY
        
#         conv_model = HuggingFaceHub(
#             repo_id=model_id, 
#             huggingfacehub_api_token=huggingface_key, 
#             model_kwargs={'temperature': 0.7, "return_full_text" : False}
#         )

#         parser = PydanticOutputParser(pydantic_object=FortuneTypes)
#         format_instructions = parser.get_format_instructions()
        
#         template = """
#         You are a highly experienced and insightful fortune teller. {format_instructions}
#         Provide today's fortune for the user based on their birth date in the following areas:

#         1. **Overall Fortune**:Summarize the user's overall fortune for today.
#         2. **Love Fortune**:Describe the user's love and relationship fortune for today.
#         3. **Health Fortune**:Predict the user's health and well-being for today.
#         4. **Career/Study Fortune**:Discuss the user's professional or academic fortune for today.
#         5. **Wealth Fortune**:Analyze the user's financial fortune for today.

#         The user's birth date is: {data}
#         """
        
#         prompt = PromptTemplate(
#             template=template,
#             input_variables=['data'],
#             partial_variables={'format_instructions': format_instructions}
#         )
        
#         chain = prompt | conv_model
#         result = chain.invoke({"data": data})
        
#         return Response(result, status=status.HTTP_200_OK)

class ChatView(APIView):
    def post(self, request):
        model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
        data = request.data['data']
        huggingface_key = settings.HUGGINGFACEHUB_API_KEY
        
        conv_model = HuggingFaceHub(
            repo_id=model_id, 
            huggingfacehub_api_token=huggingface_key, 
            model_kwargs={'temperature': 0.7, "return_full_text" : False}
        )
        
        template = """
        You are a highly experienced and insightful fortune teller, tasked with predicting today's fortune for the user. 
        Your predictions are based on the user's birth date, which you will use to draw on astrological and spiritual insights. 
        You will provide a detailed and comprehensive reading.
        Answer within 600 words, but make sure to end your response before the word limit.
        Don't include any newlines in your response.
        Only answer about the user's general fortune today, not about their health, love, career, or wealth.

        The user's birth date is: {data}
        Then, the overall fortune for the user today is:
        """.strip()
        
        prompt = PromptTemplate(template=template, input_variables=['data'])
        
        chain = LLMChain(llm=conv_model, prompt=prompt, verbose=False)
        result = chain.run(data)
        
        return Response(result, status=status.HTTP_200_OK)