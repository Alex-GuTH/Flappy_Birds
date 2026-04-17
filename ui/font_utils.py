"""字体加载工具：优先使用项目内置中文字体，其次尝试系统中文字体。"""

from pathlib import Path
import pygame


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 优先使用仓库内字体（适配 GitHub Pages / pygbag）
BUNDLED_FONT_CANDIDATES = [
    PROJECT_ROOT / "assets" / "fonts" / "NotoSansCJKsc-Regular.otf",
    PROJECT_ROOT / "assets" / "fonts" / "NotoSansSC-Regular.otf",
    PROJECT_ROOT / "assets" / "fonts" / "SourceHanSansSC-Regular.otf",
]

# 常见中文系统字体候选
SYSTEM_FONT_CANDIDATES = [
    "Microsoft YaHei",
    "Microsoft YaHei UI",
    "SimHei",
    "PingFang SC",
    "Heiti SC",
    "Noto Sans CJK SC",
    "WenQuanYi Zen Hei",
    "Arial Unicode MS",
]


def load_cjk_font(size: int) -> pygame.font.Font:
    """加载可显示中文的字体。"""
    for font_path in BUNDLED_FONT_CANDIDATES:
        if font_path.exists():
            try:
                return pygame.font.Font(str(font_path), size)
            except Exception:
                pass

    for font_name in SYSTEM_FONT_CANDIDATES:
        try:
            matched = pygame.font.match_font(font_name)
            if matched:
                return pygame.font.Font(matched, size)
        except Exception:
            pass

    # 最后兜底：可能无法显示中文，但至少不崩溃
    return pygame.font.Font(None, size)
