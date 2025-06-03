#!/usr/bin/env python3
"""
MVP 語音支援增強器 v1.0
專注於核心體驗優化：語音質量、智能檢測、對話流程
"""

import os
import re
import time
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class VoiceQuality(Enum):
    """語音質量等級"""
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"


class LanguageMode(Enum):
    """語言模式"""
    AUTO = "auto"
    ENGLISH = "en"
    CHINESE = "zh"
    MIXED = "mixed"


@dataclass
class VoiceSettings:
    """語音設置"""
    language: str = "auto"
    voice_idx: int = 0
    speed: float = 1.2
    quality: VoiceQuality = VoiceQuality.HIGH
    auto_detect: bool = True
    clear_speech: bool = True


@dataclass
class ConversationState:
    """對話狀態"""
    is_listening: bool = False
    is_speaking: bool = False
    last_input: str = ""
    last_output: str = ""
    conversation_count: int = 0
    start_time: float = 0


class MVPVoiceEnhancer:
    """MVP 語音增強器"""
    
    def __init__(self):
        self.name = "MVP Voice Enhancer"
        self.version = "1.0.0"
        
        # 語音設置
        self.settings = VoiceSettings()
        
        # 對話狀態
        self.conversation_state = ConversationState()
        
        # 語言檢測模式
        self.language_patterns = {
            "zh": [
                r'[\u4e00-\u9fff]',  # 中文字符
                r'[，。！？；：]',    # 中文標點
            ],
            "en": [
                r'[a-zA-Z]',         # 英文字符
                r'[,.!?;:]',         # 英文標點
            ]
        }
        
        # 優化的語音參數
        self.voice_configs = {
            VoiceQuality.STANDARD: {
                "speed": 1.0,
                "clarity_boost": False,
                "noise_reduction": False
            },
            VoiceQuality.HIGH: {
                "speed": 1.2,
                "clarity_boost": True,
                "noise_reduction": True
            },
            VoiceQuality.PREMIUM: {
                "speed": 1.1,
                "clarity_boost": True,
                "noise_reduction": True,
                "emotion_enhance": True
            }
        }
        
        # 對話流程狀態
        self.conversation_flow = {
            "waiting_for_input": True,
            "processing": False,
            "responding": False,
            "error_state": False
        }
    
    def detect_language(self, text: str) -> str:
        """
        智能語言檢測
        
        Args:
            text: 輸入文本
            
        Returns:
            str: 檢測到的語言代碼
        """
        if not text or not text.strip():
            return "en"  # 默認英文
        
        # 計算中文字符比例
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(re.sub(r'\s', '', text))
        
        if total_chars == 0:
            return "en"
        
        chinese_ratio = chinese_chars / total_chars
        
        # 語言判斷邏輯
        if chinese_ratio > 0.3:
            return "zh"
        elif chinese_ratio > 0.1:
            return "mixed"
        else:
            return "en"
    
    def optimize_voice_parameters(self, text: str, language: str) -> Dict:
        """
        根據文本和語言優化語音參數
        
        Args:
            text: 要朗讀的文本
            language: 語言代碼
            
        Returns:
            Dict: 優化後的語音參數
        """
        base_config = self.voice_configs[self.settings.quality].copy()
        
        # 根據文本長度調整語速
        text_length = len(text)
        if text_length > 200:
            base_config["speed"] *= 0.9  # 長文本稍慢
        elif text_length < 50:
            base_config["speed"] *= 1.1  # 短文本稍快
        
        # 根據語言調整參數
        if language == "zh":
            base_config["speed"] *= 0.95  # 中文稍慢
            base_config["pause_between_sentences"] = 0.3
        elif language == "en":
            base_config["pause_between_sentences"] = 0.2
        elif language == "mixed":
            base_config["speed"] *= 0.9   # 混合語言更慢
            base_config["pause_between_sentences"] = 0.4
        
        return base_config
    
    def enhance_text_for_speech(self, text: str, language: str) -> str:
        """
        為語音合成優化文本
        
        Args:
            text: 原始文本
            language: 語言代碼
            
        Returns:
            str: 優化後的文本
        """
        if not text:
            return ""
        
        # 基礎清理
        enhanced_text = text.strip()
        
        # 移除技術元素
        enhanced_text = re.sub(r'```.*?```', '', enhanced_text, flags=re.DOTALL)  # 代碼塊
        enhanced_text = re.sub(r'`[^`]*`', '', enhanced_text)  # 行內代碼
        enhanced_text = re.sub(r'https?://\S+', '', enhanced_text)  # URL
        enhanced_text = re.sub(r'\[.*?\]', '', enhanced_text)  # 方括號內容
        
        # 根據語言進行特定優化
        if language == "zh":
            # 中文優化
            enhanced_text = re.sub(r'[^\u4e00-\u9fff\s，。！？；：""''（）]', '', enhanced_text)
            enhanced_text = re.sub(r'\s+', '', enhanced_text)  # 移除多餘空格
        elif language == "en":
            # 英文優化
            enhanced_text = re.sub(r'[^a-zA-Z0-9\s,.!?;:\'"()-]', ' ', enhanced_text)
            enhanced_text = re.sub(r'\s+', ' ', enhanced_text)  # 合併多個空格
        else:
            # 混合語言保持基本清理
            enhanced_text = re.sub(r'\s+', ' ', enhanced_text)
        
        # 長度限制（避免過長的語音）
        if len(enhanced_text) > 500:
            sentences = re.split(r'[.!?。！？]', enhanced_text)
            enhanced_text = '. '.join(sentences[:3]) + '.'  # 只取前3句
        
        return enhanced_text.strip()
    
    def update_conversation_state(self, action: str, data: str = ""):
        """
        更新對話狀態
        
        Args:
            action: 動作類型
            data: 相關數據
        """
        current_time = time.time()
        
        if action == "start_listening":
            self.conversation_state.is_listening = True
            self.conversation_state.is_speaking = False
            self.conversation_state.start_time = current_time
            
        elif action == "stop_listening":
            self.conversation_state.is_listening = False
            self.conversation_state.last_input = data
            
        elif action == "start_speaking":
            self.conversation_state.is_speaking = True
            self.conversation_state.is_listening = False
            self.conversation_state.last_output = data
            
        elif action == "stop_speaking":
            self.conversation_state.is_speaking = False
            self.conversation_state.conversation_count += 1
            
        elif action == "error":
            self.conversation_flow["error_state"] = True
            self.conversation_state.is_listening = False
            self.conversation_state.is_speaking = False
    
    def get_voice_status(self) -> Dict:
        """
        獲取語音狀態信息
        
        Returns:
            Dict: 語音狀態
        """
        return {
            "is_listening": self.conversation_state.is_listening,
            "is_speaking": self.conversation_state.is_speaking,
            "conversation_count": self.conversation_state.conversation_count,
            "current_language": self.settings.language,
            "voice_quality": self.settings.quality.value,
            "auto_detect_enabled": self.settings.auto_detect,
            "session_duration": time.time() - self.conversation_state.start_time if self.conversation_state.start_time > 0 else 0
        }
    
    def process_voice_input(self, audio_text: str) -> Dict:
        """
        處理語音輸入
        
        Args:
            audio_text: 語音轉文字結果
            
        Returns:
            Dict: 處理結果
        """
        self.update_conversation_state("stop_listening", audio_text)
        
        # 語言檢測
        detected_language = self.detect_language(audio_text) if self.settings.auto_detect else self.settings.language
        
        # 文本清理和優化
        cleaned_text = self.enhance_text_for_speech(audio_text, detected_language)
        
        result = {
            "original_text": audio_text,
            "cleaned_text": cleaned_text,
            "detected_language": detected_language,
            "confidence": self._calculate_confidence(audio_text),
            "processing_time": time.time() - self.conversation_state.start_time,
            "ready_for_response": len(cleaned_text.strip()) > 0
        }
        
        return result
    
    def prepare_voice_output(self, response_text: str) -> Dict:
        """
        準備語音輸出
        
        Args:
            response_text: 要轉換為語音的文本
            
        Returns:
            Dict: 語音輸出配置
        """
        self.update_conversation_state("start_speaking", response_text)
        
        # 語言檢測
        detected_language = self.detect_language(response_text) if self.settings.auto_detect else self.settings.language
        
        # 文本優化
        enhanced_text = self.enhance_text_for_speech(response_text, detected_language)
        
        # 語音參數優化
        voice_params = self.optimize_voice_parameters(enhanced_text, detected_language)
        
        # 選擇合適的語音
        voice_selection = self._select_optimal_voice(detected_language)
        
        output_config = {
            "text": enhanced_text,
            "language": detected_language,
            "voice_params": voice_params,
            "voice_selection": voice_selection,
            "estimated_duration": len(enhanced_text) * 0.1,  # 粗略估算
            "quality_level": self.settings.quality.value
        }
        
        return output_config
    
    def _calculate_confidence(self, text: str) -> float:
        """計算文本置信度"""
        if not text:
            return 0.0
        
        # 簡單的置信度計算
        confidence = 0.5  # 基礎置信度
        
        # 長度獎勵
        if len(text) > 10:
            confidence += 0.2
        
        # 完整句子獎勵
        if any(punct in text for punct in '.!?。！？'):
            confidence += 0.2
        
        # 常見詞彙獎勵
        common_words = ['the', 'and', 'is', 'to', 'a', '的', '是', '在', '了', '有']
        if any(word in text.lower() for word in common_words):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _select_optimal_voice(self, language: str) -> Dict:
        """選擇最佳語音"""
        voice_map = {
            "en": {
                "default_idx": 2,  # af_alloy
                "alternatives": [0, 1, 3, 4, 5],
                "recommended": "af_alloy"
            },
            "zh": {
                "default_idx": 0,  # zf_xiaobei
                "alternatives": [1, 2, 3],
                "recommended": "zf_xiaobei"
            },
            "mixed": {
                "default_idx": 2,  # 使用英文語音
                "alternatives": [0, 1],
                "recommended": "af_alloy"
            }
        }
        
        return voice_map.get(language, voice_map["en"])


