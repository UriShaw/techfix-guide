-- ============================================================
-- TechFix Guide (TFG) — Database Schema
-- MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS techfix_guide CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE techfix_guide;

-- ============================================================
-- TABLE: Devices
-- ============================================================
CREATE TABLE Devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: OperatingSystems
-- ============================================================
CREATE TABLE OperatingSystems (
    id INT AUTO_INCREMENT PRIMARY KEY,
    os_name VARCHAR(100) NOT NULL,
    device_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES Devices(id) ON DELETE SET NULL
);

-- ============================================================
-- TABLE: ErrorCategories
-- ============================================================
CREATE TABLE ErrorCategories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: Errors
-- ============================================================
CREATE TABLE Errors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    error_code VARCHAR(50),
    error_name VARCHAR(200) NOT NULL,
    description TEXT,
    solution TEXT,
    video_link VARCHAR(500),
    device_id INT,
    os_id INT,
    category_id INT,
    severity ENUM('low','medium','high','critical') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES Devices(id) ON DELETE SET NULL,
    FOREIGN KEY (os_id) REFERENCES OperatingSystems(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES ErrorCategories(id) ON DELETE SET NULL
);

-- ============================================================
-- TABLE: Scripts
-- ============================================================
CREATE TABLE Scripts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    script_name VARCHAR(200) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    script_type ENUM('.bat','.py','.sh','.ps1') NOT NULL,
    compatible_os VARCHAR(200),
    download_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: Guides
-- ============================================================
CREATE TABLE Guides (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    content LONGTEXT,
    device_type VARCHAR(100),
    os_type VARCHAR(100),
    category VARCHAR(100),
    thumbnail VARCHAR(500),
    view_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: Error_Scripts (Link table — Errors <-> Scripts)
-- ============================================================
CREATE TABLE Error_Scripts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    error_id INT NOT NULL,
    script_id INT NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (error_id) REFERENCES Errors(id) ON DELETE CASCADE,
    FOREIGN KEY (script_id) REFERENCES Scripts(id) ON DELETE CASCADE,
    UNIQUE KEY unique_error_script (error_id, script_id)
);

-- ============================================================
-- SAMPLE DATA: Devices
-- ============================================================
INSERT INTO Devices (device_name) VALUES
('Laptop'),
('Smartphone');

-- ============================================================
-- SAMPLE DATA: OperatingSystems
-- ============================================================
INSERT INTO OperatingSystems (os_name, device_id) VALUES
('Windows 10', 1),
('Windows 11', 1),
('macOS', 1),
('Android', 2),
('iOS', 2),
('HarmonyOS', 2);

-- ============================================================
-- SAMPLE DATA: ErrorCategories
-- ============================================================
INSERT INTO ErrorCategories (category_name, description) VALUES
('Software', 'Lỗi phần mềm, hệ điều hành, ứng dụng'),
('Hardware', 'Lỗi phần cứng, linh kiện vật lý'),
('Network', 'Lỗi kết nối mạng, WiFi, Bluetooth'),
('Performance', 'Lỗi hiệu năng, máy chậm, quá nhiệt'),
('Storage', 'Lỗi ổ cứng, bộ nhớ, lưu trữ'),
('Display', 'Lỗi màn hình, đồ họa'),
('Battery', 'Lỗi pin, sạc, nguồn điện'),
('Mobile App', 'Lỗi ứng dụng trên điện thoại');

