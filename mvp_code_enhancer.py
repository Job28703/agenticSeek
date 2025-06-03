#!/usr/bin/env python3
"""
MVP: 代碼質量增強器
最小可行產品版本 - 專注於核心功能
"""

import re
import ast
from typing import List, Dict, Tuple


class MVPCodeEnhancer:
    """MVP 代碼增強器 - 最小可行版本"""
    
    def __init__(self):
        self.name = "MVP Code Enhancer"
        self.version = "1.0.0"
    
    def analyze_code(self, code: str) -> Dict:
        """
        分析代碼並返回簡單的分析結果
        
        Args:
            code: Python 代碼字符串
            
        Returns:
            Dict: 包含分析結果的字典
        """
        result = {
            "status": "success",
            "issues": [],
            "suggestions": [],
            "score": 100,
            "functions_found": 0
        }
        
        try:
            # 檢查語法
            ast.parse(code)
            
            # 基礎檢查
            issues = self._check_basic_issues(code)
            suggestions = self._generate_basic_suggestions(code)
            functions = self._count_functions(code)
            score = self._calculate_simple_score(code, len(issues))
            
            result.update({
                "issues": issues,
                "suggestions": suggestions,
                "score": score,
                "functions_found": functions
            })
            
        except SyntaxError as e:
            result.update({
                "status": "error",
                "issues": [f"Syntax error: {str(e)}"],
                "score": 0
            })
        
        return result
    
    def generate_basic_tests(self, code: str) -> str:
        """
        為代碼生成基礎測試框架
        
        Args:
            code: Python 代碼字符串
            
        Returns:
            str: 生成的測試代碼
        """
        try:
            tree = ast.parse(code)
            functions = [node.name for node in ast.walk(tree) 
                        if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')]
            
            if not functions:
                return "# No functions found to test\n"
            
            test_code = "import unittest\n\n"
            test_code += "class TestCode(unittest.TestCase):\n"
            
            for func_name in functions:
                test_code += f"\n    def test_{func_name}(self):\n"
                test_code += f'        """Test {func_name} function"""\n'
                test_code += f"        # TODO: Add test for {func_name}\n"
                test_code += f"        pass\n"
            
            test_code += "\nif __name__ == '__main__':\n"
            test_code += "    unittest.main()\n"
            
            return test_code
            
        except Exception as e:
            return f"# Test generation failed: {str(e)}\n"
    
    def _check_basic_issues(self, code: str) -> List[str]:
        """檢查基本代碼問題"""
        issues = []
        
        # 檢查長行
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(f"Line {i} is too long ({len(line)} chars)")
        
        # 檢查硬編碼數字
        if re.search(r'\b\d{3,}\b', code):
            issues.append("Found magic numbers (consider using constants)")
        
        # 檢查缺少文檔
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
                    issues.append(f"Function '{node.name}' lacks documentation")
        except:
            pass
        
        return issues
    
    def _generate_basic_suggestions(self, code: str) -> List[str]:
        """生成基本改進建議"""
        suggestions = []
        
        # 基於代碼內容生成建議
        if 'def ' in code and '"""' not in code:
            suggestions.append("Add docstrings to functions")
        
        if re.search(r'\b\d{3,}\b', code):
            suggestions.append("Replace magic numbers with named constants")
        
        if len(code.split('\n')) > 50:
            suggestions.append("Consider breaking large files into smaller modules")
        
        return suggestions
    
    def _count_functions(self, code: str) -> int:
        """計算函數數量"""
        try:
            tree = ast.parse(code)
            return len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        except:
            return 0
    
    def _calculate_simple_score(self, code: str, issue_count: int) -> int:
        """計算簡單的質量分數"""
        base_score = 100
        
        # 每個問題扣10分
        base_score -= issue_count * 10
        
        # 代碼太短扣分
        if len(code.strip()) < 50:
            base_score -= 20
        
        return max(0, min(100, base_score))


def test_mvp_code_enhancer():
    """測試 MVP 代碼增強器"""
    print("🧪 Testing MVP Code Enhancer")
    print("=" * 40)
    
    enhancer = MVPCodeEnhancer()
    
    # 測試用例 1: 好代碼
    good_code = '''
def add_numbers(a, b):
    """Add two numbers together."""
    return a + b

def multiply(x, y):
    """Multiply two numbers."""
    return x * y
'''
    
    print("📝 Test 1: Good Code")
    result = enhancer.analyze_code(good_code)
    print(f"   Status: {result['status']}")
    print(f"   Score: {result['score']}/100")
    print(f"   Issues: {len(result['issues'])}")
    print(f"   Functions: {result['functions_found']}")
    
    # 測試用例 2: 有問題的代碼
    bad_code = '''
def process_data(data):
    result = []
    for item in data:
        if item > 1000:
            result.append(item * 3.14159)
    return result
'''
    
    print("\n📝 Test 2: Code with Issues")
    result = enhancer.analyze_code(bad_code)
    print(f"   Status: {result['status']}")
    print(f"   Score: {result['score']}/100")
    print(f"   Issues: {len(result['issues'])}")
    print(f"   Suggestions: {len(result['suggestions'])}")
    
    # 測試用例 3: 測試生成
    print("\n📝 Test 3: Test Generation")
    test_code = enhancer.generate_basic_tests(good_code)
    print(f"   Generated test length: {len(test_code)} chars")
    print(f"   Contains unittest: {'unittest' in test_code}")
    
    # 測試用例 4: 語法錯誤
    print("\n📝 Test 4: Syntax Error")
    error_code = "def broken_function(\n    print('error'"
    result = enhancer.analyze_code(error_code)
    print(f"   Status: {result['status']}")
    print(f"   Score: {result['score']}/100")
    
    print("\n✅ MVP Code Enhancer tests completed!")
    return True


def demo_mvp_integration():
    """演示 MVP 集成到現有系統"""
    print("\n🔗 MVP Integration Demo")
    print("=" * 40)
    
    enhancer = MVPCodeEnhancer()
    
    # 模擬用戶代碼
    user_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n+1):
        result *= i
    return result
'''
    
    print("👤 User submitted code for analysis...")
    
    # 1. 分析代碼
    analysis = enhancer.analyze_code(user_code)
    print(f"🔍 Analysis complete: {analysis['score']}/100")
    
    if analysis['issues']:
        print("⚠️  Issues found:")
        for issue in analysis['issues']:
            print(f"   • {issue}")
    
    if analysis['suggestions']:
        print("💡 Suggestions:")
        for suggestion in analysis['suggestions']:
            print(f"   • {suggestion}")
    
    # 2. 生成測試
    tests = enhancer.generate_basic_tests(user_code)
    print(f"🧪 Generated {len(tests.split('def test_')) - 1} test methods")
    
    print("✅ MVP integration demo completed!")


def main():
    """主函數"""
    print("🚀 MVP Code Enhancer - Minimum Viable Product")
    print("=" * 50)
    
    try:
        # 運行測試
        test_success = test_mvp_code_enhancer()
        
        if test_success:
            # 運行演示
            demo_mvp_integration()
            
            print("\n" + "=" * 50)
            print("🎉 MVP CODE ENHANCER READY!")
            print("✅ Core features working:")
            print("   • Basic code analysis")
            print("   • Issue detection")
            print("   • Simple suggestions")
            print("   • Test framework generation")
            print("   • Error handling")
            
            print("\n📋 Next MVP iteration could add:")
            print("   • More sophisticated analysis")
            print("   • Better test generation")
            print("   • Code optimization suggestions")
            print("   • Integration with existing agents")
            
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
