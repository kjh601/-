import pygame
from Client import GameClient
from Message import Message

# Pygame 초기화
pygame.init()

# 상수 정의
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 20
FONT_SIZE = 20

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class GameClientGUI:
    def __init__(self):
        self.client = GameClient()
        pygame.init()
        # 게임 화면 설정
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Multiplayer Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.attack_effect = None
        self.attack_time = 0

    def run(self):
        # 서버에 연결하고 게임 루프 시작
        self.client.connect()

        while self.client.running:
            self.handle_events()
            self.update_screen()
            self.clock.tick(60)  # 60 FPS로 게임 실행

        pygame.quit()
        self.client.close()

    def handle_events(self):
        # 사용자 입력 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.client.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 좌클릭: 이동
                    x, y = event.pos
                    self.client.send_message(Message(0x01, len(f"{x} {y}"), f"{x} {y}"))
                elif event.button == 3:  # 우클릭: 공격
                    x, y = event.pos
                    self.client.send_message(Message(0x02, len(f"{x} {y}"), f"{x} {y}"))
                    self.attack_effect = (x, y)
                    self.attack_time = pygame.time.get_ticks()

    def update_screen(self):
        # 화면 업데이트
        self.screen.fill(WHITE)

        for character in self.client.characters:
            # 캐릭터 색상 설정 (자신은 파란색, 다른 플레이어는 빨간색)
            color = BLUE if character['name'] == self.client.character_name else RED
            x, y = int(character['x']), int(character['y'])

            # 캐릭터 사각형 그리기
            rect_x = x - PLAYER_SIZE // 2
            rect_y = y - PLAYER_SIZE // 2
            pygame.draw.rect(self.screen, color, (rect_x, rect_y, PLAYER_SIZE, PLAYER_SIZE))

            # 정확한 위치 표시 (점)
            pygame.draw.circle(self.screen, BLACK, (x, y), 3)

            # 캐릭터 이름 표시
            name_text = self.font.render(character['name'], True, BLACK)
            self.screen.blit(name_text, (rect_x, rect_y - FONT_SIZE))

            # 캐릭터 체력 표시
            health_text = self.font.render(f"HP: {character['health']}", True, GREEN)
            self.screen.blit(health_text, (rect_x, rect_y + PLAYER_SIZE))

        # 공격 효과 그리기
        if self.attack_effect:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time < 500:  # 500ms 동안 효과 표시
                pygame.draw.circle(self.screen, (255, 255, 0), self.attack_effect, 20, 2)
            else:
                self.attack_effect = None

        pygame.display.flip()  # 화면 업데이트

if __name__ == "__main__":
    client_gui = GameClientGUI()
    client_gui.run()