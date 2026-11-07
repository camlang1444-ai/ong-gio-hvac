"""Vẽ ảnh thông số từng mảnh co 90° (PNG có ghi kích thước) bằng matplotlib.

Chạy:  python tools/ve_anh_co90.py   -> docs/co90/*.png
"""

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, Rectangle, Wedge  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from co90_thong_so import (  # noqa: E402
    ARC_IN, ARC_OUT, CHEEK_BLANK, H, HEEL_BLANK, L, LEN_HEEL, LEN_THROAT, PITTS_MALE,
    PITTS_POCKET, R_IN, R_OUT, T, TDC_ALLOW, TDC_FLANGE, THROAT_BLANK, W,
    total_blank_area_m2, total_mass_kg,
)

OUT = ROOT / "docs" / "co90"
OUT.mkdir(parents=True, exist_ok=True)

NET_FILL = "#cfe3f7"
ALLOW_FILL = "#ffd9a8"
TDC_FILL = "#f7b7b7"
DIM = "#c0392b"
EDGE = "#1f3b57"
plt.rcParams["font.family"] = "DejaVu Sans"


def fmt(v: float) -> str:
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"


def dim(ax, p1, p2, off, text, fs=9):
    """Kích thước thẳng giữa p1-p2, dời song song một đoạn off (theo pháp tuyến trái)."""
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    nx, ny = -uy, ux
    q1 = (x1 + nx * off, y1 + ny * off)
    q2 = (x2 + nx * off, y2 + ny * off)
    s = 1 if off >= 0 else -1
    ext = 6 * s
    ax.plot([x1, q1[0] + nx * ext], [y1, q1[1] + ny * ext], color=DIM, lw=0.6)
    ax.plot([x2, q2[0] + nx * ext], [y2, q2[1] + ny * ext], color=DIM, lw=0.6)
    ax.annotate("", xy=q2, xytext=q1,
                arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.8, mutation_scale=7))
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90 or ang <= -90:
        ang += 180
    mx, my = (q1[0] + q2[0]) / 2 + nx * 9 * s, (q1[1] + q2[1]) / 2 + ny * 9 * s
    ax.text(mx, my, text, color=DIM, fontsize=fs, rotation=ang, ha="center", va="center",
            bbox=dict(fc="white", ec="none", pad=0.6))


def radius(ax, r, ang_deg, text):
    a = math.radians(ang_deg)
    ax.annotate("", xy=(r * math.cos(a), r * math.sin(a)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=DIM, lw=0.8, mutation_scale=8))
    tx, ty = 0.55 * r * math.cos(a), 0.55 * r * math.sin(a)
    ax.text(tx, ty, text, color=DIM, fontsize=9, rotation=ang_deg, ha="center", va="bottom",
            bbox=dict(fc="white", ec="none", pad=0.6))


