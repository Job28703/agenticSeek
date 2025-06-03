#!/usr/bin/env python3
"""
增強版協作檢測算法
提升協作任務檢測準確率到 90%+
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class CollaborationPattern(Enum):
    """協作模式類型"""
    SEQUENTIAL = "sequential"      # 順序執行：先做A，然後做B
    PARALLEL = "parallel"         # 並行執行：同時做A和B
    CONDITIONAL = "conditional"   # 條件執行：如果A，則做B
    ITERATIVE = "iterative"      # 迭代執行：重複做A直到B


@dataclass
class CollaborationSignal:
    """協作信號"""
    pattern: CollaborationPattern
    confidence: float
    keywords: List[str]
    context: str


class EnhancedCollaborationDetector:
    """增強版協作檢測器"""
    
    def __init__(self):
        self.name = "Enhanced Collaboration Detector"
        self.version = "2.0.0"
        
        # 多語言協作關鍵詞庫
        self.collaboration_keywords = {
            # 順序執行關鍵詞
            "sequential": {
                "en": ["then", "after", "next", "followed by", "subsequently", "afterwards", "later", "once"],
                "zh": ["然後", "接著", "之後", "隨後", "接下來", "完成後", "做完", "先", "再"],
                "zh_traditional": ["然後", "接著", "之後", "隨後", "接下來", "完成後", "做完", "先", "再"]
            },
            
            # 並行執行關鍵詞
            "parallel": {
                "en": ["and", "also", "simultaneously", "at the same time", "meanwhile", "concurrently", "both"],
                "zh": ["並且", "同時", "還要", "也要", "一邊", "一起", "同步"],
                "zh_traditional": ["並且", "同時", "還要", "也要", "一邊", "一起", "同步"]
            },
            
            # 條件執行關鍵詞
            "conditional": {
                "en": ["if", "when", "unless", "provided that", "in case", "should", "depending on"],
                "zh": ["如果", "當", "假如", "要是", "倘若", "若是", "根據"],
                "zh_traditional": ["如果", "當", "假如", "要是", "倘若", "若是", "根據"]
            },
            
            # 迭代執行關鍵詞
            "iterative": {
                "en": ["repeat", "until", "while", "for each", "iterate", "loop", "continue"],
                "zh": ["重複", "直到", "循環", "每個", "持續", "反覆", "繼續"],
                "zh_traditional": ["重複", "直到", "循環", "每個", "持續", "反覆", "繼續"]
            }
        }
        
        # 動作詞庫（表示可執行的任務）
        self.action_verbs = {
            "en": ["search", "find", "write", "create", "build", "make", "analyze", "download", 
                   "save", "send", "read", "process", "generate", "execute", "run", "test"],
            "zh": ["搜尋", "查找", "寫", "創建", "建立", "製作", "分析", "下載", 
                   "保存", "發送", "讀取", "處理", "生成", "執行", "運行", "測試"],
            "zh_traditional": ["搜尋", "查找", "寫", "創建", "建立", "製作", "分析", "下載", 
                              "保存", "發送", "讀取", "處理", "生成", "執行", "運行", "測試"]
        }
        
        # 否定詞（降低協作可能性）
        self.negation_words = {
            "en": ["only", "just", "simply", "merely", "single", "alone", "individual"],
            "zh": ["只", "僅", "單純", "單獨", "個別", "獨自", "唯一"],
            "zh_traditional": ["只", "僅", "單純", "單獨", "個別", "獨自", "唯一"]
        }
    
    def detect_language(self, text: str) -> str:
        """簡單的語言檢測"""
        # 檢測中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text.replace(' ', ''))
        
        if chinese_chars / max(total_chars, 1) > 0.3:
            return "zh"
        return "en"
    
    def extract_sentences(self, text: str) -> List[str]:
        """提取句子"""
        # 按標點符號分割
        sentences = re.split(r'[.!?。！？；;]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def count_action_verbs(self, text: str, language: str) -> int:
        """計算動作詞數量"""
        text_lower = text.lower()
        action_verbs = self.action_verbs.get(language, self.action_verbs["en"])
        
        count = 0
        for verb in action_verbs:
            if verb in text_lower:
                count += 1
        
        return count
    
    def detect_collaboration_patterns(self, text: str) -> List[CollaborationSignal]:
        """檢測協作模式"""
        language = self.detect_language(text)
        text_lower = text.lower()
        signals = []
        
        for pattern_type, keywords_dict in self.collaboration_keywords.items():
            keywords = keywords_dict.get(language, keywords_dict["en"])
            
            found_keywords = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
            
            if found_keywords:
                # 計算置信度
                confidence = len(found_keywords) / len(keywords)
                
                # 根據模式類型調整置信度
                if pattern_type == "sequential" and any(word in text_lower for word in ["then", "然後", "接著"]):
                    confidence += 0.2
                elif pattern_type == "parallel" and any(word in text_lower for word in ["and", "並且", "同時"]):
                    confidence += 0.15
                
                confidence = min(1.0, confidence)
                
                signal = CollaborationSignal(
                    pattern=CollaborationPattern(pattern_type),
                    confidence=confidence,
                    keywords=found_keywords,
                    context=text[:100] + "..." if len(text) > 100 else text
                )
                signals.append(signal)
        
        return signals
    
    def analyze_sentence_structure(self, text: str) -> Dict[str, float]:
        """分析句子結構"""
        language = self.detect_language(text)
        
        analysis = {
            "action_verb_count": 0,
            "sentence_count": 0,
            "avg_sentence_length": 0,
            "complexity_score": 0,
            "negation_penalty": 0
        }
        
        sentences = self.extract_sentences(text)
        analysis["sentence_count"] = len(sentences)
        
        if sentences:
            total_length = sum(len(s.split()) for s in sentences)
            analysis["avg_sentence_length"] = total_length / len(sentences)
        
        # 計算動作詞數量
        analysis["action_verb_count"] = self.count_action_verbs(text, language)
        
        # 計算複雜度分數
        if analysis["action_verb_count"] >= 2:
            analysis["complexity_score"] += 0.3
        if analysis["sentence_count"] >= 2:
            analysis["complexity_score"] += 0.2
        if analysis["avg_sentence_length"] > 10:
            analysis["complexity_score"] += 0.1
        
        # 檢查否定詞
        negation_words = self.negation_words.get(language, self.negation_words["en"])
        for word in negation_words:
            if word in text.lower():
                analysis["negation_penalty"] += 0.1
        
        return analysis
    
    def calculate_collaboration_score(self, text: str) -> Tuple[float, Dict]:
        """計算協作分數（優化版）"""
        # 檢測協作模式
        signals = self.detect_collaboration_patterns(text)

        # 分析句子結構
        structure = self.analyze_sentence_structure(text)

        # 基礎分數
        base_score = 0.0

        # 協作信號分數（提高權重）
        if signals:
            signal_score = max(signal.confidence for signal in signals)
            base_score += signal_score * 0.8  # 從 0.6 提高到 0.8

        # 動作詞數量獎勵（更積極的獎勵）
        action_count = structure["action_verb_count"]
        if action_count >= 2:
            base_score += 0.4  # 從 0.2 提高到 0.4
        if action_count >= 3:
            base_score += 0.2  # 額外獎勵

        # 結構複雜度分數
        base_score += structure["complexity_score"] * 0.2  # 降低權重

        # 特殊模式檢測
        text_lower = text.lower()

        # 強協作指標
        strong_indicators = [
            "and then", "然後", "接著", "followed by", "after that",
            "and also", "並且", "同時", "simultaneously",
            "multiple", "several", "both", "各種", "多個"
        ]

        for indicator in strong_indicators:
            if indicator in text_lower:
                base_score += 0.3
                break

        # 連接詞檢測
        connectors = ["and", "then", "also", "plus", "並", "還", "也", "又"]
        connector_count = sum(1 for conn in connectors if conn in text_lower)
        if connector_count >= 2:
            base_score += 0.2

        # 否定詞懲罰
        base_score -= structure["negation_penalty"]

        # 單一動作懲罰
        if action_count == 1 and not signals:
            base_score -= 0.3

        # 確保分數在 0-1 範圍內
        final_score = max(0.0, min(1.0, base_score))

        # 詳細分析結果
        analysis_details = {
            "signals": signals,
            "structure": structure,
            "base_score": base_score,
            "final_score": final_score,
            "is_collaborative": final_score >= 0.5
        }

        return final_score, analysis_details
    
    def detect_collaborative_task(self, text: str, threshold: float = 0.5) -> bool:
        """
        檢測是否為協作任務（主要接口）
        
        Args:
            text: 輸入文本
            threshold: 判斷閾值（默認 0.5）
            
        Returns:
            bool: 是否為協作任務
        """
        score, _ = self.calculate_collaboration_score(text)
        return score >= threshold
    
    def get_detailed_analysis(self, text: str) -> Dict:
        """獲取詳細分析結果"""
        score, details = self.calculate_collaboration_score(text)
        
        return {
            "text": text,
            "collaboration_score": score,
            "is_collaborative": score >= 0.5,
            "confidence": "high" if score >= 0.7 else "medium" if score >= 0.5 else "low",
            "detected_patterns": [signal.pattern.value for signal in details["signals"]],
            "key_indicators": [signal.keywords for signal in details["signals"]],
            "analysis_details": details
        }


def test_enhanced_detector():
    """測試增強版檢測器"""
    print("🧪 Testing Enhanced Collaboration Detector")
    print("=" * 50)
    
    detector = EnhancedCollaborationDetector()
    
    # 測試用例
    test_cases = [
        # 明確的協作任務
        ("Search for Python tutorials and then write a script", True),
        ("Find the latest news and save it to a file", True),
        ("Write code, test it, and then deploy", True),
        ("搜尋資料然後分析結果", True),
        ("先下載文件，接著處理數據", True),
        
        # 並行協作任務
        ("Search for tutorials and also download examples", True),
        ("Write code and simultaneously test it", True),
        ("同時搜尋和分析數據", True),
        
        # 條件協作任務
        ("If the file exists, then process it", True),
        ("When you find the data, analyze it", True),
        ("如果找到結果，就保存文件", True),
        
        # 非協作任務
        ("Hello, how are you?", False),
        ("Just say hello", False),
        ("Only search for information", False),
        ("僅僅問候一下", False),
        ("單純的搜尋", False),
        
        # 邊界情況
        ("Search for information", False),  # 單一動作
        ("Write a simple script", False),   # 單一動作
        ("Create multiple files and organize them", True),  # 多動作
    ]
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    print("📋 Test Results:")
    print("-" * 30)
    
    for text, expected in test_cases:
        analysis = detector.get_detailed_analysis(text)
        predicted = analysis["is_collaborative"]
        score = analysis["collaboration_score"]
        confidence = analysis["confidence"]
        
        is_correct = predicted == expected
        if is_correct:
            correct_predictions += 1
        
        status = "✅" if is_correct else "❌"
        print(f"{status} '{text[:40]}...'")
        print(f"   Expected: {expected}, Got: {predicted} (Score: {score:.2f}, {confidence})")
        
        if analysis["detected_patterns"]:
            print(f"   Patterns: {', '.join(analysis['detected_patterns'])}")
        
        print()
    
    accuracy = correct_predictions / total_tests * 100
    print("=" * 50)
    print(f"📊 Overall Accuracy: {accuracy:.1f}% ({correct_predictions}/{total_tests})")
    
    if accuracy >= 90:
        print("🎉 EXCELLENT! Target accuracy achieved!")
    elif accuracy >= 80:
        print("✅ GOOD! Close to target accuracy")
    else:
        print("⚠️  NEEDS IMPROVEMENT")
    
    return accuracy >= 90


if __name__ == "__main__":
    success = test_enhanced_detector()
    exit(0 if success else 1)
