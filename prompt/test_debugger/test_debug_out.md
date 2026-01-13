## 测试报告格式（必须严格遵守）
=== Test Execution Summary ===
Total Tests: <number>
Passed: <number>
Failed: <number>
Skipped: <number>

=== Failed Test Analysis ===
- Test Case: <test_name>
  Location: <file_path>::<function_or_class>
  Failure Type: <Implementation Bug | Test Code Issue | Environment / Config Issue | Unclear>
  Failure Description:
    <简要描述失败现象>
  Root Cause Analysis:
    <对失败原因的工程化分析>
  Is Test Code Problematic: <Yes | No>
  Suggested Action:
    <修复建议：修改实现 / 修正测试 / 补充前置条件 / 进一步排查>

(如有多个失败用例，按上述结构逐条列出)

=== Overall Assessment ===
- Test Suite Quality:
  <对 tests/ 目录下测试整体质量的评价>
- Confidence in Test Results:
  <High | Medium | Low>
- Recommendations:
  <对后续测试或调试工作的总体建议>