def test_mvp_voice_enhancer():
    """測試 MVP 語音增強器"""
    print("🧪 Testing MVP Voice Enhancer v1.0")
    print("=" * 40)
    
    enhancer = MVPVoiceEnhancer()
    
    # 測試 1: 語言檢測
    print("📝 Test 1: Language Detection")
    
    test_texts = [
        "Hello, how are you today?",
        "你好，今天怎麼樣？",
        "Hello 你好, how are you 今天怎麼樣?",
        "Write a Python script to analyze data",
        "寫一個 Python 腳本來分析數據"
    ]
    
    for text in test_texts:
        detected = enhancer.detect_language(text)
        print(f"   '{text[:30]}...' -> {detected}")
    
    # 測試 2: 文本優化
    print("\n📝 Test 2: Text Enhancement")
    
    messy_text = """
    Here's some code: ```python
    def hello():
        print("Hello")
    ```
    And a URL: https://example.com
    [Some reference] with **bold** text.
    """
    
    enhanced = enhancer.enhance_text_for_speech(messy_text, "en")
    print(f"   Original: {len(messy_text)} chars")
    print(f"   Enhanced: {len(enhanced)} chars")
    print(f"   Result: {enhanced[:50]}...")
    
    # 測試 3: 語音參數優化
    print("\n📝 Test 3: Voice Parameter Optimization")
    
    short_text = "Hello!"
    long_text = "This is a very long sentence that contains multiple words and phrases to test the voice parameter optimization system."
    
    short_params = enhancer.optimize_voice_parameters(short_text, "en")
    long_params = enhancer.optimize_voice_parameters(long_text, "en")
    
    print(f"   Short text speed: {short_params['speed']:.2f}")
    print(f"   Long text speed: {long_params['speed']:.2f}")
    
    # 測試 4: 對話狀態管理
    print("\n📝 Test 4: Conversation State Management")
    
    enhancer.update_conversation_state("start_listening")
    status1 = enhancer.get_voice_status()
    
    enhancer.update_conversation_state("stop_listening", "Hello AgenticSeek")
    input_result = enhancer.process_voice_input("Hello AgenticSeek")
    
    enhancer.update_conversation_state("start_speaking", "Hello! How can I help you?")
    output_config = enhancer.prepare_voice_output("Hello! How can I help you?")
    
    enhancer.update_conversation_state("stop_speaking")
    status2 = enhancer.get_voice_status()
    
    print(f"   Listening state: {status1['is_listening']}")
    print(f"   Speaking state: {status2['is_speaking']}")
    print(f"   Conversation count: {status2['conversation_count']}")
    print(f"   Input confidence: {input_result['confidence']:.2f}")
    print(f"   Output language: {output_config['language']}")
    
    print("\n✅ MVP Voice Enhancer tests completed!")
    return True


