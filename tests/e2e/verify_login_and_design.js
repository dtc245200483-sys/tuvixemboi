const { chromium } = require('d:/ung dung tri tue nhan ao/tuvixemboi/node_modules/playwright-core');
const http = require('http');

(async () => {
  console.log('=== BẮT ĐẦU BƯỚC 5: XÁC NHẬN TRỰC QUAN TRANG ĐĂNG NHẬP & HỆ THỐNG ===');

  // 1. Kiểm tra Backend Swagger Docs & Health
  console.log('\n[1] Kiểm tra Backend Swagger Docs & Health...');
  const checkHealth = () => new Promise((resolve, reject) => {
    http.get('http://localhost:8000/health', res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ statusCode: res.statusCode, body: data }));
    }).on('error', reject);
  });

  const checkDocs = () => new Promise((resolve, reject) => {
    http.get('http://localhost:8000/docs', res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ statusCode: res.statusCode, length: data.length }));
    }).on('error', reject);
  });

  const healthRes = await checkHealth();
  console.log(`  GET /health: Status=${healthRes.statusCode}, Body=${healthRes.body.trim()}`);

  const docsRes = await checkDocs();
  console.log(`  GET /docs (Swagger UI): Status=${docsRes.statusCode}, Length=${docsRes.length} bytes`);

  // 2. Khởi động Headless Edge
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 850 }
  });
  const page = await context.newPage();

  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('  [CONSOLE ERROR]:', msg.text());
      consoleErrors.push(msg.text());
    }
  });
  page.on('pageerror', err => {
    console.log('  [RUNTIME ERROR]:', err.message);
    consoleErrors.push(err.message);
  });

  // Đảm bảo không còn token cũ
  await page.goto('http://localhost:5180/login', { waitUntil: 'networkidle' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle' });

  // 3. Xác nhận trực quan trang đăng nhập
  console.log('\n[2] Xác nhận trực quan trang LoginPage...');
  console.log('  Tiêu đề trang:', await page.title());

  const emailInput = await page.$('input[type="email"], input[name="email"]');
  const passwordInput = await page.$('input[type="password"], input[name="password"]');
  const submitButton = await page.$('button[type="submit"]');
  const registerLink = await page.$('a[href*="register"]');

  console.log('  Ô nhập Email:', emailInput ? 'CÓ [✓]' : 'THIẾU [X]');
  console.log('  Ô nhập Mật khẩu:', passwordInput ? 'CÓ [✓]' : 'THIẾU [X]');
  console.log('  Nút Đăng nhập:', submitButton ? 'CÓ [✓]' : 'THIẾU [X]');
  console.log('  Link Đăng ký:', registerLink ? 'CÓ [✓]' : 'THIẾU [X]');

  // Lấy màu nền và màu nút để kiểm tra Design System
  const styles = await page.evaluate(() => {
    const body = document.body;
    const btn = document.querySelector('button[type="submit"]');
    const bgCol = window.getComputedStyle(body).backgroundColor;
    const btnCol = btn ? window.getComputedStyle(btn).backgroundColor : '';
    return { bodyBg: bgCol, btnBg: btnCol };
  });
  console.log(`  Design System - Màu nền Body: ${styles.bodyBg}, Màu nút Submit: ${styles.btnBg}`);

  // Chụp ảnh màn hình trang đăng nhập
  await page.screenshot({ path: 'd:/ung dung tri tue nhan ao/tuvixemboi/login_page_verified.png' });
  console.log('  [✓] Đã chụp ảnh màn hình LoginPage: login_page_verified.png');

  // 4. Thực hiện đăng nhập thử
  console.log('\n[3] Thực hiện đăng nhập thử với admin@khaitamhuyenhoc.com...');
  await page.fill('input[type="email"], input[name="email"]', 'admin@khaitamhuyenhoc.com');
  await page.fill('input[type="password"], input[name="password"]', 'Admin@123456');

  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle', timeout: 10000 }).catch(() => {}),
    page.click('button[type="submit"]')
  ]);

  await page.waitForTimeout(2000);
  const currentUrl = page.url();
  console.log('  URL sau khi đăng nhập:', currentUrl);

  const isSuccess = currentUrl.includes('/dashboard') || currentUrl.includes('/birth-profile');
  console.log('  Đăng nhập thành công và chuyển hướng:', isSuccess ? 'THÀNH CÔNG [✓]' : 'THẤT BẠI [X]');

  await page.screenshot({ path: 'd:/ung dung tri tue nhan ao/tuvixemboi/dashboard_verified.png' });
  console.log('  [✓] Đã chụp ảnh màn hình sau đăng nhập: dashboard_verified.png');

  console.log('\n[4] Kiểm tra Console (F12)...');
  console.log('  Tổng số lỗi Console JavaScript đỏ:', consoleErrors.length);

  await browser.close();

  console.log('\n=============================================================');
  console.log('                 KẾT QUẢ BƯỚC 5 HOÀN TẤT                     ');
  console.log('=============================================================');
})();
