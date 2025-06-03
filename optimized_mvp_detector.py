#!/usr/bin/env python3
"""
優化版 MVP 協作檢測算法
專注於性能優化和準確性提升
"""

import re
from typing import Set, Tuple


class OptimizedMVPDetector:
    """優化版 MVP 協作檢測器"""
    
    def __init__(self):
        self.name = "Optimized MVP Collaboration Detector"
        self.version = "1.0.1"
        
        # 預編譯正則表達式以提升性能
        self._compile_patterns()
        
        # 使用集合以提升查找性能
        self.strong_indicators = {
            "and then", "然後", "接著", "and also", "並且", "同時"
        }
        
        self.exclusion_words = {
            "only", "just", "simply", "single", "alone",
            "只", "僅", "單純", "單獨", "獨自"
        }
    
    def _compile_patterns(self):
        """預編譯正則表達式模式"""
        # 協作關鍵詞模式
        collab_keywords = [
            r"\band then\b", r"\bthen\b", r"\bafter\b", r"\bnext\b", 
            r"\bfollowed by\b", r"\band also\b", r"\balso\b", r"\band\b", 
            r"\bboth\b", r"\bsimultaneously\b",
            r"然後", r"接著", r"之後", r"再", r"先",
            r"並且", r"同時", r"還要", r"也要", r"一起"
        ]
        
        # 動作詞模式
        action_words = [
            r"\bsearch\b", r"\bfind\b", r"\bwrite\b", r"\bcreate\b", 
            r"\bbuild\b", r"\bmake\b", r"\banalyze\b", r"\bdownload\b", 
            r"\bsave\b", r"\bsend\b", r"\bread\b", r"\bprocess\b",
            r"搜尋", r"查找", r"寫", r"創建", r"建立", r"製作", 
            r"分析", r"下載", r"保存", r"發送", r"讀取", r"處理"
        ]
        
        # 編譯模式
        self.collab_pattern = re.compile("|".join(collab_keywords), re.IGNORECASE)
        self.action_pattern = re.compile("|".join(action_words), re.IGNORECASE)
        
        # 排除詞模式
        exclusion_words = [
            r"\bonly\b", r"\bjust\b", r"\bsimply\b", r"\bsingle\b", r"\balone\b",
            r"只", r"僅", r"單純", r"單獨", r"獨自"
        ]
        self.exclusion_pattern = re.compile("|".join(exclusion_words), re.IGNORECASE)
    
    def detect_collaborative_task(self, text: str) -> bool:
        """
        快速檢測協作任務
        
        Args:
            text: 輸入文本
            
        Returns:
            bool: 是否為協作任務
        """
        if not text or not text.strip():
            return False
        
        text_lower = text.lower()
        
        # 快速排除檢查
        if self.exclusion_pattern.search(text):
            return False
        
        # 檢查強協作指標
        for indicator in self.strong_indicators:
            if indicator in text_lower:
                return True
        
        # 檢查協作關鍵詞和動作詞
        collab_matches = self.collab_pattern.findall(text)
        action_matches = self.action_pattern.findall(text)
        
        # 檢測邏輯
        if collab_matches and len(action_matches) >= 2:
            return True
        
        # 多動作詞檢查
        if len(action_matches) >= 3:
            return True
        
        return False
    
    def get_analysis_details(self, text: str) -> dict:
        """獲取詳細分析結果"""
        if not text or not text.strip():
            return {
                "text": text,
                "is_collaborative": False,
                "collaboration_keywords_found": [],
                "action_word_count": 0,
                "has_exclusion_words": False,
                "confidence": "low"
            }
        
        # 執行檢測
        is_collaborative = self.detect_collaborative_task(text)
        
        # 收集詳細信息
        collab_matches = self.collab_pattern.findall(text)
        action_matches = self.action_pattern.findall(text)
        has_exclusion = bool(self.exclusion_pattern.search(text))
        
        # 計算置信度
        confidence = "low"
        if len(collab_matches) >= 2 or len(action_matches) >= 3:
            confidence = "high"
        elif collab_matches or len(action_matches) >= 2:
            confidence = "medium"
        
        return {
            "text": text,
            "is_collaborative": is_collaborative,
            "collaboration_keywords_found": collab_matches,
            "action_word_count": len(action_matches),
            "has_exclusion_words": has_exclusion,
            "confidence": confidence
        }


