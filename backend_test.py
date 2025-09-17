#!/usr/bin/env python3
"""
WhatsApp Bot Management System - Backend API Tests
Testing all endpoints for functionality and proper responses
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://chatops-control.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class WhatsAppBotTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, "Service is healthy", data)
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected status: {data.get('status')}", data)
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test authentication endpoints"""
        # Test login
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.log_test("Authentication Login", True, f"Login successful for user: {data['user']['username']}", data)
                    
                    # Test get current user with token
                    headers = {"Authorization": f"Bearer {self.auth_token}"}
                    me_response = self.session.get(f"{API_BASE}/auth/me", headers=headers, timeout=10)
                    
                    if me_response.status_code == 200:
                        me_data = me_response.json()
                        self.log_test("Authentication Me", True, f"User info retrieved: {me_data.get('username')}", me_data)
                        return True
                    else:
                        self.log_test("Authentication Me", False, f"HTTP {me_response.status_code}: {me_response.text}")
                        return False
                else:
                    self.log_test("Authentication Login", False, "Missing access_token or user in response", data)
                    return False
            else:
                self.log_test("Authentication Login", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Connection error: {str(e)}")
            return False
    
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/dashboard/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_instances", "active_instances", "total_messages", "messages_today", 
                                 "total_campaigns", "active_campaigns", "total_revenue", "monthly_revenue"]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Dashboard Stats", True, f"All statistics retrieved: {len(required_fields)} fields", data)
                    return True
                else:
                    self.log_test("Dashboard Stats", False, f"Missing fields: {missing_fields}", data)
                    return False
            else:
                self.log_test("Dashboard Stats", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Stats", False, f"Connection error: {str(e)}")
            return False
    
    def test_whatsapp_instances(self):
        """Test WhatsApp instances endpoints"""
        try:
            # Test GET instances
            response = self.session.get(f"{API_BASE}/instances", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("WhatsApp Instances List", True, f"Retrieved {len(data)} instances", data)
                    
                    # Test POST create instance
                    new_instance = {
                        "name": "Test Instance",
                        "description": "Created by automated test"
                    }
                    
                    create_response = self.session.post(f"{API_BASE}/instances", json=new_instance, timeout=10)
                    
                    if create_response.status_code == 200:
                        create_data = create_response.json()
                        if "id" in create_data and "name" in create_data:
                            self.log_test("WhatsApp Instance Create", True, f"Instance created with ID: {create_data['id']}", create_data)
                            return True
                        else:
                            self.log_test("WhatsApp Instance Create", False, "Missing id or name in response", create_data)
                            return False
                    else:
                        self.log_test("WhatsApp Instance Create", False, f"HTTP {create_response.status_code}: {create_response.text}")
                        return False
                else:
                    self.log_test("WhatsApp Instances List", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("WhatsApp Instances List", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("WhatsApp Instances", False, f"Connection error: {str(e)}")
            return False
    
    def test_messages(self):
        """Test messages endpoints"""
        try:
            # Test GET messages
            response = self.session.get(f"{API_BASE}/messages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Messages List", True, f"Retrieved {len(data)} messages", data)
                    
                    # Test POST send message
                    message_data = {
                        "instance_id": "1",
                        "to": "+5511999999999",
                        "message": "Test message from automated testing"
                    }
                    
                    send_response = self.session.post(f"{API_BASE}/messages/send", json=message_data, timeout=10)
                    
                    if send_response.status_code == 200:
                        send_data = send_response.json()
                        if "id" in send_data and "status" in send_data:
                            self.log_test("Message Send", True, f"Message sent with status: {send_data['status']}", send_data)
                            return True
                        else:
                            self.log_test("Message Send", False, "Missing id or status in response", send_data)
                            return False
                    else:
                        self.log_test("Message Send", False, f"HTTP {send_response.status_code}: {send_response.text}")
                        return False
                else:
                    self.log_test("Messages List", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("Messages List", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Messages", False, f"Connection error: {str(e)}")
            return False
    
    def test_campaigns(self):
        """Test campaigns endpoints"""
        try:
            # Test GET campaigns
            response = self.session.get(f"{API_BASE}/campaigns", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Campaigns List", True, f"Retrieved {len(data)} campaigns", data)
                    
                    # Test POST create campaign
                    campaign_data = {
                        "name": "Test Campaign",
                        "message": "🧪 This is a test campaign message created by automated testing"
                    }
                    
                    create_response = self.session.post(f"{API_BASE}/campaigns", json=campaign_data, timeout=10)
                    
                    if create_response.status_code == 200:
                        create_data = create_response.json()
                        if "id" in create_data and "name" in create_data:
                            self.log_test("Campaign Create", True, f"Campaign created with ID: {create_data['id']}", create_data)
                            return True
                        else:
                            self.log_test("Campaign Create", False, "Missing id or name in response", create_data)
                            return False
                    else:
                        self.log_test("Campaign Create", False, f"HTTP {create_response.status_code}: {create_response.text}")
                        return False
                else:
                    self.log_test("Campaigns List", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("Campaigns List", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Campaigns", False, f"Connection error: {str(e)}")
            return False
    
    def test_finances(self):
        """Test finances endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/finances", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Finances", True, f"Retrieved {len(data)} financial entries", data)
                    return True
                else:
                    self.log_test("Finances", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("Finances", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Finances", False, f"Connection error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print(f"\n🚀 Starting WhatsApp Bot Management System Backend Tests")
        print(f"📡 Testing API at: {API_BASE}")
        print("=" * 80)
        
        # Run tests in order
        tests = [
            self.test_health_check,
            self.test_authentication,
            self.test_dashboard_stats,
            self.test_whatsapp_instances,
            self.test_messages,
            self.test_campaigns,
            self.test_finances
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print("-" * 40)
        
        # Summary
        print("\n" + "=" * 80)
        print(f"📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! WhatsApp Bot Management System is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return passed == total

def main():
    """Main test execution"""
    tester = WhatsAppBotTester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open("/app/test_results_backend.json", "w") as f:
        json.dump(tester.test_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/test_results_backend.json")
    
    return success

if __name__ == "__main__":
    main()