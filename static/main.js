// 作品一覧のカテゴリ絞り込み
document.querySelectorAll(".filter").forEach((btn) => {
  btn.addEventListener("click", () => {
    const value = btn.dataset.filter;
    document.querySelectorAll(".filter").forEach((b) => b.classList.toggle("is-active", b === btn));
    document.querySelectorAll(".card").forEach((card) => {
      card.hidden = value !== "all" && card.dataset.category !== value;
    });
  });
});