-- ============================================================
-- SAMPLE DATA: Scripts
-- ============================================================
INSERT INTO Scripts (script_name, description, file_path, script_type, compatible_os) VALUES
('Windows Cleaner', 'Dọn dẹp file rác, temp files, cache hệ thống Windows', 'scripts/windows_cleaner.bat', '.bat', 'Windows 10, Windows 11'),
('Battery Health Check', 'Kiểm tra tình trạng pin laptop, xuất báo cáo chi tiết', 'scripts/battery_check.py', '.py', 'Windows 10, Windows 11'),
('SSD Health Check', 'Kiểm tra sức khỏe ổ cứng SSD/HDD qua SMART data', 'scripts/ssd_health.py', '.py', 'Windows 10, Windows 11'),
('Remove Bloatware', 'Xóa ứng dụng rác cài sẵn của Windows, tăng hiệu năng', 'scripts/remove_bloatware.bat', '.bat', 'Windows 10, Windows 11'),
('Network Reset', 'Reset cấu hình mạng, xóa cache DNS, Winsock reset', 'scripts/network_reset.bat', '.bat', 'Windows 10, Windows 11'),
('Startup Optimizer', 'Tối ưu chương trình khởi động, giảm thời gian boot', 'scripts/startup_optimizer.py', '.py', 'Windows 10, Windows 11'),
('Driver Backup', 'Sao lưu toàn bộ driver hiện tại trước khi cài lại Windows', 'scripts/driver_backup.bat', '.bat', 'Windows 10, Windows 11'),
('RAM Diagnostic', 'Chạy kiểm tra bộ nhớ RAM, phát hiện lỗi memory', 'scripts/ram_diagnostic.bat', '.bat', 'Windows 10, Windows 11');

-- ============================================================
-- SAMPLE DATA: Errors (Laptop - Windows)
-- ============================================================
INSERT INTO Errors (error_code, error_name, description, solution, video_link, device_id, os_id, category_id, severity) VALUES

-- BSOD / Blue Screen
('0x0000007E', 'Blue Screen of Death – SYSTEM_THREAD_EXCEPTION', 
 'Màn hình xanh chết chóc xuất hiện khi khởi động hoặc trong lúc sử dụng. Thường do driver lỗi hoặc phần cứng hỏng.',
 '1. Khởi động vào Safe Mode (F8 khi boot)\n2. Cập nhật hoặc rollback driver liên quan\n3. Chạy "sfc /scannow" trong Command Prompt\n4. Kiểm tra RAM bằng Windows Memory Diagnostic\n5. Nếu lỗi vẫn còn, dùng System Restore',
 'https://www.youtube.com/watch?v=example1', 1, 2, 6, 'critical'),

('0x000000EF', 'Critical Process Died – Windows 11',
 'Tiến trình hệ thống quan trọng bị dừng đột ngột, gây BSOD ngay lập tức.',
 '1. Chạy "sfc /scannow" và "DISM /Online /Cleanup-Image /RestoreHealth"\n2. Kiểm tra ổ cứng bằng chkdsk /f /r\n3. Cập nhật Windows lên phiên bản mới nhất\n4. Reset Windows nếu các bước trên không giải quyết được',
 'https://www.youtube.com/watch?v=example2', 1, 2, 1, 'critical'),

-- WiFi Issues
('NET-001', 'WiFi Không Kết Nối Được – Windows 11',
 'Laptop không thể kết nối WiFi dù thấy tên mạng. Icon WiFi hiển thị dấu chấm than.',
 '1. Chạy Network Troubleshooter\n2. Reset TCP/IP: "netsh int ip reset"\n3. Flush DNS: "ipconfig /flushdns"\n4. Gỡ và cài lại driver WiFi\n5. Kiểm tra dịch vụ WLAN AutoConfig trong Services',
 'https://www.youtube.com/watch?v=example3', 1, 2, 3, 'high'),

('NET-002', 'WiFi Chập Chờn, Hay Bị Ngắt Kết Nối',
 'WiFi kết nối được nhưng hay bị ngắt sau vài phút, tốc độ chậm.',
 '1. Tắt Power Management của WiFi adapter\n2. Đổi DNS sang 8.8.8.8 / 8.8.4.4\n3. Chỉnh kênh WiFi router tránh nhiễu\n4. Cập nhật firmware router\n5. Kiểm tra can nhiễu từ thiết bị 2.4GHz',
 'https://www.youtube.com/watch?v=example4', 1, 1, 3, 'medium'),

