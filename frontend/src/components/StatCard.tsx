type Props = {
  label: string;
  value: number | string;
  tone?: "default" | "accent" | "coral";
};

export function StatCard({ label, value, tone = "default" }: Props) {
  const toneClass =
    tone === "accent"
      ? "bg-accent text-white"
      : tone === "coral"
        ? "bg-coral text-white"
        : "bg-white text-ink";
  return (
    <div className={`rounded-3xl p-5 shadow-card ${toneClass}`}>
      <div className="text-sm opacity-80">{label}</div>
      <div className="mt-3 text-4xl font-semibold tracking-tight">{value}</div>
    </div>
  );
}

