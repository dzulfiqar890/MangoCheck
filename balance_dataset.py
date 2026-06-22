"""
balance_dataset.py
Script untuk menyeimbangkan distribusi kelas dataset MangoCheck.

Strategi: Random Undersampling pada kelas mayoritas (Rotten).
- Gambar berlebih DIPINDAHKAN ke folder _excluded, bukan dihapus.
- Jumlah target = jumlah kelas terkecil per split (train/validation).
- Random seed tetap agar hasilnya reproducible.

Jalankan sekali saja:
    python balance_dataset.py
"""

import os
import shutil
import random

DATASET_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
EXCLUDED_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "_excluded")
SEED = 42


def get_image_files(folder: str) -> list[str]:
    """Mendapatkan daftar nama file gambar dalam folder."""
    return sorted([
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ])


def balance_split(split_name: str) -> None:
    """
    Menyeimbangkan satu split (train atau validation).
    Target jumlah gambar per kelas = jumlah kelas terkecil di split tersebut.
    """
    split_dir = os.path.join(DATASET_ROOT, split_name)
    classes = [d for d in os.listdir(split_dir) 
               if os.path.isdir(os.path.join(split_dir, d)) and not d.startswith("_")]

    # Hitung jumlah per kelas
    counts = {}
    for cls in classes:
        cls_dir = os.path.join(split_dir, cls)
        counts[cls] = len(get_image_files(cls_dir))

    print(f"\n{'='*50}")
    print(f"  {split_name.upper()} — Sebelum Balancing")
    print(f"{'='*50}")
    for cls, count in sorted(counts.items()):
        print(f"  {cls:>10}: {count:>5} gambar")

    # Target = jumlah kelas terkecil
    target_count = min(counts.values())
    print(f"\n  Target per kelas: {target_count} gambar")

    total_moved = 0

    for cls in classes:
        cls_dir = os.path.join(split_dir, cls)
        files = get_image_files(cls_dir)
        current_count = len(files)

        if current_count <= target_count:
            print(f"  {cls}: sudah seimbang ({current_count} <= {target_count}), skip.")
            continue

        # Acak file dan pilih yang akan dipertahankan
        random.seed(SEED)
        random.shuffle(files)

        keep = files[:target_count]
        exclude = files[target_count:]

        # Buat folder _excluded untuk kelas ini
        excluded_dir = os.path.join(EXCLUDED_ROOT, split_name, cls)
        os.makedirs(excluded_dir, exist_ok=True)

        # Pindahkan file berlebih
        for filename in exclude:
            src = os.path.join(cls_dir, filename)
            dst = os.path.join(excluded_dir, filename)
            shutil.move(src, dst)

        total_moved += len(exclude)
        print(f"  {cls}: {current_count} -> {target_count} (dipindahkan {len(exclude)} ke _excluded/)")

    # Verifikasi setelah balancing
    print(f"\n  Setelah Balancing:")
    for cls in sorted(classes):
        cls_dir = os.path.join(split_dir, cls)
        new_count = len(get_image_files(cls_dir))
        print(f"  {cls:>10}: {new_count:>5} gambar")

    print(f"\n  Total dipindahkan: {total_moved} gambar")
    return total_moved


def main():
    print("MangoCheck — Dataset Balancing Tool")
    print("Strategi: Random Undersampling (non-destructive)")
    print(f"Gambar berlebih dipindahkan ke: dataset/_excluded/")

    total = 0
    total += balance_split("train")
    total += balance_split("validation")

    print(f"\n{'='*50}")
    print(f"  SELESAI — Total {total} gambar dipindahkan ke _excluded/")
    print(f"{'='*50}")
    print(f"\nUntuk mengembalikan gambar, pindahkan dari dataset/_excluded/ ke folder asalnya.")
    print(f"Untuk menghapus permanen, hapus folder dataset/_excluded/.")


if __name__ == "__main__":
    main()
