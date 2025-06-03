#!/usr/bin/env python3
"""
測試 MVP 協作檢測器集成效果
"""

import sys
import os

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_mvp_detector_integration():
    """測試 MVP 檢測器集成到路由器"""
    print("🧪 Testing MVP Detector Integration")
    print("=" * 40)
    
    try:
        # 創建模擬代理
        class MockAgent:
            def __init__(self, name: str, role: str):
                self.agent_name = name
                self.role = role
                self.type = role
        
        # 創建路由器
        from sources.router import AgentRouter
        
        agents = [
            MockAgent("CodeAgent", "code"),
            MockAgent("WebAgent", "web"),
            MockAgent("FileAgent", "files"),
            MockAgent("TalkAgent", "talk")
        ]
        
        router = AgentRouter(agents)
        
        # 測試用例
        test_cases = [
            # 協作任務
            ("Search for Python tutorials and then write a script", True),
            ("Find the latest news and save it to a file", True),
            ("搜尋資料然後分析結果", True),
            ("Create multiple files and organize them", True),
            
            # 非協作任務
            ("Hello, how are you?", False),
            ("Just search for information", False),
            ("Only write a script", False),
            ("僅僅問候一下", False),
        ]
        
        correct_predictions = 0
        total_tests = len(test_cases)
        
        print("📋 Integration Test Results:")
        print("-" * 30)
        
        for text, expected in test_cases:
            detected = router.detect_collaborative_task(text)
            is_correct = detected == expected
            
            if is_correct:
                correct_predictions += 1
            
            status = "✅" if is_correct else "❌"
            print(f"{status} '{text[:35]}...'")
            print(f"   Expected: {expected}, Got: {detected}")
        
        accuracy = correct_predictions / total_tests * 100
        print(f"\n📊 Integration Accuracy: {accuracy:.1f}% ({correct_predictions}/{total_tests})")
        
        return accuracy >= 80
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def test_performance_comparison():
    """測試性能對比"""
    print("\n⚡ Testing Performance Comparison")
    print("=" * 40)
    
    try:
        import time
        
        # 創建模擬路由器
        class MockRouter:
            def __init__(self):
                self._mvp_detector = None
            
            def _create_mvp_detector(self):
                from mvp_collaboration_detector import MVPCollaborationDetector
                return MVPCollaborationDetector()
            
            def detect_collaborative_task_mvp(self, text: str) -> bool:
                if not hasattr(self, '_mvp_detector') or self._mvp_detector is None:
                    self._mvp_detector = self._create_mvp_detector()
                return self._mvp_detector.detect_collaborative_task(text)
            
            def detect_collaborative_task_old(self, text: str) -> bool:
                # 舊版檢測邏輯
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
        
        router = MockRouter()
        
        # 測試文本
        test_texts = [
            "Search for Python tutorials and then write a script",
            "Find the latest news and save it to a file",
            "Hello, how are you?",
            "Just search for information"
        ] * 25  # 重複25次，總共100個測試
        
        # 測試 MVP 版本
        start_time = time.time()
        mvp_results = []
        for text in test_texts:
            result = router.detect_collaborative_task_mvp(text)
            mvp_results.append(result)
        mvp_time = time.time() - start_time
        
        # 測試舊版本
        start_time = time.time()
        old_results = []
        for text in test_texts:
            result = router.detect_collaborative_task_old(text)
            old_results.append(result)
        old_time = time.time() - start_time
        
        print(f"📊 Performance Results:")
        print(f"   MVP Version: {mvp_time:.4f}s for {len(test_texts)} tests")
        print(f"   Old Version: {old_time:.4f}s for {len(test_texts)} tests")
        print(f"   Performance ratio: {mvp_time/old_time:.2f}x")
        
        # 比較結果一致性
        consistency = sum(1 for i in range(len(mvp_results)) if mvp_results[i] == old_results[i])
        consistency_rate = consistency / len(mvp_results) * 100
        print(f"   Result consistency: {consistency_rate:.1f}%")
        
        return mvp_time < old_time * 2  # MVP 版本不應該慢太多
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def test_edge_cases():
    """測試邊界情況"""
    print("\n🔍 Testing Edge Cases")
    print("=" * 40)
    
    try:
        from mvp_collaboration_detector import MVPCollaborationDetector
        
        detector = MVPCollaborationDetector()
        
        # 邊界測試用例
        edge_cases = [
            # 空字符串和特殊字符
            ("", False),
            ("   ", False),
            ("!!!", False),
            
            # 混合語言
            ("Search for 資料 and then 分析", True),
            ("Find data 然後 process it", True),
            
            # 長文本
            ("This is a very long sentence that contains multiple words and phrases but only has one main action which is to search for information", False),
            
            # 複雜標點
            ("Search, find, and then analyze data!", True),
            ("Search; find; analyze data.", True),
            
            # 大小寫混合
            ("SEARCH FOR DATA AND THEN ANALYZE", True),
            ("search for data and then analyze", True),
        ]
        
        passed_tests = 0
        total_tests = len(edge_cases)
        
        print("📋 Edge Case Results:")
        print("-" * 30)
        
        for text, expected in edge_cases:
            try:
                result = detector.detect_collaborative_task(text)
                is_correct = result == expected
                
                if is_correct:
                    passed_tests += 1
                
                status = "✅" if is_correct else "❌"
                print(f"{status} '{text[:30]}...' -> {result} (expected {expected})")
                
            except Exception as e:
                print(f"❌ Error processing '{text[:20]}...': {e}")
        
        success_rate = passed_tests / total_tests * 100
        print(f"\n📊 Edge Case Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        return success_rate >= 70
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        return False


def main():
    """主測試函數"""
    print("🚀 MVP Collaboration Detector Integration Test")
    print("=" * 60)
    
    test_results = []
    
    # 運行所有測試
    tests = [
        ("MVP Detector Integration", test_mvp_detector_integration),
        ("Performance Comparison", test_performance_comparison),
        ("Edge Cases", test_edge_cases)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            test_results.append((test_name, False))
    
    # 總結結果
    print("\n" + "=" * 60)
    print("📊 MVP Integration Test Results")
    print("=" * 60)
    
    passed_tests = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    success_rate = passed_tests / len(test_results) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{len(test_results)})")
    
    if success_rate >= 80:
        print("\n🎉 MVP INTEGRATION SUCCESSFUL!")
        print("✅ MVP detector properly integrated")
        print("✅ Performance is acceptable")
        print("✅ Edge cases handled well")
        print("\n🚀 Ready to proceed to step 2: Privacy and Localization MVP!")
    else:
        print("\n⚠️  INTEGRATION NEEDS IMPROVEMENT")
        print("❌ Some tests failed")
        print("🔧 Review and fix issues before proceeding")
    
    return success_rate >= 80


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
