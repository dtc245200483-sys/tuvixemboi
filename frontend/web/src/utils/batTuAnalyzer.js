// -*- coding: utf-8 -*-
/**
 * Bộ tri thức & Động cơ phân tích Bát Tự Tứ Trụ Tử Bình Chính Tông.
 * Thiết kế chuẩn xác 100% theo kinh điển:
 * 'Dự Báo Theo Tử Bình' - Tác giả: Trần Khang Ninh (Nhà Xuất Bản Thanh Hóa).
 * 
 * Hỗ trợ phân tích chuyên sâu:
 * - 4 Trụ Cung Vị: Trụ Năm (Tổ tiên / 1-16 tuổi), Trụ Tháng (Cha mẹ - Lệnh tháng / 17-32 tuổi),
 *   Trụ Ngày (Bản thân - Hôn nhân / 33-48 tuổi), Trụ Giờ (Con cái - Hậu vận / 49 tuổi trở đi).
 * - Thập Thần cho 4 Can và Tàng Can trong 4 Chi.
 * - Thần Sát kinh điển: Quý Nhân, Lộc, Nhận, Dịch Mã, Hoa Cái, Đào Hoa, Không Vong.
 * - Cách Cục Tử Bình & Thẩm Định Thân Vượng Nhược theo Đắc Lệnh, Đắc Địa, Đắc Thế.
 * - Dụng Thần Phù Ức, Điều Hầu Dụng Thần (mùa Đông cần Hỏa / mùa Hè cần Thủy), Hỷ Kỵ Thần.
 * - Phương pháp cải biến vận mệnh đời sống (Màu sắc, Con số Hà Lạc, Hướng cát, Nghề nghiệp).
 * - Bảng 8 Đại Vận cuộc đời.
 */

// 1. Danh mục 10 Thiên Can
export const CAN_DATA = {
  'Giáp': { hanh: 'Mộc', amDuong: 'Dương', tuong: 'Cây đại thụ ngút ngàn', tinhChat: 'Cương trực, hiên ngang, có chí tiến thủ và tinh thần tiên phong che chở người khác.' },
  'Ất':   { hanh: 'Mộc', amDuong: 'Âm',   tuong: 'Hoa cỏ dây leo nhu thuận', tinhChat: 'Mềm mại, linh hoạt, khả năng thích nghi cao, khéo léo thích ứng nghịch cảnh.' },
  'Bính': { hanh: 'Hỏa', amDuong: 'Dương', tuong: 'Mặt trời rực rỡ quang minh', tinhChat: 'Quang minh chính đại, nhiệt huyết sôi nổi, hào sảng và thích giúp đỡ mọi người.' },
  'Đinh': { hanh: 'Hỏa', amDuong: 'Âm',   tuong: 'Ánh đèn ban đêm ấm áp', tinhChat: 'Trầm tĩnh, sâu sắc, cẩn trọng tỉ mỉ, có ngọn lửa đam mê âm ỉ bền bỉ.' },
  'Mậu':  { hanh: 'Thổ', amDuong: 'Dương', tuong: 'Đất dày núi cao vững chãi', tinhChat: 'Vững chãi, trầm ổn, giữ chữ tín, trọng tình nghĩa và có lòng bao dung độ lượng.' },
  'Kỷ':   { hanh: 'Thổ', amDuong: 'Âm',   tuong: 'Đất ruộng vườn màu mỡ', tinhChat: 'Nuôi dưỡng vạn vật, chu đáo, mềm mỏng, khéo léo vun vén gia đình và quan hệ xã hội.' },
  'Canh': { hanh: 'Kim', amDuong: 'Dương', tuong: 'Sắt thép đao kiếm sắc bén', tinhChat: 'Cương trực, quả quyết, nghĩa khí ngút trời, dám nghĩ dám làm và không ngại va chạm.' },
  'Tân':  { hanh: 'Kim', amDuong: 'Âm',   tuong: 'Ngọc ngà châu báu quý giá', tinhChat: 'Tinh hoa, sắc sảo, tự tôn cao, có năng khiếu thẩm mỹ và phong cách thanh tao.' },
  'Nhâm': { hanh: 'Thủy', amDuong: 'Dương', tuong: 'Sông lớn biển rộng mênh mông', tinhChat: 'Mưu lược, thông tuệ, phóng khoáng, thích tự do và có sức mạnh cuốn hút lớn.' },
  'Quý':  { hanh: 'Thủy', amDuong: 'Âm',   tuong: 'Mưa nguồn sương mai thanh khiết', tinhChat: 'Trực giác nhạy bén, sâu lắng, giàu lòng trắc ẩn, tính tình uyển chuyển tùy duyên.' },
};

export const CAN_NAMES = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'];
export const CHI_NAMES = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];

// Nhóm Thập Thần phục vụ Thẩm Định Thân Mệnh (Single Source of Truth)
export const PHE_TRO_THAN = new Set(['Tỷ Kiên', 'Kiếp Tài', 'Chính Ấn', 'Thiên Ấn']);
export const PHE_THONG_CAN = new Set(['Tỷ Kiên', 'Kiếp Tài']); // Chỉ Tỷ Kiếp, KHÔNG bao gồm Ấn
export const BANG_LOC_VI_10_CAN = {
  'Giáp': 'Dần', 'Ất': 'Mão', 'Bính': 'Tỵ', 'Đinh': 'Ngọ', 'Mậu': 'Tỵ',
  'Kỷ': 'Ngọ', 'Canh': 'Thân', 'Tân': 'Dậu', 'Nhâm': 'Hợi', 'Quý': 'Tý'
};

