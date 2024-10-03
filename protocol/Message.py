import struct
from dataclasses import dataclass

# 프로토콜 정의
@dataclass
class Message:
    message_type: int    # 메시지 타입 (1바이트)
    data_length: int     # 데이터 길이 (4바이트)
    data: str            # 실제 데이터 (문자열)

    def encode(self) -> bytes:
        # 메시지를 바이트 스트림으로 인코딩
        header = struct.pack('!BI', self.message_type, self.data_length)
        return header + self.data.encode('utf-8')

    @classmethod
    def decode(cls, data: bytes):
        # 바이트 스트림에서 메시지 디코딩
        # 처음 5바이트에서 메시지 타입(1바이트)과 데이터 길이(4바이트)를 언패킹
        message_type, data_length = struct.unpack('!BI', data[:5])
        # 나머지 바이트를 UTF-8로 디코딩하여 실제 데이터 추출
        data = data[5:].decode('utf-8')
        return cls(message_type, data_length, data)

# 메시지 타입
# 0x00: 연결 요청
# 0x01: 위치 업데이트
# 0x02: 공격 행동
# 0x03: 게임 상태 업데이트