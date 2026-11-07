"""Co 90° ống gió chữ nhật 400x200, cổ thẳng L100 mỗi đầu, nối bích TDC.

Thông số dùng chung nằm trong co90_thong_so.py.
Hệ trục: tâm cung tại gốc O, mặt phẳng uốn là XY, cạnh H theo trục Z.
Đầu 1: cổ chạy theo -Y. Đầu 2: cổ chạy theo -X.
"""

from cadgen import build123d as bd
from cadgen import step

from co90_thong_so import H, L, R_IN, R_OUT, T, TDC_FLANGE

FLANGE_FACE = 5.0    # bề dày mặt bích TDC (mô hình hóa đơn giản)
BOLT_D = 10.0        # lỗ bu lông góc bích


def _profile_rect(x0: float, x1: float, z0: float, z1: float):
    """Hình chữ nhật trên mặt phẳng XZ (y = 0)."""
    return bd.Plane.XZ * bd.Pos((x0 + x1) / 2, (z0 + z1) / 2) * bd.Rectangle(x1 - x0, z1 - z0)


def _box(x0, x1, y0, y1, z0, z1):
    return bd.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * bd.Box(x1 - x0, y1 - y0, z1 - z0)


def bend_section():
    """Đoạn cong 90°: tiết diện thành mỏng quay quanh trục Z."""
    outer = _profile_rect(R_IN - T, R_OUT + T, -H / 2 - T, H / 2 + T)
    inner = _profile_rect(R_IN, R_OUT, -H / 2, H / 2)
    return bd.revolve(outer - inner, axis=bd.Axis.Z, revolution_arc=90)


def leg_with_tdc():
    """Cổ thẳng đầu 1 (chạy theo -Y) kèm bích TDC ở mép."""
    xo0, xo1 = R_IN - T, R_OUT + T
    zo = H / 2 + T
    leg = _box(xo0, xo1, -L, 0, -zo, zo) - _box(R_IN, R_OUT, -L - 1, 1, -H / 2, H / 2)

    f = TDC_FLANGE
    flange = (_box(xo0 - f, xo1 + f, -L, -L + FLANGE_FACE, -zo - f, zo + f)
              - _box(xo0, xo1, -L - 1, -L + FLANGE_FACE + 1, -zo, zo))
    for x in (xo0 - f / 2, xo1 + f / 2):
        for z in (-zo - f / 2, zo + f / 2):
            hole = bd.Pos(x, -L + FLANGE_FACE / 2, z) * bd.Rot(90, 0, 0) * bd.Cylinder(BOLT_D / 2, FLANGE_FACE + 2)
            flange -= hole
    return leg + flange


def elbow():
    leg1 = leg_with_tdc()
    leg2 = bd.mirror(leg1, about=bd.Plane(origin=(0, 0, 0), z_dir=(1, -1, 0)))
    body = bend_section() + leg1 + leg2
    solids = body.solids()
    return solids[0] if len(solids) == 1 else body


@step(out="../STEP/co90_400x200_L100.step")
def co90_400x200_L100():
    part = elbow()
    part.label = "co90_400x200_L100_TDC"
    return part


if __name__ == "__main__":
    co90_400x200_L100()
