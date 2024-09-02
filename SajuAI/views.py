from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from langchain.chat_models import ChatOpenAI

# from langchain_community.llms import HuggingFaceHub
from langchain_core.prompts import PromptTemplate

from django.conf import settings

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import AIRequestSerializer

# 응답 형식 정의
class FortuneMain(BaseModel):
    headline: str = Field(description="headline of the fortune")
    content: str = Field(description="detailed description of the fortune")

class FortuneShort(BaseModel):
    content: str = Field(description="detailed description of the fortune")

class FortuneTypes(BaseModel):
    generalFortune: FortuneMain = Field(description="overall fortune for today. Do not include health, love, career, or wealth.")
    healthFortune: FortuneShort = Field(description="health fortune for today")
    loveFortune: FortuneShort = Field(description="love fortune for today")
    careerFortune: FortuneShort = Field(description="career fortune for today")
    wealthFortune: FortuneShort = Field(description="wealth fortune for today")

class ChatView(APIView):
    @swagger_auto_schema(
    operation_id="AI 운세 결과 생성",
    operation_description="""
    생년월일 정보를 기반으로 오늘의 운세를 생성합니다.
    주의사항: OPENAI API를 사용하므로 요청 건마다 요금이 부과됩니다.
    """,
    request_body=AIRequestSerializer,
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'generalFortune': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'headline': openapi.Schema(type=openapi.TYPE_STRING, description="오늘의 운세 한 줄 요악"),
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description="종합 운세"),
                    },
                ),
                'healthFortune': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description="건강 운세"),
                    },
                ),
                'loveFortune': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description="애정 운세"),
                    },
                ),
                'careerFortune': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description="직업 운세"),
                    },
                ),
                'wealthFortune': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description="건강 운세"),
                    },
                ),
            },
            description="운세 결과를 포함하는 응답"
        ),
        500: "일시적인 오류로 결과를 불러올 수 없습니다."
        }
    )
    def post(self, request):

        data = request.data['data']
        openai_key = settings.OPENAI_API_KEY

        # 모델 생성
        model_id = "gpt-3.5-turbo"
        model = ChatOpenAI(
            model_name=model_id,
            openai_api_key=openai_key,
        )

#         model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
#         model = HuggingFaceHub(
#             repo_id=model_id,
#             huggingfacehub_api_token=huggingface_key,
#             model_kwargs={'temperature': 0.75, "return_full_text" : False,'max_new_tokens': 800}
#         )

        output_parser = JsonOutputParser(pydantic_object=FortuneTypes)
        format_instructions = output_parser.get_format_instructions()
        
        template = """
        **반드시!! 한국어만 사용해서 응답해**
        Based on the date {data}, tell my fortune for today in korean in the following JSON format:
        {format_instructions}
        예시:
                "
                generalFortune :
                - headline: 주도적이고 철저한 계획이 필요한 날,변화에 유연하게 대처하세요!
                - content: 매사에 있어서 주도면밀한 태도를 가질 필요가 있는 날이 될 것으로 보입니다. 처음에는 쉽게 뜻대로 잘 풀려 나갔던 일들이 후반으로 갈수록 어려워지는 날입니다. 일관된 태도를 견지해야 합니다 그래야만 손해를 줄이고 이윤을 볼 수 있겠습니다. 아주 시급한 사건만 아니라면 여유를 가지고 사안을 분석해보세요. 가능한한 많은 변인을 찾아보고 그것에 대해 미리 대책을 세워 놓고 있는 것이 해답을 빨리 찾을 수 있는 지름길이 아닐까 싶습니다.
                healthFortune :
                - content: 건강 면에서 무난한 하루가 될 것입니다. 특별한 건강 문제나 불편함 없이 일상을 보낼 수 있을 것입니다. 그러나 긴장이나 스트레스를 피하는 것이 중요합니다. 식이조절과 규칙적인 운동을 통해 건강을 유지하는 데 신경 써야 합니다.
                careerFortune:
                - content: 취업이나 학업에서는 오늘 새로운 기회가 찾아올 수 있는 긍정적인 날입니다. 노력이 보상받을 수 있는 시기이니 성실하게 임하는 것이 중요합니다. 특히 의견을 주고 받는 상황에서 자신의 의견을 확실히 표현하는 것이 좋습니다.
                loveFortune :
                - content: 연애 운세는 조금 불안정할 수 있습니다. 상대방과의 의사소통에 어려움이 있을 수 있으니 이해하려는 노력이 필요합니다. 감정의 변화에 따라 변동성이 있을 수 있으니 서로의 감정을 주고 받는 것에 주의를 기울이세요.
                wealthFortune :
                - content: 자산 관리에 대한 새로운 아이디어나 기회가 찾아올 수 있는 날입니다. 금융 상품이나 투자에 관심을 가지고 다양한 정보를 모으는 것이 좋습니다. 소비와 절약에 대한 균형을 유지하는 것이 중요합니다.
                "
        **반드시!! 한국어만 사용해서 응답해**
        위와 다른 **새로운** 글을 써주길 바란다. 각각의 문장의 구성또한 달라질 수 있으며 다양한 표현을 사용할 수록 좋다. 각 항목은 세 문장 이상이면 좋다. 반드시 **한국어**로 대답하여라.
        정해진 json 형식을 벗어나는 답변은 허용하지 않으므로 {format_instructions}대로만 답변해라
        **반드시!! 한국어만 사용해서 응답해**


        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=['data'],
            partial_variables={'format_instructions': format_instructions}
        )
        
        chain = prompt | model | output_parser

        try:
            result = chain.invoke({'data': data})
            return Response(result, status=status.HTTP_200_OK)
        except:
            return Response({"error": "일시적인 오류로 결과를 불러올 수 없습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)