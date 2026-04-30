# CẨM NANG ĐỌC BIỂU ĐỒ PHÂN TÍCH (DATA VISUALIZATION GUIDE)

Tài liệu này là "chìa khóa" giúp bạn và bất kỳ ai (kể cả những người không rành về kỹ thuật) có thể hiểu ngay lập tức ý nghĩa đằng sau hàng tá biểu đồ mà nhóm Data Science đã dày công vẽ ra trong dự án này.

---

## 1. Biểu đồ Vĩ mô Tổng hợp (`03_Plots/macro_trends_yearly.png`)
**Đây là biểu đồ quan trọng nhất của toàn bộ dự án.** Biểu đồ này bao gồm 5 hàng (subplots), giúp người xem nắm bắt toàn bộ dòng chảy kinh doanh trong 11 năm chỉ bằng một cái liếc mắt.

*   **Cách đọc:** Nhìn từ trên xuống dưới theo từng trục năm để thấy sự đồng pha.
    *   *Đường xanh dương & Xanh lá (Doanh thu & Lợi nhuận):* Chú ý sự rớt thảm hại từ năm 2019 đến 2022.
    *   *Đường màu cam (Lượng truy cập web):* Bạn sẽ thấy nghịch lý. Dù doanh thu rớt từ 2019, lượng truy cập web lại đi lên liên tục. Đây chính là minh chứng cho sự "sụp đổ tỷ lệ chuyển đổi" trong thời kỳ COVID.
    *   *Đường màu tím (Tập khách hàng):* Đường này cong thoải (chứng tỏ lượng người đăng ký mới ngày càng ít đi, thị trường đã bão hòa). Tuyệt đối không dùng thước để kẻ đường thẳng dự báo tương lai cho đường này.

## 2. Bức tranh Toàn cảnh Liên tục (`03_Plots/continuous_sales_trend.png`)
**Biểu đồ này giải mã tại sao công ty lại bị lỗ định kỳ.**

*   **Cách đọc:** Theo dõi sự đan xen giữa hai đường Xanh (Doanh thu) và Đỏ (Lợi nhuận) qua 132 tháng liên tiếp.
    *   *Những vùng được tô đen dưới đáy:* Đó là Lợi nhuận Âm (Lỗ). Hãy đếm số năm! Bạn sẽ thấy nó chỉ đâm thủng mốc 0 vào các "Năm Lẻ" (2013, 2015, 2017, 2019, 2021). 
    *   *Tại sao năm 2012 lại thấp tủn mủn?* Đó không phải do công ty làm ăn bết bát. Đó là "Bẫy dữ liệu" (Data trap). File dữ liệu của chúng ta chỉ bắt đầu ghi nhận từ tháng 7/2012, tức là nó bị mất nửa năm doanh thu.

## 3. Biểu đồ Phân Tích Mùa Vụ (`03_Plots/yearly_plots/sales_*.png`)
**Thư mục này chứa 11 biểu đồ, mỗi biểu đồ "zoom" cận cảnh vào từng tháng của một năm.**

*   **Cách đọc:** Hai cột (Cột xanh là Doanh thu, Cột cam là Lợi nhuận).
    *   Bạn hãy để ý tháng 4, 5, 6 của bất kỳ năm nào: Hai cột này luôn dựng đứng như những tòa nhà chọc trời. Đó là mùa gặt hái (Mid-Year Sale).
    *   Hãy mở một năm lẻ (Ví dụ: `sales_2015.png`): Nhìn vào tháng 8, bạn sẽ thấy cột Doanh thu vẫn cao ngất ngưởng, nhưng cột Lợi nhuận thì lặn mất tăm xuống dưới mặt đất. Đó chính là sự kiện Xả kho Urban Blowout (Giảm 50% dưới giá vốn).

## 4. Biểu đồ Nghịch Lý Tồn Kho (`03_Plots/yearly_inventory_plots/inventory_*.png`)
**Biểu đồ này giúp bạn không bị mô hình lừa phỉnh về lượng Tồn kho.**

