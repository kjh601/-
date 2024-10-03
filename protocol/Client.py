import socket
import json
import threading
from Message import Message

# 서버 연결 정보
SERVER_IP = "127.0.0.1"  # 로컬호스트 IP 주소
SERVER_PORT = 5000  # 서버 포트 번호
SERVER_ADDR = (SERVER_IP, SERVER_PORT)  # 서버 주소 튜플


class GameClient:
    def __init__(self):
        # 소켓 초기화 및 클라이언트 상태 변수 설정
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.character_name = ""
        self.running = True
        self.characters = []  # 게임 내 모든 캐릭터 정보를 저장할 리스트

    def connect(self):
        # 서버에 연결하고 캐릭터 이름 설정
        self.socket.connect(SERVER_ADDR)
        self.character_name = input("캐릭터 이름을 입력하시오 (최대 10자): ")[:10]

        # 연결 메시지 생성 및 전송
        connect_message = Message(0x00, len(self.character_name), self.character_name)
        self.send_message(connect_message)

        # 서버로부터 업데이트를 받는 스레드 시작
        threading.Thread(target=self.receive_updates, daemon=True).start()

    def send_message(self, message: Message):
        # 서버에 메시지 전송
        self.socket.sendall(message.encode())

    def receive_updates(self):
        # 서버로부터 지속적으로 업데이트 수신
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                message = Message.decode(data)
                if message.message_type == 0x03:  # 게임 상태 업데이트 메시지 타입
                    self.update_game_state(message.data)
            except Exception as e:
                print(f"업데이트 수신 중 오류 발생: {e}")
                self.running = False

    def update_game_state(self, data):
        # 수신한 게임 상태 데이터를 처리하여 캐릭터 정보 업데이트
        try:
            self.characters = json.loads(data)
            print(f"업데이트된 캐릭터 정보: {self.characters}")  # 디버그용 출력
        except json.JSONDecodeError:
            print("게임 상태 데이터 디코딩 중 오류 발생")

    def close(self):
        # 클라이언트 종료 처리
        self.running = False
        self.socket.close()