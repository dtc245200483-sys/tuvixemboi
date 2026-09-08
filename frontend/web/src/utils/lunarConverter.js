/**
 * Module chuyển đổi Dương lịch sang Âm lịch chuẩn xác theo thuật toán thiên văn Hồ Ngọc Đức (Múi giờ GMT+7).
 */

const THIEN_CAN = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'];
const DIA_CHI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
const EPOCH_2000 = 2451550.09765;
const SYNODIC_MONTH = 29.530588853;
const DR = Math.PI / 180.0;

export function jdn(d, m, y) {
  const a = Math.floor((14 - m) / 12);
  const y2 = y + 4800 - a;
  const m2 = m + 12 * a - 3;
  return d + Math.floor((153 * m2 + 2) / 5) + 365 * y2 + Math.floor(y2 / 4) - Math.floor(y2 / 100) + Math.floor(y2 / 400) - 32045;
}

export function getNewMoonDay(k, timeZone = 7.0) {
  const T = k / 1236.85;
  const T2 = T * T;
  const T3 = T2 * T;
  const Jd1 = 2451550.09765 + SYNODIC_MONTH * k + 0.0001337 * T2 - 0.000000150 * T3 + 0.00000000073 * T3 * T;
  const M = 2.5534 + 29.10535669 * k - 0.0000218 * T2 - 0.00000011 * T3;
  const Mprime = 201.5643 + 385.81693528 * k + 0.0107438 * T2 + 0.00001239 * T3 - 0.000000058 * T3 * T;
  const F = 160.7108 + 390.67050274 * k - 0.0016341 * T2 - 0.00000227 * T3 + 0.000000011 * T3 * T;
  const dJ = (0.1734 - 0.000393 * T) * Math.sin(M * DR)
    + 0.0021 * Math.sin(2 * DR * M)
    - 0.4068 * Math.sin(Mprime * DR)
    + 0.0161 * Math.sin(2 * DR * Mprime)
    - 0.0004 * Math.sin(3 * DR * Mprime)
    + 0.0104 * Math.sin(2 * DR * F)
    - 0.0051 * Math.sin((M + Mprime) * DR)
    - 0.0074 * Math.sin((M - Mprime) * DR)
    + 0.0004 * Math.sin((2 * F + M) * DR)
    - 0.0004 * Math.sin((2 * F - M) * DR)
    - 0.0006 * Math.sin((2 * F + Mprime) * DR)
    + 0.0010 * Math.sin((2 * F - Mprime) * DR)
    + 0.0005 * Math.sin((2 * Mprime + M) * DR);
  return Math.floor(Jd1 + dJ + 0.5 + timeZone / 24.0);
}

export function getSunLongitude(jdnVal, timeZone = 7.0) {
  const T = (jdnVal - 0.5 - timeZone / 24.0 - 2451545.0) / 36525.0;
  const T2 = T * T;
  const M = 357.52910 + 35999.05029 * T - 0.0001537 * T2;
  const C = (1.914602 - 0.004817 * T - 0.000014 * T2) * Math.sin(M * DR) + (0.019993 - 0.000101 * T) * Math.sin(2 * M * DR) + 0.000289 * Math.sin(3 * M * DR);
  const L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T2;
  const lambdaDeg = (L0 + C + 360000.0) % 360.0;
  return Math.floor(lambdaDeg / 30.0);
}

export function getLunarMonth11(yy, timeZone = 7.0) {
  const off = jdn(31, 12, yy) - EPOCH_2000;
  let k = Math.floor(off / SYNODIC_MONTH);
  let nm = getNewMoonDay(k, timeZone);
  const sunLong = getSunLongitude(nm, timeZone);
  if (sunLong >= 9) {
    nm = getNewMoonDay(k - 1, timeZone);
  }
  return nm;
}

export function getLeapMonthOffset(a11, timeZone = 7.0) {
  let k = Math.floor((a11 - EPOCH_2000) / SYNODIC_MONTH + 0.5);
  let arc = getSunLongitude(a11, timeZone);
  let i = 1;
  while (true) {
    k++;
    const d = getNewMoonDay(k, timeZone);
    const newArc = getSunLongitude(d, timeZone);
    if (newArc === arc) return i - 1;
    arc = newArc;
    i++;
    if (arc === 8 || i > 14) break;
  }
  return 0;
}

/**
 * Chuyển đổi ngày tháng năm Dương Lịch sang Âm Lịch
 */
export function solarToLunar(d, m, y, timeZone = 7.0) {
  const dayNumber = jdn(d, m, y);
  let k = Math.floor((dayNumber - EPOCH_2000) / SYNODIC_MONTH);
  let monthStart = getNewMoonDay(k + 1, timeZone);
  if (monthStart > dayNumber) {
    monthStart = getNewMoonDay(k, timeZone);
  } else {
    k += 1;
  }
  let a11 = getLunarMonth11(y, timeZone);
  let b11 = a11;
  let lunarYear;
  if (a11 >= monthStart) {
    lunarYear = y;
    a11 = getLunarMonth11(y - 1, timeZone);
  } else {
    lunarYear = y + 1;
    b11 = getLunarMonth11(y + 1, timeZone);
  }
  const lunarDay = dayNumber - monthStart + 1;
  const diff = Math.floor((monthStart - a11) / 29.0);
  let lunarLeap = false;
  let lunarMonth = diff + 11;
  if ((b11 - a11) > 365) {
    const leapMonthDiff = getLeapMonthOffset(a11, timeZone);
    if (diff >= leapMonthDiff) {
      lunarMonth = diff + 10;
      if (diff === leapMonthDiff) lunarLeap = true;
    }
  }
  if (lunarMonth > 12) lunarMonth -= 12;
  if (lunarMonth >= 11 && diff < 4) lunarYear -= 1;

  const canNamIdx = (lunarYear + 6) % 10;
  const chiNamIdx = (lunarYear + 8) % 12;
  const canNam = THIEN_CAN[canNamIdx];
  const chiNam = DIA_CHI[chiNamIdx];

  const canThang1 = (canNamIdx % 5 * 2 + 2) % 10;
  const canThangIdx = (canThang1 + lunarMonth - 1) % 10;
  const chiThangIdx = (2 + lunarMonth - 1) % 12;

  return {
    lunarDay,
    lunarMonth,
    lunarYear,
    isLeap: lunarLeap,
    yearCanChi: `${canNam} ${chiNam}`,
    monthCanChi: `${THIEN_CAN[canThangIdx]} ${DIA_CHI[chiThangIdx]}`
  };
}

/**
 * Lấy thông tin Âm Lịch cho một Tháng Dương Lịch (lấy ngày giữa tháng 15)
 */
export function getLunarInfoForSolarMonth(solarMonth, solarYear) {
  const m = parseInt(solarMonth, 10) || 1;
  const y = parseInt(solarYear, 10) || 2026;
  const info = solarToLunar(15, m, y);
  return {
    solarMonth: m,
    solarYear: y,
    lunarMonth: info.lunarMonth,
    lunarYear: info.lunarYear,
    isLeap: info.isLeap,
    yearCanChi: info.yearCanChi,
    monthCanChi: info.monthCanChi,
    textDisplay: `Tháng ${m} DL (~ Th.${info.lunarMonth} ÂL)`
  };
}