def finish(ax, fig, title, name, note=None):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", color=EDGE, loc="left")
    if note:
        fig.text(0.02, 0.015, note, fontsize=8.5, color="#333", va="bottom")
    fig.savefig(OUT / name, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def legend(ax, x, y):
    items = [(NET_FILL, "Kích thước tinh"), (ALLOW_FILL, "Mí ghép Pittsburgh"), (TDC_FILL, "Phần bù cán TDC")]
    for i, (c, lbl) in enumerate(items):
        ax.add_patch(Rectangle((x, y - i * 28), 30, 18, fc=c, ec=EDGE, lw=0.6))
        ax.text(x + 40, y - i * 28 + 9, lbl, fontsize=8.5, va="center")
    ax.plot([x, x + 30], [y - 3 * 28 + 9] * 2, ls="--", color=EDGE, lw=0.9)
    ax.text(x + 40, y - 3 * 28 + 9, "Đường gập", fontsize=8.5, va="center")


# ------------------------------------------------------------------- MÁ --------

def draw_cheek():
    p, t = PITTS_POCKET, TDC_ALLOW
    fig, ax = plt.subplots(figsize=(10, 10))
    # mí âm
    ax.add_patch(Wedge((0, 0), R_OUT + p, 0, 90, width=p, fc=ALLOW_FILL, ec="none"))
    ax.add_patch(Wedge((0, 0), R_IN, 0, 90, width=p, fc=ALLOW_FILL, ec="none"))
    for (x0, y0, w, h) in [(R_OUT, -L, p, L), (R_IN - p, -L, p, L), (-L, R_OUT, L, p), (-L, R_IN - p, L, p)]:
        ax.add_patch(Rectangle((x0, y0), w, h, fc=ALLOW_FILL, ec="none"))
    # TDC
    ax.add_patch(Rectangle((R_IN, -L - t), W, t, fc=TDC_FILL, ec="none"))
    ax.add_patch(Rectangle((-L - t, R_IN), t, W, fc=TDC_FILL, ec="none"))
    # tinh
    ax.add_patch(Wedge((0, 0), R_OUT, 0, 90, width=W, fc=NET_FILL, ec="none"))
    ax.add_patch(Rectangle((R_IN, -L), W, L, fc=NET_FILL, ec="none"))
    ax.add_patch(Rectangle((-L, R_IN), L, W, fc=NET_FILL, ec="none"))
    # đường gập (biên tinh)
    kw = dict(color=EDGE, lw=0.9, ls="--")
    ax.add_patch(Arc((0, 0), 2 * R_OUT, 2 * R_OUT, theta1=0, theta2=90, **kw))
    ax.add_patch(Arc((0, 0), 2 * R_IN, 2 * R_IN, theta1=0, theta2=90, **kw))
    for xs, ys in [([R_OUT, R_OUT], [-L, 0]), ([R_IN, R_IN], [-L, 0]), ([0, -L], [R_OUT, R_OUT]),
                   ([0, -L], [R_IN, R_IN]), ([R_IN, R_OUT], [-L, -L]), ([-L, -L], [R_IN, R_OUT])]:
        ax.plot(xs, ys, **kw)
    # đường cắt (biên phôi)
    ck = dict(color=EDGE, lw=1.5)
    ax.add_patch(Arc((0, 0), 2 * (R_OUT + p), 2 * (R_OUT + p), theta1=0, theta2=90, **ck))
    ax.add_patch(Arc((0, 0), 2 * (R_IN - p), 2 * (R_IN - p), theta1=0, theta2=90, **ck))
    seg = [
        ([R_OUT + p, R_OUT + p], [0, -L]), ([R_OUT + p, R_OUT], [-L, -L]), ([R_OUT, R_OUT], [-L, -L - t]),
        ([R_OUT, R_IN], [-L - t, -L - t]), ([R_IN, R_IN], [-L - t, -L]), ([R_IN, R_IN - p], [-L, -L]),
        ([R_IN - p, R_IN - p], [-L, 0]),
        ([0, -L], [R_OUT + p, R_OUT + p]), ([-L, -L], [R_OUT + p, R_OUT]), ([-L, -L - t], [R_OUT, R_OUT]),
        ([-L - t, -L - t], [R_OUT, R_IN]), ([-L - t, -L], [R_IN, R_IN]), ([-L, -L], [R_IN, R_IN - p]),
        ([-L, 0], [R_IN - p, R_IN - p]),
    ]
    for xs, ys in seg:
        ax.plot(xs, ys, **ck)
    ax.plot(0, 0, "+", color=DIM, ms=10)
    ax.text(8, -18, "Tâm O", color=DIM, fontsize=8)

    # kích thước
    radius(ax, R_IN, 30, f"R{fmt(R_IN)} (tinh)")
    radius(ax, R_OUT, 72, f"R{fmt(R_OUT)} (tinh)")
    dim(ax, (R_IN, -L - t), (R_OUT, -L - t), -35, f"{fmt(W)} (tinh)")
    dim(ax, (R_OUT + p, -L), (R_OUT + p, 0), -30, f"L={fmt(L)}")
    dim(ax, (R_OUT + p, -L - t), (R_OUT + p, -L), -30, f"TDC {fmt(t)}", fs=8)
    dim(ax, (-L, R_IN), (-L, R_OUT), 70, f"{fmt(W)} (tinh)")
    dim(ax, (-L, R_OUT + p), (0, R_OUT + p), 22, f"L={fmt(L)}", fs=8)
    dim(ax, (-L - t, R_OUT + p), (R_OUT + p, R_OUT + p), 55, f"Phôi {fmt(CHEEK_BLANK[0])}")
    dim(ax, (-L - t, -L - t), (-L - t, R_OUT + p), 95, f"Phôi {fmt(CHEEK_BLANK[1])}")
    ax.text(-L - t / 2, (R_IN + R_OUT) / 2, f"TDC {fmt(t)}", rotation=90, ha="center", va="center", fontsize=8)
    a = math.radians(20)
    ax.annotate(f"Mí âm {fmt(p)}", xy=((R_OUT + p / 2) * math.cos(a), (R_OUT + p / 2) * math.sin(a)),
                xytext=(R_OUT + 40, 320), color=DIM, fontsize=9,
                arrowprops=dict(arrowstyle="-|>", color=DIM, lw=0.8))
    a = math.radians(65)
    ax.annotate(f"Mí âm {fmt(p)}", xy=((R_IN - p / 2) * math.cos(a), (R_IN - p / 2) * math.sin(a)),
                xytext=(20, 110), color=DIM, fontsize=9, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=DIM, lw=0.8))
    ax.text(410, 300, "MÁ  ×2\n(tôn %.2f mm)" % T, fontsize=14, fontweight="bold", color=EDGE, ha="center")
    legend(ax, -L - t - 60, -L - t - 70)
    ax.set_xlim(-L - t - 175, R_OUT + p + 130)
    ax.set_ylim(-L - t - 190, R_OUT + p + 120)
    finish(ax, fig, "Mảnh 1 – MÁ co 90° 400x200 (2 tấm giống nhau)", "1_ma.png",
           note=(f"Phôi cắt {fmt(CHEEK_BLANK[0])}×{fmt(CHEEK_BLANK[1])} mm (hộp bao).  "
                 f"Mí âm Pittsburgh {fmt(p)} mm chạy dọc cung trong/ngoài và cổ.  "
                 f"Phần bù TDC {fmt(t)} mm ở 2 đầu, cắt góc tại giao mí."))


