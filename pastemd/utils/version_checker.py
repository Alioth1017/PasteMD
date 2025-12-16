"""版本更新检查器"""

import json
import re
from typing import Tuple
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

from .app_logging import log


class VersionChecker:
    """检查 GitHub 最新版本"""
    
    GITHUB_API_URL = "https://api.github.richqaq.cn/repos/RICHQAQ/PasteMD/releases/latest"
    TIMEOUT = 5  # 超时时间（秒）
    PRERANK = {"dev": 0, "rc": 1, "final": 2}
    
    def __init__(self, current_version: str):
        """
        初始化版本检查器
        
        Args:
            current_version: 当前应用版本号
        """
        self.current_version = current_version
    
    def check_update(self) -> Optional[Dict[str, Any]]:
        """
        检查是否有新版本
        
        Returns:
            如果有新版本，返回包含以下字段的字典：
            - has_update: bool, 是否有更新
            - latest_version: str, 最新版本号
            - release_url: str, 发布页面链接
            - release_notes: str, 发布说明
            如果检查失败，返回 None
        """
        try:
            # 获取最新版本信息
            latest_info = self._fetch_latest_release()
            if not latest_info:
                return None
            
            latest_version = latest_info.get("tag_name", "").lstrip("v")
            if not latest_version:
                log("Failed to parse latest version from GitHub")
                return None
            
            # 比较版本号
            if self._compare_versions(latest_version, self.current_version):
                return {
                    "has_update": True,
                    "latest_version": latest_version,
                    "current_version": self.current_version,
                    "release_url": latest_info.get("html_url", ""),
                    "release_notes": latest_info.get("body", "暂无发布说明")[:200]  # 限制长度
                }
            else:
                log(f"Already on latest version: {self.current_version}")
                return {
                    "has_update": False,
                    "latest_version": latest_version,
                    "current_version": self.current_version
                }
                
        except Exception as e:
            log(f"Version check failed: {e}")
            return None
    
    def _fetch_latest_release(self) -> Optional[Dict[str, Any]]:
        """
        从 GitHub API 获取最新 release 信息

        优先尝试直连（不使用任何代理），如果失败，再回退到使用系统代理。
        """
        req = urllib.request.Request(
            self.GITHUB_API_URL,
            headers={
                "User-Agent": f"PasteMD/{self.current_version}",
                "version": self.current_version,
            },
        )

        # 依次尝试：先不使用代理，再使用系统代理
        for use_proxy in (False, True):
            try:
                if not use_proxy:
                    # 先不使用代理
                    log("Checking version (no proxy)...")
                    opener = urllib.request.build_opener(
                        urllib.request.ProxyHandler({})
                    )
                    response = opener.open(req, timeout=self.TIMEOUT)
                else:
                    # 回退：使用系统代理 / 环境变量配置的代理
                    log("Direct check failed, retrying with system proxy...")
                    response = urllib.request.urlopen(req, timeout=self.TIMEOUT)

                with response:
                    if response.status == 200:
                        try:
                            data = json.loads(response.read().decode("utf-8"))
                            return data
                        except json.JSONDecodeError as e:
                            log(f"Failed to parse GitHub API response: {e}")
                            return None

            except urllib.error.URLError as e:
                # 第一轮直连失败会进入这里，for 循环会继续第二轮使用代理
                # 第二轮再失败就直接退出循环
                mode = "no-proxy" if not use_proxy else "proxy"
                log(f"Network error while checking version ({mode}): {e}")
            except Exception as e:
                mode = "no-proxy" if not use_proxy else "proxy"
                log(f"Unexpected error while fetching release info ({mode}): {e}")

        # 两种方式都失败
        return None
    
    def _compare_versions(self, latest: str, current: str) -> bool:
        ln, lrank, lpre = self._parse_version_parts(latest)
        cn, crank, cpre = self._parse_version_parts(current)

        n = max(len(ln), len(cn))
        ln = ln + (0,) * (n - len(ln))
        cn = cn + (0,) * (n - len(cn))

        return (ln, lrank, lpre) > (cn, crank, cpre)

    def _parse_version_parts(self, version_str: str) -> Tuple[Tuple[int, ...], int, int]:
        s = (version_str or "").strip().lstrip("vV").lower()
        if not s:
            return (), self.PRERANK["final"], 0

        s = s.split("+", 1)[0]

        pre_tag = None
        pre_num = 0
        m = re.search(r"(?:^|[.\-_])?(dev|rc)\s*\.?\s*(\d*)\b", s)
        if m:
            pre_tag = m.group(1)
            pre_num = int(m.group(2) or 0)

        parts = re.split(r"[.\-_]", s)
        nums = []
        for part in parts:
            if not part:
                continue
            m2 = re.match(r"(\d+)", part)
            if not m2:
                break
            nums.append(int(m2.group(1)))

        if not nums:
            return (), self.PRERANK["final"], 0

        rank = self.PRERANK["final"] if pre_tag is None else self.PRERANK[pre_tag]
        return tuple(nums), rank, pre_num