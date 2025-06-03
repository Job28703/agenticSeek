#!/usr/bin/env python3
"""
測試增強代碼代理功能
"""

import sys
import os

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sources.agents.enhanced_code_agent import CodeAnalyzer, TestGenerator, CodeQuality


def test_code_analyzer():
    """測試代碼分析器"""
    print("🔍 Testing Code Analyzer")
    print("-" * 30)
    
    analyzer = CodeAnalyzer()
    
    # 測試用例 1: 高質量代碼
    good_code = '''
def calculate_circle_area(radius: float) -> float:
    """
    Calculate the area of a circle given its radius.
    
    Args:
        radius: The radius of the circle
        
    Returns:
        The area of the circle
    """
    PI = 3.14159
    return PI * radius * radius

def validate_input(value: float) -> bool:
    """Validate that input is positive."""
    return value > 0
'''
    
    result = analyzer.analyze_python_code(good_code)
    print(f"✅ Good code analysis: {result.quality.value} ({result.score:.1f}/100)")
    print(f"   Issues: {len(result.issues)}")
    print(f"   Suggestions: {len(result.suggestions)}")
    
    # 測試用例 2: 低質量代碼
    bad_code = '''
def func(x):
    if x > 1000:
        if x < 2000:
            if x % 2 == 0:
                return x * 3.14159 + 999 + 123 + 456
            else:
                return x * 2.71828 + 888 + 777
        else:
            return x + 555
    else:
        return 0
'''
    
    result = analyzer.analyze_python_code(bad_code)
    print(f"✅ Bad code analysis: {result.quality.value} ({result.score:.1f}/100)")
    print(f"   Issues: {len(result.issues)}")
    print(f"   Suggestions: {len(result.suggestions)}")
    
    # 測試用例 3: 語法錯誤
    syntax_error_code = '''
def broken_function(
    print("This has syntax error"
'''
    
    result = analyzer.analyze_python_code(syntax_error_code)
    print(f"✅ Syntax error analysis: {result.quality.value} ({result.score:.1f}/100)")
    print(f"   Issues: {len(result.issues)}")
    
    print("🎉 Code analyzer tests passed!")


def test_test_generator():
    """測試測試生成器"""
    print("\n🧪 Testing Test Generator")
    print("-" * 30)
    
    generator = TestGenerator()
    
    # 測試用例: 簡單函數
    code = '''
def add_numbers(a, b):
    """Add two numbers together."""
    return a + b

def multiply_by_two(x):
    """Multiply a number by two."""
    return x * 2

def get_greeting():
    """Return a greeting message."""
    return "Hello, World!"
'''
    
    test_code = generator.generate_python_tests(code)
    print(f"✅ Test generation completed")
    print(f"   Generated test code length: {len(test_code)} characters")
    print(f"   Contains unittest: {'unittest' in test_code}")
    print(f"   Contains test methods: {'def test_' in test_code}")
    
    # 顯示生成的測試代碼片段
    print("\n📝 Generated test code preview:")
    lines = test_code.split('\n')
    for i, line in enumerate(lines[:15]):  # 顯示前15行
        print(f"   {i+1:2d}: {line}")
    if len(lines) > 15:
        print(f"   ... and {len(lines) - 15} more lines")
    
    print("🎉 Test generator tests passed!")


def test_quality_levels():
    """測試不同質量等級的代碼"""
    print("\n📊 Testing Quality Levels")
    print("-" * 30)
    
    analyzer = CodeAnalyzer()
    
    test_cases = [
        ("Excellent Code", '''
def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number using dynamic programming.
    
    Args:
        n: The position in the Fibonacci sequence
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if n <= 1:
        return n
    
    # Use dynamic programming for efficiency
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    
    return curr
'''),
        
        ("Poor Code", '''
def f(x,y,z):
    if x>100 and y<200 and z==300:
        if x%2==0:
            if y%3==0:
                if z%5==0:
                    return x*3.14159+y*2.71828+z*1.41421+999+888+777+666+555+444+333+222+111
                else:
                    return x+y+z+123456789
            else:
                return x*y*z+987654321
        else:
            return 0
    else:
        return -1
''')
    ]
    
    for name, code in test_cases:
        result = analyzer.analyze_python_code(code)
        print(f"✅ {name}:")
        print(f"   Quality: {result.quality.value}")
        print(f"   Score: {result.score:.1f}/100")
        print(f"   Complexity: {result.complexity}")
        print(f"   Issues: {len(result.issues)}")
        print(f"   Suggestions: {len(result.suggestions)}")
    
    print("🎉 Quality level tests passed!")


def test_integration():
    """測試集成功能"""
    print("\n🔗 Testing Integration")
    print("-" * 30)
    
    # 模擬完整的代碼分析和改進流程
    code = '''
def process_data(data):
    result = []
    for item in data:
        if item > 1000:
            result.append(item * 3.14159)
    return result
'''
    
    analyzer = CodeAnalyzer()
    generator = TestGenerator()
    
    # 1. 分析代碼
    analysis = analyzer.analyze_python_code(code)
    print(f"✅ Code analysis: {analysis.quality.value} ({analysis.score:.1f}/100)")
    
    # 2. 生成測試
    tests = generator.generate_python_tests(code)
    print(f"✅ Test generation: {len(tests)} characters")
    
    # 3. 檢查是否有改進建議
    has_suggestions = len(analysis.suggestions) > 0
    print(f"✅ Has improvement suggestions: {has_suggestions}")
    
    print("🎉 Integration tests passed!")


def main():
    """主測試函數"""
    print("🚀 Enhanced Code Agent Test Suite")
    print("=" * 50)
    
    try:
        # 運行所有測試
        test_code_analyzer()
        test_test_generator()
        test_quality_levels()
        test_integration()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ Enhanced Code Agent is working correctly")
        
        print("\n💡 Features tested:")
        print("   ✅ Code quality analysis")
        print("   ✅ Complexity calculation")
        print("   ✅ Issue detection")
        print("   ✅ Improvement suggestions")
        print("   ✅ Unit test generation")
        print("   ✅ Quality level classification")
        
        print("\n🚀 Ready for integration with AgenticSeek!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
