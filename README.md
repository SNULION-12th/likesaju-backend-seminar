# 🦁 멋쟁이 사주처럼 🦁

중요!!! requirements에 추가 안됨 ㅜㅠ 
pip install 'uvicorn[standard]' 하세요!!

중요!! uvicorn server 켜는 command
uvicorn likesaju.asgi:application --port 8000 --workers 4 --log-level debug --reload


시원 0811)
webchat application 생성
webchat에 모델 생성 : Conversation, Messages
webchat messageView 추가 : Conversation id 지정하면 Messages 목록 반환 (Swagger 반영 완료)
likesaju url에 webchat messageView 로 가는 url 추가 

시원 해야할 것)
messageView 테스트 API 만들기
웹소켓 프로토콜용 view 만들기 (채널 생성 및 채팅)

시원 0812)
./manage.py startapp webchat
consumer.py 생성 : view의 역할과 비슷하다고 보면 된다 
consumer : 메세지를 받아서 어떻게 답할지 결정하는 파이썬 클래스라고 보면된다.

websocket protocol은 http protocol과 달리 stateful!
logging credential , session info 등을 서버에서 기억한다
=> 이것이 채팅에서 웹소켓 프로토콜을 사용하는 이유임

http를 사용한다면, 서버에게 새로운 메세지가 왔는지 요청하지 않는 이상,
서버가 수신인에게 먼저 메세지를 전달할 수 없다.

웹소켓 프로토콜을 사용한다면 챗서버에 속한 사람이 누구인지 기억할 수 있으며, 채팅방에 속한 사람에게 바로 메세지를 보낼 수 있다. (서버에게 묻는 과정 없이도) 



프론트엔드에서 웹소켓 요청 테스트 )
npm => react-use-websocket 사용

import useWebSocket from "react-use-websocket";
// const socketUrl = `ws://127.0.0.1:8000/${serverId}/${channelId}`
const socketUrl = `ws://127.0.0.1:8000/ws/test`

const { } = useWebSocket(socketUrl, {
    onOpen: () => {
      console.log("Connected");
    },
    onClose: () => {
      console.log("Closed!");
    },
    onError: () => {
      console.log("Error!");
    },
    onMessage: () => {
    },
  });


- http 요청 테스트 
- 모델 변경되었으므로 python manage.py migrate , python manage.py makemigrations
- 유비콘 서버 켜지 말고 그냥 python manage.py runserver
- http://127.0.0.1:8000/swagger/

- ws 요청 테스트 (아직 테스트 안해봄)
- 유비콘 서버 켜서 
- uvicorn likesaju.asgi:application --port 8000 --workers 4 --log-level debug --reload
- ws://127.0.0.1:8000/ws/test/
- 메세지 보낼때 이제 channel_id 명시해야함
message = content.get("message")
channel_id = content.get("channel_id")