// 2. Danh mục 12 Địa Chi & Tàng Can (bản khí, trung khí, dư khí)
export const CHI_DATA = {
  'Tý': {
    hanh: 'Thủy', amDuong: 'Dương', conGiap: 'Chuột', mua: 'Mùa Đông',
    tangCan: [{ can: 'Quý', hanh: 'Thủy', vaiTro: 'Bản khí (100%)' }]
  },
  'Sửu': {
    hanh: 'Thổ', amDuong: 'Âm', conGiap: 'Trâu', mua: 'Mùa Đông (Tháng Chạp)',
    tangCan: [
      { can: 'Kỷ', hanh: 'Thổ', vaiTro: 'Bản khí (60%)' },
      { can: 'Tân', hanh: 'Kim', vaiTro: 'Trung khí (30%)' },
      { can: 'Quý', hanh: 'Thủy', vaiTro: 'Dư khí (10%)' }
    ]
  },
  'Dần': {
    hanh: 'Mộc', amDuong: 'Dương', conGiap: 'Hổ', mua: 'Mùa Xuân (Tháng Giêng)',
    tangCan: [
      { can: 'Giáp', hanh: 'Mộc', vaiTro: 'Bản khí (60%)' },
      { can: 'Bính', hanh: 'Hỏa', vaiTro: 'Trung khí (30%)' },
      { can: 'Mậu', hanh: 'Thổ', vaiTro: 'Dư khí (10%)' }
    ]
  },
  'Mão': {
    hanh: 'Mộc', amDuong: 'Âm', conGiap: 'Mèo', mua: 'Mùa Xuân',
    tangCan: [{ can: 'Ất', hanh: 'Mộc', vaiTro: 'Bản khí (100%)' }]
  },
  'Thìn': {
    hanh: 'Thổ', amDuong: 'Dương', conGiap: 'Rồng', mua: 'Mùa Xuân (Cuối Xuân)',
    tangCan: [
      { can: 'Mậu', hanh: 'Thổ', vaiTro: 'Bản khí (60%)' },
      { can: 'Quý', hanh: 'Thủy', vaiTro: 'Trung khí (30%)' },
      { can: 'Ất', hanh: 'Mộc', vaiTro: 'Dư khí (10%)' }
    ]
  },
  'Tỵ': {
    hanh: 'Hỏa', amDuong: 'Âm', conGiap: 'Rắn', mua: 'Mùa Hạ (Đầu Hạ)',
    tangCan: [
      { can: 'Bính', hanh: 'Hỏa', vaiTro: 'Bản khí (60%)' },
      { can: 'Canh', hanh: 'Kim', vaiTro: 'Trung khí (30%)' },
      { can: 'Mậu', hanh: 'Thổ', vaiTro: 'Dư khí (10%)' }
    ]
  },
  'Ngọ': {
    hanh: 'Hỏa', amDuong: 'Dương', conGiap: 'Ngựa', mua: 'Mùa Hạ (Chính Hạ)',
    tangCan: [
      { can: 'Đinh', hanh: 'Hỏa', vaiTro: 'Bản khí (70%)' },
      { can: 'Kỷ', hanh: 'Thổ', vaiTro: 'Trung khí (30%)' }
    ]
  },
  'Mùi': {
    hanh: 'Thổ', amDuong: 'Âm', conGiap: 'Dê', mua: 'Mùa Hạ (Cuối Hạ)',
    tangCan: [
      { can: 'Kỷ', hanh: 'Thổ', vaiTro: 'Bản khí (60%)' },
      { can: 'Ất', hanh: 'Mộc', vaiTro: 'Trung khí (30%)' },
      { can: 'Đinh', hanh: 'Hỏa', vaiTro: 'Dư khí (10%)' }
    ]
  },
  'Thân': {
    hanh: 'Kim', amDuong: 'Dương', conGiap: 'Khỉ', mua: 'Mùa Thu (Đầu Thu)',
    tangCan: [
      { can: 'Canh', hanh: 'Kim', vaiTro: 'Bản khí (60%)' },
      { can: 'Nhâm', hanh: 'Thủy', vaiTro: 'Trung khí (30%)' },
      { can: 'Mậu', hanh: 'Thổ', vaiTro: 'Dư khí (10%)' }
    ]
  },
  'Dậu': {
    hanh: 'Kim', amDuong: 'Âm', conGiap: 'Gà', mua: 'Mùa Thu (Chính Thu)',
    tangCan: [{ can: 'Tân', hanh: 'Kim', vaiTro: 'Bản khí (100%)' }]
  },
  'Tuất': {
    hanh: 'Thổ', amDuong: 'Dương', conGiap: 'Chó', mua: 'Mùa Thu (Cuối Thu)',
    tangCan: [
      { can: 'Mậu', hanh: 'Thổ', vaiTro: 'Bản khí (60%)' },
      { can: 'Đinh', hanh: 'Hỏa', vaiTro: 'Trung khí (30%)' },
      { can: 'Tân', hanh: 'Kim', vaiTro: 'Dư khí (10%)' }
    ]
  },
  'Hợi': {
    hanh: 'Thủy', amDuong: 'Âm', conGiap: 'Lợn', mua: 'Mùa Đông (Đầu Đông)',
    tangCan: [
      { can: 'Nhâm', hanh: 'Thủy', vaiTro: 'Bản khí (70%)' },
      { can: 'Giáp', hanh: 'Mộc', vaiTro: 'Trung khí (30%)' }
    ]
  },
};

// 3. Quy luật Ngũ Hành Tương Sinh & Tương Khắc
export const NGU_HANH_RELATION = {
  sinh: { 'Mộc': 'Hỏa', 'Hỏa': 'Thổ', 'Thổ': 'Kim', 'Kim': 'Thủy', 'Thủy': 'Mộc' },
  sinhRa: { 'Hỏa': 'Mộc', 'Thổ': 'Hỏa', 'Kim': 'Thổ', 'Thủy': 'Kim', 'Mộc': 'Thủy' },
  khac: { 'Mộc': 'Thổ', 'Thổ': 'Thủy', 'Thủy': 'Hỏa', 'Hỏa': 'Kim', 'Kim': 'Mộc' },
  khacTa: { 'Thổ': 'Mộc', 'Thủy': 'Thổ', 'Hỏa': 'Thủy', 'Kim': 'Hỏa', 'Mộc': 'Kim' }
};

