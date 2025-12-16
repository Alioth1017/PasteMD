"""Single instance check to prevent multiple application instances."""

import sys
import os
import errno
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
        """Unix-like 平台检查（使用文件锁），带陈旧锁自检"""

        def _lock() -> bool:
            log(f"Attempting to acquire lock: {self.lock_file_path}")
            self.lock_file = open(self.lock_file_path, "a+")
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            # 写入当前 PID，便于崩溃后识别陈旧锁
            try:
                self.lock_file.seek(0)
                self.lock_file.truncate()
                self.lock_file.write(str(os.getpid()))
                self.lock_file.flush()
            except Exception as e:
                log(f"Failed to write PID to lock file: {e}")
            log(f"Lock file acquired: {self.lock_file_path} (PID: {os.getpid()})")
            return False

        def _is_stale() -> bool:
            try:
                with open(self.lock_file_path, "r") as f:
                    pid_str = f.read().strip()
                    log(f"Lock file contains PID: '{pid_str}'")
                    if not pid_str.isdigit():
                        log("Lock file PID is not a number, treating as stale")
                        return True
                    pid = int(pid_str)
                # 检查进程是否存在
                try:
                    os.kill(pid, 0)
                    log(f"Process {pid} exists, lock is NOT stale")
                except OSError as e:
                    is_dead = e.errno == errno.ESRCH
                    log(f"Process {pid} check result: errno={e.errno}, dead={is_dead}")
                    return is_dead  # 进程不存在
                return False
            except FileNotFoundError:
                log("Lock file not found, treating as stale")
                return True
            except Exception as e:
                log(f"Error checking if lock is stale: {e}")
                return False

        try:
            return _lock()
        except IOError as e:
            log(f"Failed to acquire lock (errno={e.errno}), checking if stale...")
            # 尝试判断是否陈旧锁
            if _is_stale():
                log("Lock is stale, attempting to clean and retry")
                try:
                    os.unlink(self.lock_file_path)
                    log(f"Removed stale lock file: {self.lock_file_path}")
                except Exception as unlink_err:
                    log(f"Failed to remove stale lock: {unlink_err}")
                try:
                    return _lock()
                except Exception as retry_err:
                    log(f"Retry lock failed after cleaning stale lock: {retry_err}")
                    return True
            log(f"Lock file already held by live process: {self.lock_file_path}")
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
    log("=== Starting single instance check ===")
    checker = SingleInstanceChecker()
    
    # 检查是否已有实例在运行
    if checker.is_already_running():
        log("*** Another instance detected, exiting ***")
        return False
    
    # 尝试获取锁
    if not checker.acquire_lock():
        log("*** Failed to acquire application lock, exiting ***")
        return False
    
    # 保存检查器实例以便后续释放锁
    app_state.instance_checker = checker
    log("=== Single instance check passed ===")
    
    return True
