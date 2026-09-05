const { chromium } = require('d:/ung dung tri tue nhan ao/tuvixemboi/node_modules/playwright-core');

(async () => {
  console.log('=== KIỂM TRA LUỒNG NGƯỜI DÙNG: TẠO HỒ SƠ -> XEM LÁ SỐ TỬ VI & BÁT TỰ ===');

  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1366, height: 850 }
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

  // 1. Đăng nhập
  console.log('\n[1] Thực hiện Đăng nhập...');
  await page.goto('http://localhost:5180/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="email"], input[name="email"]', 'admin@khaitamhuyenhoc.com');
  await page.fill('input[type="password"], input[name="password"]', 'Admin@123456');
  await page.click('button[type="submit"]');

  await page.waitForTimeout(1500);
  console.log('  Trang sau đăng nhập:', page.url());

  // 2. Đi tới trang nhập hồ sơ sinh
  console.log('\n[2] Chuyển tới /birth-profile...');
  await page.goto('http://localhost:5180/birth-profile', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  // Điền thông tin sinh
  console.log('  Nhập họ tên và ngày giờ sinh...');
  await page.fill('input[placeholder*="Nguyễn Văn A"]', 'Trần Mệnh Chủ');
  await page.fill('input[type="date"]', '1992-08-18');
  await page.selectOption('select:has-option("14 - Mùi")', { label: '14 - Mùi' }).catch(async () => {
    // Nếu select không tìm thấy option text cụ thể, tìm theo index hoặc value
    const selects = await page.$$('select');
    if (selects.length >= 2) {
      await selects[0].selectOption({ value: '14' });
      await selects[1].selectOption({ value: '30' });
    }
  });

  // Click Submit
  console.log('  Gửi form tạo hồ sơ sinh...');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(2000);

  // Kiểm tra xem thẻ xác nhận hồ sơ đã hiển thị chưa
  const btnTuVi = await page.$('#btn-view-tuvi');
  const btnBatTu = await page.$('#btn-view-battu');
  const btnDash = await page.$('#btn-goto-dashboard');

  console.log('  Nút [Xem Lá Số Tử Vi]:', btnTuVi ? 'CÓ [✓]' : 'CHƯA THẤY [X]');
  console.log('  Nút [Xem Bát Tự Tứ Trụ]:', btnBatTu ? 'CÓ [✓]' : 'CHƯA THẤY [X]');
  console.log('  Nút [Vào Bàn Làm Việc Dashboard]:', btnDash ? 'CÓ [✓]' : 'CHƯA THẤY [X]');

  await page.screenshot({ path: 'd:/ung dung tri tue nhan ao/tuvixemboi/birth_profile_success.png' });
  console.log('  [✓] Đã chụp ảnh kết quả tạo hồ sơ: birth_profile_success.png');

  // 3. Click nút "Xem Lá Số Tử Vi"
  if (btnTuVi) {
    console.log('\n[3] Click "Xem Lá Số Tử Vi"...');
    await btnTuVi.click();
    await page.waitForTimeout(3000);
    console.log('  URL sau khi click:', page.url());

    // Chụp màn hình Lá Số Tử Vi
    await page.screenshot({ path: 'd:/ung dung tri tue nhan ao/tuvixemboi/tuvi_laso_screen.png' });
    console.log('  [✓] Đã chụp màn hình Lá Số Tử Vi: tuvi_laso_screen.png');
  }

  // 4. Kiểm tra Dashboard
  console.log('\n[4] Kiểm tra trang Dashboard (/dashboard)...');
  await page.goto('http://localhost:5180/dashboard', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  console.log('  Dashboard URL:', page.url());
  await page.screenshot({ path: 'd:/ung dung tri tue nhan ao/tuvixemboi/dashboard_screen.png' });
  console.log('  [✓] Đã chụp màn hình Dashboard: dashboard_screen.png');

  // 5. Kiểm tra Bát Tự Tứ Trụ
  console.log('\n[5] Kiểm tra trang Bát Tự (/bat-tu)...');
  await page.goto('http://localhost:5180/bat-tu', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  console.log('  Bát Tự URL:', page.url());
  await page.screenshot({ path: 'd:/ung dung tri tue nhan ao/tuvixemboi/battu_screen.png' });
  console.log('  [✓] Đã chụp màn hình Bát Tự: battu_screen.png');

  console.log('\nTổng số lỗi console:', consoleErrors.length);
  await browser.close();
  console.log('\n=== HOÀN TẤT KIỂM TRA LUỒNG NGƯỜI DÙNG ===');
})();
