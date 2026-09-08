import React, { useMemo } from 'react';

// Bảng ánh xạ 12 Địa Chi sang số thứ tự 0..11
const BRANCH_NAMES = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];

/**
 * Tọa độ 12 Địa Chi nằm sát các mép viền của Khung Mệnh Chủ (Thiên Tâm 2x2).
 * Tỷ lệ % (x, y) từ 0 đến 100 của chính ô Mệnh Chủ.
 * Các cặp đối cung (Tý-Ngọ, Sửu-Mùi...) đối xứng hoàn hảo qua tâm (50%, 50%).
 */
const CENTER_PALACE_COORDINATES = {
  'Tỵ':   { x: 0,   y: 0 },    // Góc trên - trái (chạm thẳng góc Cung Tỵ)
  'Ngọ':  { x: 25,  y: 0 },    // Mép trên (chạm thẳng vào giữa Cung Ngọ)
  'Mùi':  { x: 75,  y: 0 },    // Mép trên (chạm thẳng vào giữa Cung Mùi)
  'Thân': { x: 100, y: 0 },    // Góc trên - phải (chạm thẳng góc Cung Thân)
  'Dậu':  { x: 100, y: 25 },   // Mép phải (chạm thẳng vào giữa Cung Dậu)
  'Tuất': { x: 100, y: 75 },   // Mép phải (chạm thẳng vào giữa Cung Tuất)
  'Hợi':  { x: 100, y: 100 },  // Góc dưới - phải (chạm thẳng góc Cung Hợi)
  'Tý':   { x: 75,  y: 100 },  // Mép dưới (chạm thẳng vào giữa Cung Tý)
  'Sửu':  { x: 25,  y: 100 },  // Mép dưới (chạm thẳng vào giữa Cung Sửu)
  'Dần':  { x: 0,   y: 100 },  // Góc dưới - trái (chạm thẳng góc Cung Dần)
  'Mão':  { x: 0,   y: 75 },   // Mép trái (chạm thẳng vào giữa Cung Mão)
  'Thìn': { x: 0,   y: 25 },   // Mép trái (chạm thẳng vào giữa Cung Thìn)
};

// 4 Bộ Tam Hợp
const TAM_HOP_GROUPS = [
  ['Thân', 'Tý', 'Thìn'], // Thủy cục
  ['Dần', 'Ngọ', 'Tuất'], // Hỏa cục
  ['Tỵ', 'Dậu', 'Sửu'],   // Kim cục
  ['Hợi', 'Mão', 'Mùi'],  // Mộc cục
];

// 6 Cặp Đối Cung (Xung Chiếu xuyên tâm)
const DOI_CUNG_MAP = {
  'Tý': 'Ngọ', 'Ngọ': 'Tý',
  'Sửu': 'Mùi', 'Mùi': 'Sửu',
  'Dần': 'Thân', 'Thân': 'Dần',
  'Mão': 'Dậu', 'Dậu': 'Mão',
  'Thìn': 'Tuất', 'Tuất': 'Thìn',
  'Tỵ': 'Hợi', 'Hợi': 'Tỵ',
};

/**
 * Component SVG Overlay vẽ Tam Phương Tứ Chính THU GỌN TRONG KHUNG MỆNH CHỦ (Ô THIÊN TÂM)
 * - Đường nét mảnh mai, thanh thoát (1px nhờ non-scaling-stroke).
 * - Nét đứt nhỏ nhắn, tinh tế (stroke-dasharray="3, 2").
 * - KHÔNG có màu nền tím (fill="none").
 * - KHÔNG có nút tròn ở các đỉnh.
 */
const TamPhuongTuChinhOverlay = ({
  selectedBranch,
  selectedBranchIndex,
  showTamHop = true,
  showXungChieu = true,
  tamHopColor = '#7E22CE',    // Tím huyền cơ thanh nhã
  xungChieuColor = '#DC2626', // Đỏ son
}) => {
  // Chuẩn hóa tên địa chi mục tiêu
  const targetBranch = useMemo(() => {
    if (selectedBranch && CENTER_PALACE_COORDINATES[selectedBranch]) {
      return selectedBranch;
    }
    if (typeof selectedBranchIndex === 'number' && selectedBranchIndex >= 0 && selectedBranchIndex < 12) {
      return BRANCH_NAMES[selectedBranchIndex];
    }
    return null;
  }, [selectedBranch, selectedBranchIndex]);

  // Bộ 3 đỉnh Tam Hợp
  const tamHopVertices = useMemo(() => {
    if (!targetBranch) return null;
    const group = TAM_HOP_GROUPS.find((g) => g.includes(targetBranch));
    if (!group) return null;
    return group.map((b) => CENTER_PALACE_COORDINATES[b]);
  }, [targetBranch]);

  // 2 Điểm Xung Chiếu
  const xungChieuPoints = useMemo(() => {
    if (!targetBranch) return null;
    const opp = DOI_CUNG_MAP[targetBranch];
    if (!opp) return null;
    return {
      source: CENTER_PALACE_COORDINATES[targetBranch],
      target: CENTER_PALACE_COORDINATES[opp],
    };
  }, [targetBranch]);

  if (!targetBranch) return null;

  const polygonPointsStr = tamHopVertices
    ? tamHopVertices.map((p) => `${p.x},${p.y}`).join(' ')
    : '';

  return (
    <svg
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      className="absolute inset-0 w-full h-full pointer-events-none z-20 overflow-visible transition-all duration-300"
      style={{ pointerEvents: 'none' }}
    >
      {/* 1. TAM GIÁC TAM HỢP (Nét đứt nhỏ mịn, KHÔNG tô màu tím, KHÔNG có nút tròn) */}
      {showTamHop && tamHopVertices && (
        <polygon
          vectorEffect="non-scaling-stroke"
          points={polygonPointsStr}
          fill="none"
          stroke={tamHopColor}
          strokeWidth="1.1"
          strokeOpacity="0.65"
          strokeDasharray="3.5, 2.5"
          strokeLinejoin="round"
          style={{ transition: 'points 0.3s ease' }}
        />
      )}

      {/* 2. ĐƯỜNG XUNG CHIẾU (Nét mảnh, đứt nhỏ gọn xuyên tâm, KHÔNG có nút tròn) */}
      {showXungChieu && xungChieuPoints && (
        <line
          vectorEffect="non-scaling-stroke"
          x1={xungChieuPoints.source.x}
          y1={xungChieuPoints.source.y}
          x2={xungChieuPoints.target.x}
          y2={xungChieuPoints.target.y}
          stroke={xungChieuColor}
          strokeWidth="1.1"
          strokeOpacity="0.7"
          strokeDasharray="4, 2.5"
          style={{ transition: 'all 0.3s ease' }}
        />
      )}
    </svg>
  );
};

export default TamPhuongTuChinhOverlay;
