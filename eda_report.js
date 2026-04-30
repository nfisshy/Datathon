const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, PageBreak, TabStopType, TabStopPosition,
  VerticalAlign
} = require('docx');
const fs = require('fs');

const BRAND = "2E75B6";
const BRAND_LIGHT = "D6E4F0";
const RED = "C0392B";
const RED_LIGHT = "FADBD8";
const ORANGE = "D35400";
const ORANGE_LIGHT = "FDEBD0";
const GREEN = "1A7A50";
const GREEN_LIGHT = "D5F5E3";
const GRAY = "5D6D7E";
const GRAY_LIGHT = "EAF0F1";
const DARK = "1A2530";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: BRAND, space: 6 } },
    children: [new TextRun({ text, bold: true, color: DARK, font: "Arial", size: 32 })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 120 },
    children: [new TextRun({ text, bold: true, color: BRAND, font: "Arial", size: 26 })]
  });
}

function h3(text, color = DARK) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text, bold: true, color, font: "Arial", size: 22 })]
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 60, after: 80 },
    children: [new TextRun({ text, font: "Arial", size: 22, color: opts.color || "000000", bold: opts.bold || false, italics: opts.italic || false })]
  });
}

function bullet(text, level = 0, ref = "bullets") {
  return new Paragraph({
    numbering: { reference: ref, level },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: "Arial", size: 22, color: "1A2530" })]
  });
}

function bulletBold(boldText, normalText) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 40, after: 40 },
    children: [
      new TextRun({ text: boldText, font: "Arial", size: 22, bold: true }),
      new TextRun({ text: normalText, font: "Arial", size: 22 })
    ]
  });
}

function subbullet(text) {
  return new Paragraph({
    numbering: { reference: "subbullets", level: 0 },
    spacing: { before: 30, after: 30 },
    children: [new TextRun({ text, font: "Arial", size: 20, color: GRAY })]
  });
}

function spacer(size = 120) {
  return new Paragraph({ spacing: { before: size, after: 0 }, children: [new TextRun("")] });
}

function calloutBox(title, text, fillColor = BRAND_LIGHT, borderColor = BRAND) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [
      new TableRow({
        children: [new TableCell({
          borders: { top: { style: BorderStyle.SINGLE, size: 8, color: borderColor }, bottom: border, left: { style: BorderStyle.SINGLE, size: 8, color: borderColor }, right: border },
          shading: { fill: fillColor, type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 160, right: 160 },
          width: { size: 9360, type: WidthType.DXA },
          children: [
            new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: title, font: "Arial", size: 22, bold: true, color: borderColor })] }),
            new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text, font: "Arial", size: 20, color: DARK })] })
          ]
        })]
      })
    ]
  });
}

function statusTable(rows) {
  // rows: [{metric, before, after, status}]
  const headerRow = new TableRow({
    children: [
      "Chỉ số", "Trước 2019", "Sau 2019", "Đánh giá"
    ].map((t, i) => new TableCell({
      borders,
      shading: { fill: BRAND, type: ShadingType.CLEAR },
      width: { size: [2500, 2200, 2200, 2460][i], type: WidthType.DXA },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({ text: t, font: "Arial", size: 20, bold: true, color: "FFFFFF" })] })]
    }))
  });
  const dataRows = rows.map(r => new TableRow({
    children: [r.metric, r.before, r.after, r.status].map((t, i) => {
      const isLast = i === 3;
      const fill = isLast ? (t.includes("🔴") ? RED_LIGHT : t.includes("🟡") ? ORANGE_LIGHT : GREEN_LIGHT) : "FFFFFF";
      return new TableCell({
        borders,
        shading: { fill, type: ShadingType.CLEAR },
        width: { size: [2500, 2200, 2200, 2460][i], type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: t, font: "Arial", size: 20 })] })]
      });
    })
  }));
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [2500, 2200, 2200, 2460], rows: [headerRow, ...dataRows] });
}

function sectionCard(num, title, color) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [600, 8760],
    rows: [new TableRow({
      children: [
        new TableCell({
          borders: noBorders,
          shading: { fill: color, type: ShadingType.CLEAR },
          width: { size: 600, type: WidthType.DXA },
          margins: { top: 100, bottom: 100, left: 120, right: 120 },
          verticalAlign: VerticalAlign.CENTER,
          children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: num, font: "Arial", size: 28, bold: true, color: "FFFFFF" })] })]
        }),
        new TableCell({
          borders: { top: noBorder, bottom: noBorder, right: noBorder, left: { style: BorderStyle.SINGLE, size: 4, color } },
          shading: { fill: "F8F9FA", type: ShadingType.CLEAR },
          width: { size: 8760, type: WidthType.DXA },
          margins: { top: 100, bottom: 100, left: 200, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: title, font: "Arial", size: 24, bold: true, color: DARK })] })]
        })
      ]
    })]
  });
}