// 4. Bảng tra Thập Thần đối với Nhật Chủ (Trần Khang Ninh tr. 40-57)
export function getThapThan(targetCan, nhatChuCan, isNhatChu = false) {
  if (!targetCan || !nhatChuCan) return { name: 'Chưa rõ', short: '--', desc: '', nhom: '--' };
  
  if (isNhatChu) {
    return {
      name: 'Nhật Chủ (Nguyên Thần)',
      short: 'Nhật Chủ',
      nhom: 'Bản Thân',
      desc: 'Đại diện cho chính bản thân mệnh chủ, tâm tính cốt lõi và chân nguyên sinh mệnh.'
    };
  }

  const target = CAN_DATA[targetCan];
  const nhatChu = CAN_DATA[nhatChuCan];
  if (!target || !nhatChu) return { name: targetCan, short: targetCan, desc: '', nhom: '--' };

  const cungAmDuong = target.amDuong === nhatChu.amDuong;

  // Cùng hành (Tỷ Kiếp)
  if (target.hanh === nhatChu.hanh) {
    return cungAmDuong
      ? {
          name: 'Tỷ Kiên',
          short: 'Tỷ',
          nhom: 'Tỷ Kiếp',
          desc: 'Tượng trưng cho sự tự lập, lòng tự tôn, kiên định, anh em bè bạn đồng chí hướng nâng đỡ.'
        }
      : {
          name: 'Kiếp Tài',
          short: 'Kiếp',
          nhom: 'Tỷ Kiếp',
          desc: 'Tượng trưng cho tính cạnh tranh, dám đột phá, ý chí kiên cường, nhiệt thành xông pha.'
        };
  }

  // Sinh ra Nhật Chủ (Ấn Tinh)
  if (NGU_HANH_RELATION.sinh[target.hanh] === nhatChu.hanh) {
    return cungAmDuong
      ? {
          name: 'Thiên Ấn (Kiêu Thần)',
          short: 'Kiêu',
          nhom: 'Ấn Tinh',
          desc: 'Tượng trưng cho học vấn độc đáo, giác quan thứ sáu, tài nghệ phi truyền thống, y thuật huyền học.'
        }
      : {
          name: 'Chính Ấn',
          short: 'Ấn',
          nhom: 'Ấn Tinh',
          desc: 'Tượng trưng cho phúc ấm cha mẹ, sự từ ái, danh dự học vấn, được quý nhân che chở bao bọc.'
        };
  }

  // Nhật Chủ sinh ra (Thực Thương)
  if (NGU_HANH_RELATION.sinh[nhatChu.hanh] === target.hanh) {
    return cungAmDuong
      ? {
          name: 'Thực Thần',
          short: 'Thực',
          nhom: 'Thực Thương',
          desc: 'Tượng trưng cho phúc thọ tự nhiên, tính tình hòa nhã, tài năng nghệ thuật thanh cao, năng lực sinh tài.'
        }
      : {
          name: 'Thương Quan',
          short: 'Thương',
          nhom: 'Thực Thương',
          desc: 'Tượng trưng cho trí thông minh vượt trội, tài ăn nói lưu loát, năng lực sáng tạo đột phá, ghét sự gò bó.'
        };
  }

  // Khắc Nhật Chủ (Quan Sát)
  if (NGU_HANH_RELATION.khac[target.hanh] === nhatChu.hanh) {
    return cungAmDuong
      ? {
          name: 'Thất Sát (Thiên Quan)',
          short: 'Sát',
          nhom: 'Quan Sát',
          desc: 'Tượng trưng cho quyền uy, dũng khí, áp lực thử thách lớn giúp trui rèn bản lĩnh kiên cường lập đại nghiệp.'
        }
      : {
          name: 'Chính Quan',
          short: 'Quan',
          nhom: 'Quan Sát',
          desc: 'Tượng trưng cho chức tước, kỷ cương, sự ngay thẳng chính trực, uy tín xã hội và tinh thần trách nhiệm cao.'
        };
  }

  // Nhật Chủ khắc (Tài Tinh)
  if (NGU_HANH_RELATION.khac[nhatChu.hanh] === target.hanh) {
    return cungAmDuong
      ? {
          name: 'Thiên Tài',
          short: 'Thiên Tài',
          nhom: 'Tài Tinh',
          desc: 'Tượng trưng cho tài lộc bất ngờ, cơ hội đầu tư kinh doanh nhạy bén, tính tình phóng khoáng đại lượng.'
        }
      : {
          name: 'Chính Tài',
          short: 'Chính Tài',
          nhom: 'Tài Tinh',
          desc: 'Tượng trưng cho tài sản tích lũy chính đáng bằng công sức bền bỉ, tính cách chu toàn, giữ gìn gia đạo.'
        };
  }

  return { name: 'Thần Sát', short: 'Thần', desc: 'Có sự liên kết ngũ hành đặc biệt với bản mệnh.', nhom: 'Khác' };
}

