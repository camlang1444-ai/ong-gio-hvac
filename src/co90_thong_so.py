"""Thông số chung cho co 90° 400x200 L100 mí TDC.

File thuần Python (không import cadgen) để mô hình 3D, bản vẽ trải phẳng DXF
và script vẽ ảnh thông số dùng chung một bộ số.

Quy ước:
- W = cạnh nằm trong mặt phẳng uốn (cạnh quay), H = cạnh còn lại (bề rộng lưng).
- Kích thước 400x200 là LÒNG TRONG.
- "Má" = 2 tấm hông phẳng hình chữ L cong; "Lưng trong" (bụng/throat) và
  "Lưng ngoài" (heel) = 2 dải tôn cuốn theo cung.
"""

import math

# --- Kích thước co -----------------------------------------------------------
W = 400.0            # cạnh quay (mm)
H = 200.0            # cạnh còn lại = bề rộng 2 tấm lưng (mm)
L = 100.0            # cổ thẳng mỗi đầu (mm)
R_IN = 200.0         # bán kính lưng trong (bụng)  -> R tâm = 1.0 x W (SMACNA)
R_OUT = R_IN + W     # bán kính lưng ngoài = 600
R_CENTER = (R_IN + R_OUT) / 2
ANGLE = 90.0         # góc co (độ)

# --- Vật liệu ------------------------------------------------------------------
T = 0.75             # tôn mạ kẽm dày 0.75 mm (cạnh lớn 301–750 mm)
DENSITY = 7850.0     # kg/m3

# --- Mí / phần bù gia công (tham khảo, chỉnh theo máy của xưởng) ---------------
TDC_FLANGE = 30.0    # chiều cao bích TDC sau khi cán (TDC 30)
TDC_ALLOW = 40.0     # phần bù trải phẳng để cán TDC, mỗi đầu
PITTS_POCKET = 25.0  # mí âm (Pittsburgh) trên má, dọc cạnh ghép với lưng
PITTS_MALE = 8.0     # mí dương (gập 90°) trên lưng, mỗi bên

# --- Kích thước tính toán --------------------------------------------------------


def arc_len(r: float, angle_deg: float = ANGLE) -> float:
    return math.pi * r * angle_deg / 180.0


ARC_IN = arc_len(R_IN)                      # 314.16
ARC_OUT = arc_len(R_OUT)                    # 942.48
LEN_THROAT = L + ARC_IN + L                 # chiều dài tinh lưng trong
LEN_HEEL = L + ARC_OUT + L                  # chiều dài tinh lưng ngoài

# Má (tinh): hộp bao (-L..R_OUT) x (-L..R_OUT)
CHEEK_NET = (R_OUT + L, R_OUT + L)
# Má (phôi cắt) = tinh + mí âm phía ngoài + TDC mỗi đầu
CHEEK_BLANK = (R_OUT + PITTS_POCKET + L + TDC_ALLOW,
               R_OUT + PITTS_POCKET + L + TDC_ALLOW)

THROAT_BLANK = (LEN_THROAT + 2 * TDC_ALLOW, H + 2 * PITTS_MALE)
HEEL_BLANK = (LEN_HEEL + 2 * TDC_ALLOW, H + 2 * PITTS_MALE)


def cheek_net_area() -> float:
    sector = math.pi * (R_OUT**2 - R_IN**2) * ANGLE / 360.0
    return sector + 2 * W * L


def cheek_blank_area() -> float:
    sector = math.pi * ((R_OUT + PITTS_POCKET)**2 - (R_IN - PITTS_POCKET)**2) * ANGLE / 360.0
    legs = 2 * (W + 2 * PITTS_POCKET) * L
    tdc = 2 * W * TDC_ALLOW
    return sector + legs + tdc


def strip_blank_area(length: float) -> float:
    return length * (H + 2 * PITTS_MALE) + 2 * H * TDC_ALLOW


def total_blank_area_m2() -> float:
    a = 2 * cheek_blank_area() + strip_blank_area(LEN_THROAT) + strip_blank_area(LEN_HEEL)
    return a / 1e6


def total_mass_kg() -> float:
    return total_blank_area_m2() * T / 1000.0 * DENSITY
