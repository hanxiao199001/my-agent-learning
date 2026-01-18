"""
Agent 通信基础
学习目标:
1. Agent如何传递信息
2. 共享状态管理
3. 消息格式设计
"""

from typing import Dict, List, Any
from datetime import datetime
import json

class Message:
    """Agent间的消息"""
    
    def __init__(self, sender: str, receiver: str, content: Any, msg_type: str = "info"):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.msg_type = msg_type  # info, request, response, error
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.msg_type,
            "timestamp": self.timestamp
        }
    
    def __repr__(self):
        return f"[{self.sender} → {self.receiver}] {self.msg_type}: {self.content}"


class SharedState:
    """
    多Agent共享的状态
    类似BettaFish中的全局状态
    """
    
    def __init__(self):
        self.data = {}
        self.history = []  # 所有消息历史
        
    def update(self, key: str, value: Any, agent_name: str):
        """更新状态"""
        self.data[key] = value
        self.history.append({
            "action": "update",
            "key": key,
            "agent": agent_name,
            "timestamp": datetime.now().isoformat()
        })
        print(f"📝 {agent_name} 更新状态: {key} = {value}")
    
    def get(self, key: str, default=None):
        """获取状态"""
        return self.data.get(key, default)
    
    def get_all(self):
        """获取所有状态"""
        return self.data.copy()
    
    def add_message(self, message: Message):
        """记录消息"""
        self.history.append({
            "action": "message",
            "message": message.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
    
    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return [h for h in self.history if h.get("action") == "message"]
    
    def print_status(self):
        """打印当前状态"""
        print("\n" + "="*60)
        print("📊 共享状态:")
        print("="*60)
        for key, value in self.data.items():
            print(f"  {key}: {value}")
        print("="*60 + "\n")


class MessageBus:
    """
    消息总线 - Agent间通信的中枢
    类似BettaFish的论坛机制
    """
    
    def __init__(self):
        self.messages: List[Message] = []
        self.subscribers: Dict[str, List] = {}  # agent_name -> callback函数列表
        
    def subscribe(self, agent_name: str, callback):
        """Agent订阅消息"""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)
        print(f"✅ {agent_name} 已订阅消息总线")
    
    def publish(self, message: Message):
        """发布消息"""
        self.messages.append(message)
        print(f"\n📨 消息发送: {message}")
        
        # 通知接收者
        if message.receiver in self.subscribers:
            for callback in self.subscribers[message.receiver]:
                callback(message)
        elif message.receiver == "all":
            # 广播给所有Agent
            for agent_name, callbacks in self.subscribers.items():
                if agent_name != message.sender:
                    for callback in callbacks:
                        callback(message)
    
    def get_messages_for(self, agent_name: str) -> List[Message]:
        """获取某个Agent的所有消息"""
        return [msg for msg in self.messages 
                if msg.receiver == agent_name or msg.receiver == "all"]
    
    def print_all_messages(self):
        """打印所有消息"""
        print("\n" + "="*60)
        print("📬 消息历史:")
        print("="*60)
        for i, msg in enumerate(self.messages, 1):
            print(f"{i}. {msg}")
        print("="*60 + "\n")


# ========== 测试通信系统 ==========

def test_communication():
    """测试Agent通信"""
    
    print("\n🧪 测试 Agent 通信系统\n")
    
    # 1. 创建共享状态和消息总线
    state = SharedState()
    bus = MessageBus()
    
    # 2. 模拟Agent A的消息处理
    def agent_a_handler(message: Message):
        print(f"✅ Agent A 收到消息: {message.content}")
        if message.msg_type == "request":
            # 回复消息
            response = Message(
                sender="AgentA",
                receiver=message.sender,
                content=f"已处理你的请求: {message.content}",
                msg_type="response"
            )
            bus.publish(response)
    
    # 3. 模拟Agent B的消息处理
    def agent_b_handler(message: Message):
        print(f"✅ Agent B 收到消息: {message.content}")
    
    # 4. 订阅消息
    bus.subscribe("AgentA", agent_a_handler)
    bus.subscribe("AgentB", agent_b_handler)
    
    # 5. Agent B 向 Agent A 发送请求
    msg1 = Message(
        sender="AgentB",
        receiver="AgentA",
        content="请帮我查询天气",
        msg_type="request"
    )
    bus.publish(msg1)
    
    # 6. Agent A 更新状态
    state.update("weather", "晴天 25°C", "AgentA")
    
    # 7. 广播消息
    msg2 = Message(
        sender="AgentA",
        receiver="all",
        content="天气查询完成",
        msg_type="info"
    )
    bus.publish(msg2)
    
    # 8. 查看结果
    state.print_status()
    bus.print_all_messages()


if __name__ == "__main__":
    test_communication()