# ----------------------------------------------------------------- LƯNG --------

def draw_strip(length, arc, r, title, name, label):
    f, t = PITTS_MALE, TDC_ALLOW
    blank = (length + 2 * t, H + 2 * f)
    fig, ax = plt.subplots(figsize=(13, 4.8))
    ax.add_patch(Rectangle((0, -f), length, f, fc=ALLOW_FILL, ec="none"))
    ax.add_patch(Rectangle((0, H), length, f, fc=ALLOW_FILL, ec="none"))
    ax.add_patch(Rectangle((-t, 0), t, H, fc=TDC_FILL, ec="none"))
    ax.add_patch(Rectangle((length, 0), t, H, fc=TDC_FILL, ec="none"))
    ax.add_patch(Rectangle((0, 0), length, H, fc=NET_FILL, ec="none"))
    ax.add_patch(Rectangle((L, 0), arc, H, fc="#b3d3f0", ec="none"))
    kw = dict(color=EDGE, lw=0.9, ls="--")
    for xs, ys in [([0, length], [0, 0]), ([0, length], [H, H]), ([0, 0], [0, H]), ([length, length], [0, H])]:
        ax.plot(xs, ys, **kw)
    for x in (L, length - L):
        ax.plot([x, x], [-f, H + f], color="#2c7a3f", lw=1.0, ls="-.")
    ck = dict(color=EDGE, lw=1.5)
    pts = [(0, -f), (length, -f), (length, 0), (length + t, 0), (length + t, H), (length, H),
           (length, H + f), (0, H + f), (0, H), (-t, H), (-t, 0), (0, 0), (0, -f)]
    ax.plot([q[0] for q in pts], [q[1] for q in pts], **ck)

    ax.text(L + arc / 2, H / 2, f"CUỐN CONG R{fmt(r)}\n(mặt tinh quay\nvào trong)",
            ha="center", va="center", fontsize=9.5, color=EDGE)
    ax.text(L / 2, H / 2, "cổ\nthẳng", ha="center", va="center", fontsize=8.5)
    ax.text(length - L / 2, H / 2, "cổ\nthẳng", ha="center", va="center", fontsize=8.5)
    ax.text(-t / 2, H / 2, "TDC", rotation=90, ha="center", va="center", fontsize=8)
    ax.text(length + t / 2, H / 2, "TDC", rotation=90, ha="center", va="center", fontsize=8)

    dim(ax, (0, H + f), (L, H + f), 22, f"{fmt(L)}")
    dim(ax, (L, H + f), (L + arc, H + f), 22, f"Cung {arc:.1f}  (= π×{fmt(r)}/2)")
    dim(ax, (L + arc, H + f), (length, H + f), 22, f"{fmt(L)}")
    dim(ax, (0, H + f), (length, H + f), 55, f"Dài tinh {length:.1f}")
    dim(ax, (-t, -f), (length + t, -f), -45, f"Phôi {blank[0]:.1f}")
    ax.annotate(f"Mí dương {fmt(f)} mm (gập 90°) – cả 2 cạnh dài", xy=(L + arc * 0.25, -f / 2),
                xytext=(L + arc * 0.25 + 40, -f - 22), va="top",
                color=DIM, fontsize=8.5, arrowprops=dict(arrowstyle="-|>", color=DIM, lw=0.8))
    dim(ax, (length + t, 0), (length + t, H), -30, f"{fmt(H)}")
    dim(ax, (length + t, -f), (length + t, H + f), -75, f"Phôi {fmt(blank[1])}")
    dim(ax, (-t, 0), (0, 0), -20, f"{fmt(t)}", fs=8)
    ax.text(length / 2, -f - 100, f"{label}  ×1   (tôn {T:.2f} mm)", ha="center", fontsize=13,
            fontweight="bold", color=EDGE)
    ax.set_xlim(-t - 90, length + t + 140)
    ax.set_ylim(-f - 130, H + f + 110)
    finish(ax, fig, title, name,
           note=(f"Phôi cắt {blank[0]:.1f}×{fmt(blank[1])} mm.  Mí dương (gập 90°) {fmt(f)} mm mỗi bên "
                 f"để móc vào mí âm của má.  Vạch xanh = điểm bắt đầu/kết thúc cuốn cong."))


