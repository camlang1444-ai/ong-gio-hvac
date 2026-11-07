"""Ống gió chữ nhật 700x200, dài L800, nối mí C ở 2 đầu.

Giả định (chỉnh tham số bên dưới nếu khác):
- 700x200 là kích thước LÒNG TRONG ống (mm).
- Tôn mạ kẽm dày 0.75 mm (cạnh lớn <= 750 mm).
- Mí C: mép 2 đầu ống bẻ gập ngược ra ngoài 180° (hem) dài 15 mm,
  để đóng nẹp C (drive cleat) nối với ống kế tiếp. L800 tính cả mí.
"""

from cadgen import build123d as bd
from cadgen import step

W = 700.0      # rộng lòng trong
H = 200.0      # cao lòng trong
L = 800.0      # chiều dài tổng (tính cả mí)
T = 0.75       # độ dày tôn
HEM = 15.0     # chiều dài mí gập ngược
GAP = 0.75     # khe hở trong của nếp gập (~ bán kính uốn)


def rect_tube(w_in: float, h_in: float, t: float, length: float, z0: float):
    """Ống chữ nhật thành mỏng, lòng trong w_in x h_in, chạy theo trục Z từ z0."""
    outer = bd.Box(w_in + 2 * t, h_in + 2 * t, length,
                   align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    inner = bd.Box(w_in, h_in, length + 2,
                   align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    return bd.Pos(0, 0, z0) * outer - bd.Pos(0, 0, z0 - 1) * inner


def hem_end(z_end: float, direction: int):
    """Mí C tại một đầu ống. direction=+1: đầu trên (z=L), -1: đầu dưới (z=0)."""
    # Lớp tôn gập ngược nằm ngoài thân ống, cách thân 1 khe GAP
    w_hem = W + 2 * (T + GAP)
    h_hem = H + 2 * (T + GAP)
    z_hem0 = z_end - HEM if direction > 0 else z_end
    fold = rect_tube(w_hem, h_hem, T, HEM, z_hem0)
    # Phần uốn 180° ở mép (đóng khe giữa thân và lớp gập)
    z_b0 = z_end - T if direction > 0 else z_end
    bend = rect_tube(W, H, 2 * T + GAP, T, z_b0)
    return fold + bend


@step(out="../STEP/ong_gio_700x200_L800.step")
def ong_gio_700x200_L800():
    body = rect_tube(W, H, T, L, 0.0)
    duct = body + hem_end(L, +1) + hem_end(0.0, -1)
    if len(duct.solids()) == 1:
        duct = duct.solids()[0]
    duct.label = "ong_gio_700x200_L800_mi_C"
    return duct


if __name__ == "__main__":
    ong_gio_700x200_L800()