-- Performance
('PERF-001', 'Laptop Chạy Chậm, CPU 100%',
 'Máy ì ạch, CPU luôn ở mức 100% dù không làm gì nặng. Thường do Windows Update hoặc malware.',
 '1. Mở Task Manager kiểm tra tiến trình ngốn CPU\n2. Tắt Windows Search indexing tạm thời\n3. Chạy Windows Defender Full Scan\n4. Tắt các startup program không cần thiết\n5. Nâng cấp RAM nếu dưới 8GB',
 'https://www.youtube.com/watch?v=example5', 1, 2, 4, 'high'),

('PERF-002', 'Laptop Quá Nhiệt, Tắt Nguồn Đột Ngột',
 'Nhiệt độ CPU/GPU vượt 95°C, máy tự tắt để bảo vệ linh kiện.',
 '1. Vệ sinh tản nhiệt, thay keo tản nhiệt\n2. Dùng đế tản nhiệt\n3. Cài HWMonitor theo dõi nhiệt độ\n4. Giảm TDP bằng ThrottleStop\n5. Kiểm tra quạt tản nhiệt còn hoạt động',
 NULL, 1, 1, 4, 'critical'),

-- Storage
('SSD-001', 'Ổ Cứng Không Nhận, Không Boot Được',
 'Máy báo "No Boot Device" hoặc "Operating System Not Found" khi khởi động.',
 '1. Kiểm tra kết nối cable SATA/NVMe\n2. Vào BIOS kiểm tra ổ cứng có được nhận không\n3. Dùng Bootable USB để kiểm tra ổ cứng\n4. Chạy "bootrec /fixmbr" và "bootrec /fixboot"\n5. Nếu ổ cứng hỏng, cần thay thế ngay',
 NULL, 1, 2, 5, 'critical'),

-- Battery
('BAT-001', 'Pin Laptop Không Sạc Được, Báo 0%',
 'Laptop cắm sạc nhưng pin không tăng, icon pin hiển thị "Plugged in, not charging".',
 '1. Remove battery (nếu rời) và cắm điện trực tiếp\n2. Cập nhật driver ACPI và Battery\n3. Calibrate pin: xả hết rồi sạc đầy 100%\n4. Kiểm tra adapter sạc bằng adapter khác\n5. Thay pin mới nếu pin đã phồng hoặc chai',
 NULL, 1, 2, 7, 'high'),

-- Display
('DSP-001', 'Màn Hình Laptop Bị Sọc, Nhấp Nháy',
 'Màn hình xuất hiện các sọc ngang/dọc hoặc nhấp nháy liên tục.',
 '1. Cập nhật driver GPU (Intel/NVIDIA/AMD)\n2. Kiểm tra Hz màn hình trong Display Settings\n3. Tắt Hardware Acceleration trong trình duyệt\n4. Kiểm tra cable màn hình bên trong laptop\n5. Test với màn hình ngoài để xác định nguồn lỗi',
 NULL, 1, 2, 6, 'medium'),

-- Software
('SW-001', 'Windows Update Bị Lỗi, Không Cài Được',
 'Windows Update báo lỗi 0x80070002, 0x8024402F hoặc update mắc kẹt ở 0%.',
 '1. Chạy Windows Update Troubleshooter\n2. Xóa folder SoftwareDistribution\n3. Reset Windows Update Services\n4. Dùng DISM để sửa image Windows\n5. Cập nhật thủ công từ Microsoft Update Catalog',
 NULL, 1, 1, 1, 'medium');

-- ============================================================
-- SAMPLE DATA: Errors (Smartphone)
-- ============================================================
INSERT INTO Errors (error_code, error_name, description, solution, video_link, device_id, os_id, category_id, severity) VALUES

