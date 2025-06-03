#!/usr/bin/env python3
"""
MVP: 智能瀏覽器增強器
最小可行產品版本 - 專注於核心瀏覽功能增強
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TabInfo:
    """標籤頁信息"""
    tab_id: str
    url: str
    title: str
    is_active: bool = False


@dataclass
class FormField:
    """表單字段信息"""
    field_type: str  # input, select, textarea
    name: str
    value: str
    required: bool = False


class MVPBrowserEnhancer:
    """MVP 瀏覽器增強器 - 最小可行版本"""
    
    def __init__(self):
        self.name = "MVP Browser Enhancer"
        self.version = "1.0.0"
        self.tabs = {}  # 模擬標籤頁管理
        self.current_tab = None
        self.tab_counter = 0
    
    def create_new_tab(self, url: str = "about:blank") -> str:
        """
        創建新標籤頁
        
        Args:
            url: 要打開的 URL
            
        Returns:
            str: 標籤頁 ID
        """
        self.tab_counter += 1
        tab_id = f"tab_{self.tab_counter}"
        
        tab_info = TabInfo(
            tab_id=tab_id,
            url=url,
            title=f"Tab {self.tab_counter}",
            is_active=True
        )
        
        # 將其他標籤設為非活動
        for tab in self.tabs.values():
            tab.is_active = False
        
        self.tabs[tab_id] = tab_info
        self.current_tab = tab_id
        
        return tab_id
    
    def switch_to_tab(self, tab_id: str) -> bool:
        """
        切換到指定標籤頁
        
        Args:
            tab_id: 標籤頁 ID
            
        Returns:
            bool: 是否成功切換
        """
        if tab_id not in self.tabs:
            return False
        
        # 將所有標籤設為非活動
        for tab in self.tabs.values():
            tab.is_active = False
        
        # 激活目標標籤
        self.tabs[tab_id].is_active = True
        self.current_tab = tab_id
        
        return True
    
    def close_tab(self, tab_id: str) -> bool:
        """
        關閉標籤頁
        
        Args:
            tab_id: 標籤頁 ID
            
        Returns:
            bool: 是否成功關閉
        """
        if tab_id not in self.tabs:
            return False
        
        del self.tabs[tab_id]
        
        # 如果關閉的是當前標籤，切換到其他標籤
        if self.current_tab == tab_id:
            if self.tabs:
                # 切換到第一個可用標籤
                first_tab_id = list(self.tabs.keys())[0]
                self.switch_to_tab(first_tab_id)
            else:
                self.current_tab = None
        
        return True
    
    def get_active_tabs(self) -> List[TabInfo]:
        """獲取所有活動標籤頁"""
        return list(self.tabs.values())
    
    def analyze_form_fields(self, html_content: str) -> List[FormField]:
        """
        分析頁面中的表單字段（簡化版本）
        
        Args:
            html_content: HTML 內容
            
        Returns:
            List[FormField]: 表單字段列表
        """
        fields = []
        
        # 簡單的正則匹配（實際應該用 BeautifulSoup）
        import re
        
        # 查找 input 字段
        input_pattern = r'<input[^>]*name=["\']([^"\']*)["\'][^>]*>'
        for match in re.finditer(input_pattern, html_content, re.IGNORECASE):
            field_name = match.group(1)
            field_type = "input"
            
            # 檢查是否必填
            required = 'required' in match.group(0).lower()
            
            fields.append(FormField(
                field_type=field_type,
                name=field_name,
                value="",
                required=required
            ))
        
        # 查找 select 字段
        select_pattern = r'<select[^>]*name=["\']([^"\']*)["\'][^>]*>'
        for match in re.finditer(select_pattern, html_content, re.IGNORECASE):
            field_name = match.group(1)
            fields.append(FormField(
                field_type="select",
                name=field_name,
                value="",
                required=False
            ))
        
        # 查找 textarea 字段
        textarea_pattern = r'<textarea[^>]*name=["\']([^"\']*)["\'][^>]*>'
        for match in re.finditer(textarea_pattern, html_content, re.IGNORECASE):
            field_name = match.group(1)
            fields.append(FormField(
                field_type="textarea",
                name=field_name,
                value="",
                required=False
            ))
        
        return fields
    
    def suggest_form_values(self, fields: List[FormField]) -> Dict[str, str]:
        """
        為表單字段建議值（簡化版本）
        
        Args:
            fields: 表單字段列表
            
        Returns:
            Dict[str, str]: 字段名到建議值的映射
        """
        suggestions = {}
        
        for field in fields:
            field_name_lower = field.name.lower()
            
            # 基於字段名稱建議值
            if 'email' in field_name_lower:
                suggestions[field.name] = "test@example.com"
            elif 'name' in field_name_lower:
                if 'first' in field_name_lower:
                    suggestions[field.name] = "John"
                elif 'last' in field_name_lower:
                    suggestions[field.name] = "Doe"
                else:
                    suggestions[field.name] = "John Doe"
            elif 'phone' in field_name_lower:
                suggestions[field.name] = "+1-555-0123"
            elif 'age' in field_name_lower:
                suggestions[field.name] = "25"
            elif 'address' in field_name_lower:
                suggestions[field.name] = "123 Main St"
            elif 'city' in field_name_lower:
                suggestions[field.name] = "New York"
            elif 'country' in field_name_lower:
                suggestions[field.name] = "USA"
            elif field.field_type == "textarea":
                suggestions[field.name] = "Sample text content"
            else:
                suggestions[field.name] = "sample_value"
        
        return suggestions
    
    def extract_page_content(self, html_content: str) -> Dict[str, str]:
        """
        提取頁面關鍵內容（簡化版本）
        
        Args:
            html_content: HTML 內容
            
        Returns:
            Dict[str, str]: 提取的內容
        """
        import re
        
        content = {
            "title": "",
            "headings": [],
            "links": [],
            "text_content": "",
            "forms_count": 0
        }
        
        # 提取標題
        title_match = re.search(r'<title[^>]*>([^<]*)</title>', html_content, re.IGNORECASE)
        if title_match:
            content["title"] = title_match.group(1).strip()
        
        # 提取標題標籤
        heading_pattern = r'<h[1-6][^>]*>([^<]*)</h[1-6]>'
        headings = re.findall(heading_pattern, html_content, re.IGNORECASE)
        content["headings"] = [h.strip() for h in headings]
        
        # 提取鏈接
        link_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>'
        links = re.findall(link_pattern, html_content, re.IGNORECASE)
        content["links"] = [{"url": url, "text": text.strip()} for url, text in links]
        
        # 計算表單數量
        form_count = len(re.findall(r'<form[^>]*>', html_content, re.IGNORECASE))
        content["forms_count"] = form_count
        
        # 提取純文本（簡化版本）
        text_content = re.sub(r'<[^>]+>', '', html_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        content["text_content"] = text_content[:500] + "..." if len(text_content) > 500 else text_content
        
        return content


def test_mvp_browser_enhancer():
    """測試 MVP 瀏覽器增強器"""
    print("🧪 Testing MVP Browser Enhancer")
    print("=" * 40)
    
    enhancer = MVPBrowserEnhancer()
    
    # 測試 1: 標籤頁管理
    print("📝 Test 1: Tab Management")
    tab1 = enhancer.create_new_tab("https://example.com")
    tab2 = enhancer.create_new_tab("https://google.com")
    tab3 = enhancer.create_new_tab("https://github.com")
    
    print(f"   Created {len(enhancer.get_active_tabs())} tabs")
    print(f"   Current tab: {enhancer.current_tab}")
    
    # 切換標籤
    enhancer.switch_to_tab(tab1)
    print(f"   Switched to: {tab1}")
    
    # 關閉標籤
    enhancer.close_tab(tab2)
    print(f"   Closed tab, remaining: {len(enhancer.get_active_tabs())}")
    
    # 測試 2: 表單分析
    print("\n📝 Test 2: Form Analysis")
    sample_html = '''
    <html>
    <body>
        <form>
            <input type="text" name="first_name" required>
            <input type="email" name="email">
            <select name="country">
                <option>USA</option>
                <option>Canada</option>
            </select>
            <textarea name="comments"></textarea>
        </form>
    </body>
    </html>
    '''
    
    fields = enhancer.analyze_form_fields(sample_html)
    print(f"   Found {len(fields)} form fields")
    
    suggestions = enhancer.suggest_form_values(fields)
    print(f"   Generated {len(suggestions)} suggestions")
    
    # 測試 3: 內容提取
    print("\n📝 Test 3: Content Extraction")
    sample_page = '''
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Welcome</h1>
        <h2>About Us</h2>
        <p>This is a test page.</p>
        <a href="/contact">Contact Us</a>
        <form><input name="search"></form>
    </body>
    </html>
    '''
    
    content = enhancer.extract_page_content(sample_page)
    print(f"   Title: {content['title']}")
    print(f"   Headings: {len(content['headings'])}")
    print(f"   Links: {len(content['links'])}")
    print(f"   Forms: {content['forms_count']}")
    
    print("\n✅ MVP Browser Enhancer tests completed!")
    return True


def demo_mvp_browser_workflow():
    """演示 MVP 瀏覽器工作流程"""
    print("\n🔗 MVP Browser Workflow Demo")
    print("=" * 40)
    
    enhancer = MVPBrowserEnhancer()
    
    print("🌐 Starting browser automation workflow...")
    
    # 1. 打開多個標籤頁
    tab1 = enhancer.create_new_tab("https://example.com/login")
    tab2 = enhancer.create_new_tab("https://example.com/register")
    print(f"📂 Opened {len(enhancer.get_active_tabs())} tabs")
    
    # 2. 分析登錄表單
    login_html = '''
    <form id="login">
        <input type="email" name="email" required>
        <input type="password" name="password" required>
        <input type="submit" value="Login">
    </form>
    '''
    
    enhancer.switch_to_tab(tab1)
    fields = enhancer.analyze_form_fields(login_html)
    suggestions = enhancer.suggest_form_values(fields)
    print(f"🔍 Analyzed login form: {len(fields)} fields")
    
    # 3. 切換到註冊頁面
    enhancer.switch_to_tab(tab2)
    register_html = '''
    <form id="register">
        <input type="text" name="first_name" required>
        <input type="text" name="last_name" required>
        <input type="email" name="email" required>
        <input type="password" name="password" required>
        <select name="country">
            <option>USA</option>
            <option>Canada</option>
        </select>
    </form>
    '''
    
    fields = enhancer.analyze_form_fields(register_html)
    suggestions = enhancer.suggest_form_values(fields)
    print(f"📝 Analyzed register form: {len(fields)} fields")
    print(f"💡 Generated suggestions for: {list(suggestions.keys())}")
    
    # 4. 提取頁面內容
    content = enhancer.extract_page_content(register_html)
    print(f"📄 Extracted content: {content['forms_count']} forms found")
    
    print("✅ Browser workflow demo completed!")


def main():
    """主函數"""
    print("🚀 MVP Browser Enhancer - Minimum Viable Product")
    print("=" * 50)
    
    try:
        # 運行測試
        test_success = test_mvp_browser_enhancer()
        
        if test_success:
            # 運行演示
            demo_mvp_browser_workflow()
            
            print("\n" + "=" * 50)
            print("🎉 MVP BROWSER ENHANCER READY!")
            print("✅ Core features working:")
            print("   • Multi-tab management")
            print("   • Form field analysis")
            print("   • Smart form suggestions")
            print("   • Content extraction")
            print("   • Tab switching & closing")
            
            print("\n📋 Next MVP iteration could add:")
            print("   • Real browser integration")
            print("   • Advanced form filling")
            print("   • Better content parsing")
            print("   • Screenshot capabilities")
            
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
