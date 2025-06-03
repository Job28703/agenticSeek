#!/usr/bin/env python3
"""
MVP 協作檢測算法 v1.0
最小可行產品 - 專注於核心檢測功能
"""

from typing import List, Tuple


class MVPCollaborationDetector:
    """MVP 協作檢測器 - 最小可行版本"""
    
    def __init__(self):
        self.name = "MVP Collaboration Detector"
        self.version = "1.0.0"
        
        # 核心協作關鍵詞（最明顯的指標）
        self.collaboration_keywords = [
            # 英文順序指標
            "and then", "then", "after", "next", "followed by",
            
            # 英文並行指標  
            "and also", "also", "and", "both", "simultaneously",
            
            # 中文順序指標
            "然後", "接著", "之後", "再", "先",
            
            # 中文並行指標
            "並且", "同時", "還要", "也要", "一起"
        ]
        
        # 動作詞（表示可執行任務）
        self.action_words = [
            # 英文動作詞
            "search", "find", "write", "create", "build", "make", 
            "analyze", "download", "save", "send", "read", "process",
            
            # 中文動作詞
            "搜尋", "查找", "寫", "創建", "建立", "製作", 
            "分析", "下載", "保存", "發送", "讀取", "處理"
        ]
        
        # 排除詞（降低協作可能性）
        self.exclusion_words = [
            "only", "just", "simply", "single", "alone",
            "只", "僅", "單純", "單獨", "獨自"
        ]
    
    def count_action_words(self, text: str) -> int:
        """計算動作詞數量"""
        text_lower = text.lower()
        count = 0
        
        for word in self.action_words:
            if word in text_lower:
                count += 1
        
        return count
    
    def has_collaboration_keywords(self, text: str) -> Tuple[bool, List[str]]:
        """檢查是否包含協作關鍵詞"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.collaboration_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    def has_exclusion_words(self, text: str) -> bool:
        """檢查是否包含排除詞"""
        text_lower = text.lower()
        
        for word in self.exclusion_words:
            if word in text_lower:
                return True
        
        return False
    
    def detect_collaborative_task(self, text: str) -> bool:
        """
        檢測是否為協作任務（主要接口）
        
        簡單邏輯：
        1. 如果有排除詞 -> 非協作
        2. 如果有協作關鍵詞 AND 多個動作詞 -> 協作
        3. 如果有強協作關鍵詞 -> 協作
        4. 其他情況 -> 非協作
        
        Args:
            text: 輸入文本
            
        Returns:
            bool: 是否為協作任務
        """
        # 規則 1：排除詞檢查
        if self.has_exclusion_words(text):
            return False
        
        # 規則 2：協作關鍵詞 + 多動作詞
        has_collab_keywords, found_keywords = self.has_collaboration_keywords(text)
        action_count = self.count_action_words(text)
        
        if has_collab_keywords and action_count >= 2:
            return True
        
        # 規則 3：強協作關鍵詞
        strong_keywords = ["and then", "然後", "接著", "and also", "並且", "同時"]
        text_lower = text.lower()
        
        for keyword in strong_keywords:
            if keyword in text_lower:
                return True
        
        # 規則 4：多動作詞（3個以上）
        if action_count >= 3:
            return True
        
        # 默認：非協作
        return False
    
    def get_analysis_details(self, text: str) -> dict:
        """獲取詳細分析結果"""
        has_collab, found_keywords = self.has_collaboration_keywords(text)
        action_count = self.count_action_words(text)
        has_exclusion = self.has_exclusion_words(text)
        is_collaborative = self.detect_collaborative_task(text)
        
        return {
            "text": text,
            "is_collaborative": is_collaborative,
            "collaboration_keywords_found": found_keywords,
            "action_word_count": action_count,
            "has_exclusion_words": has_exclusion,
            "confidence": "high" if len(found_keywords) >= 2 or action_count >= 3 else "medium" if found_keywords or action_count >= 2 else "low"
        }


def test_mvp_detector():
    """測試 MVP 檢測器"""
    print("🧪 Testing MVP Collaboration Detector v1.0")
    print("=" * 50)
    
    detector = MVPCollaborationDetector()
    
    # 精選測試用例（專注於最明顯的情況）
    test_cases = [
        # 明確的協作任務（應該檢測到）
        ("Search for Python tutorials and then write a script", True),
        ("Find the latest news and save it to a file", True),
        ("搜尋資料然後分析結果", True),
        ("先下載文件，接著處理數據", True),
        ("Search for tutorials and also download examples", True),
        ("Write code and test it", True),
        ("Create multiple files and organize them", True),
        
        # 非協作任務（應該排除）
        ("Hello, how are you?", False),
        ("Just say hello", False),
        ("Only search for information", False),
        ("僅僅問候一下", False),
        ("Search for information", False),  # 單一動作
        ("Write a simple script", False),   # 單一動作
        
        # 邊界情況
        ("Find and analyze data", True),    # 簡單的 and 連接
        ("Search, download, and process", True),  # 多動作
    ]
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    print("📋 Test Results:")
    print("-" * 30)
    
    for text, expected in test_cases:
        analysis = detector.get_analysis_details(text)
        predicted = analysis["is_collaborative"]
        
        is_correct = predicted == expected
        if is_correct:
            correct_predictions += 1
        
        status = "✅" if is_correct else "❌"
        print(f"{status} '{text[:40]}...'")
        print(f"   Expected: {expected}, Got: {predicted}")
        print(f"   Keywords: {analysis['collaboration_keywords_found']}")
        print(f"   Actions: {analysis['action_word_count']}, Confidence: {analysis['confidence']}")
        print()
    
    accuracy = correct_predictions / total_tests * 100
    print("=" * 50)
    print(f"📊 MVP v1.0 Accuracy: {accuracy:.1f}% ({correct_predictions}/{total_tests})")
    
    if accuracy >= 80:
        print("🎉 EXCELLENT! MVP v1.0 ready for integration!")
        print("✅ Core detection logic is solid")
        print("🚀 Ready for MVP v1.1 (multi-language enhancement)")
    elif accuracy >= 70:
        print("✅ GOOD! MVP v1.0 meets minimum requirements")
        print("🔧 Minor tweaks needed before v1.1")
    else:
        print("⚠️  NEEDS IMPROVEMENT")
        print("🔧 Core logic needs refinement")
    
    return accuracy >= 70


def demo_mvp_usage():
    """演示 MVP 使用方式"""
    print("\n🔗 MVP Usage Demo")
    print("=" * 30)
    
    detector = MVPCollaborationDetector()
    
    # 模擬實際使用場景
    user_inputs = [
        "Search for weather API and then create an app",
        "Just tell me the weather",
        "Find Python tutorials, download examples, and practice coding"
    ]
    
    for user_input in user_inputs:
        print(f"👤 User: {user_input}")
        
        is_collaborative = detector.detect_collaborative_task(user_input)
        analysis = detector.get_analysis_details(user_input)
        
        if is_collaborative:
            print(f"🤝 → Collaborative task detected!")
            print(f"   Keywords: {', '.join(analysis['collaboration_keywords_found'])}")
            print(f"   Actions: {analysis['action_word_count']}")
            print(f"   → Route to: Multi-Agent Collaboration System")
        else:
            print(f"👤 → Single task detected")
            print(f"   → Route to: Single Agent")
        
        print()


def main():
    """主函數"""
    print("🚀 MVP Collaboration Detector - Minimum Viable Product")
    print("=" * 60)
    
    try:
        # 運行測試
        test_success = test_mvp_detector()
        
        if test_success:
            # 運行演示
            demo_mvp_usage()
            
            print("\n" + "=" * 60)
            print("🎉 MVP COLLABORATION DETECTOR v1.0 READY!")
            print("✅ Core features working:")
            print("   • Basic collaboration detection")
            print("   • Action word counting")
            print("   • Exclusion word filtering")
            print("   • Simple but reliable logic")
            
            print("\n📋 Next MVP iteration (v1.1) will add:")
            print("   • Enhanced multi-language support")
            print("   • Confidence scoring")
            print("   • Pattern recognition")
            print("   • Integration with router")
            
            return True
        else:
            print("❌ MVP v1.0 needs improvement")
            return False
            
    except Exception as e:
        print(f"❌ MVP failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
