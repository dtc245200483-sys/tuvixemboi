// ==============================================================================
// IZTRO TỬ VI ĐẨU SỐ — CALCULATOR ENGINE CHO TUVIXEMBOI
// ==============================================================================

const path = require('path');
const fs = require('fs');
const Module = require('module');

// Cấu hình đường dẫn tìm kiếm module tuyệt đối cho cả môi trường local và container
const p1 = path.join(__dirname, 'node_modules');
const p2 = path.join(__dirname, 'iztro_lib', 'node_modules');
[p1, p2].forEach(p => {
  if (Module.globalPaths && Module.globalPaths.indexOf(p) === -1) Module.globalPaths.unshift(p);
  if (module.paths && module.paths.indexOf(p) === -1) module.paths.unshift(p);
});

let iztro;
try {
  iztro = require('./iztro_lib');
} catch (err) {
  console.error(JSON.stringify({ error: 'Lỗi nạp ./iztro_lib: ' + err.message, stack: err.stack }));
  process.exit(1);
}

// LỤC THẬP HOA GIÁP NẠP ÂM (60 HOA GIÁP)
const NAP_AM = {
  'Giáp Tý': 'Hải Trung Kim', 'Ất Sửu': 'Hải Trung Kim',
  'Bính Dần': 'Lư Trung Hỏa', 'Đinh Mão': 'Lư Trung Hỏa',
  'Mậu Thìn': 'Đại Lâm Mộc', 'Kỷ Tỵ': 'Đại Lâm Mộc',
  'Canh Ngọ': 'Lộ Bàng Thổ', 'Tân Mùi': 'Lộ Bàng Thổ',
  'Nhâm Thân': 'Kiếm Phong Kim', 'Quý Dậu': 'Kiếm Phong Kim',
  'Giáp Tuất': 'Sơn Đầu Hỏa', 'Ất Hợi': 'Sơn Đầu Hỏa',
  'Bính Tý': 'Giản Hạ Thủy', 'Đinh Sửu': 'Giản Hạ Thủy',
  'Mậu Dần': 'Thành Đầu Thổ', 'Kỷ Mão': 'Thành Đầu Thổ',
  'Canh Thìn': 'Bạch Lạp Kim', 'Tân Tỵ': 'Bạch Lạp Kim',
  'Nhâm Ngọ': 'Dương Liễu Mộc', 'Quý Mùi': 'Dương Liễu Mộc',
  'Giáp Thân': 'Tuyền Trung Thủy', 'Ất Dậu': 'Tuyền Trung Thủy',
  'Bính Tuất': 'Ốc Thượng Thổ', 'Đinh Hợi': 'Ốc Thượng Thổ',
  'Mậu Tý': 'Tích Lịch Hỏa', 'Kỷ Sửu': 'Tích Lịch Hỏa',
  'Canh Dần': 'Tùng Bách Mộc', 'Tân Mão': 'Tùng Bách Mộc',
  'Nhâm Thìn': 'Trường Lưu Thủy', 'Quý Tỵ': 'Trường Lưu Thủy',
  'Giáp Ngọ': 'Sa Trung Kim', 'Ất Mùi': 'Sa Trung Kim',
  'Bính Thân': 'Sơn Hạ Hỏa', 'Đinh Dậu': 'Sơn Hạ Hỏa',
  'Mậu Tuất': 'Bình Địa Mộc', 'Kỷ Hợi': 'Bình Địa Mộc',
  'Canh Tý': 'Bích Thượng Thổ', 'Tân Sửu': 'Bích Thượng Thổ',
  'Nhâm Dần': 'Kim Bạc Kim', 'Quý Mão': 'Kim Bạc Kim',
  'Giáp Thìn': 'Phúc Đăng Hỏa', 'Ất Tỵ': 'Phúc Đăng Hỏa',
  'Bính Ngọ': 'Thiên Hà Thủy', 'Đinh Mùi': 'Thiên Hà Thủy',
  'Mậu Thân': 'Đại Trạch Thổ', 'Kỷ Dậu': 'Đại Trạch Thổ',
  'Canh Tuất': 'Thoa Xuyến Kim', 'Tân Hợi': 'Thoa Xuyến Kim',
  'Nhâm Tý': 'Tang Đố Mộc', 'Quý Sửu': 'Tang Đố Mộc',
  'Giáp Dần': 'Đại Khê Thủy', 'Ất Mão': 'Đại Khê Thủy',
  'Bính Thìn': 'Sa Trung Thổ', 'Đinh Tỵ': 'Sa Trung Thổ',
  'Mậu Ngọ': 'Thiên Thượng Hỏa', 'Kỷ Mùi': 'Thiên Thượng Hỏa',
  'Canh Thân': 'Thạch Lựu Mộc', 'Tân Dậu': 'Thạch Lựu Mộc',
  'Nhâm Tuất': 'Đại Hải Thủy', 'Quý Hợi': 'Đại Hải Thủy'
};

