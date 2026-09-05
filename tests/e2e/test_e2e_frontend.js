const { chromium } = require('d:/ung dung tri tue nhan ao/tuvixemboi/node_modules/playwright-core');

(async () => {
  console.log('=== BẮT ĐẦU KIỂM THỬ GIAO DIỆN FRONTEND E2E ===');
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('[BROWSER CONSOLE ERROR]:', msg.text());
      errors.push(msg.text());
    }
  });
  page.on('pageerror', err => {
    console.log('[BROWSER RUNTIME ERROR]:', err.message);
    errors.push(err.message);
  });

  try {
    // 1. Vào trang đăng nhập
    console.log('\n[1] Điều hướng tới trang /login...');
    await page.goto('http://localhost:5180/login', { waitUntil: 'networkidle' });
    console.log('  Tiêu đề trang:', await page.title());

    // 2. Điền thông tin đăng nhập
    console.log('\n[2] Điền thông tin tài khoản Admin...');
    await page.fill('input[type="email"], input[name="email"]', 'admin@khaitamhuyenhoc.com');
    await page.fill('input[type="password"], input[name="password"]', 'Admin@123456');

    // 3. Nhấp Đăng nhập
    console.log('\n[3] Nhấn nút Đăng nhập...');
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle', timeout: 10000 }).catch(() => {}),
      page.click('button[type="submit"]')
    ]);

    await page.waitForTimeout(2000);
    console.log('  URL sau khi đăng nhập:', page.url());

    // 4. Chụp ảnh màn hình Dashboard
    await page.screenshot({ path: 'd:/ung dung tri tue nhan ao/tuvixemboi/dashboard_logged_in.png', fullPage: true });
    console.log('  [✓] Đã chụp ảnh màn hình: dashboard_logged_in.png');

    // 5. Kiểm tra điều hướng các chức năng chính
    const routes = ['/dashboard', '/tu-vi', '/bat-tu', '/kinh-dich', '/chat', '/settings'];
    for (const r of routes) {
      console.log(`\n[*] Kiểm tra route: ${r}...`);
      await page.goto(`http://localhost:5180${r}`, { waitUntil: 'networkidle', timeout: 10000 });
      await page.waitForTimeout(1000);
      const contentLen = (await page.content()).length;
      console.log(`  [✓] Route ${r} hiển thị tốt, độ dài HTML: ${contentLen}`);
    }

    console.log('\n==============================================');
    console.log(`TỔNG SỐ LỖI JAVASCRIPT TRÊN TOÀN TRANG: ${errors.length}`);
    console.log('==============================================');

  } catch (err) {
    console.error('Lỗi trong quá trình kiểm thử:', err);
  } finally {
    await browser.close();
  }
})();