*   **Cách đọc:** 
    *   Đường nét đứt màu xám là Tổng Hàng Tồn (Stock on hand).
    *   Cột màu xanh là Hàng Nhập Về (Units Received), Cột màu đỏ là Hàng Bán Ra (Units Sold).
    *   Thông thường, ở tháng 8 (Xả kho), cột màu đỏ cực cao, đáng lẽ đường Tồn kho màu xám phải giảm. Nhưng không! Đường màu xám vẫn đi ngang hoặc đi lên.
    *   Bí mật nằm ở cột màu xanh dương: Bộ phận thu mua cũng ồ ạt nhập hàng mới về ngay trong tháng 8 để chuẩn bị bán mùa thu. Hàng cũ vơi đi, hàng mới lấp vào $\rightarrow$ Tổng kho không đổi. 
    *   *Kết luận:* Đừng dùng Tổng tồn kho để dự đoán giảm giá.

## 5. Biểu đồ Quy Luật Người Dùng (`03_Plots/yearly_web_traffic_plots/`)
**Biểu đồ này chứng minh "Cỗ máy kéo Traffic" của công ty hoạt động như thế nào.**

*   **Cách đọc:** Đường cong màu xanh nối các cột thể hiện Tổng số lượt truy cập (Sessions).
    *   Bạn sẽ thấy một **đường cong hình quả chuông (Bell Curve)** lặp lại hoàn hảo qua tất cả 11 năm.
    *   Đáy luôn ở mùa Đông (Tháng 1-3, 10-12).
    *   Đỉnh núi khổng lồ luôn nằm ở mùa Hè (Tháng 4-6).
    *   *Ý nghĩa cho Model:* Nhờ tính lặp lại cực kỳ ổn định này, `sessions` trở thành một "đặc trưng vàng" (Leading Indicator) để dự báo sức mua của khách hàng. Nó đáng tin cậy hơn bất kỳ chỉ số nào khác.

## 6. Biểu đồ Lượng Khách Hàng Mới (`03_Plots/yearly_signup_plots/`)
**Biểu đồ này trả lời câu hỏi: Khi nào công ty thu hút được khách mới?**

*   **Cách đọc:** Cột màu tím thể hiện số lượng tài khoản đăng ký mới.
    *   Giống như Web Traffic, lượng người đăng ký mới cũng nhảy vọt vào các đợt Sale mùa Hè. 
    *   Tuy nhiên, nếu bạn mở các biểu đồ của những năm cuối (2020-2022), bạn sẽ thấy các cột này "lùn" đi rất nhiều so với thời kỳ 2013-2015. 
    *   *Ý nghĩa cho Model:* Sự lùn đi này nhắc nhở chúng ta rằng thị trường đang bão hòa. Chúng ta phải dùng hàm Logarit để "kìm hãm" sức mạnh của tập khách hàng lũy kế trong tương lai, tránh dự báo doanh thu ảo.

## 7. Biểu đồ Hàng Nhập Về (`03_Plots/yearly_received_plots/`)
**Biểu đồ này lật tẩy "Kế hoạch Thu mua" cứng nhắc của công ty.**

*   **Cách đọc:** Cột màu xanh lá biểu thị lượng hàng nhập kho (`units_received`).
    *   Nếu bạn nhìn kỹ, tháng 8 năm nào cũng có một cột nhập hàng cao vọt lên (thậm chí cao hơn cả mùa sale hè). 
    *   Đó chính là lượng hàng mùa thu đông nhập về để chuẩn bị cho sự kiện `Fall Launch` (30/08).
    *   *Ý nghĩa cho Model:* Vì nhập hàng quá nhiều vào tháng 8, tỷ lệ `receive_to_sold_ratio` (Nhập/Bán) sẽ là một biến cực tốt để dự báo nguy cơ quá tải kho và bắt buộc phải giảm giá xả lỗ (Urban Blowout).

## 8. Biểu đồ Khách Hủy Đơn (`03_Plots/yearly_cancel_plots/`)
**Đây là biểu đồ duy nhất mang ý nghĩa "Vô dụng".**

*   **Cách đọc:** Đường thẳng nét đứt màu đỏ là Tỷ lệ Hủy Đơn (`Cancel Rate`).
    *   Bạn sẽ thấy nó luôn là một đường "Flatline" (phẳng lỳ) dao động quanh mức 9%. Bất chấp mọi nỗ lực Marketing, Sale sốc hay mùa ế ẩm, khách hàng vẫn luôn hủy 9% số đơn.
    *   *Ý nghĩa cho Model:* Vì nó là một Hằng số ngẫu nhiên không có tính mùa vụ, biến này mang lại lượng thông tin bằng 0 (Zero Information Gain). Chúng ta sẽ **LOẠI BỎ** đặc trưng này khỏi mô hình để tránh nhiễu.
