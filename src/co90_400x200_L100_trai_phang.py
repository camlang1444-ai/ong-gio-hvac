"""Bản vẽ trải phẳng (phôi cắt) các mảnh co 90° 400x200 L100 mí TDC.

Lớp:
- CUT              : đường cắt phôi (đã cộng mí Pittsburgh + phần bù TDC, cắt góc)
- BEND_FOLD        : đường gập mí / gập TDC (= biên kích thước tinh)
- REFERENCE_ROLL   : vạch bắt đầu / kết thúc đoạn cuốn cong trên 2 tấm lưng
"""

from cadgen import build123d as bd
from cadgen import dxf

from co90_thong_so import (
    H, L, LEN_HEEL, LEN_THROAT, PITTS_MALE, PITTS_POCKET, R_IN, R_OUT, TDC_ALLOW,
)

GAP = 80.0  # khoảng cách giữa các mảnh trên bản vẽ


def _rect(x0, x1, y0, y1):
    return bd.Pos((x0 + x1) / 2, (y0 + y1) / 2) * bd.Rectangle(x1 - x0, y1 - y0)


def _ring_sector(r1, r2):
    ring = bd.Circle(r2) - bd.Circle(r1)
    return ring & _rect(0, r2 + 1, 0, r2 + 1)


# ---------------------------------------------------------------- Má (cheek) --

def cheek_cut():
    p, t = PITTS_POCKET, TDC_ALLOW
    net = _ring_sector(R_IN, R_OUT) + _rect(R_IN, R_OUT, -L, 0) + _rect(-L, 0, R_IN, R_OUT)
    outer_band = _ring_sector(R_OUT, R_OUT + p) + _rect(R_OUT, R_OUT + p, -L, 0) + _rect(-L, 0, R_OUT, R_OUT + p)
    inner_band = _ring_sector(R_IN - p, R_IN) + _rect(R_IN - p, R_IN, -L, 0) + _rect(-L, 0, R_IN - p, R_IN)
    tdc = _rect(R_IN, R_OUT, -L - t, -L) + _rect(-L - t, -L, R_IN, R_OUT)
    return net + outer_band + inner_band + tdc


def cheek_folds():
    lines = [
        # biên tinh phía ngoài (gập mí âm)
        bd.Line((R_OUT, -L), (R_OUT, 0)),
        bd.CenterArc((0, 0), R_OUT, 0, 90),
        bd.Line((0, R_OUT), (-L, R_OUT)),
        # biên tinh phía trong
        bd.Line((R_IN, -L), (R_IN, 0)),
        bd.CenterArc((0, 0), R_IN, 0, 90),
        bd.Line((0, R_IN), (-L, R_IN)),
        # đường gập TDC
        bd.Line((R_IN, -L), (R_OUT, -L)),
        bd.Line((-L, R_IN), (-L, R_OUT)),
    ]
    return bd.Compound(children=lines)


# ------------------------------------------------------------ Lưng (strips) --

def strip_cut(length):
    f, t = PITTS_MALE, TDC_ALLOW
    return (_rect(0, length, -f, H + f)
            + _rect(-t, 0, 0, H) + _rect(length, length + t, 0, H))


def strip_folds(length):
    return bd.Compound(children=[
        bd.Line((0, 0), (length, 0)),
        bd.Line((0, H), (length, H)),
        bd.Line((0, 0), (0, H)),
        bd.Line((length, 0), (length, H)),
    ])


def strip_roll_marks(length):
    return bd.Compound(children=[
        bd.Line((L, 0), (L, H)),
        bd.Line((length - L, 0), (length - L, H)),
    ])


@dxf(out="../DXF/co90_400x200_L100_trai_phang.dxf")
def co90_400x200_L100_trai_phang():
    cheek_w = R_OUT + PITTS_POCKET + L + TDC_ALLOW
    # Má 1 và Má 2 cạnh nhau; gốc tọa độ má = tâm cung
    m1 = bd.Pos(0, 0)
    m2 = bd.Pos(cheek_w + GAP, 0)
    # Lưng trong / lưng ngoài xếp phía dưới
    y_strip1 = -L - TDC_ALLOW - GAP - (H + PITTS_MALE)
    y_strip2 = y_strip1 - GAP - (H + 2 * PITTS_MALE)
    s1 = bd.Pos(-L, y_strip1)
    s2 = bd.Pos(-L, y_strip2)

    cut = [m1 * cheek_cut(), m2 * cheek_cut(), s1 * strip_cut(LEN_THROAT), s2 * strip_cut(LEN_HEEL)]
    folds = [m1 * cheek_folds(), m2 * cheek_folds(),
             s1 * strip_folds(LEN_THROAT), s2 * strip_folds(LEN_HEEL)]
    rolls = [s1 * strip_roll_marks(LEN_THROAT), s2 * strip_roll_marks(LEN_HEEL)]

    return {
        "CUT": bd.Compound(children=[c.faces()[0] if len(c.faces()) == 1 else c for c in cut]),
        "BEND_FOLD": bd.Compound(children=folds),
        "REFERENCE_ROLL": bd.Compound(children=rolls),
    }


if __name__ == "__main__":
    co90_400x200_L100_trai_phang()