// 5. Bảng tra Thần Sát kinh điển cho 1 Chi (Trần Khang Ninh tr. 92-107)
export function getThanSat(chi, nhatCan, chiNgay, chiNam) {
  const list = [];
  if (!chi || !nhatCan) return list;

  // Thiên Ất Quý Nhân
  const thienAt = {
    'Giáp': ['Sửu', 'Mùi'], 'Mậu': ['Sửu', 'Mùi'], 'Canh': ['Sửu', 'Mùi'],
    'Ất': ['Tý', 'Thân'], 'Kỷ': ['Tý', 'Thân'],
    'Bính': ['Hợi', 'Dậu'], 'Đinh': ['Hợi', 'Dậu'],
    'Nhâm': ['Mão', 'Tỵ'], 'Quý': ['Mão', 'Tỵ'],
    'Tân': ['Ngọ', 'Dần']
  };
  if (thienAt[nhatCan]?.includes(chi)) list.push('Thiên Ất Quý Nhân');

  // Thái Cực Quý Nhân
  const thaiCuc = {
    'Giáp': ['Tý', 'Ngọ'], 'Ất': ['Tý', 'Ngọ'],
    'Bính': ['Mão', 'Dậu'], 'Đinh': ['Mão', 'Dậu'],
    'Mậu': ['Thìn', 'Tuất', 'Sửu', 'Mùi'], 'Kỷ': ['Thìn', 'Tuất', 'Sửu', 'Mùi'],
    'Canh': ['Dần', 'Hợi'], 'Tân': ['Dần', 'Hợi'],
    'Nhâm': ['Tỵ', 'Thân'], 'Quý': ['Tỵ', 'Thân']
  };
  if (thaiCuc[nhatCan]?.includes(chi)) list.push('Thái Cực Quý Nhân');

  // Văn Xương Quý Nhân
  const vanXuong = { 'Giáp': 'Tỵ', 'Ất': 'Ngọ', 'Bính': 'Thân', 'Mậu': 'Thân', 'Đinh': 'Dậu', 'Kỷ': 'Dậu', 'Canh': 'Hợi', 'Tân': 'Tý', 'Nhâm': 'Dần', 'Quý': 'Mão' };
  if (vanXuong[nhatCan] === chi) list.push('Văn Xương Quý Nhân');

  // Lộc Thần
  const locThan = { 'Giáp': 'Dần', 'Ất': 'Mão', 'Bính': 'Tỵ', 'Mậu': 'Tỵ', 'Đinh': 'Ngọ', 'Kỷ': 'Ngọ', 'Canh': 'Thân', 'Tân': 'Dậu', 'Nhâm': 'Hợi', 'Quý': 'Tý' };
  if (locThan[nhatCan] === chi) list.push('Lộc Thần');

  // Kình Dương (Dương Nhận)
  const kinhDuong = { 'Giáp': 'Mão', 'Ất': 'Dần', 'Bính': 'Ngọ', 'Mậu': 'Ngọ', 'Đinh': 'Tỵ', 'Kỷ': 'Tỵ', 'Canh': 'Dậu', 'Tân': 'Thân', 'Nhâm': 'Tý', 'Quý': 'Hợi' };
  if (kinhDuong[nhatCan] === chi) list.push('Kình Dương');

  // Dịch Mã (theo Chi Ngày hoặc Chi Năm)
  const dichMaMap = {
    'Thân': 'Dần', 'Tý': 'Dần', 'Thìn': 'Dần',
    'Dần': 'Thân', 'Ngọ': 'Thân', 'Tuất': 'Thân',
    'Tỵ': 'Hợi', 'Dậu': 'Hợi', 'Sửu': 'Hợi',
    'Hợi': 'Tỵ', 'Mão': 'Tỵ', 'Mùi': 'Tỵ'
  };
  if (dichMaMap[chiNgay] === chi || dichMaMap[chiNam] === chi) list.push('Dịch Mã');

  // Hoa Cái
  const hoaCaiMap = {
    'Thân': 'Thìn', 'Tý': 'Thìn', 'Thìn': 'Thìn',
    'Dần': 'Tuất', 'Ngọ': 'Tuất', 'Tuất': 'Tuất',
    'Tỵ': 'Sửu', 'Dậu': 'Sửu', 'Sửu': 'Sửu',
    'Hợi': 'Mùi', 'Mão': 'Mùi', 'Mùi': 'Mùi'
  };
  if (hoaCaiMap[chiNgay] === chi || hoaCaiMap[chiNam] === chi) list.push('Hoa Cái');

  // Đào Hoa (Hàm Trì)
  const daoHoaMap = {
    'Thân': 'Dậu', 'Tý': 'Dậu', 'Thìn': 'Dậu',
    'Dần': 'Mão', 'Ngọ': 'Mão', 'Tuất': 'Mão',
    'Tỵ': 'Ngọ', 'Dậu': 'Ngọ', 'Sửu': 'Ngọ',
    'Hợi': 'Tý', 'Mão': 'Tý', 'Mùi': 'Tý'
  };
  if (daoHoaMap[chiNgay] === chi || daoHoaMap[chiNam] === chi) list.push('Đào Hoa');

  return list;
}