('AND-001', 'Android Bị Treo Logo, Không Vào Được',
 'Điện thoại Android bị kẹt ở màn hình logo nhà sản xuất, không boot vào được hệ thống.',
 '1. Giữ Power + Volume Down để force restart\n2. Vào Recovery Mode (Power + Volume Up)\n3. Chọn "Wipe Cache Partition"\n4. Nếu vẫn lỗi, thực hiện Factory Reset\n5. Flash lại ROM gốc nếu tất cả thất bại',
 NULL, 2, 4, 1, 'critical'),

('AND-002', 'WiFi Android Không Bắt Được, Xám Xịt',
 'Biểu tượng WiFi bị xám, không thể bật lên hoặc không thấy mạng nào.',
 '1. Restart điện thoại\n2. Vào Settings > WiFi > thêm mạng thủ công\n3. Reset Network Settings\n4. Vào Safe Mode kiểm tra app lạ\n5. Flash lại firmware nếu do lỗi phần mềm sâu',
 NULL, 2, 4, 3, 'high'),

('AND-003', 'Fix Lỗi Đăng Nhập WeChat Trên Android',
 'WeChat báo lỗi "Login Failed" hoặc không nhận SMS xác minh.',
 '1. Xóa cache WeChat: Settings > Apps > WeChat > Clear Cache\n2. Kiểm tra quyền SMS và Phone trong App Permissions\n3. Thử đăng nhập bằng tài khoản email\n4. Gỡ và cài lại WeChat từ nguồn chính thống\n5. Liên hệ WeChat support nếu tài khoản bị khóa',
 NULL, 2, 4, 8, 'medium'),

('IOS-001', 'iPhone Không Vào Được App Store',
 'App Store báo lỗi "Cannot connect to App Store" hoặc trống trắng.',
 '1. Kiểm tra kết nối mạng\n2. Đăng xuất và đăng nhập lại Apple ID\n3. Vào Settings > General > Date & Time > Set Automatically\n4. Reset Network Settings\n5. Update iOS lên phiên bản mới nhất',
 NULL, 2, 5, 8, 'medium'),

('IOS-002', 'iPhone Sạc Chậm, Pin Hao Nhanh',
 'iPhone sạc rất chậm dù dùng adapter chính hãng, pin giảm nhanh bất thường.',
 '1. Vào Settings > Battery > Battery Health kiểm tra %\n2. Tắt Background App Refresh\n3. Tắt Location Services cho app không cần thiết\n4. Enable Low Power Mode khi pin dưới 50%\n5. Thay pin tại Apple Store nếu Battery Health dưới 80%',
 NULL, 2, 5, 7, 'medium'),

('AND-004', 'Cài Tiếng Việt Cho Máy Android Nội Địa Trung',
 'Máy Android mua ở Trung Quốc chỉ có tiếng Trung, không có tùy chọn tiếng Việt.',
 '1. Tải app "More Locale 2" từ APKPure\n2. Kết nối USB debugging với ADB\n3. Chạy lệnh: adb shell pm grant jp.co.c_lis.ccl.morelocale android.permission.CHANGE_CONFIGURATION\n4. Mở app chọn Vietnamese (vi_VN)\n5. Hoặc flash ROM quốc tế có hỗ trợ tiếng Việt',
 NULL, 2, 4, 1, 'low'),

('AND-005', 'Giải Phóng Bộ Nhớ Other Storage Android',
 'Mục "Other" trong Storage chiếm quá nhiều dung lượng không giải phóng được.',
 '1. Settings > Apps > xem app nào chiếm nhiều\n2. Clear cache tất cả app\n3. Dùng Files by Google để dọn file rác\n4. Xóa conversation Zalo/Messenger cũ\n5. Factory Reset là cách cuối cùng nếu Other > 10GB',
 NULL, 2, 4, 5, 'medium');

