#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_logbook.settings')
django.setup()

from issues.models import AuditLog

def check_audit_logs():
    print("🔍 Checking Recent Audit Logs")
    print("=" * 40)
    
    logs = AuditLog.objects.all().order_by('-created_at')[:10]
    
    print(f"Total audit logs: {AuditLog.objects.count()}")
    print(f"Showing recent {len(logs)} logs:")
    print()
    
    for log in logs:
        user_name = log.user.username if log.user else "System"
        issue_info = f" (Issue: {log.issue.auto_title})" if log.issue else ""
        print(f"📝 {user_name}: {log.get_action_display()}")
        print(f"   Description: {log.description}")
        print(f"   Time: {log.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   IP: {log.ip_address or 'N/A'}{issue_info}")
        if log.metadata:
            print(f"   Metadata: {log.metadata}")
        print()

if __name__ == "__main__":
    check_audit_logs() 