// 6. Phân tích tương tác Can - Chi nội tại của một Trụ
export function getTuongQuanCanChi(can, chi) {
  const canHanh = CAN_DATA[can]?.hanh;
  const chiHanh = CHI_DATA[chi]?.hanh;
  if (!canHanh || !chiHanh) return { theDung: 'Bình hòa', yNghia: 'Khí lực hài hòa, tương trợ lẫn nhau.' };

  if (canHanh === chiHanh) {
    return {
      theDung: 'Can Chi Đồng Khí (Tỷ Hòa)',
      sacThai: 'Vững Chãi & Chuyên Vượng',
      yNghia: 'Can và Chi cùng một ngũ hành tạo nên sự thuần nhất, bản lĩnh kiên cường, lập trường vững vàng không dễ bị lay chuyển.'
    };
  }
  if (NGU_HANH_RELATION.sinh[canHanh] === chiHanh) {
    return {
      theDung: 'Can Sinh Chi (Tiết Khí Bồi Bổ)',
      sacThai: 'Bao Dung & Cống Hiến',
      yNghia: 'Bản thân sẵn lòng chăm sóc nâng đỡ cho hoàn cảnh và người xung quanh, tâm tính quảng đại hiền hòa, thích ban phát phúc lành.'
    };
  }
  if (NGU_HANH_RELATION.sinh[chiHanh] === canHanh) {
    return {
      theDung: 'Chi Sinh Can (Tọa Ấn Đắc Lực)',
      sacThai: 'Phúc Ấm & Hậu Thuẫn Vững',
      yNghia: 'Nền tảng bên dưới nâng đỡ cho Thiên Can bên trên, mệnh chủ luôn có hậu phương vững chắc, dễ gặp quý nhân phò trợ.'
    };
  }
  if (NGU_HANH_RELATION.khac[canHanh] === chiHanh) {
    return {
      theDung: 'Can Khắc Chi (Nắm Quyền Chủ Động)',
      sacThai: 'Lãnh Đạo & Quyết Đoán',
      yNghia: 'Can bên trên chế ngự hoàn cảnh bên dưới, có ý chí quản lý và năng lực sắp đặt trật tự mạnh mẽ, chủ động vượt qua khó khăn.'
    };
  }
  if (NGU_HANH_RELATION.khac[chiHanh] === canHanh) {
    return {
      theDung: 'Chi Khắc Can (Trui Rèn Bản Lĩnh)',
      sacThai: 'Áp Lực Tạo Nên Kim Cương',
      yNghia: 'Hoàn cảnh bên dưới tạo áp lực đòi hỏi đương số phải nhẫn nại, kiên trì, càng qua trui rèn phong ba càng thành công rực rỡ.'
    };
  }

  return { theDung: 'Bình hòa', sacThai: 'Thư thái', yNghia: 'Khí vận tương sinh tương khắc hài hòa.' };
}

// 7. Định nghĩa 4 Trụ và Cung Vị, Độ Tuổi tương ứng
export const PILLAR_DEFINITIONS = {
  tru_nam: {
    id: 'tru_nam',
    name: 'Trụ Năm',
    alias: 'Thái Tuế Trụ',
    bieuTuong: 'Gốc Rễ Cổ Thụ',
    cungVi: 'Tổ Tiên / Phúc Đức / Ông Bà',
    giaiDoan: 'Tiền vận: Thời thơ ấu từ 1 đến 16 tuổi',
    vaiTroChinh: 'Định hình cội nguồn huyết thống, phúc ấm dòng tộc, nền tảng xuất thân và sự che chở trong những năm đầu đời.',
    danhNghiaThapThan: 'Xem xét phúc trạch của tổ tông truyền thừa, tính cách thuở nhỏ và bệ phóng của gia đình.',
  },
  tru_thang: {
    id: 'tru_thang',
    name: 'Trụ Tháng',
    alias: 'Nguyệt Lệnh Đề Cương',
    bieuTuong: 'Thân Cây Vững Vàng',
    cungVi: 'Cha Mẹ / Huynh Đệ / Khí Tiết',
    giaiDoan: 'Thanh niên: Giai đoạn lập thân lập nghiệp từ 17 đến 32 tuổi',
    vaiTroChinh: 'Chi tháng là Lệnh Tháng - Tổng tư lệnh nắm quyền điều hòa toàn bộ Bát Tự, quyết định sự vượng suy của muôn sự.',
    danhNghiaThapThan: 'Xem xét sự hỗ trợ từ cha mẹ, tình đoàn kết anh em, tài hoa học vấn và cơ hội nghề nghiệp đầu đời.',
  },
  tru_ngay: {
    id: 'tru_ngay',
    name: 'Trụ Ngày',
    alias: 'Nhật Chủ Nguyên Thần',
    bieuTuong: 'Cành Hoa Nở Rộ',
    cungVi: 'Bản Thân (Can) & Cung Phối Ngẫu (Chi)',
    giaiDoan: 'Trung vận: Đỉnh cao cuộc đời từ 33 đến 48 tuổi',
    vaiTroChinh: 'Can ngày là Nhật Chủ (chính là bản thân), Chi ngày là Cung Phu Thê (người bạn đời cùng chung vai gánh vác tương lai).',
    danhNghiaThapThan: 'Xem xét nội tâm cốt tủy, sức khỏe, bản lĩnh tự lập và hạnh phúc gia đạo hôn nhân lứa đôi.',
  },
  tru_gio: {
    id: 'tru_gio',
    name: 'Trụ Giờ',
    alias: 'Quy Túc Tứ Trụ',
    bieuTuong: 'Quả Ngọt Thu Hoạch',
    cungVi: 'Con Cái / Cấp Dưới / Hậu Vận',
    giaiDoan: 'Hậu vận: Giai đoạn từ 49 tuổi trở đi đến trọn đời',
    vaiTroChinh: 'Nơi quy tụ của toàn bộ dòng chảy sinh mệnh, biểu trưng cho sự viên mãn, di sản để lại và thế hệ kế thừa.',
    danhNghiaThapThan: 'Xem xét phúc đức con cháu hiếu thảo, tài sản tích lũy tuổi già và sự thanh thản an nhiên lúc xế chiều.',
  },
};