-- ============================================================
-- SAMPLE DATA: Guides
-- ============================================================
INSERT INTO Guides (title, content, device_type, os_type, category) VALUES
('Hướng Dẫn Tạo USB Boot Windows 11', 
 '# Tạo USB Boot Windows 11\n\n## Chuẩn bị\n- USB tối thiểu 8GB\n- File ISO Windows 11 từ Microsoft\n- Phần mềm Rufus (miễn phí)\n\n## Các bước thực hiện\n\n### Bước 1: Tải Rufus\nTải Rufus từ https://rufus.ie - chọn phiên bản Portable.\n\n### Bước 2: Cắm USB và mở Rufus\nCắm USB vào máy, mở Rufus với quyền Administrator.\n\n### Bước 3: Cấu hình\n- Device: chọn USB của bạn\n- Boot selection: chọn file ISO Windows 11\n- Partition scheme: GPT (cho máy UEFI) hoặc MBR (cho máy cũ)\n- File system: NTFS\n\n### Bước 4: Bắt đầu tạo\nNhấn START và chờ khoảng 10-15 phút.',
 'Laptop', 'Windows 11', 'Software'),

('Cách Sửa Lỗi Màn Hình Xanh (BSOD) Nhanh Nhất',
 '# Sửa Blue Screen of Death\n\n## Màn hình xanh là gì?\nBSOD (Blue Screen of Death) là lỗi nghiêm trọng khiến Windows phải dừng đột ngột để tránh hỏng dữ liệu.\n\n## Các bước xử lý\n\n### Bước 1: Ghi lại mã lỗi\nChụp ảnh màn hình xanh, đặc biệt là mã lỗi dạng 0x00000XXX.\n\n### Bước 2: Khởi động Safe Mode\nKhởi động lại, nhấn F8 liên tục → chọn Safe Mode.\n\n### Bước 3: Kiểm tra driver\nVào Device Manager, tìm driver có dấu chấm than vàng.\n\n### Bước 4: Chạy SFC\n```\nsfc /scannow\nDISM /Online /Cleanup-Image /RestoreHealth\n```\n\n### Bước 5: Kiểm tra RAM\nChạy Windows Memory Diagnostic để kiểm tra RAM.',
 'Laptop', 'Windows 10, Windows 11', 'Software'),

('Fix Lỗi Đăng Nhập WeChat – Hướng Dẫn 2024',
 '# Fix WeChat Login Error\n\n## Các lỗi thường gặp\n- "Login Failed"\n- Không nhận được SMS xác minh\n- Tài khoản bị tạm khóa\n\n## Cách sửa lỗi theo từng trường hợp\n\n### Không nhận SMS\n1. Kiểm tra số điện thoại đúng định dạng +84xxxxxxxxx\n2. Tắt tính năng block SMS lạ\n3. Thử lại sau 10 phút (giới hạn gửi SMS)\n4. Dùng email backup thay thế\n\n### Clear Cache WeChat\n1. Settings > Apps > WeChat\n2. Storage > Clear Cache\n3. Đăng nhập lại\n\n### Cài lại WeChat sạch\n1. Gỡ cài đặt WeChat\n2. Tải lại từ CH Play / App Store\n3. Đăng nhập fresh',
 'Smartphone', 'Android, iOS', 'Mobile App'),

('Tối Ưu Hiệu Năng Windows 11 – 10 Bước Đơn Giản',
 '# Tăng Tốc Windows 11\n\n## Mục tiêu\nGiảm thời gian boot, tăng tốc độ mở app, giảm RAM usage.\n\n## 10 bước tối ưu\n\n1. **Disable Visual Effects**: Right-click This PC > Properties > Advanced > Performance Settings > Adjust for best performance\n\n2. **Tắt Startup Programs**: Task Manager > Startup tab > Disable hết app không cần\n\n3. **Storage Sense**: Settings > System > Storage > Storage Sense > bật lên\n\n4. **Power Plan**: Chọn High Performance hoặc Balanced, tránh Power Saver\n\n5. **Virtual Memory**: Nếu RAM < 8GB, tăng Virtual Memory lên 2x RAM\n\n6. **Defragment HDD**: Nếu dùng HDD, chạy Defragment & Optimize Drives hàng tuần\n\n7. **Update Drivers**: Cập nhật driver GPU, WiFi, Chipset\n\n8. **Disable Telemetry**: Tắt Windows telemetry để giảm tải nền\n\n9. **Clean Temp Files**: Nhấn Win+R > %temp% > xóa hết\n\n10. **SSD Trim**: Nếu dùng SSD, bật TRIM trong Windows',
 'Laptop', 'Windows 11', 'Performance'),