# ------------------------------------------------------------ TỔNG QUAN --------

def draw_overview():
    fig, ax = plt.subplots(figsize=(9, 9))
    # mặt bằng co (nhìn từ trên), nét liền = thành trong
    ax.add_patch(Wedge((0, 0), R_OUT, 0, 90, width=W, fc=NET_FILL, ec=EDGE, lw=1.2))
    ax.add_patch(Rectangle((R_IN, -L), W, L, fc=NET_FILL, ec=EDGE, lw=1.2))
    ax.add_patch(Rectangle((-L, R_IN), L, W, fc=NET_FILL, ec=EDGE, lw=1.2))
    f = TDC_FLANGE
    ax.add_patch(Rectangle((R_IN - f, -L - 5), W + 2 * f, 5, fc=TDC_FILL, ec=EDGE, lw=1))
    ax.add_patch(Rectangle((-L - 5, R_IN - f), 5, W + 2 * f, fc=TDC_FILL, ec=EDGE, lw=1))
    ax.plot([R_IN + W / 2, R_IN + W / 2], [-L - 40, 0], color="#888", lw=0.7, ls="-.")
    ax.add_patch(Arc((0, 0), R_IN + R_OUT, R_IN + R_OUT, theta1=0, theta2=90, color="#888", lw=0.7, ls="-."))
    ax.plot([0, -L - 40], [R_IN + W / 2] * 2, color="#888", lw=0.7, ls="-.")
    radius(ax, R_IN, 30, f"R trong {fmt(R_IN)}")
    radius(ax, R_OUT, 55, f"R ngoài {fmt(R_OUT)}")
    dim(ax, (R_IN, -L - 5), (R_OUT, -L - 5), -50, f"W {fmt(W)} (lòng trong)")
    dim(ax, (R_OUT + f, -L), (R_OUT + f, 0), -25, f"L {fmt(L)}")
    dim(ax, (-L, R_OUT + f), (0, R_OUT + f), 25, f"L {fmt(L)}")
    ax.text(330, 300, f"CO 90°\n{fmt(W)}×{fmt(H)}\nL{fmt(L)} – bích TDC{fmt(f)}", fontsize=13,
            fontweight="bold", color=EDGE, ha="center")
    ax.text(R_IN + W / 2, -L - 115, "Đầu 1 – bích TDC", ha="center", fontsize=9)
    ax.text(-L - 60, R_IN + W / 2, "Đầu 2 – bích TDC", rotation=90, ha="center", va="center", fontsize=9)
    ax.set_xlim(-L - 120, R_OUT + 120)
    ax.set_ylim(-L - 150, R_OUT + 110)
    finish(ax, fig, "Tổng quan – mặt bằng co 90° (chiều cao lòng trong H = 200)", "0_tong_quan.png",
           note=(f"Gồm 4 mảnh: 2 má + lưng trong + lưng ngoài.  Tổng diện tích phôi ≈ "
                 f"{total_blank_area_m2():.3f} m²,  khối lượng tôn ≈ {total_mass_kg():.2f} kg "
                 f"(tôn {T} mm)."))


if __name__ == "__main__":
    draw_overview()
    draw_cheek()
    draw_strip(LEN_THROAT, ARC_IN, R_IN, "Mảnh 2 – LƯNG TRONG (bụng co)", "2_lung_trong.png", "LƯNG TRONG")
    draw_strip(LEN_HEEL, ARC_OUT, R_OUT, "Mảnh 3 – LƯNG NGOÀI", "3_lung_ngoai.png", "LƯNG NGOÀI")
    print("blanks:", CHEEK_BLANK, THROAT_BLANK, HEEL_BLANK)
    print("area m2:", round(total_blank_area_m2(), 4), "mass kg:", round(total_mass_kg(), 2))
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))