const DUONG_CAN = ['Giáp', 'Bính', 'Mậu', 'Canh', 'Nhâm'];
const DUONG_CHI = ['Tý', 'Dần', 'Thìn', 'Ngọ', 'Thân', 'Tuất'];
const BRANCHES = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];

// CÂN XƯƠNG TÍNH SỐ (CÂN LƯỢNG CHỈ)
const CAN_CHI_WEIGHT = {
  'Giáp Tý': 12, 'Bính Tý': 16, 'Mậu Tý': 15, 'Canh Tý': 7, 'Nhâm Tý': 5,
  'Ất Sửu': 9, 'Đinh Sửu': 8, 'Kỷ Sửu': 7, 'Tân Sửu': 7, 'Quý Sửu': 5,
  'Bính Dần': 6, 'Mậu Dần': 8, 'Canh Dần': 9, 'Nhâm Dần': 12, 'Giáp Dần': 12,
  'Ất Mão': 7, 'Đinh Mão': 7, 'Kỷ Mão': 19, 'Tân Mão': 12, 'Quý Mão': 12,
  'Giáp Thìn': 8, 'Bính Thìn': 8, 'Mậu Thìn': 12, 'Canh Thìn': 12, 'Nhâm Thìn': 10,
  'Ất Tỵ': 7, 'Đinh Tỵ': 16, 'Kỷ Tỵ': 5, 'Tân Tỵ': 12, 'Quý Tỵ': 7,
  'Giáp Ngọ': 15, 'Bính Ngọ': 13, 'Mậu Ngọ': 19, 'Canh Ngọ': 9, 'Nhâm Ngọ': 8,
  'Ất Mùi': 6, 'Đinh Mùi': 5, 'Kỷ Mùi': 6, 'Tân Mùi': 8, 'Quý Mùi': 7,
  'Giáp Thân': 15, 'Bính Thân': 5, 'Mậu Thân': 14, 'Canh Thân': 8, 'Nhâm Thân': 7,
  'Ất Dậu': 15, 'Đinh Dậu': 14, 'Kỷ Dậu': 5, 'Tân Dậu': 16, 'Quý Dậu': 8,
  'Giáp Tuất': 15, 'Bính Tuất': 6, 'Mậu Tuất': 14, 'Canh Tuất': 9, 'Nhâm Tuất': 10,
  'Ất Hợi': 9, 'Đinh Hợi': 26, 'Kỷ Hợi': 9, 'Tân Hợi': 17, 'Quý Hợi': 6
};
const MONTH_WEIGHT = { 1: 6, 2: 7, 3: 18, 4: 9, 5: 5, 6: 16, 7: 9, 8: 15, 9: 18, 10: 8, 11: 9, 12: 5 };
const DAY_WEIGHT = {
  1: 5, 2: 10, 3: 8, 4: 15, 5: 16, 6: 15, 7: 8, 8: 16, 9: 8, 10: 16,
  11: 9, 12: 17, 13: 8, 14: 17, 15: 10, 16: 8, 17: 9, 18: 18, 19: 5, 20: 15,
  21: 10, 22: 9, 23: 8, 24: 9, 25: 15, 26: 18, 27: 7, 28: 8, 29: 16, 30: 6
};
const HOUR_WEIGHT = {
  'Tý': 16, 'Sửu': 6, 'Dần': 7, 'Mão': 10, 'Thìn': 9, 'Tỵ': 16,
  'Ngọ': 10, 'Mùi': 8, 'Thân': 8, 'Dậu': 9, 'Tuất': 6, 'Hợi': 6
};

