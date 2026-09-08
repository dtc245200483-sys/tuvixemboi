import React, { useMemo } from 'react';

/**
 * Render chuỗi có chứa **in đậm** thành các thẻ strong đẹp mắt
 */
function renderFormattedText(text) {
  if (!text) return null;
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-bold text-[#1F1916] text-[101%]">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

/**
 * Làm sạch hoàn toàn nội dung phản hồi từ AI:
 * - Bóc tách triệt để các vỏ bọc JSON ({ "chu_de": ..., "noi_dung": ... })
 * - Unescape các ký tự escape: \n, \", \\
 * - BỎ 100% CHỮ HÁN / TIẾNG TRUNG ([\u4e00-\u9fa5])
 * - BỎ 100% TIẾNG ANH THUẬT NGỮ NỬA MÙA: (Direct Resource), (Rob Wealth), (Fire, Yang)...
 * - BỎ KÝ TỰ BẢNG VỠ THÔ (||------|--------|) và chuyển thành danh sách mạch lạc
 * - Chuyển đổi thành văn phong bình dân, dễ hiểu cho người mới bắt đầu.
 */
export function extractCleanCommentText(raw) {
  if (!raw) return '';
  let str = '';
  if (typeof raw === 'object' && raw !== null) {
    str = raw.noi_dung || raw.content || raw.cau_tra_loi || raw.text || '';
    if (!str && !Array.isArray(raw)) {
      str = JSON.stringify(raw);
    }
  } else {
    str = String(raw);
  }

  let s = str.trim();

  // 1. Parse JSON nếu có
  if (s.startsWith('{') || s.includes('"noi_dung":') || s.includes('"chu_de":')) {
    try {
      const parsed = JSON.parse(s);
      if (parsed && typeof parsed === 'object') {
        s = parsed.noi_dung || parsed.content || parsed.cau_tra_loi || s;
      }
    } catch {
      const match = s.match(/[*"]*noi_dung[*"]*\s*:\s*[*"]*([\s\S]*)/);
      if (match) {
        let extracted = match[1];
        extracted = extracted.replace(/",\s*"muc_do_tin_cay"[\s\S]*$/, '');
        extracted = extracted.replace(/"\s*}\s*$/, '');
        s = extracted;
      }
    }
  }

  // 2. Unescape các ký tự literal
  s = s
    .replace(/\\n/g, '\n')
    .replace(/\\"/g, '"')
    .replace(/\\\\/g, '\\');

  // 3. Loại bỏ vỏ bọc JSON còn sót nếu có
  s = s.replace(/^\s*\{\s*[*"]*chu_de[*"]*\s*:\s*[^,\n]*,?\s*[*"]*noi_dung[*"]*\s*:\s*[*"]*?/is, '');
  s = s.replace(/"?\s*(?:,\s*"muc_do_tin_cay"[^}]*)?\}\s*$/is, '');
  s = s.replace(/^\s*\{+/, '').replace(/\}+\s*$/, '');

  // 4. LOẠI BỎ TOÀN BỘ CHỮ HÁN / TIẾNG TRUNG
  s = s.replace(/[\u4e00-\u9fff]+/g, '');

  // 5. LOẠI BỎ TIẾNG ANH THUẬT NGỮ NỬA MÙA
  s = s.replace(/\s*\(\s*(?:Direct Resource|Rob Wealth|Hurting Officer|Seven Killings|Friend|Eating God|Proper Officer|Indirect Wealth|Direct Wealth|Indirect Resource|Fire|Water|Earth|Metal|Wood|Yang|Yin|Positive|Negative)[^)]*\)/gi, '');
  s = s.replace(/\s*[-–—]\s*(?:Direct Resource|Rob Wealth|Hurting Officer|Seven Killings|Friend|Eating God|Proper Officer|Indirect Wealth|Direct Wealth|Indirect Resource|Fire|Water|Earth|Metal|Wood)/gi, '');
  s = s.replace(/\(\s*(?:Fire|Water|Earth|Metal|Wood)\s*,\s*(?:Yang|Yin)\s*\)/gi, '');
  s = s.replace(/\(\s*(?:Fire|Water|Earth|Metal|Wood|Yang|Yin)\s*\)/gi, '');

  // 6. XỬ LÝ BẢNG MARKDOWN VỠ: chuyển thành danh sách sạch đẹp dễ đọc
  // Xóa bỏ hoàn toàn các dòng kẻ phân cách bảng như |------|--------| hoặc ||------|
  s = s.replace(/\|*[-:]{2,}\|+[-:\s|]*/g, '');

  // Xử lý từng dòng để format bảng thành gạch đầu dòng rõ ràng
  const lines = s.split('\n');
  const processedLines = [];

  for (let line of lines) {
    let l = line.trim();
    if (!l) {
      processedLines.push('');
      continue;
    }

    // Nếu dòng có chứa ký tự bảng |
    if (l.includes('|')) {
      const cells = l.split('|').map(c => c.trim()).filter(Boolean);
      // Bỏ qua dòng tiêu đề bảng kỹ thuật
      const firstCellLower = (cells[0] || '').toLowerCase();
      if (
        firstCellLower.includes('trụ') ||
        firstCellLower.includes('vận') ||
        firstCellLower.includes('stt') ||
        firstCellLower.includes('can lộ') ||
        firstCellLower.includes('thiên can')
      ) {
        continue;
      }
      if (cells.length >= 2) {
        processedLines.push(`• **${cells[0]}**: ${cells.slice(1).join(' — ')}`);
        continue;
      }
    }

    // Chuẩn hóa gạch đầu dòng
    if (/^\s*[\*\-]\s+/.test(l)) {
      l = l.replace(/^\s*[\*\-]\s+/, '• ');
    }

    processedLines.push(l);
  }

  s = processedLines.join('\n');

  // 7. Dọn dẹp ký tự thừa: dấu pipe còn sót, ngoặc đơn rỗng, khoảng trắng thừa
  s = s.replace(/\|+/g, ' ');
  s = s.replace(/\(\s*[-–—]\s*\)/g, '');
  s = s.replace(/\(\s*\)/g, '');
  s = s.replace(/[ \t]{2,}/g, ' ');
  s = s.replace(/\n\s*\n\s*\n+/g, '\n\n');

  return s.trim();
}

/**
 * Component hiển thị luận giải bình dân, dễ hiểu, thẩm mỹ cao:
 * - Tiêu đề từng mục nổi bật, rõ ràng
 * - Giữ lại in đậm để làm nổi bật từ khóa
 * - Gạch đầu dòng tinh tế, thoáng mắt
 * - 100% tiếng Việt, không chữ Hán, không ký tự thừa.
 */
export function CleanCommentView({ content, className = '' }) {
  const cleaned = useMemo(() => extractCleanCommentText(content), [content]);

  if (!cleaned) {
    return (
      <p className="text-sm font-body text-text-secondary italic">
        Chưa có nội dung bình luận cho mục này.
      </p>
    );
  }

  const lines = cleaned.split('\n').map(l => l.trim()).filter(Boolean);

  return (
    <div className={`space-y-2.5 font-body leading-relaxed text-[#2C2420] ${className}`}>
      {lines.map((line, idx) => {
        // Kiểm tra xem dòng có phải là tiêu đề mục không (### Mục 1, I. ..., II. ..., Mục 1: ...)
        const isHeading =
          /^#{1,3}\s+/.test(line) ||
          /^(?:Mục|Phần)\s+\d+/i.test(line) ||
          /^[I|V|X]+\.\s+/i.test(line) ||
          /^Bước\s+\d+/i.test(line);

        if (isHeading) {
          const headingText = line.replace(/^#{1,3}\s+/, '').replace(/^[I|V|X]+\.\s*/, '').replace(/^\d+\.\s*/, '');
          return (
            <div key={idx} className="pt-4 pb-1 border-b border-[#EAE2D2] mb-2 first:pt-1">
              <h4 className="font-heading font-bold text-base sm:text-lg text-[#8B1C13] flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-[#D4AF37] inline-block shrink-0 shadow-2xs" />
                <span>{renderFormattedText(line.replace(/^#{1,3}\s+/, ''))}</span>
              </h4>
            </div>
          );
        }

        // Kiểm tra dòng gạch đầu dòng (• )
        const isBullet = line.startsWith('• ');

        if (isBullet) {
          const textAfterBullet = line.replace(/^•\s*/, '');
          return (
            <div key={idx} className="flex items-start gap-2.5 pl-2 sm:pl-3 py-0.5">
              <span className="text-[#8B1C13] font-bold text-base shrink-0 select-none leading-tight mt-0.5">•</span>
              <div className="flex-1 text-sm sm:text-base leading-relaxed text-[#2C2420]">
                {renderFormattedText(textAfterBullet)}
              </div>
            </div>
          );
        }

        // Dòng đoạn văn thông thường
        return (
          <p key={idx} className="text-sm sm:text-base leading-relaxed text-[#2C2420] py-0.5">
            {renderFormattedText(line)}
          </p>
        );
      })}
    </div>
  );
}