('Hướng Dẫn Cài Office 365 Miễn Phí Cho Sinh Viên',
 '# Cài Office 365 Miễn Phí\n\n## Điều kiện\nCần email trường đại học (@edu.vn hoặc @*.edu)\n\n## Các bước\n\n### Bước 1: Đăng ký\nTruy cập office.com, nhấn "Get Office" > nhập email trường.\n\n### Bước 2: Xác minh email\nKiểm tra hộp thư trường, nhấn link xác minh.\n\n### Bước 3: Tải về\nDownload Office 365 Education gồm Word, Excel, PowerPoint, Teams.\n\n### Bước 4: Cài đặt\nChạy file cài đặt, đăng nhập bằng email trường.\n\n## Lưu ý\n- Miễn phí khi còn là sinh viên\n- Có thể dùng online tại office.com không cần cài',
 'Laptop', 'Windows 10, Windows 11', 'Software'),

('Fix Douyin Login Error – Máy Nội Địa Trung',
 '# Sửa Lỗi Đăng Nhập Douyin\n\n## Lỗi thường gặp\n- Yêu cầu số điện thoại Trung Quốc\n- SMS xác minh không về Việt Nam\n- App crash khi đăng nhập\n\n## Giải pháp\n\n### Cách 1: Dùng VPN\n1. Tải VPN (Windscribe, ProtonVPN free)\n2. Kết nối server Trung Quốc\n3. Đăng nhập Douyin\n\n### Cách 2: Đăng nhập qua WeChat\n1. Mở Douyin > Đăng nhập\n2. Chọn "Login with WeChat"\n3. Quét QR code bằng WeChat\n\n### Cách 3: Tạo tài khoản mới\n1. Mua SIM Trung Quốc ảo tại simhostvn.com\n2. Đăng ký tài khoản mới\n3. Sau đó đổi số về SIM Việt Nam',
 'Smartphone', 'Android, iOS', 'Mobile App');

-- ============================================================
-- SAMPLE DATA: Error_Scripts mapping
-- ============================================================
INSERT INTO Error_Scripts (error_id, script_id, note) VALUES
(1, 1, 'Dọn temp files trước khi sửa BSOD'),
(1, 2, 'Kiểm tra RAM trước khi rollback driver'),
(3, 5, 'Reset mạng để sửa WiFi không kết nối'),
(4, 5, 'Network reset cho WiFi chập chờn'),
(5, 1, 'Dọn hệ thống khi CPU 100%'),
(5, 6, 'Tắt startup apps để giảm tải CPU'),
(7, 3, 'Kiểm tra ổ cứng trước khi sửa boot'),
(8, 2, 'Kiểm tra pin trước khi thay'),
(10, 4, 'Xóa bloatware sau khi fix Windows Update');

-- ============================================================
-- INDEX để tối ưu query
-- ============================================================
CREATE INDEX idx_errors_device ON Errors(device_id);
CREATE INDEX idx_errors_os ON Errors(os_id);
CREATE INDEX idx_errors_category ON Errors(category_id);
CREATE INDEX idx_errors_code ON Errors(error_code);
CREATE INDEX idx_guides_device ON Guides(device_type);
CREATE INDEX idx_guides_os ON Guides(os_type);
CREATE INDEX idx_error_scripts_error ON Error_Scripts(error_id);
CREATE INDEX idx_error_scripts_script ON Error_Scripts(script_id);
