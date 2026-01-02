## 用例 ID: TC_LOGIN_01 (密码错误锁定)
- **前置条件**: 模拟 UserDao 返回一个存在的用户，且 failedAttempts=2。
- **输入**: username="alice", password="wrong_password"
- **步骤**: 调用 login 方法。
- **预期结果 (Oracle)**:
  1. 抛出 InvalidCredentialsException。
  2. 验证 UserDao.updateUser 被调用一次（用于锁定账户）。
## 用例 ID: TC_LOGIN_01 (密码错误锁定)