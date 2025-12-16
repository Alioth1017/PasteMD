"""Single instance check to prevent multiple application instances."""

import sys
import os
from .state import app_state
from ..utils.app_logging import log

if sys.platform == 'win32':
    import ctypes
    # Windows API 函数定义
    kernel32 = ctypes.windll.kernel32
    # 常量
    ERROR_ALREADY_EXISTS = 183
else:
    import fcntl
    import tempfile


class SingleInstanceChecker:
    """检查和管理应用的单实例运行 - Windows 使用 Mutex，macOS/Linux 使用文件锁"""
    
    def __init__(self, app_name: str = "PasteMD"):
        self.app_name = app_name
        if sys.platform == 'win32':
            self.mutex_name = f"Global\\{app_name}-Mutex"
            self.mutex_handle = None
        else:
            # macOS/Linux: 使用临时文件锁
            self.lock_file_path = os.path.join(tempfile.gettempdir(), f"{app_name}.lock")
            self.lock_file = None
    
    def is_already_running(self) -> bool:
        """
        检查是否已有实例在运行
        
        Returns:
            bool: 如果已有实例运行返回 True，否则返回 False
        """
        if sys.platform == 'win32':
            return self._is_already_running_windows()
        else:
            return self._is_already_running_unix()
    
    def _is_already_running_windows(self) -> bool:
        """Windows 平台检查（使用 Mutex）"""
        try:
            # 创建或打开一个命名互斥体
            self.mutex_handle = kernel32.CreateMutexW(
                None,  # 默认安全属性
                True,  # 初始拥有者
                self.mutex_name  # 互斥体名称
            )
            
            if self.mutex_handle:
                last_error = kernel32.GetLastError()
                if last_error == ERROR_ALREADY_EXISTS:
                    log("Mutex already exists, another instance is running")
                    return True
                else:
                    log("Mutex created successfully")
                    return False
            else:
                log("Failed to create mutex")
                return False
        except Exception as e:
            log(f"Error checking single instance: {e}")
            return False
    
    def _is_already_running_unix(self) -> bool:
        """Unix-like 平台检查（使用文件锁）"""
        try:
            self.lock_file = open(self.lock_file_path, 'w')
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            log(f"Lock file acquired: {self.lock_file_path}")
            return False
        except IOError:
            log(f"Lock file already held, another instance is running: {self.lock_file_path}")
            return True
        except Exception as e:
            log(f"Error checking single instance: {e}")
            return False
    
    def acquire_lock(self) -> bool:
        """
        获取应用锁
        
        Returns:
            bool: 成功获取锁返回 True
        """
        if sys.platform == 'win32':
            # Mutex 已经在 is_already_running 中创建和获取
            if self.mutex_handle:
                log("Mutex lock acquired")
                return True
            return False
        else:
            # 文件锁已经在 is_already_running 中获取
            if self.lock_file:
                log("File lock acquired")
                return True
            return False
    
    def release_lock(self) -> None:
        """释放应用锁"""
        try:
            if sys.platform == 'win32':
                if self.mutex_handle:
                    kernel32.ReleaseMutex(self.mutex_handle)
                    kernel32.CloseHandle(self.mutex_handle)
                    self.mutex_handle = None
                    log("Mutex released")
            else:
                if self.lock_file:
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                    self.lock_file.close()
                    self.lock_file = None
                    # 尝试删除锁文件
                    try:
                        os.unlink(self.lock_file_path)
                    except Exception:
                        pass
                    log("File lock released")
        except Exception as e:
            log(f"Error releasing lock: {e}")


def check_single_instance() -> bool:
    """
    检查并确保应用只有一个实例运行
    
    Returns:
        bool: 如果这是第一个实例返回 True，否则返回 False 并退出程序
    """
    checker = SingleInstanceChecker()
    
    # 检查是否已有实例在运行
    if checker.is_already_running():
        log("Another instance of the application is already running")
        return False
    
    # 尝试获取锁
    if not checker.acquire_lock():
        log("Failed to acquire application lock")
        return False
    
    # 保存检查器实例以便后续释放锁
    app_state.instance_checker = checker
    
    return True