function toSlug(str) {
  return String(str || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'd')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function calculateAstrolabe(params) {
  const name = (params.name || params.ho_ten || '').trim();

  // 1. Ngày sinh
  const year = parseInt(params.yearOfDOB || params.year || '1990', 10);
  const month = parseInt(params.monthOfDOB || params.month || '1', 10);
  const day = parseInt(params.dayOfDOB || params.day || '1', 10);
  const dateStr = params.date || `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

  // 2. Giờ sinh
  const hour = parseInt(params.hourOfDOB !== undefined ? params.hourOfDOB : (params.hour !== undefined ? params.hour : '12'), 10);
  const min = parseInt(params.minOfDOB !== undefined ? params.minOfDOB : (params.min !== undefined ? params.min : '0'), 10);
  const timeIndex = params.timeIndex !== undefined
    ? parseInt(params.timeIndex, 10)
    : Math.floor(((hour + 1) % 24) / 2);

  // 3. Giới tính
  const gStr = String(params.gender !== undefined ? params.gender : (params.gioi_tinh || 'nam')).toLowerCase().trim();
  const gender = (gStr === 'true' || gStr === '1' || gStr === 'male' || gStr === 'nam') ? 'male' : 'female';

  // 4. Lịch Dương hay Âm
  const calStr = String(params.calendar !== undefined ? params.calendar : (params.option !== undefined ? params.option : 'solar')).toLowerCase().trim();
  const calendar = (calStr === 'false' || calStr === '0' || calStr === '2' || calStr === 'lunar' || calStr === 'am') ? 'lunar' : 'solar';

  // 5. Năm/Tháng xem hạn
  const currentYear = new Date().getFullYear();
  const viewYear = parseInt(params.viewYear || params.targetYear || params['nam-xem'] || currentYear, 10);
  const viewMonth = parseInt(params.viewMonth || params.targetMonth || params['thang-xem'] || '7', 10);
  const targetDateStr = params.targetDate || `${viewYear}-${String(viewMonth).padStart(2, '0')}-15`;
  const isLeapMonth = params.isLeapMonth === true || params.isLeapMonth === 'true';
  const lang = params.lang || 'vi-VN';

  // 6. Gọi Engine Iztro
  let astrolabe;
  if (calendar === 'lunar') {
    try {
      astrolabe = iztro.astro.byLunar(dateStr, timeIndex, gender, isLeapMonth, true, lang);
    } catch (err) {
      if (err.message && err.message.includes('only 29 days')) {
        const adjustedDate = `${year}-${String(month).padStart(2, '0')}-29`;
        astrolabe = iztro.astro.byLunar(adjustedDate, timeIndex, gender, isLeapMonth, true, lang);
      } else {
        throw err;
      }
    }
  } else {
    astrolabe = iztro.astro.bySolar(dateStr, timeIndex, gender, true, lang);
  }

  // 7. Ghi đè quy tắc Nam Phái Việt Nam
  if (typeof iztro.applyVietnamAstrologyRules === 'function') {
    astrolabe = iztro.applyVietnamAstrologyRules(astrolabe, viewYear);
  } else if (typeof iztro.vietnamAstrologyAdapter === 'function') {
    astrolabe = iztro.vietnamAstrologyAdapter(astrolabe, viewYear);
  }

  // 8. Tính toán Overlay Vận Hạn
  let overlayData = null;
  try {
    if (typeof iztro.getOverlayData === 'function') {
      overlayData = iztro.getOverlayData(astrolabe, targetDateStr);
    }
  } catch (err) {
    // silently catch overlay error
  }

  // 9. Tính toán các thuộc tính tuvi.vn
  const birthYearCanChi = (astrolabe.chineseDate || '').split('-')[0].trim();
  const [birthCan, birthChi] = birthYearCanChi.split(' ');
  const isDuongCan = DUONG_CAN.includes(birthCan);
  const isNam = gender === 'male';

  const menhPalace = astrolabe.palaces.find(p => p.name === 'Mệnh' || p.name === 'soul') || astrolabe.palaces[0];
  const thanPalace = astrolabe.palaces.find(p => p.isBodyPalace) || menhPalace;
  const isDuongCung = DUONG_CHI.includes(menhPalace.earthlyBranch);

  const isThuanLy = (isDuongCan && isDuongCung) || (!isDuongCan && !isDuongCung);
  const amDuongPrefix = (isDuongCan ? 'Dương ' : 'Âm ') + (isNam ? 'Nam' : 'Nữ');
  const amDuongBanMenh = `${amDuongPrefix} (${isThuanLy ? 'Âm Dương Thuận lý' : 'Âm Dương Nghịch lý'})`;

  const napAm = NAP_AM[birthYearCanChi] || 'Bản Mệnh';

  // Cân xương tính số
  const hourBranch = BRANCHES[timeIndex % 12];
  const wYear = CAN_CHI_WEIGHT[birthYearCanChi] || 10;
  const lMonth = astrolabe.rawDates?.lunarDate?.lunarMonth || month;
  const lDay = astrolabe.rawDates?.lunarDate?.lunarDay || day;
  const lYear = astrolabe.rawDates?.lunarDate?.lunarYear || year;
  const wMonth = MONTH_WEIGHT[lMonth] || 10;
  const wDay = DAY_WEIGHT[lDay] || 10;
  const wHour = HOUR_WEIGHT[hourBranch] || 10;
  const totalWeight = wYear + wMonth + wDay + wHour;
  const luong = Math.floor(totalWeight / 10);
  const chi = totalWeight % 10;
  const canLuong = chi === 0 ? `${luong} lượng` : `${luong} lượng ${chi} chỉ`;

  const menhMajorStars = (menhPalace.majorStars || []).map(s => s.name).join(', ');
  const menhChinhTinh = menhMajorStars || 'Vô chính diệu';

  const thanMajorStars = (thanPalace.majorStars || []).map(s => s.name).join(', ');
  const thanChinhTinh = thanMajorStars || 'Vô chính diệu';

  const age = Math.max(1, viewYear - lYear + 1);
  const viewYearStr = `${astrolabe.targetYearCanChi} (${viewYear}), ${age} tuổi`;
  const hourStr = `${hourBranch} (${String(hour).padStart(2, '0')}:${String(min).padStart(2, '0')})`;

  const lasoId = Math.floor(Math.random() * 900000) + 100000;
  const slug = toSlug(`la-so-${amDuongPrefix}-${isThuanLy ? 'am-duong-thuan-ly' : 'am-duong-nghich-ly'}-${day}-${month}-${year}-${hourBranch}-${lasoId}`);

  const lasoInfo = {
    id: lasoId,
    name: name,
    gender: isNam ? 'Nam Mệnh' : 'Nữ Mệnh',
    day: day,
    month: month,
    year: year,
    hour: timeIndex,
    am_duong_ban_menh: amDuongBanMenh,
    can_chi_tuoi: birthYearCanChi,
    can_luong: canLuong,
    cuc_cua_tuoi: astrolabe.fiveElementsClass,
    loai_hanh_cua_ban_menh: napAm,
    slug: slug,
    created: new Date().toISOString(),
    updated: new Date().toISOString()
  };

  const palacesData = astrolabe.palaces.map(p => ({
    index: p.index,
    name: p.name,
    isBodyPalace: p.isBodyPalace,
    isOriginalPalace: p.isOriginalPalace,
    heavenlyStem: p.heavenlyStem,
    earthlyBranch: p.earthlyBranch,
    majorStars: p.majorStars || [],
    minorStars: p.minorStars || [],
    adjectiveStars: p.adjectiveStars || [],
    goodStars: p.goodStars || [],
    badStars: p.badStars || [],
    changsheng12: p.changsheng12,
    boshi12: p.boshi12,
    jiangqian12: p.jiangqian12,
    suiqian12: p.suiqian12,
    decadal: p.decadal,
    ages: p.ages,
    hasTuan: p.hasTuan || false,
    hasTriet: p.hasTriet || false,
    yearlyStars: p.yearlyStars || [],
  }));

  // Cung cấp các trường tương thích với AI interpretation của tuvixemboi
  const saoChuDao = menhMajorStars ? menhMajorStars.split(', ')[0] : 'Tử Vi';

  return {
    code: "200",
    msg: "Successfully",
    success: true,
    data: {
      id: lasoId,
      name: name,
      gender: isNam ? 'Nam Mệnh' : 'Nữ Mệnh',
      gender_raw: gender,
      day: day,
      month: month,
      year: year,
      hour: hourStr,
      hour_index: timeIndex,
      calendar: calendar === 'solar' ? 'Dương lịch' : 'Âm lịch',
      view_year: viewYearStr,
      view_month: viewMonth,
      am_duong_ban_menh: amDuongBanMenh,
      can_chi_tuoi: birthYearCanChi,
      can_luong: canLuong,
      cuc_cua_tuoi: astrolabe.fiveElementsClass,
      loai_hanh_cua_ban_menh: napAm,
      menh_chinh_tinh: menhChinhTinh,
      than_chinh_tinh: thanChinhTinh,
      menh_chu: astrolabe.menhChu || astrolabe.masterStar || astrolabe.soul,
      than_chu: astrolabe.thanChu || astrolabe.body,
      slug: slug,
      solarDate: astrolabe.solarDate,
      lunarDate: astrolabe.lunarDate,
      chineseDate: astrolabe.chineseDate,
      laso: lasoInfo,
      palaces: palacesData,
      overlay: overlayData,
      // Tương thích AI interpretation
      cung_menh: `${menhPalace.name} tại ${menhPalace.earthlyBranch} (${menhChinhTinh})`,
      cung_than: `${thanPalace.name} tại ${thanPalace.earthlyBranch} (${thanChinhTinh})`,
      cuc: astrolabe.fiveElementsClass,
      chinh_tinh: menhChinhTinh,
      sao_chu_dao: saoChuDao,
      chi_tiet_cung: `Mệnh cư ${menhPalace.earthlyBranch}, Thân cư ${thanPalace.earthlyBranch}, Cục ${astrolabe.fiveElementsClass}`
    },
    solarDate: astrolabe.solarDate,
    lunarDate: astrolabe.lunarDate,
    chineseDate: astrolabe.chineseDate,
    time: astrolabe.time,
    timeRange: astrolabe.timeRange,
    gender: astrolabe.gender,
    sign: astrolabe.sign,
    zodiac: astrolabe.zodiac,
    soul: astrolabe.soul,
    masterStar: astrolabe.masterStar || astrolabe.soul,
    menhChu: astrolabe.menhChu || astrolabe.masterStar || astrolabe.soul,
    body: astrolabe.body,
    bodyStar: astrolabe.bodyStar || astrolabe.body,
    thanChu: astrolabe.thanChu || astrolabe.body,
    fiveElementsClass: astrolabe.fiveElementsClass,
    earthlyBranchOfBodyPalace: astrolabe.earthlyBranchOfBodyPalace,
    earthlyBranchOfSoulPalace: astrolabe.earthlyBranchOfSoulPalace,
    targetYear: astrolabe.targetYear,
    targetYearCanChi: astrolabe.targetYearCanChi,
    yearlyMutagen: astrolabe.yearlyMutagen || [],
    yearlyMutagens: astrolabe.yearlyMutagens || null,
    yearlyStars: astrolabe.yearlyStars || [],
    palaces: palacesData,
    overlay: overlayData
  };
}

// Chạy trực tiếp từ CLI / Subprocess
if (require.main === module) {
  let inputStr = process.argv[2];
  if (inputStr && inputStr.trim().startsWith('{')) {
    try {
      const params = JSON.parse(inputStr);
      const result = calculateAstrolabe(params);
      console.log(JSON.stringify(result));
    } catch (err) {
      console.error(JSON.stringify({ error: err.message }));
      process.exit(1);
    }
  } else {
    // Đọc từ stdin
    let body = '';
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', chunk => body += chunk);
    process.stdin.on('end', () => {
      try {
        const trimmed = (body || '').trim();
        const params = JSON.parse(trimmed || '{}');
        const result = calculateAstrolabe(params);
        console.log(JSON.stringify(result));
      } catch (err) {
        console.error(JSON.stringify({ error: err.message }));
        process.exit(1);
      }
    });
  }
}

module.exports = { calculateAstrolabe };
