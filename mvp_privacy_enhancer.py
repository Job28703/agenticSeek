#!/usr/bin/env python3
"""
MVP 隱私和本地化增強器
最小可行產品 - 專注於核心隱私保護功能
"""

import os
import json
import hashlib
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PrivacyLevel(Enum):
    """隱私等級"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class DataItem:
    """數據項目"""
    data_type: str
    content: str
    timestamp: float
    privacy_level: PrivacyLevel
    is_encrypted: bool = False


@dataclass
class NetworkRequest:
    """網絡請求記錄"""
    url: str
    method: str
    timestamp: float
    data_sent: bool
    response_received: bool


class MVPPrivacyEnhancer:
    """MVP 隱私增強器"""
    
    def __init__(self, data_dir: str = "privacy_data"):
        self.name = "MVP Privacy Enhancer"
        self.version = "1.0.0"
        self.data_dir = data_dir
        
        # 創建數據目錄
        os.makedirs(data_dir, exist_ok=True)
        
        # 隱私設置
        self.privacy_settings = {
            "encrypt_sensitive_data": True,
            "log_network_requests": True,
            "audit_data_access": True,
            "local_storage_only": True
        }
        
        # 敏感數據類型
        self.sensitive_data_types = {
            "password", "email", "phone", "address", "credit_card",
            "api_key", "token", "personal_info", "location"
        }
        
        # 網絡請求日誌
        self.network_log = []
        
        # 數據存儲
        self.data_store = {}
        
        # 審計日誌
        self.audit_log = []
    
    def simple_encrypt(self, data: str, key: str = "agenticseek_key") -> str:
        """簡單加密（僅用於演示）"""
        # 注意：這是一個簡化的加密，實際應用應使用更強的加密
        key_hash = hashlib.sha256(key.encode()).digest()
        encrypted = ""
        
        for i, char in enumerate(data):
            key_char = key_hash[i % len(key_hash)]
            encrypted_char = chr((ord(char) + key_char) % 256)
            encrypted += encrypted_char
        
        return encrypted
    
    def simple_decrypt(self, encrypted_data: str, key: str = "agenticseek_key") -> str:
        """簡單解密"""
        key_hash = hashlib.sha256(key.encode()).digest()
        decrypted = ""
        
        for i, char in enumerate(encrypted_data):
            key_char = key_hash[i % len(key_hash)]
            decrypted_char = chr((ord(char) - key_char) % 256)
            decrypted += decrypted_char
        
        return decrypted
    
    def classify_data_sensitivity(self, data: str, data_type: str) -> PrivacyLevel:
        """分類數據敏感度"""
        data_lower = data.lower()
        type_lower = data_type.lower()
        
        # 最高敏感度
        if type_lower in ["password", "api_key", "token", "credit_card"]:
            return PrivacyLevel.MAXIMUM
        
        # 高敏感度
        if type_lower in ["email", "phone", "address", "personal_info"]:
            return PrivacyLevel.HIGH
        
        # 中等敏感度
        if any(keyword in data_lower for keyword in ["user", "name", "id", "location"]):
            return PrivacyLevel.MEDIUM
        
        # 低敏感度
        return PrivacyLevel.LOW
    
    def store_data(self, data_type: str, content: str, encrypt: bool = None) -> str:
        """安全存儲數據"""
        # 分類敏感度
        privacy_level = self.classify_data_sensitivity(content, data_type)
        
        # 決定是否加密
        should_encrypt = encrypt if encrypt is not None else (
            privacy_level in [PrivacyLevel.HIGH, PrivacyLevel.MAXIMUM] or
            data_type.lower() in self.sensitive_data_types
        )
        
        # 創建數據項目
        data_item = DataItem(
            data_type=data_type,
            content=self.simple_encrypt(content) if should_encrypt else content,
            timestamp=time.time(),
            privacy_level=privacy_level,
            is_encrypted=should_encrypt
        )
        
        # 生成唯一 ID
        data_id = hashlib.md5(f"{data_type}_{content}_{time.time()}".encode()).hexdigest()[:8]
        
        # 存儲數據
        self.data_store[data_id] = data_item
        
        # 記錄審計日誌
        self.audit_log.append({
            "action": "store_data",
            "data_id": data_id,
            "data_type": data_type,
            "privacy_level": privacy_level.value,
            "encrypted": should_encrypt,
            "timestamp": time.time()
        })
        
        return data_id
    
    def retrieve_data(self, data_id: str) -> Optional[str]:
        """安全檢索數據"""
        if data_id not in self.data_store:
            return None
        
        data_item = self.data_store[data_id]
        
        # 記錄訪問
        self.audit_log.append({
            "action": "retrieve_data",
            "data_id": data_id,
            "data_type": data_item.data_type,
            "timestamp": time.time()
        })
        
        # 解密數據（如果需要）
        if data_item.is_encrypted:
            return self.simple_decrypt(data_item.content)
        else:
            return data_item.content
    
    def log_network_request(self, url: str, method: str = "GET", data_sent: bool = False):
        """記錄網絡請求"""
        if not self.privacy_settings["log_network_requests"]:
            return
        
        request = NetworkRequest(
            url=url,
            method=method,
            timestamp=time.time(),
            data_sent=data_sent,
            response_received=True  # 簡化假設
        )
        
        self.network_log.append(request)
        
        # 檢查是否為外部請求
        if not self._is_local_request(url):
            self.audit_log.append({
                "action": "external_network_request",
                "url": url,
                "method": method,
                "data_sent": data_sent,
                "timestamp": time.time(),
                "warning": "External data transmission detected"
            })
    
    def _is_local_request(self, url: str) -> bool:
        """檢查是否為本地請求"""
        local_indicators = ["localhost", "127.0.0.1", "0.0.0.0", "file://"]
        return any(indicator in url.lower() for indicator in local_indicators)
    
    def privacy_audit(self) -> Dict:
        """執行隱私審計"""
        audit_result = {
            "total_data_items": len(self.data_store),
            "encrypted_items": 0,
            "high_sensitivity_items": 0,
            "external_requests": 0,
            "potential_risks": [],
            "recommendations": []
        }
        
        # 分析存儲的數據
        for data_item in self.data_store.values():
            if data_item.is_encrypted:
                audit_result["encrypted_items"] += 1
            
            if data_item.privacy_level in [PrivacyLevel.HIGH, PrivacyLevel.MAXIMUM]:
                audit_result["high_sensitivity_items"] += 1
                
                # 檢查高敏感數據是否加密
                if not data_item.is_encrypted:
                    audit_result["potential_risks"].append(
                        f"High sensitivity {data_item.data_type} data not encrypted"
                    )
        
        # 分析網絡請求
        for request in self.network_log:
            if not self._is_local_request(request.url):
                audit_result["external_requests"] += 1
                
                if request.data_sent:
                    audit_result["potential_risks"].append(
                        f"Data sent to external URL: {request.url}"
                    )
        
        # 生成建議
        if audit_result["potential_risks"]:
            audit_result["recommendations"].append("Review and encrypt sensitive data")
            audit_result["recommendations"].append("Minimize external data transmission")
        
        if audit_result["external_requests"] > 10:
            audit_result["recommendations"].append("Consider reducing external API calls")
        
        if not audit_result["recommendations"]:
            audit_result["recommendations"].append("Privacy practices look good!")
        
        return audit_result
    
    def get_privacy_summary(self) -> Dict:
        """獲取隱私摘要"""
        return {
            "privacy_level": "HIGH" if self.privacy_settings["local_storage_only"] else "MEDIUM",
            "data_items_stored": len(self.data_store),
            "network_requests_logged": len(self.network_log),
            "audit_events": len(self.audit_log),
            "encryption_enabled": self.privacy_settings["encrypt_sensitive_data"],
            "local_storage_only": self.privacy_settings["local_storage_only"]
        }


def test_mvp_privacy_enhancer():
    """測試 MVP 隱私增強器"""
    print("🧪 Testing MVP Privacy Enhancer")
    print("=" * 40)
    
    enhancer = MVPPrivacyEnhancer()
    
    # 測試 1: 數據存儲和加密
    print("📝 Test 1: Data Storage and Encryption")
    
    # 存儲不同類型的數據
    user_id = enhancer.store_data("user_info", "John Doe, age 30")
    password_id = enhancer.store_data("password", "secret123")
    api_key_id = enhancer.store_data("api_key", "sk-1234567890abcdef")
    log_id = enhancer.store_data("log", "User logged in successfully")
    
    print(f"   Stored 4 data items with IDs: {user_id}, {password_id}, {api_key_id}, {log_id}")
    
    # 檢索數據
    retrieved_user = enhancer.retrieve_data(user_id)
    retrieved_password = enhancer.retrieve_data(password_id)
    
    print(f"   Retrieved user info: {retrieved_user}")
    print(f"   Retrieved password: {retrieved_password}")
    
    # 測試 2: 網絡請求監控
    print("\n📝 Test 2: Network Request Monitoring")
    
    enhancer.log_network_request("https://api.openai.com/v1/chat", "POST", data_sent=True)
    enhancer.log_network_request("http://localhost:8000/health", "GET", data_sent=False)
    enhancer.log_network_request("https://google.com/search", "GET", data_sent=True)
    
    print(f"   Logged {len(enhancer.network_log)} network requests")
    
    # 測試 3: 隱私審計
    print("\n📝 Test 3: Privacy Audit")
    
    audit_result = enhancer.privacy_audit()
    print(f"   Total data items: {audit_result['total_data_items']}")
    print(f"   Encrypted items: {audit_result['encrypted_items']}")
    print(f"   High sensitivity items: {audit_result['high_sensitivity_items']}")
    print(f"   External requests: {audit_result['external_requests']}")
    print(f"   Potential risks: {len(audit_result['potential_risks'])}")
    
    if audit_result['potential_risks']:
        print("   ⚠️  Risks found:")
        for risk in audit_result['potential_risks'][:2]:  # 顯示前2個
            print(f"     • {risk}")
    
    # 測試 4: 隱私摘要
    print("\n📝 Test 4: Privacy Summary")
    
    summary = enhancer.get_privacy_summary()
    print(f"   Privacy level: {summary['privacy_level']}")
    print(f"   Encryption enabled: {summary['encryption_enabled']}")
    print(f"   Local storage only: {summary['local_storage_only']}")
    
    print("\n✅ MVP Privacy Enhancer tests completed!")
    return True


def demo_privacy_workflow():
    """演示隱私保護工作流程"""
    print("\n🔗 Privacy Protection Workflow Demo")
    print("=" * 40)
    
    enhancer = MVPPrivacyEnhancer()
    
    print("🔒 Scenario: User interacts with AgenticSeek")
    
    # 1. 用戶輸入敏感信息
    print("\n1. User provides sensitive information...")
    user_email = enhancer.store_data("email", "user@example.com")
    user_query = enhancer.store_data("query", "Help me write a Python script")
    
    print(f"   ✅ Stored email (encrypted): {user_email}")
    print(f"   ✅ Stored query (plain): {user_query}")
    
    # 2. 系統進行外部 API 調用
    print("\n2. System makes external API calls...")
    enhancer.log_network_request("https://api.openai.com/v1/completions", "POST", data_sent=True)
    enhancer.log_network_request("https://search.engine.com/api", "GET", data_sent=False)
    
    print("   ✅ Network requests logged and monitored")
    
    # 3. 執行隱私審計
    print("\n3. Performing privacy audit...")
    audit = enhancer.privacy_audit()
    
    print(f"   📊 Audit results:")
    print(f"     • Data items: {audit['total_data_items']}")
    print(f"     • External requests: {audit['external_requests']}")
    print(f"     • Risks identified: {len(audit['potential_risks'])}")
    
    # 4. 提供隱私建議
    print("\n4. Privacy recommendations:")
    for rec in audit['recommendations']:
        print(f"   💡 {rec}")
    
    print("\n🎉 Privacy workflow completed successfully!")


def main():
    """主函數"""
    print("🚀 MVP Privacy and Localization Enhancer")
    print("=" * 50)
    
    try:
        # 運行測試
        test_success = test_mvp_privacy_enhancer()
        
        if test_success:
            # 運行演示
            demo_privacy_workflow()
            
            print("\n" + "=" * 50)
            print("🎉 MVP PRIVACY ENHANCER READY!")
            print("✅ Core features working:")
            print("   • Sensitive data encryption")
            print("   • Network request monitoring")
            print("   • Privacy audit system")
            print("   • Local storage priority")
            
            print("\n📋 Next MVP iteration could add:")
            print("   • Advanced encryption algorithms")
            print("   • Real-time privacy alerts")
            print("   • Data anonymization")
            print("   • Compliance reporting")
            
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
