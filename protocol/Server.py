import socket
import json
import threading
from dataclasses import asdict, dataclass
import random

from Message import Message

@dataclass
class Character:
    name: str
    x: int
    y: int
    health: int = 500
    attack_power: int = 10

class GameServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.characters = {}  # 캐릭터 정보를 저장하는 딕셔너리
        self.clients = {}     # 클라이언트 소켓과 캐릭터 이름을 매핑하는 딕셔너리

    def start(self):
        # 서버 소켓 생성 및 바인딩
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        print(f'서버가 {self.host}:{self.port}에서 시작되었습니다.')

        # 게임 상태를 주기적으로 브로드캐스트하는 스레드 시작
        threading.Thread(target=self.broadcast_state, daemon=True).start()

        # 클라이언트 연결을 무한히 대기
        while True:
            client_socket, addr = server_socket.accept()
            print(f"새로운 연결: {addr}")
            # 각 클라이언트에 대해 새로운 스레드 생성
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        # 클라이언트로부터 메시지를 지속적으로 수신
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = Message.decode(data)
                self.process_message(message, client_socket)
            except Exception as e:
                print(f"클라이언트 처리 중 오류 발생: {e}")
                break
        # 연결이 종료되면 클라이언트 제거
        self.remove_client(client_socket)
        client_socket.close()

    def process_message(self, message: Message, client_socket):
        # 메시지 타입에 따라 적절한 처리 함수 호출
        if message.message_type == 0x00:  # 연결 요청
            self.handle_connection(message.data, client_socket)
        elif message.message_type == 0x01:  # 위치 업데이트
            self.handle_position_update(message.data, client_socket)
        elif message.message_type == 0x02:  # 행동 명령
            self.handle_action(message.data, client_socket)

    def handle_connection(self, character_name: str, client_socket):
        # 새로운 캐릭터 생성 및 등록
        character = Character(name=character_name, x=random.randint(0, 800), y=random.randint(0, 600))
        self.characters[character_name] = character
        self.clients[client_socket] = character_name
        print(f"새로운 캐릭터 연결: {character_name}")

    def handle_position_update(self, data: str, client_socket):
        # 캐릭터 위치 업데이트
        character_name = self.clients[client_socket]
        x, y = map(int, data.split())
        self.characters[character_name].x = x
        self.characters[character_name].y = y

    def handle_action(self, data: str, client_socket):
        # 공격 행동 처리
        attacker_name = self.clients[client_socket]
        target_x, target_y = map(int, data.split())

        for character in self.characters.values():
            if character.name != attacker_name and \
                    abs(character.x - target_x) < 5 and abs(character.y - target_y) < 5:
                character.health -= self.characters[attacker_name].attack_power
                print(f"{attacker_name}이(가) {character.name}을(를) 공격했습니다.")
                if character.health <= 0:
                    print(f"{character.name}이(가) 패배했습니다.")
                break

    def remove_client(self, client_socket):
        # 클라이언트 연결 종료 시 처리
        if client_socket in self.clients:
            character_name = self.clients[client_socket]
            del self.characters[character_name]
            del self.clients[client_socket]

    def broadcast_state(self):
        # 게임 상태를 모든 클라이언트에게 주기적으로 전송
        while True:
            state_data = json.dumps([asdict(char) for char in self.characters.values()])
            state_message = Message(0x03, len(state_data), state_data)
            encoded_message = state_message.encode()

            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.sendall(encoded_message)
                except Exception:
                    self.remove_client(client_socket)

            threading.Event().wait(0.02)  # 20ms 간격으로 대기 (약 50Hz)

if __name__ == "__main__":
    game_server = GameServer()
    try:
        game_server.start()
    except KeyboardInterrupt:
        print("서버를 종료합니다...")