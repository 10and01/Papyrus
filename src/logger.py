import logging
import os
from datetime import datetime
import json

class PapyrusLogger:
    """Papyrus日志管理器"""
    
    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # 日志文件路径
        self.log_file = os.path.join(log_dir, "papyrus.log")
        self.error_log_file = os.path.join(log_dir, "error.log")
        self.activity_log_file = os.path.join(log_dir, "activity.log")
        # 结构化事件日志（JSONL）：用于监控 AI 工具调用 / MCP 请求等
        self.events_log_file = os.path.join(log_dir, "events.log")

        # 配置主日志记录器
        self.logger = logging.getLogger("Papyrus")
        self.logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 文件处理器 - 所有日志
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 错误日志处理器
        error_handler = logging.FileHandler(self.error_log_file, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(file_formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """记录信息日志"""
        self.logger.info(message)
    
    def error(self, message):
        """记录错误日志"""
        self.logger.error(message)
    
    def warning(self, message):
        """记录警告日志"""
        self.logger.warning(message)
    
    def debug(self, message):
        """记录调试日志"""
        self.logger.debug(message)
    
    def _sanitize(self, obj, max_str_len=800):
        """尽量安全地写入日志：
        - 对可能的密钥字段做脱敏
        - 对超长字符串做截断
        """

        def _mask_value(v):
            if not isinstance(v, str):
                return v
            if len(v) <= 8:
                return "***"
            return v[:3] + "***" + v[-2:]

        def _truncate_str(s: str):
            if len(s) <= max_str_len:
                return s
            return s[:max_str_len] + f"...<truncated:{len(s)}chars>"

        if obj is None:
            return None

        if isinstance(obj, str):
            return _truncate_str(obj)

        if isinstance(obj, (int, float, bool)):
            return obj

        if isinstance(obj, list):
            return [self._sanitize(x, max_str_len=max_str_len) for x in obj]

        if isinstance(obj, dict):
            masked = {}
            for k, v in obj.items():
                key_lower = str(k).lower()
                if any(t in key_lower for t in ["api_key", "authorization", "token", "secret", "password", "key"]):
                    masked[k] = _mask_value(v)
                else:
                    masked[k] = self._sanitize(v, max_str_len=max_str_len)
            return masked

        # fallback：转字符串
        return _truncate_str(str(obj))

    def log_event(self, event_type, data=None, level="INFO"):
        """记录结构化事件（JSONL），用于监控 AI 工具调用 / MCP 服务器等"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "level": level,
            "data": self._sanitize(data or {}),
        }

        try:
            with open(self.events_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as e:
            self.error(f"记录事件失败: {e}")

    def log_activity(self, activity_type, details):
        """记录用户活动"""
        activity = {
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "details": self._sanitize(details or {}),
        }
        
        try:
            with open(self.activity_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(activity, ensure_ascii=False) + "\n")
        except Exception as e:
            self.error(f"记录活动失败: {e}")
    
    def get_logs(self, log_type="all", limit=100):
        """获取日志内容"""
        log_file_map = {
            "all": self.log_file,
            "error": self.error_log_file,
            "activity": self.activity_log_file,
            "events": self.events_log_file,
        }
        
        log_file = log_file_map.get(log_type, self.log_file)
        
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return lines[-limit:] if limit else lines
        except Exception as e:
            self.error(f"读取日志失败: {e}")
            return []
    
    def clear_logs(self):
        """清空日志文件"""
        for log_file in [
            self.log_file,
            self.error_log_file,
            self.activity_log_file,
            self.events_log_file,
        ]:
            if os.path.exists(log_file):
                try:
                    open(log_file, "w").close()
                    self.info("日志已清空")
                except Exception as e:
                    self.error(f"清空日志失败: {e}")
    
    def export_logs(self, export_path):
        """导出日志到指定路径"""
        try:
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = os.path.join(export_path, f"papyrus_logs_{timestamp}.txt")
            os.makedirs(export_path, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as out:
                out.write("=" * 50 + "\n")
                out.write("Papyrus 日志导出\n")
                out.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                out.write("=" * 50 + "\n\n")
                
                # 导出主日志
                out.write("【主日志】\n")
                out.write("-" * 50 + "\n")
                logs = self.get_logs("all", limit=None)
                out.writelines(logs)
                out.write("\n\n")
                
                # 导出错误日志
                out.write("【错误日志】\n")
                out.write("-" * 50 + "\n")
                error_logs = self.get_logs("error", limit=None)
                out.writelines(error_logs)
                out.write("\n\n")
                
                # 导出活动日志
                out.write("【活动日志】\n")
                out.write("-" * 50 + "\n")
                activity_logs = self.get_logs("activity", limit=None)
                out.writelines(activity_logs)
                out.write("\n\n")

                # 导出事件日志
                out.write("【事件日志】\n")
                out.write("-" * 50 + "\n")
                events_logs = self.get_logs("events", limit=None)
                out.writelines(events_logs)

            return export_file
        except Exception as e:
            self.error(f"导出日志失败: {e}")
            return None