// ============================================================
// DOCUMENT
// ============================================================
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: DARK },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: BRAND },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: DARK },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "subbullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 360 } }, run: { color: GRAY } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1260, bottom: 1440, left: 1260 }
      }
    },
    children: [

      // ===== COVER =====
      spacer(480),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 60 },
        children: [new TextRun({ text: "DATATHON 2026 — THE GRIDBREAKER", font: "Arial", size: 20, color: GRAY, allCaps: true, characterSpacing: 80 })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 120 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: BRAND, space: 8 } },
        children: [new TextRun({ text: "Phân tích Dữ liệu Thương mại Điện tử Thời trang Việt Nam", font: "Arial", size: 40, bold: true, color: DARK })]
      }),
      spacer(60),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 80 },
        children: [new TextRun({ text: "Phần 2 — Trực quan hoá & Phân tích EDA", font: "Arial", size: 28, color: BRAND, bold: true })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 60 },
        children: [new TextRun({ text: "Chủ đề trọng tâm: Chẩn đoán nguyên nhân sụt giảm doanh thu 2019–2022", font: "Arial", size: 24, color: GRAY, italics: true })]
      }),
      spacer(360),

      // 4 pillars summary table
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2340, 2340, 2340, 2340],
        rows: [new TableRow({
          children: [
            ["📊 Descriptive", "Dữ liệu nói gì?"],
            ["🔬 Diagnostic", "Tại sao xảy ra?"],
            ["📈 Predictive", "Điều gì sẽ đến?"],
            ["💡 Prescriptive", "Phải làm gì?"],
          ].map(([t, s], i) => new TableCell({
            borders,
            shading: { fill: [BRAND, "1A5276", "1A7A50", "6E2F8B"][i], type: ShadingType.CLEAR },
            width: { size: 2340, type: WidthType.DXA },
            margins: { top: 120, bottom: 120, left: 120, right: 120 },
            children: [
              new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: t, font: "Arial", size: 22, bold: true, color: "FFFFFF" })] }),
              new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: s, font: "Arial", size: 18, color: "E8F0FE", italics: true })] }),
            ]
          }))
        })]
      }),
      spacer(240),

      // ===== PAGE BREAK =====
      new Paragraph({ children: [new PageBreak()] }),

      // ===== 0. LỜI MỞ ĐẦU =====
      h1("0. Lời mở đầu — Cách đọc báo cáo này"),
      body("Báo cáo này phân tích bộ dữ liệu 10 năm (2012–2022) của một doanh nghiệp thương mại điện tử thời trang Việt Nam, bao gồm 14 file CSV với hơn 1.5 triệu records. Mục tiêu trọng tâm là chẩn đoán nguyên nhân doanh thu sụt giảm mạnh từ năm 2019 và không phục hồi trong các năm tiếp theo."),
      spacer(80),
      body("Báo cáo được cấu trúc theo 4 cấp độ phân tích tăng dần:"),
      spacer(60),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [1200, 2000, 3200, 2960],
        rows: [
          new TableRow({ children: ["Cấp độ", "Câu hỏi", "Nội dung", "Section"].map((t, i) => new TableCell({
            borders, shading: { fill: BRAND, type: ShadingType.CLEAR },
            width: { size: [1200, 2000, 3200, 2960][i], type: WidthType.DXA },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({ children: [new TextRun({ text: t, font: "Arial", size: 20, bold: true, color: "FFFFFF" })] })]
          })) }),
          ...[
            ["Descriptive", "Chuyện gì xảy ra?", "Tổng quan dữ liệu, xu hướng doanh thu, thống kê cơ bản", "Section 1–2"],
            ["Diagnostic", "Tại sao xảy ra?", "Phân tích 3 vòng xoáy tiêu cực: acquisition, retention, portfolio", "Section 3–4"],
            ["Predictive", "Điều gì tiếp theo?", "Dự báo xu hướng, nhận diện nhóm rủi ro", "Section 5"],
            ["Prescriptive", "Phải làm gì?", "Khuyến nghị hành động có định lượng", "Section 6"],
          ].map(row => new TableRow({ children: row.map((t, i) => new TableCell({
            borders,
            width: { size: [1200, 2000, 3200, 2960][i], type: WidthType.DXA },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({ children: [new TextRun({ text: t, font: "Arial", size: 20, color: DARK })] })]
          })) }))
        ]
      }),
      spacer(160),

      // ===== 1. TỔNG QUAN DỮ LIỆU =====
      h1("1. Tổng quan Dữ liệu (Data Overview)"),
      body("Trước khi đi vào phân tích nguyên nhân sụt giảm, cần thiết lập nền tảng hiểu biết về bộ dữ liệu: cấu trúc, phạm vi, chất lượng, và những điểm bất thường cần lưu ý khi diễn giải kết quả. Bỏ qua bước này dễ dẫn đến kết luận sai từ dữ liệu chưa được làm sạch."),
      spacer(100),

      h2("1.1 Cấu trúc & Phạm vi Dữ liệu"),
      body("Trình bày sơ đồ quan hệ giữa 14 bảng, phân loại theo 4 lớp: Master, Transaction, Analytical, Operational. Nêu rõ phạm vi thời gian và quy mô dataset."),
      spacer(60),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Sơ đồ ERD đơn giản hóa thể hiện quan hệ giữa các bảng chính\n• Bảng tóm tắt: tên bảng — số dòng — số cột — khoảng thời gian — vai trò",
        BRAND_LIGHT, BRAND),
      spacer(80),
      h3("Số liệu cần nêu:"),
      bullet("14 files CSV, 4 lớp dữ liệu (Master / Transaction / Analytical / Operational)"),
      bullet("646,945 đơn hàng · 121,930 khách hàng · 2,412 SKUs · 10.3 năm dữ liệu (2012–2022)"),
      bullet("Bảng doanh thu hàng ngày (sales.csv) là backbone của toàn bộ phân tích time-series"),
      spacer(80),

      h2("1.2 Data Quality & Cleaning Decisions"),
      body("Mô tả ngắn gọn các vấn đề dữ liệu được phát hiện và quyết định xử lý. Phần này chứng minh tính nghiêm túc của quá trình phân tích và tạo sự tin cậy với người đọc."),
      spacer(60),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Bảng Data Quality Audit: bảng dữ liệu — vấn đề phát hiện — verdict (DROP/FIX/FLAG/KEEP) — lý do\n• Biểu đồ missing values heatmap theo bảng",
        BRAND_LIGHT, BRAND),
      spacer(80),
      h3("7 phát hiện chính — trình bày dạng bảng verdict:"),
      bulletBold("DROP — ", "39 SKU 'ghost twin' giá <100 VND, chưa từng bán (phantom records)"),
      bulletBold("FIX — ", "1,094 records installments=2, avg value 708 VND (recode về mode=1)"),
      bulletBold("FLAG — ", "382 ngày lỗ gộp (Revenue < COGS) — 100% trùng với promo days, đây là sự kiện kinh doanh thực"),
      bulletBold("SPLIT — ", "20,852 đơn 'stuck' (status=created/paid) — tách riêng cho funnel analysis"),
      bulletBold("FLAG — ", "564 đơn 2022 thiếu shipment record — pipeline lag, không xóa"),
      bulletBold("NOTE — ", "bounce_rate ~0.45% (thấp hơn industry 100 lần) — chỉ dùng so sánh tương đối nội bộ"),
      bulletBold("NOTE — ", "51% inventory records vừa stockout vừa overstock — vấn đề phân bổ kho, không phải lỗi data"),
      spacer(160),

      h2("1.3 Thống kê Mô tả Tổng quan (Descriptive Statistics)"),
      body("Cung cấp bức tranh 'baseline' về quy mô và sức khỏe của doanh nghiệp trước khi đi vào phân tích sâu. Đây là cấp độ Descriptive — trả lời 'chuyện gì xảy ra'."),
      spacer(60),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Biểu đồ doanh thu theo năm (bar) với đường GP margin (line) — trục kép\n• Bảng phân phối đơn hàng theo status, device, payment method, order source\n• Biểu đồ phân phối rating 1–5 sao\n• Heatmap: doanh thu trung bình theo tháng × năm (seasonality map)",
        BRAND_LIGHT, BRAND),
      spacer(80),
      h3("Key numbers cần highlight:"),
      bullet("Tổng doanh thu 10 năm: ~16.4 tỷ VND | Đỉnh 2016: 2.1 tỷ | Đáy 2021: 1.04 tỷ"),
      bullet("Biên lợi nhuận gộp: dao động 7.9%–20.7%, không ổn định (std = 12.7%)"),
      bullet("79.9% đơn delivered | 9.2% cancelled | 5.6% returned"),
      bullet("Tính mùa vụ rõ: Tháng 4–6 doanh thu gấp 2.5 lần tháng 11–12"),
      bullet("Avg rating 3.94/5 — ổn định suốt 10 năm (không phải nguyên nhân sụt giảm)"),
      spacer(200),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 2. BỨC TRANH DOANH THU =====
      h1("2. Bức tranh Doanh thu — Descriptive Analysis"),
      body("Section này thiết lập 'what happened' một cách rõ ràng trước khi lý giải nguyên nhân. Mục tiêu: người đọc thấy được quy mô và tính chất của vấn đề trước khi đọc phần chẩn đoán."),
      spacer(100),

      h2("2.1 Xu hướng Doanh thu 2012–2022"),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Line chart: Revenue + Gross Profit theo năm (2012–2022), đánh dấu điểm gãy 2019\n• Bar chart: Số đơn hàng vs Avg order value theo năm (trục kép) — cho thấy volume giảm, AOV tăng\n• Waterfall chart: Decompose revenue thay đổi 2018→2019 (volume effect vs price effect)",
        BRAND_LIGHT, BRAND),
      spacer(80),
      h3("Phát hiện chính:"),
      bullet("Doanh thu giảm 38.5% từ 2018 (1.85 tỷ) → 2019 (1.14 tỷ) — mức giảm lớn nhất trong lịch sử"),
      bullet("Số đơn hàng giảm 40%: 60,966 → 36,431. Avg order value TĂNG 2% (25,459 → 25,957 VND) — không bù được volume loss"),
      bullet("Giai đoạn 2019–2022 'đi ngang' ở mức 1.04–1.17 tỷ — không phục hồi về đỉnh 2016"),
      bullet("Gross Profit 2021 chỉ còn 102 tỷ — thấp hơn cả 2013 (191 tỷ) dù revenue cao hơn → vấn đề margin nghiêm trọng hơn vấn đề revenue"),
      spacer(80),

      h2("2.2 Phân tích Tính mùa vụ (Seasonality)"),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Heatmap tháng × năm (avg daily revenue) — nhận diện peak season và sự thay đổi theo năm\n• Box plot: phân phối doanh thu theo tháng (cho thấy variance trong peak vs off-peak)\n• Line chart: Web sessions theo tháng vs Revenue theo tháng (correlation = 0.458)",
        BRAND_LIGHT, BRAND),
      spacer(80),
      h3("Phát hiện chính:"),
      bullet("Tháng 4–6 là 'mùa vàng' (avg >6.5 triệu VND/ngày). Tháng 11–12 là đáy (~2.5 triệu/ngày)"),
      bullet("Peak season thu hẹp dần sau 2019 — đỉnh mùa hè 2019–2022 chỉ bằng 60% đỉnh 2016–2018"),
      bullet("382 ngày lỗ gộp tập trung tháng 8 (40%) và tháng 12 (32%) — flash sale ăn vào margin"),
      spacer(200),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 3. CHẨN ĐOÁN — 3 VÒNG XOÁY =====
      h1("3. Chẩn đoán Nguyên nhân — Diagnostic Analysis"),
      body("Đây là section cốt lõi của báo cáo. Ba vòng xoáy tiêu cực cộng hưởng nhau giải thích toàn bộ sự sụt giảm. Mỗi vòng xoáy được phân tích từ dữ liệu thực tế với số liệu cụ thể."),
      spacer(60),
      calloutBox("🔍 Luận điểm trung tâm",
        "Sự sụt giảm 2019 KHÔNG phải do một nguyên nhân đơn lẻ. Đây là sự cộng hưởng của 3 vòng xoáy tiêu cực: (1) Acquisition collapse — người đến nhưng không mua; (2) Retention collapse — khách hàng cũ không quay lại; (3) Portfolio collapse — danh mục sản phẩm không còn hấp dẫn. Mỗi vòng xoáy tự củng cố nhau và bắt đầu từ trước 2019 rất lâu.",
        ORANGE_LIGHT, ORANGE),
      spacer(120),

      h2("3.1 Vòng xoáy 1 — Acquisition Collapse: Traffic tăng nhưng không ai mua"),
      body("Web traffic tăng 63% trong 10 năm nhưng conversion rate giảm liên tục từ 1.02% (2013) xuống 0.28% (2022). Đây là xu hướng dài hạn, không phải sự kiện đột ngột."),
      spacer(60),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Dual-axis chart: Web sessions (bar) vs Conversion rate (line) 2013–2022 — gap ngày càng rộng\n• Funnel chart: Signups → First purchase → Repeat purchase (3 tầng dropout)\n• Bar chart: Phân loại 121,930 signups: Guest checkout 63.7% / Prospect chưa mua 28.4% / Prospect mua sau 7.9%\n• Scatter plot: Thời gian chờ từ signup → first purchase (9,595 prospects)",
        BRAND_LIGHT, BRAND),
      spacer(80),
      h3("3.1.1 Phát hiện quan trọng — Guest checkout vs Prospect"),
      bullet("63.7% 'signups' đã mua TRƯỚC khi đăng ký (guest-first behavior) — không phải vấn đề"),
      bullet("28.4% (34,650 người) chưa từng mua sau khi đăng ký — prospect bị bỏ rơi"),
      bullet("Với 9,595 prospect thực (signup trước, mua sau): median chờ 579 ngày, 65.1% không mua trong 1 năm"),
      bullet("Không có kênh acquisition nào nổi trội (purchase rate 71.1%–72.2%) → vấn đề nằm ở on-site experience, không phải traffic quality"),
      spacer(60),
      h3("3.1.2 Địa lý: Central coast thấp hơn 10%"),
      bullet("Da Nang 65.2%, Tuy Hoa 65.7% vs Buon Ma Thuot 77.9%, Son Tay 77.3%"),
      bullet("Phản ánh mức độ thâm nhập e-commerce và thu nhập khả dụng khác nhau theo vùng"),
      spacer(80),

      h2("3.2 Vòng xoáy 2 — Retention Collapse: 59% khách 2018 không quay lại 2019"),
      body("Đây là nguyên nhân trực tiếp nhất của cú sốc 2019. Repeat purchase rate giảm từ 44% (2014–2015) xuống 27% (2020–2022) — một xu hướng dài hạn mà 2019 chỉ là điểm bùng phát."),
      spacer(60),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Stacked bar: New vs Returning customer revenue 2013–2022 — tỷ lệ khách mới từ 57% (2013) → 4.4% (2022)\n• Line chart: Repeat purchase rate theo năm (2012–2022) với điểm đánh dấu 2019\n• Cohort retention heatmap: Nhóm khách theo năm đầu mua, theo dõi % còn mua trong N năm tiếp\n• Bar chart: 2018→2019 churn: 35,181 active → 14,423 retained (41%) / 20,758 churned (59%)",
        BRAND_LIGHT, BRAND),
      spacer(80),
      h3("3.2.1 Chứng minh: Vấn đề không phải service quality"),
      statusTable([
        { metric: "Avg delivery days", before: "~4.5 ngày", after: "~4.5 ngày", status: "🟢 Ổn định" },
        { metric: "Avg review rating", before: "3.93/5", after: "3.94/5", status: "🟢 Ổn định" },
        { metric: "Cancellation rate", before: "~9.2%", after: "~9.2%", status: "🟢 Ổn định" },
        { metric: "Return rate", before: "~3.9%", after: "~3.9%", status: "🟢 Ổn định" },
        { metric: "Repeat purchase rate", before: "40.5% (2018)", after: "30.7% (2019)", status: "🔴 Giảm 25%" },
        { metric: "New first-purchase", before: "3,745 (2018)", after: "1,898 (2019)", status: "🔴 Giảm 49%" },
      ]),
      spacer(80),
      body("→ Khi tất cả service metrics ổn định nhưng retention giảm mạnh, nguyên nhân nằm ở product relevance, không phải operational quality. Khách không tìm thấy lý do để quay lại, không phải vì trải nghiệm tệ.", { italic: true }),
      spacer(80),
      h3("3.2.2 LTV & Revenue Concentration Risk"),
      bullet("Top 10% khách hàng đóng góp 39.5% tổng revenue. Top 20% đóng góp 60%"),
      bullet("Bottom 50% chỉ đóng góp 10.7% — phân phối power-law cực đoan"),
      bullet("Khi nhóm top 20% churn → revenue sụp ngay lập tức, không có gì thay thế"),
      spacer(80),

      h2("3.3 Vòng xoáy 3 — Portfolio Collapse: Mất Outdoor, Streetwear bão hòa"),
      body("Danh mục sản phẩm là yếu tố sâu xa nhất. Outdoor sụp từ 2013 (không được nhận ra), Streetwear bão hòa từ 2017–2018. Khi cả hai trụ cột cùng yếu đi, không có danh mục thứ ba đủ lớn để bù đắp."),
      spacer(60),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Area chart: Outdoor vs Streetwear revenue 2012–2022 — minh họa hai trụ cột sụp đổ\n• Dual-axis chart: Streetwear unit price (line) vs Quantity sold (bar) — price elasticity -9.4x\n• Stacked bar: Streetwear segment mix shift 2012→2022 (Everyday thu hẹp, Balanced mở rộng)\n• Line chart: Outdoor sell-through rate (%) vs Days of supply (trục kép) 2012–2022\n• Bar chart: SKUs mới ra mắt theo năm và theo category (Streetwear: 281→40; Outdoor: 201→17)",
        BRAND_LIGHT, BRAND),
      spacer(80),
      h3("3.3.1 Streetwear: Price shock + Portfolio stagnation"),
      bullet("Price elasticity 2019 = -9.4: tăng giá 4.5% → giảm 42% lượng bán — thị trường quá bão hòa, nhạy cảm giá cực cao"),
      bullet("SKU mới Streetwear: 281 SKUs (2012) → 40–68 SKUs/năm (2014–2022) — lineup không đổi mới đủ nhanh"),
      bullet("Segment mix drift: Everyday (mass market) 49% → 26%; Balanced (mid-premium) 35% → 58% — mất thị trường đại trà chưa thay được bằng premium"),
      spacer(60),
      h3("3.3.2 Outdoor: Chết trong tồn kho từ 2013"),
      bullet("Overstock rate: 46% (2012) → 85% (2018–2022). Days of supply: 118 ngày → 1,998 ngày (5.5 năm!)"),
      bullet("Sell-through rate: 26.7% (2012) → 9.6% (2022) — chỉ bán được 1/10 hàng có"),
      bullet("Vốn bị chôn trong tồn Outdoor không được tái đầu tư vào SKU mới hay marketing"),
      bullet("Chỉ 2 segments (Activewear + Premium) — không có mid-range để giữ khách khi Activewear mất giá cạnh tranh"),
      spacer(200),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 4. NGUYÊN NHÂN ẨN =====
      h1("4. Nguyên nhân Ẩn — Các chỉ số bị bỏ qua khi chỉ nhìn Revenue"),
      body("Revenue ổn định giai đoạn 2019–2022 che giấu các vấn đề nghiêm trọng hơn ở cấp độ sâu hơn. Section này chứng minh tại sao doanh nghiệp không nên dùng Revenue làm KPI duy nhất."),
      spacer(100),

      h2("4.1 Gross Profit thực sự đang sụp — Revenue che giấu điều này"),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Dual-axis: Revenue (bar xanh) vs Gross Profit (bar đỏ) theo năm — GP gap ngày càng lớn\n• Line chart: COGS % of Revenue theo năm — trend tăng dần với biến động mạnh\n• Scatter: Promo days (x) vs Daily margin (y) — cho thấy promo = ngày lỗ",
        BRAND_LIGHT, BRAND),
      spacer(80),
      bullet("2021: COGS chiếm 90.2% revenue — GP margin chỉ 7.9% (tệ nhất 10 năm)"),
      bullet("GP tuyệt đối 2021: 102 tỷ — thấp hơn 2013 (191 tỷ) dù revenue cao hơn 40%"),
      bullet("Biên dao động cực mạnh: -57% đến +29% — không ổn định để lập kế hoạch"),
      bullet("382 ngày lỗ gộp (10% chuỗi thời gian) — 100% trùng promo days → flash sale đang phá margin có hệ thống"),
      spacer(80),

      h2("4.2 Promo Dependency — Vòng lặp nguy hiểm"),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Bar chart: Promo lift (%) theo mức discount — cho thấy discount 12% lift +55-79%, discount 18-20% lift âm -31-35%\n• Bar chart: Stackable vs Non-stackable promo lift (+25.8% vs -5.9%)\n• Scatter: Discount value (x) vs Revenue lift (y) — diminishing returns pattern",
        BRAND_LIGHT, BRAND),
      spacer(80),
      bullet("33–46% đơn hàng có promo — dao động nhưng không giảm suốt 10 năm (promo dependency cấu trúc)"),
      bullet("Avg discount per line tăng từ 998 VND (2013) lên 1,429 VND (2022) — tăng 43% trong 10 năm"),
      bullet("Fixed discount 50K VND: lift âm -21% trong mọi trường hợp — loại bỏ ngay"),
      bullet("Promo 18–20%: lift âm -31% đến -35% — gây hiệu ứng 'chờ sale', triệt tiêu demand bình thường"),
      spacer(80),

      h2("4.3 Inventory Capital Trap — Vốn bị giam trong hàng tồn"),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Dual-axis: Days of supply (bar) vs Sell-through rate (line) theo năm cho từng category\n• Stacked bar: Inventory flag combinations (only stockout / only overstock / both / neither)\n• Bubble chart: Category × (avg days of supply, sell-through rate, revenue)",
        BRAND_LIGHT, BRAND),
      spacer(80),
      bullet("50.6% inventory records vừa stockout vừa overstock cùng tháng — sai SKU, không phải thiếu vốn"),
      bullet("Outdoor days of supply: 118 ngày (2012) → 1,998 ngày (2022) — vốn chết"),
      bullet("Sell-through toàn danh mục chỉ 15.2% — 85% hàng nhập không bán được trong tháng"),
      bullet("Vốn bị chôn trong inventory = không có tiền để đổi mới SKU, marketing, hay mở rộng danh mục"),
      spacer(200),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 5. PREDICTIVE =====
      h1("5. Predictive Analysis — Điều gì sẽ xảy ra nếu không can thiệp?"),
      body("Dựa trên các xu hướng đã quan sát, section này ngoại suy để nhận diện rủi ro tương lai và xác định nhóm cần ưu tiên hành động."),
      spacer(100),

      h2("5.1 Khách hàng 'Ngủ đông' — Tệp có thể tái kích hoạt"),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Histogram: Phân phối khoảng cách giữa các lần mua (inter-order gap) — cho thấy đuôi dài >365 ngày\n• RFM segmentation matrix: Phân nhóm khách hàng theo Recency / Frequency / Monetary\n• Bar chart: Số khách theo nhóm RFM và avg revenue per customer",
        BRAND_LIGHT, BRAND),
      spacer(80),
      bullet("28.5% khoảng cách giữa các lần mua vượt 365 ngày — nhóm 'ngủ đông' có thể tái kích hoạt"),
      bullet("Median inter-order gap: 175 ngày (~6 tháng) — window tự nhiên để trigger retention campaign"),
      bullet("10% gap vượt 826 ngày — nhóm có nguy cơ churn vĩnh viễn nếu không can thiệp sớm"),
      spacer(80),

      h2("5.2 Dự báo xu hướng Revenue & Gross Profit"),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Line chart: Trend extrapolation Revenue và GP (2019–2022 → 2023–2024) với confidence band\n• Scenario analysis: 3 kịch bản (no action / moderate intervention / full recovery)\n• Line chart: Repeat rate trend → dự báo revenue base từ tệp khách trung thành",
        BRAND_LIGHT, BRAND),
      spacer(80),
      bullet("Nếu repeat rate tiếp tục giảm từ 27% → 20%: mất thêm ~150 tỷ revenue từ tệp hiện tại"),
      bullet("Nếu first-purchase tiếp tục ở mức 1,300/năm: không đủ bù churn tự nhiên của tệp cũ"),
      bullet("GP margin dao động quanh 10–13% — cần cải thiện mix hoặc giảm discount để đạt 15%+"),
      spacer(200),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 6. PRESCRIPTIVE =====
      h1("6. Prescriptive Analysis — Khuyến nghị Hành động"),
      body("Mỗi khuyến nghị phải được gắn với số liệu cụ thể từ dữ liệu, có ước lượng tác động, và có thể thực hiện ngay. Đây là yêu cầu của cấp độ Prescriptive trong rubric."),
      spacer(60),
      calloutBox("📋 Visualizations cần thực hiện",
        "• Priority matrix: Impact (trục y) vs Effort (trục x) cho các khuyến nghị\n• Bảng tóm tắt: Hành động — Cơ sở dữ liệu — Tác động ước tính — Timeline",
        BRAND_LIGHT, BRAND),
      spacer(100),

      h2("6.1 Ưu tiên 1 — Tái kích hoạt tệp khách trung thành"),
      h3("Cơ sở:", RED),
      bullet("59% khách 2018 không quay lại 2019. 28.5% gaps >365 ngày. Top 20% = 60% revenue"),
      h3("Hành động:"),
      bulletBold("Email win-back campaign — ", "Nhắm 20,758 khách churn 2019, offer 12% discount (không phải 18–20%). Cơ sở: promo 12% có lift +55–79%, promo 18–20% lift âm"),
      bulletBold("Trigger tại mốc 150 ngày — ", "Median gap là 175 ngày, gửi nhắc nhở ở 150 ngày để intercept trước khi churn"),
      bulletBold("Protect top 20% — ", "Early access promo, loyalty tier, free shipping không điều kiện"),
      spacer(80),

      h2("6.2 Ưu tiên 2 — Chặn promo race-to-bottom"),
      h3("Cơ sở:", RED),
      bullet("Fixed discount lift âm -21%. Promo 18–20% lift âm -35%. Avg discount/line tăng 43% trong 10 năm"),
      h3("Hành động:"),
      bulletBold("Giới hạn discount ceiling ≤15% — ", "Loại bỏ hoàn toàn fixed discount và percentage >15%"),
      bulletBold("Tăng tỷ lệ stackable promo từ 24% → 40% — ", "Stackable promo lift +25.8% vs non-stackable -5.9%"),
      bulletBold("Dồn promo vào peak season (tháng 4–6) — ", "Giữ margin ổn định 10–11 tháng còn lại"),
      spacer(80),

      h2("6.3 Ưu tiên 3 — Giải phóng tồn kho Outdoor, tái phân bổ vốn"),
      h3("Cơ sở:", RED),
      bullet("Outdoor days of supply 1,998 ngày. Sell-through 9.6%. 85% tháng overstock"),
      h3("Hành động:"),
      bulletBold("Flash clearance Outdoor — ", "Dùng promo 12% stackable để giải phóng tồn kho có kiểm soát, lấy vốn tái đầu tư"),
      bulletBold("Thêm mid-range segment cho Outdoor — ", "Hiện chỉ có Activewear + Premium. Thêm tier giá 150K–300K để giữ khách mass market"),
      bulletBold("Tăng SKU mới: Outdoor ≥25 SKUs/năm, Streetwear ≥80 SKUs/năm — ", "Từ mức 17 và 40 hiện tại"),
      spacer(80),

      h2("6.4 Ưu tiên 4 — Chuyển đổi 34,650 prospect chưa mua"),
      h3("Cơ sở:", RED),
      bullet("34,650 accounts đã đăng ký nhưng chưa mua. Prospect thực mua sau signup: median 579 ngày chờ"),
      h3("Hành động:"),
      bulletBold("Email nurturing sequence 3 bước — ", "Ngày 7: welcome + best-seller showcase. Ngày 30: 10% first-order discount. Ngày 90: cuối cùng trước khi xem là cold"),
      bulletBold("Nhắm địa lý: Central coast cities — ", "Da Nang, Tuy Hoa, Dong Hoi có purchase rate thấp 10% — cần content phù hợp địa phương"),
      spacer(80),

      h2("6.5 Chỉ số Theo dõi Thay thế Revenue"),
      body("Revenue một mình không đủ để phản ánh sức khỏe kinh doanh. Đề xuất dashboard 5 chỉ số:"),
      spacer(60),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2000, 2200, 2200, 2960],
        rows: [
          new TableRow({ children: ["KPI", "Hiện tại", "Target", "Lý do quan trọng hơn Revenue"].map((t, i) => new TableCell({
            borders, shading: { fill: BRAND, type: ShadingType.CLEAR },
            width: { size: [2000,2200,2200,2960][i], type: WidthType.DXA },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({ children: [new TextRun({ text: t, font: "Arial", size: 20, bold: true, color: "FFFFFF" })] })]
          })) }),
          ...([
            ["Gross Profit margin", "7.9%–15.7%", ">15% ổn định", "Revenue tăng nhưng GP giảm → bán nhiều hơn để kiếm ít hơn"],
            ["Repeat Purchase Rate", "27% (2022)", ">35%", "Leading indicator của revenue 6–12 tháng sau"],
            ["First-purchase/year", "1,316 (2022)", ">3,000", "Pipeline khách mới cạn → không bù được churn tự nhiên"],
            ["Sell-through Rate", "9.6–15%", ">25%", "Thấp = vốn chết trong kho, không tái đầu tư được"],
            ["Revenue per top 20%", "60% tổng", "Giảm concentration", "Fragile base — một nhóm nhỏ churn = disaster"],
          ]).map(row => new TableRow({ children: row.map((t, i) => new TableCell({
            borders,
            width: { size: [2000,2200,2200,2960][i], type: WidthType.DXA },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({ children: [new TextRun({ text: t, font: "Arial", size: 20, color: DARK })] })]
          })) }))
        ]
      }),
      spacer(200),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== 7. KẾT LUẬN =====
      h1("7. Kết luận"),
      spacer(80),
      calloutBox("📌 Tóm tắt chẩn đoán",
        "Doanh thu sụt giảm 2019 không phải sự cố đột ngột — đây là hệ quả tích lũy của 3 vòng xoáy tiêu cực kéo dài nhiều năm:\n\n• Acquisition: Conversion rate giảm liên tục từ 2013 (1.02% → 0.28%), prospect không được nurture\n• Retention: Repeat rate giảm từ 44% (2014) → 27% (2022), tệp khách cạn dần không được bổ sung\n• Portfolio: Outdoor chết trong tồn kho từ 2013, Streetwear price shock 2019 với elasticity -9.4x\n\nVà 2 nguyên nhân ẩn bị che khuất bởi revenue đi ngang:\n• Gross Profit thực sự đang sụp (GP 2021 chỉ 102 tỷ, thấp hơn 2013)\n• Promo dependency tăng dần: discount ngày càng sâu, margin ngày càng mỏng",
        ORANGE_LIGHT, ORANGE),
      spacer(120),
      body("Doanh nghiệp không gặp vấn đề về service quality (delivery, rating, cancellation đều ổn định). Vấn đề nằm ở product-market fit và chiến lược danh mục — đây là vấn đề khó hơn nhưng cũng là vấn đề có thể giải quyết được nếu hành động đúng thứ tự ưu tiên."),
      spacer(80),
      body("Cơ hội lớn nhất trong ngắn hạn: 20,758 khách churn 2018→2019 với LTV trung bình 145–148K VND/khách. Tái kích hoạt 30% trong số này = ~900 triệu VND doanh thu bổ sung, chưa cần thu hút khách mới."),
      spacer(200),

    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('/home/claude/EDA_Report_Outline.docx', buf);
  console.log('Done');
});