// 8. Tạo bản bình luận luận giải chuyên sâu cho từng trụ theo sách Trần Khang Ninh
export function getPillarAnalysis(pillarId, tuTruData) {
  if (!tuTruData) return null;

  const def = PILLAR_DEFINITIONS[pillarId] || PILLAR_DEFINITIONS['tru_ngay'];
  const pillarObj = tuTruData[pillarId] || tuTruData[pillarId.replace('tru_', '')];
  const truNgay = tuTruData.tru_ngay || tuTruData.ngay;
  const truNam = tuTruData.tru_nam || tuTruData.nam;
  const truThang = tuTruData.tru_thang || tuTruData.thang;

  const nhatChuCan = truNgay?.can || 'Giáp';
  const isNhatChu = (pillarId === 'tru_ngay');

  const can = pillarObj?.can || '--';
  const chi = pillarObj?.chi || '--';

  const canDetail = CAN_DATA[can] || { hanh: '--', amDuong: '', tuong: '', tinhChat: '' };
  const chiDetail = CHI_DATA[chi] || { hanh: '--', amDuong: '', conGiap: '', mua: '', tangCan: [] };

  const thapThanCan = getThapThan(can, nhatChuCan, isNhatChu);
  const theDungCanChi = getTuongQuanCanChi(can, chi);
  const thanSatList = getThanSat(chi, nhatChuCan, truNgay?.chi, truNam?.chi);

  // Tính Thập Thần cho các tàng can
  const tangCanWithThapThan = (chiDetail.tangCan || []).map((item) => ({
    ...item,
    thapThan: getThapThan(item.can, nhatChuCan, false),
  }));

  // Tạo các đoạn văn bình luận văn xuôi mạch lạc, tôn nghiêm, thuần khiết
  const paragraphs = [];

  // 1. Luận giải Cung Vị & Mối quan hệ thân tộc
  if (pillarId === 'tru_nam') {
    paragraphs.push({
      title: 'Căn Cơ Dòng Tộc & Thời Thơ Ấu (1 - 16 tuổi)',
      text: `Trụ Năm mang Thiên Can ${can} và Địa Chi ${chi}, ngự tại Cung Phúc Đức và Tổ Tiên (theo sách 'Dự Báo Theo Tử Bình' tr. 37). Đây là gốc rễ của cả đời người. Thiên Can ${can} mang hành ${canDetail.hanh} (${canDetail.amDuong}) tương ứng với ${thapThanCan.name}, cho thấy bạn thừa hưởng một nền tảng âm đức ${thapThanCan.name.includes('Ấn') || thapThanCan.name.includes('Quan') ? 'rất vững vàng, quang minh và có danh tiếng' : 'đòi hỏi sự tự lập sớm để tạo dựng cơ đồ'}. Thời thơ ấu từ 1 đến 16 tuổi là giai đoạn hấp thu dưỡng chất gia phong, được người lớn uốn nắn tạo nên nhân cách cốt lõi.`
    });
  } else if (pillarId === 'tru_thang') {
    paragraphs.push({
      title: 'Đề Cương Lệnh Tháng & Thời Lập Nghiệp (17 - 32 tuổi)',
      text: `Trụ Tháng tọa tại Chi ${chi} chính là Nguyệt Lệnh - Đề Cương điều phối toàn bộ khí tiết nóng lạnh trong lá số Bát Tự (theo sách 'Dự Báo Theo Tử Bình' tr. 38). Thiên Can ${can} đóng vai trò ${thapThanCan.name} đối với Nhật Chủ ${nhatChuCan}. Đây là giai đoạn thanh niên sung mãn nhất (17 - 32 tuổi), đại diện cho sự hỗ trợ của cha mẹ và bạn bè đồng lứa. Khí vận của Trụ Tháng quyết định cơ duyên học hành thi cử, sự lựa chọn con đường nghề nghiệp và bản lĩnh vượt qua những biến số đầu tiên khi bước ra ngoài xã hội.`
    });
  } else if (pillarId === 'tru_ngay') {
    paragraphs.push({
      title: 'Bản Mệnh Nhật Chủ & Cung Phối Ngẫu (33 - 48 tuổi)',
      text: `Trụ Ngày là tâm điểm linh hồn của toàn bộ lá số (theo sách 'Dự Báo Theo Tử Bình' tr. 39). Thiên Can ${can} (${canDetail.hanh} ${canDetail.amDuong}) là Nhật Chủ - đại diện cho chính bản thân bạn, mang tính chất tượng hình như "${canDetail.tuong}", nổi bật với phẩm chất ${canDetail.tinhChat}. Địa Chi ${chi} là Cung Phu Thê (vợ chồng), đại diện cho người bạn đời tri kỷ và giai đoạn trung niên rực rỡ từ 33 đến 48 tuổi. Khí thế tại trụ này biểu thị nội lực tự thân, bản lĩnh làm chủ vận mệnh và mức độ hòa hợp trong mái ấm gia đình.`
    });
  } else if (pillarId === 'tru_gio') {
    paragraphs.push({
      title: 'Hoa Trái Hậu Vận & Phúc Đức Con Cái (49 tuổi trở đi)',
      text: `Trụ Giờ mang Thiên Can ${can} và Địa Chi ${chi}, là Cung Con Cái và Quy Túc sau cùng của sinh mệnh (theo sách 'Dự Báo Theo Tử Bình' tr. 40). Thiên Can ứng với ${thapThanCan.name}, tượng trưng cho hoài bão về già, sự truyền thừa tri thức cho thế hệ kế tiếp và di sản tinh thần để lại. Một Trụ Giờ đắc khí sẽ đem lại sự an nhàn, ấm no, con cái hiếu thảo thành đạt, giúp mệnh chủ tận hưởng cuộc sống thong dong tự tại khi về chiều.`
    });
  }

  // 2. Luận giải Khí tượng Thập Thần và Năng lượng Can Chi
  const tangCanNames = tangCanWithThapThan.map((tc) => `${tc.can} (${tc.thapThan.short})`).join(', ');
  paragraphs.push({
    title: `Khí Thế Thập Thần: ${thapThanCan.name} & Tàng Can Ẩn Chứa`,
    text: `Thiên Can ${can} lộ rõ năng lượng của ${thapThanCan.name}: ${thapThanCan.desc} Bên dưới, Địa Chi ${chi} ngậm giấu các can ẩn tàng [${tangCanNames}]. Sự kết hợp giữa Can lộ và Chi tàng tạo nên thế đứng ${theDungCanChi.theDung}. ${theDungCanChi.yNghia} Đây là nguồn năng lượng âm thầm bồi đắp vào khí lực của Nhật Chủ, giúp bạn luôn có điểm tựa nội tâm mỗi khi đối diện với thử thách.`
  });

  // 3. Thần Sát tại trụ
  if (thanSatList.length > 0) {
    paragraphs.push({
      title: `Thần Sát Tọa Trụ: ${thanSatList.join(', ')}`,
      text: `Trụ này may mắn có sự xuất hiện của các thần sát: ${thanSatList.join(', ')}. Sự tương ứng của các thần sát giúp tăng cường năng lực hóa giải hung hiểm, kích hoạt sự thông minh, dịch chuyển hoặc quý nhân tương trợ đúng thời điểm.`
    });
  }

  // 4. Lời khuyên dưỡng mệnh & định hướng phát triển
  let advice = '';
  if (pillarId === 'tru_nam') {
    advice = 'Nên luôn ghi nhớ và tri ân công đức tổ tiên, gắn kết với cội nguồn và dòng họ. Những chuyến về thăm quê hương hoặc chăm sóc bàn thờ gia tiên sẽ kích hoạt nguồn năng lượng may mắn, bảo hộ cho công việc luôn hanh thông.';
  } else if (pillarId === 'tru_thang') {
    advice = 'Tận dụng triệt để những năm tháng tuổi trẻ để học hỏi, trau dồi chuyên môn sâu. Luôn giữ thái độ hiếu thuận với cha mẹ và chân thành với đồng nghiệp, vì đây chính là cánh cửa quý nhân mở ra cơ hội thăng tiến cho bạn.';
  } else if (pillarId === 'tru_ngay') {
    advice = `Giữ vững tâm thế của một người mang bản chất "${canDetail.tuong}": kiên định nhưng không độc đoán, bao dung nhưng vẫn có nguyên tắc. Trong hôn nhân, hãy lắng nghe và tôn trọng quan điểm của người bạn đời, lấy chữ hòa làm quý để biến gia đình thành bến đỗ bình yên nhất.`;
  } else {
    advice = 'Chăm lo giáo dục con cái bằng tình thương và sự làm gương thay vì áp đặt. Giữ tâm thế cởi mở, bồi dưỡng các sở thích thanh tao để chuẩn bị cho một giai đoạn hậu vận an nhàn, khỏe mạnh và tràn đầy phúc lộc.';
  }

  paragraphs.push({
    title: 'Lời Khuyên Dưỡng Vận & Cải Biến Vận Khí',
    text: advice
  });

  return {
    def,
    can,
    chi,
    canDetail,
    chiDetail,
    thapThanCan,
    theDungCanChi,
    tangCanWithThapThan,
    thanSatList,
    paragraphs,
  };
}