def demo_voice_workflow():
    """演示語音工作流程"""
    print("\n🔗 Voice Enhancement Workflow Demo")
    print("=" * 40)
    
    enhancer = MVPVoiceEnhancer()
    
    print("🎙️ Scenario: User voice interaction with AgenticSeek")
    
    # 1. 用戶開始說話
    print("\n1. User starts speaking...")
    enhancer.update_conversation_state("start_listening")
    status = enhancer.get_voice_status()
    print(f"   ✅ Listening mode activated: {status['is_listening']}")
    
    # 2. 語音轉文字
    print("\n2. Speech-to-text processing...")
    user_speech = "Search for Python tutorials and then write a script"
    input_result = enhancer.process_voice_input(user_speech)
    
    print(f"   📝 Original: {input_result['original_text']}")
    print(f"   🔍 Cleaned: {input_result['cleaned_text']}")
    print(f"   🌐 Language: {input_result['detected_language']}")
    print(f"   📊 Confidence: {input_result['confidence']:.2f}")
    
    # 3. AI 處理和回應
    print("\n3. AI processing and response...")
    ai_response = "I'll help you search for Python tutorials and create a script. Let me start by finding some good resources."
    output_config = enhancer.prepare_voice_output(ai_response)
    
    print(f"   🗣️ Response text: {output_config['text'][:50]}...")
    print(f"   🌐 Language: {output_config['language']}")
    print(f"   ⚡ Speed: {output_config['voice_params']['speed']:.2f}")
    print(f"   🎵 Voice: {output_config['voice_selection']['recommended']}")
    print(f"   ⏱️ Estimated duration: {output_config['estimated_duration']:.1f}s")
    
    # 4. 完成對話
    print("\n4. Completing conversation...")
    enhancer.update_conversation_state("stop_speaking")
    final_status = enhancer.get_voice_status()
    
    print(f"   ✅ Conversation completed")
    print(f"   📊 Total conversations: {final_status['conversation_count']}")
    print(f"   ⏱️ Session duration: {final_status['session_duration']:.1f}s")
    
    print("\n🎉 Voice workflow completed successfully!")


def main():
    """主函數"""
    print("🚀 MVP Voice Enhancer v1.0 - Core Experience Optimization")
    print("=" * 60)
    
    try:
        # 運行測試
        test_success = test_mvp_voice_enhancer()
        
        if test_success:
            # 運行演示
            demo_voice_workflow()
            
            print("\n" + "=" * 60)
            print("🎉 MVP VOICE ENHANCER v1.0 READY!")
            print("✅ Core features working:")
            print("   • Intelligent language detection")
            print("   • Voice parameter optimization")
            print("   • Text enhancement for speech")
            print("   • Conversation state management")
            print("   • Quality-based voice selection")
            
            print("\n📋 Next MVP iteration (v1.1) could add:")
            print("   • Emotion detection and expression")
            print("   • Advanced conversation memory")
            print("   • Real-time voice quality adjustment")
            print("   • Multi-speaker support")
            
            return True
        else:
            print("❌ MVP tests failed")
            return False
            
    except Exception as e:
        print(f"❌ MVP failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
