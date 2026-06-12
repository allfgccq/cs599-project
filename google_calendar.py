import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 如果修改了这些权限，需要删除 token.json 文件
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    """获取谷歌日历服务"""
    creds = None
    
    # token.json 存储用户的访问令牌和刷新令牌
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # 如果没有有效的凭证，让用户登录
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                return None
        else:
            # 检查是否有credentials.json
            if not os.path.exists('credentials.json'):
                print("未找到 credentials.json，无法进行OAuth认证")
                return None
            
            try:
                # 使用内置的测试凭证流程（简化版）
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                
                # 使用本地服务器进行认证
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"OAuth认证失败: {e}")
                return None
        
        # 保存凭证供下次使用
        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        except Exception:
            pass
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"获取日历服务失败: {e}")
        return None

def create_calendar_event(service, title, date, description=""):
    """在谷歌日历中创建事件"""
    event = {
        'summary': title,
        'description': description,
        'start': {
            'date': date,
            'timeZone': 'Asia/Shanghai',
        },
        'end': {
            'date': date,
            'timeZone': 'Asia/Shanghai',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # 提前1天邮件提醒
                {'method': 'popup', 'minutes': 60},       # 提前1小时弹窗提醒
            ],
        },
    }
    
    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"事件创建成功: {event.get('htmlLink')}")
        return event
    except HttpError as error:
        print(f"创建事件失败: {error}")
        return None

def sync_itinerary_to_google_calendar(itinerary):
    """同步行程到谷歌日历"""
    # 检查是否有credentials.json
    if not os.path.exists('credentials.json'):
        return {"success": False, "error": "未配置谷歌日历API凭据，请提供credentials.json文件"}
    
    service = get_calendar_service()
    if not service:
        return {"success": False, "error": "无法连接到谷歌日历服务"}
    
    events_created = []
    
    try:
        for day_plan in itinerary['daily_plan']:
            event_title = f"{itinerary['destination']}旅行 Day{day_plan['day']}"
            event_date = day_plan['date']
            event_desc = "\n".join([f"- {a['name']}" for a in day_plan['attractions']])
            
            event = create_calendar_event(service, event_title, event_date, event_desc)
            if event:
                events_created.append({
                    "date": event_date,
                    "title": event_title,
                    "link": event.get('htmlLink')
                })
        
        return {
            "success": True,
            "events": events_created,
            "message": f"成功同步 {len(events_created)} 个日历事件"
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}