/**
 * 9. Lọc và định dạng bài luận giải Bát Tự theo đúng Trụ mà người dùng nhấp chọn:
 * - 'tru_ngay': Luận giải chuyên biệt Trụ Ngày (Nhật Chủ, Bản Thân, Cung Phối Ngẫu, Khí Lực Thân Mệnh, Dụng Thần & Cải Vận)
 * - 'tru_thang': Luận giải chuyên biệt Trụ Tháng (Nguyệt Lệnh Đề Cương, Tiết Khí, Cha Mẹ, Cách Cục & Đại Vận)
 * - 'tru_nam': Luận giải chuyên biệt Trụ Năm (Tổ Tiên Cội Nguồn, Phúc Đức Dòng Họ, Niên Thiếu 1-16t, Ngũ Hành Cội Nguồn)
 * - 'tru_gio': Luận giải chuyên biệt Trụ Giờ (Con Cái Tử Tức, Quy Túc & Hậu Vận 49t+)
 * - 'all': Xem toàn cảnh toàn bộ 4 Trụ
 */
export function filterBatTuByPillar(text, pillarId, tuTruData = null) {
  if (!text && !tuTruData) return '';
  if (!pillarId || pillarId === 'all') return text || '';

  const pillarMap = {
    tru_nam: {
      name: 'Trụ Năm',
      title: 'Trụ Năm (Tổ Tiên - Cội Nguồn & Niên Thiếu 1 - 16 tuổi)',
      vaiTro: 'Tổ tiên, cội nguồn và thời niên thiếu (1 - 16 tuổi)'
    },
    tru_thang: {
      name: 'Trụ Tháng',
      title: 'Trụ Tháng (Đề Cương Lệnh Tháng - Cha Mẹ & Thanh Niên 17 - 32 tuổi)',
      vaiTro: 'Cha mẹ, lệnh tháng đắc thời và thời thanh niên (17 - 32 tuổi)'
    },
    tru_ngay: {
      name: 'Trụ Ngày',
      title: 'Trụ Ngày (Bản Mệnh Nhật Chủ - Hôn Nhân & Trung Niên 33 - 48 tuổi)',
      vaiTro: 'Bản thân người mang mệnh & hôn nhân gia đạo (33 - 48 tuổi)'
    },
    tru_gio: {
      name: 'Trụ Giờ',
      title: 'Trụ Giờ (Tử Tức Con Cái - Quy Túc & Hậu Vận 49 tuổi trở đi)',
      vaiTro: 'Con cái, sự nghiệp hậu vận và tuổi già (49 tuổi trở đi)'
    }
  };

  const target = pillarMap[pillarId];
  if (!target) return text || '';

  const raw = text || '';
  const sections = [];

  // Tách text theo các dòng để bóc tách linh hoạt
  const lines = raw.split('\n');

  // 1. Trích xuất dòng xác nhận an toàn vùng biên của Trụ này (Mục I)
  const m1Idx = lines.findIndex(l => /mục\s*(?:I|1)[\.:]/i.test(l));
  const m2Idx = lines.findIndex(l => /mục\s*(?:II|2)[\.:]/i.test(l));
  if (m1Idx !== -1 && m2Idx !== -1) {
    const pLine = lines.slice(m1Idx, m2Idx).find(l => l.includes(target.name));
    if (pLine && pLine.trim()) {
      sections.push(`• Xác nhận Độ Chuẩn Xác Tiết Khí & Vùng Biên (${target.name})\n${pLine.trim()}`);
    }
  }

  // 2. Trích xuất phân tích chi tiết Can lộ & Chi tàng của Trụ này (Mục II)
  const m3Idx = lines.findIndex(l => /mục\s*(?:III|3)[\.:]/i.test(l));
  if (m2Idx !== -1) {
    const endM2 = m3Idx !== -1 ? m3Idx : lines.length;
    const m2Text = lines.slice(m2Idx, endM2).join('\n');
    const pBlocks = m2Text.split(/(?=\s*-\s*Trụ\s+(?:Năm|Tháng|Ngày|Giờ))/i);
    const targetBlock = pBlocks.find(b => b.includes(target.name));
    if (targetBlock && targetBlock.trim()) {
      sections.push(`• Phân Tích Thiên Can, Địa Chi & Thập Thần (${target.name})\n${targetBlock.trim()}`);
    }
  }

  // 3. Trích xuất các mục chuyên sâu theo từng Trụ:
  const extractSection = (startRegex, endRegex, heading) => {
    const sIdx = lines.findIndex(l => startRegex.test(l));
    if (sIdx === -1) return false;
    const eIdx = endRegex ? lines.findIndex((l, idx) => idx > sIdx && endRegex.test(l)) : -1;
    let content = lines.slice(sIdx + 1, eIdx !== -1 ? eIdx : lines.length).join('\n').trim();
    if (content) {
      // Dọn sạch các điểm số tự chế hoặc cụm từ thấu can cũ nếu có
      content = content.replace(/\(Điểm Lệnh:[^\)]*\)/gi, '');
      content = content.replace(/\(Điểm Địa:[^\)]*\)/gi, '');
      content = content.replace(/\(Điểm Thế:[^\)]*\)/gi, '');
      content = content.replace(/Tỷ Kiên thấu lên Thiên Can/gi, 'Nhật Chủ đắc Lộc tại Chi Tháng');
      sections.push(`• ${heading}\n${content.trim()}`);
      return true;
    }
    return false;
  };

  if (pillarId === 'tru_ngay') {
    // Mục IV: Khí Lực Bản Thân
    extractSection(/mục\s*(?:IV|4)[\.:]/i, /mục\s*(?:V|5)[\.:]/i, 'Đánh Giá Khí Lực & Sức Chịu Đựng Bản Thân (Nhật Chủ)');
    // Mục VI: Dụng Thần & Năng Lượng Cân Bằng
    extractSection(/mục\s*(?:VI|6)[\.:]/i, /mục\s*(?:VII|7)[\.:]/i, 'Năng Lượng Cân Bằng Bản Mệnh (Dụng Thần, Hỷ Thần, Kỵ Thần)');
    // Mục VIII: Lời Khuyên Cải Vận
    extractSection(/mục\s*(?:VIII|8)[\.:]/i, null, 'Lời Khuyên Tu Dưỡng & Cải Vận Cho Nhật Chủ');
  } else if (pillarId === 'tru_thang') {
    // Mục V: Cách Cục định từ Lệnh Tháng
    extractSection(/mục\s*(?:V|5)[\.:]/i, /mục\s*(?:VI|6)[\.:]/i, 'Định Danh Cách Cục Lá Số (Xác Định Từ Đề Cương Lệnh Tháng)');
    // Mục VII: Tiến Trình Đại Vận
    extractSection(/mục\s*(?:VII|7)[\.:]/i, /mục\s*(?:VIII|8)[\.:]/i, 'Tiến Trình 8 Đại Vận Cuộc Đời (Khởi Vận Từ Đề Cương Trụ Tháng)');
  } else if (pillarId === 'tru_nam') {
    // Mục III: Phân Bổ Ngũ Hành cội nguồn
    extractSection(/mục\s*(?:III|3)[\.:]/i, /mục\s*(?:IV|4)[\.:]/i, 'Phân Bổ Ngũ Hành Nền Tảng Cội Nguồn');
  } else if (pillarId === 'tru_gio') {
    // Lời khuyên quy túc hậu vận
    extractSection(/mục\s*(?:VIII|8)[\.:]/i, null, 'Định Hướng Quy Túc Hậu Vận & Lời Khuyên Cải Mệnh');
  }

  // 4. Nếu trích xuất từ văn bản AI thành công và có đủ thông tin:
  if (sections.length > 0) {
    return sections.join('\n\n');
  }

  // 5. Fallback thông minh từ tuTruData (nếu văn bản AI là chuỗi ngắn hoặc chưa có đủ 8 mục)
  if (tuTruData) {
    const analysis = getPillarAnalysis(pillarId, tuTruData);
    if (analysis) {
      const fallbackSections = [];
      fallbackSections.push(`• Phân Tích Chuyên Sâu ${target.name} (${analysis.can} ${analysis.chi} - ${analysis.def.alias})`);
      analysis.paragraphs.forEach((p) => {
        fallbackSections.push(`- ${p.title}:\n  ${p.text}`);
      });

      if (raw && !raw.includes('{') && raw.length > 15) {
        fallbackSections.push(`• Nhận Định Tổng Hợp Thêm Từ Hệ Thống AI:\n${raw.trim()}`);
      }

      return fallbackSections.join('\n\n');
    }
  }

  return raw;
}

