from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.enums import DiagnosisType


@dataclass
class DiagnosisMatch:
    diagnosis_type: DiagnosisType
    root_cause: str
    suggestion: str
    confidence: float
    pattern: str


class LogDiagnosisEngine:
    def __init__(self) -> None:
        self.rules: list[tuple[DiagnosisMatch, re.Pattern[str]]] = [
            (
                DiagnosisMatch(
                    diagnosis_type=DiagnosisType.MISSING_DEPENDENCY,
                    root_cause="运行环境缺少必要依赖包或模块。",
                    suggestion="检查 requirements、安装缺失包，并确认虚拟环境与运行命令一致。",
                    confidence=0.93,
                    pattern=r"(ModuleNotFoundError|No module named|ImportError)",
                ),
                re.compile(r"(ModuleNotFoundError|No module named|ImportError)", re.I),
            ),
            (
                DiagnosisMatch(
                    diagnosis_type=DiagnosisType.CUDA_OOM,
                    root_cause="CUDA 显存不足或 GPU 资源分配失败。",
                    suggestion="减小 batch size、开启梯度累积、降低输入分辨率，或切换更大显存设备。",
                    confidence=0.96,
                    pattern=r"(CUDA out of memory|CUBLAS_STATUS_ALLOC_FAILED|out of memory)",
                ),
                re.compile(r"(CUDA out of memory|CUBLAS_STATUS_ALLOC_FAILED|out of memory)", re.I),
            ),
            (
                DiagnosisMatch(
                    diagnosis_type=DiagnosisType.PATH_NOT_FOUND,
                    root_cause="输入文件、数据目录或配置中指定的路径不存在。",
                    suggestion="确认数据集、checkpoint、配置文件路径与当前工作目录一致。",
                    confidence=0.92,
                    pattern=r"(No such file or directory|FileNotFoundError|cannot find the path)",
                ),
                re.compile(r"(No such file or directory|FileNotFoundError|cannot find the path)", re.I),
            ),
            (
                DiagnosisMatch(
                    diagnosis_type=DiagnosisType.DATA_FORMAT_ERROR,
                    root_cause="数据格式与代码预期不一致，可能是字段缺失、shape 错误或解析失败。",
                    suggestion="核对数据预处理、字段命名、shape 和数据加载器逻辑。",
                    confidence=0.9,
                    pattern=r"(ValueError:.*shape|JSONDecodeError|KeyError|Unexpected token|invalid literal)",
                ),
                re.compile(r"(ValueError:.*shape|JSONDecodeError|KeyError|Unexpected token|invalid literal)", re.I),
            ),
            (
                DiagnosisMatch(
                    diagnosis_type=DiagnosisType.CHECKPOINT_LOAD_FAILED,
                    root_cause="checkpoint 与当前模型结构、设备或权重命名不兼容。",
                    suggestion="确认 checkpoint 来源、strict 参数、模型版本和设备映射方式。",
                    confidence=0.91,
                    pattern=r"(Error\(s\) in loading state_dict|size mismatch for|checkpoint.*failed)",
                ),
                re.compile(r"(Error\(s\) in loading state_dict|size mismatch for|checkpoint.*failed)", re.I),
            ),
            (
                DiagnosisMatch(
                    diagnosis_type=DiagnosisType.CONFIG_MISSING,
                    root_cause="运行所需配置项缺失，或配置文件结构不完整。",
                    suggestion="补齐默认配置、检查 YAML 键名，并为关键参数提供兜底值。",
                    confidence=0.89,
                    pattern=r"(Missing key|missing required positional argument|validation error|KeyError: 'config')",
                ),
                re.compile(r"(Missing key|missing required positional argument|validation error|KeyError: 'config')", re.I),
            ),
            (
                DiagnosisMatch(
                    diagnosis_type=DiagnosisType.NAN_OR_GRADIENT,
                    root_cause="训练过程出现数值不稳定，导致 loss=nan 或梯度异常。",
                    suggestion="降低学习率、检查归一化和混合精度配置，并观察梯度裁剪是否生效。",
                    confidence=0.94,
                    pattern=r"(loss[:=]\s*nan|gradient overflow|gradients? exploded|nan encountered)",
                ),
                re.compile(r"(loss[:=]\s*nan|gradient overflow|gradients? exploded|nan encountered)", re.I),
            ),
        ]

    def diagnose(self, log_text: str) -> list[DiagnosisMatch]:
        matches: list[DiagnosisMatch] = []
        for template, pattern in self.rules:
            if pattern.search(log_text):
                matches.append(template)
        if matches:
            return sorted(matches, key=lambda item: item.confidence, reverse=True)
        return [
            DiagnosisMatch(
                diagnosis_type=DiagnosisType.UNKNOWN,
                root_cause="未命中已知规则，需要人工查看或接入 LLM 二次分析。",
                suggestion="检查完整日志上下文，必要时补充新规则或启用 LLM 诊断扩展。",
                confidence=0.35,
                pattern="",
            )
        ]

