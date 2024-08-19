from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from langchain_community.llms import HuggingFaceHub
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

from django.conf import settings

### 1안: PydanticOutputParser를 사용하여 response를 자동 파싱하는 방법 (응답이 나오다가 알 수 없는 이유로 계속 잘려서 지금은 조금 엉성함, 하지만 프롬프팅을 잘 하거나 응답을 좀 잘게 쪼개면 가능할듯...)

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class FortuneItem(BaseModel):
    headline: str = Field(description="headline of the fortune")
    content: str = Field(description="detailed description of the fortune")

class FortuneTypes(BaseModel):
    generalFortune: FortuneItem = Field(description="overall fortune for today. Do not include health, love, career, or wealth.")
    healthFortune: FortuneItem = Field(description="health fortune for today")
    loveFortune: FortuneItem = Field(description="love fortune for today")
    careerFortune: FortuneItem = Field(description="career fortune for today")
    wealthFortune: FortuneItem = Field(description="wealth fortune for today")

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

        output_parser = JsonOutputParser(pydantic_object=FortuneTypes)
        format_instructions = output_parser.get_format_instructions()
        
        template = """
        You are a highly experienced and insightful fortune teller.
        Provide today's fortune for the user based on their birth date.
        You will provide a detailed and comprehensive reading for all the fortune types.
        You may answer as long as you like, but make sure you contain every fortune type (generalFortune, healthFortune, loveFortune, careerFortune, wealthFortune) in your response.
        {format_instructions}

        The user's birth date is: {data}
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=['data'],
            partial_variables={'format_instructions': format_instructions}
        )
        
        chain = prompt | conv_model | output_parser

        result = chain.invoke({'data': data})
        
        return Response(result, status=status.HTTP_200_OK)


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
        
#         template = """
#         You are a highly experienced and insightful fortune teller, tasked with predicting today's fortune for the user. 
#         Your predictions are based on the user's birth date, which you will use to draw on astrological and spiritual insights. 
#         You will provide a detailed and comprehensive reading.
#         Answer within 600 words, but make sure to end your response before the word limit.
#         Don't include any newlines in your response.
#         Only answer about the user's general fortune today, not about their health, love, career, or wealth.

#         The user's birth date is: {data}
#         Then, the overall fortune for the user today is:
#         """.strip()
        
#         prompt = PromptTemplate(template=template, input_variables=['data'])
        
#         chain = LLMChain(llm=conv_model, prompt=prompt, verbose=False)
#         result = chain.run(data)
        
#         return Response(result, status=status.HTTP_200_OK)