def test_optimized_detector():
    """測試優化版檢測器"""
    print("🧪 Testing Optimized MVP Detector")
    print("=" * 40)
    
    detector = OptimizedMVPDetector()
    
    # 測試用例
    test_cases = [
        # 協作任務
        ("Search for Python tutorials and then write a script", True),
        ("Find the latest news and save it to a file", True),
        ("搜尋資料然後分析結果", True),
        ("先下載文件，接著處理數據", True),
        ("Search for tutorials and also download examples", True),
        ("Create multiple files and organize them", True),
        ("Find and analyze data", True),
        ("Search, download, and process", True),
        
        # 非協作任務
        ("Hello, how are you?", False),
        ("Just say hello", False),
        ("Only search for information", False),
        ("僅僅問候一下", False),
        ("Search for information", False),
        ("Write a simple script", False),
    ]
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    print("📋 Test Results:")
    print("-" * 30)
    
    for text, expected in test_cases:
        predicted = detector.detect_collaborative_task(text)
        is_correct = predicted == expected
        
        if is_correct:
            correct_predictions += 1
        
        status = "✅" if is_correct else "❌"
        print(f"{status} '{text[:35]}...' -> {predicted} (expected {expected})")
    
    accuracy = correct_predictions / total_tests * 100
    print(f"\n📊 Optimized Accuracy: {accuracy:.1f}% ({correct_predictions}/{total_tests})")
    
    return accuracy >= 85


def test_performance():
    """測試性能"""
    print("\n⚡ Testing Performance")
    print("=" * 30)
    
    import time
    
    detector = OptimizedMVPDetector()
    
    # 測試文本
    test_texts = [
        "Search for Python tutorials and then write a script",
        "Find the latest news and save it to a file",
        "Hello, how are you?",
        "Just search for information",
        "Create multiple files and organize them",
        "搜尋資料然後分析結果"
    ] * 100  # 600 次測試
    
    # 性能測試
    start_time = time.time()
    results = []
    for text in test_texts:
        result = detector.detect_collaborative_task(text)
        results.append(result)
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time = total_time / len(test_texts) * 1000  # 毫秒
    
    print(f"📊 Performance Results:")
    print(f"   Total time: {total_time:.4f}s for {len(test_texts)} tests")
    print(f"   Average time per test: {avg_time:.4f}ms")
    print(f"   Tests per second: {len(test_texts)/total_time:.0f}")
    
    # 性能要求：每次檢測應該在 1ms 以內
    return avg_time < 1.0


def compare_with_simple_version():
    """與簡單版本比較"""
    print("\n🔄 Comparing with Simple Version")
    print("=" * 40)
    
    # 簡單版本（舊邏輯）
    def simple_detect(text: str) -> bool:
        collaborative_keywords = [
            "and then", "after that", "followed by", "next", "also",
            "並且", "然後", "接著", "同時", "還要", "另外"
        ]
        
        text_lower = text.lower()
        for keyword in collaborative_keywords:
            if keyword in text_lower:
                return True
        
        action_words = ["search", "find", "write", "create", "build", "make", "analyze", "download"]
        action_count = sum(1 for word in action_words if word in text_lower)
        
        return action_count >= 2
    
    # 優化版本
    detector = OptimizedMVPDetector()
    
    # 測試用例
    test_cases = [
        "Search for Python tutorials and then write a script",
        "Find the latest news and save it to a file",
        "Hello, how are you?",
        "Just search for information",
        "Create multiple files and organize them",
        "搜尋資料然後分析結果",
        "Write code and test it",
        "Only write a script"
    ]
    
    print("📋 Comparison Results:")
    print("-" * 30)
    
    agreement = 0
    total = len(test_cases)
    
    for text in test_cases:
        simple_result = simple_detect(text)
        optimized_result = detector.detect_collaborative_task(text)
        
        agrees = simple_result == optimized_result
        if agrees:
            agreement += 1
        
        status = "✅" if agrees else "❌"
        print(f"{status} '{text[:30]}...'")
        print(f"   Simple: {simple_result}, Optimized: {optimized_result}")
    
    agreement_rate = agreement / total * 100
    print(f"\n📊 Agreement Rate: {agreement_rate:.1f}% ({agreement}/{total})")
    
    return agreement_rate >= 75


def main():
    """主函數"""
    print("🚀 Optimized MVP Collaboration Detector")
    print("=" * 50)
    
    test_results = []
    
    # 運行測試
    tests = [
        ("Accuracy Test", test_optimized_detector),
        ("Performance Test", test_performance),
        ("Comparison Test", compare_with_simple_version)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            test_results.append((test_name, False))
    
    # 總結
    print("\n" + "=" * 50)
    print("📊 Optimized MVP Test Results")
    print("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    success_rate = passed / total * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("\n🎉 OPTIMIZED MVP READY!")
        print("✅ High accuracy maintained")
        print("✅ Performance optimized")
        print("✅ Compatible with existing logic")
        print("\n🚀 Ready for integration and step 2!")
    else:
        print("\n⚠️  NEEDS MORE OPTIMIZATION")
    
    return success_rate >= 80


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
