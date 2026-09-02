# 贡献指南 / Contributing Guide

感谢你愿意为 PasteMD 做贡献。提交 PR 前请尽量让改动保持小而清晰，并说明它解决的问题。

Thank you for contributing to PasteMD. Please keep pull requests focused and describe the problem your change solves.

## 开发环境 / Development Setup

建议使用 Python 3.12 及以上版本。

Python 3.12 or later is recommended.

```bash
git clone https://github.com/RICHQAQ/PasteMD.git
cd PasteMD

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

从源码运行：

Run from source:

```bash
python main.py
```

## 测试 / Testing

项目的自动化测试目前还在完善中，暂时不强制要求每个 PR 都必须新增或运行测试。请根据改动风险做合理验证，并在 PR 中说明你实际验证过的内容。

Automated tests are still being improved, so tests are not currently mandatory for every PR. Please verify your change in a way that matches its risk and describe what you checked in the PR.

如果 PR 新增了测试，或改动涉及已有可运行的测试，建议运行 `tests/` 或对应的测试文件：

If your PR adds tests, or your change touches behavior with existing runnable tests, we recommend running `tests/` or the specific test file:

```bash
python -m pytest tests/
# or
python -m pytest tests/test_fs.py
```

如果当前环境没有安装 pytest，可以先安装：

If pytest is not installed in your environment, install it first:

```bash
python -m pip install pytest
```

仓库中的测试体系还在完善中，`tests/` 用于自动化测试；历史上的 `test/` 内容可能包含调试脚本、样例数据或临时输出，不一定适合作为完整自动化测试直接运行。当前阶段，手动验证说明也可以接受。

The test setup is still being improved. `tests/` is used for automated tests; historical `test/` content may include debugging scripts, sample data, or temporary output, and may not be intended to run as a complete automated test suite. Manual verification notes are acceptable at this stage.

## 分支和提交信息 / Branches and Commit Messages

分支名建议按改动类型命名，例如：

Branch names should describe the change type, for example:

```bash
git switch -c fix/windows-filenames
git switch -c docs/update-readme
git switch -c feat/new-workflow
```

提交信息建议使用：

Use this commit message format:

```text
type(scope): 描述
```

描述可以是中文或英文。

The description can be written in Chinese or English.

常见类型 / Common types:

- `fix`: 修复问题 / bug fix
- `feat`: 新增功能 / feature
- `docs`: 文档改动 / documentation
- `chore`: 构建、依赖、维护类改动 / maintenance
- `ci`: CI/CD 改动 / CI/CD
- `refactor`: 重构，不改变行为 / refactor without behavior changes

示例 / Examples:

```text
fix(windows): 修复保留文件名导致保存失败
docs: update contributing guide
ci(release): 完善自动打包流程
```

## PR 要求 / Pull Request Checklist

提交 PR 时请尽量包含：

Please include the following when opening a PR:

- 改动目的和背景 / purpose and context
- 主要改动点 / main changes
- 已验证的平台和命令 / verified platforms and commands
- 相关截图或日志，如果改动涉及 UI、打包、系统权限或平台行为 / screenshots or logs when the change affects UI, packaging, system permissions, or platform behavior

请避免在一个 PR 中混入无关重构、格式化或生成文件更新。跨平台改动尤其要说明 Windows、macOS 是否受影响。

Avoid mixing unrelated refactors, formatting-only changes, or generated file updates into one PR. For cross-platform changes, state whether Windows or macOS is affected.

## 打包相关 / Packaging

macOS 打包脚本：

macOS packaging scripts:

```bash
PYTHON_BIN=python ./build_macos.sh
PYTHON_BIN=python ./build_dist_dmg.sh
```

Windows 打包流程主要由 `.github/workflows/build-release.yml` 维护。修改打包相关逻辑时，请同步检查 CI 配置和本地脚本。

Windows packaging is mainly maintained in `.github/workflows/build-release.yml`. When changing packaging behavior, check both CI configuration and local scripts.

## 许可证 / License

提交贡献即表示你同意贡献内容按本项目许可证发布。

By contributing, you agree that your contributions are licensed under this project's license.
