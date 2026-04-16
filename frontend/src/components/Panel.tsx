type Props = {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
};

export function Panel({ title, subtitle, children }: Props) {
  return (
    <section className="rounded-3xl border border-black/5 bg-white p-6 shadow-card">
      <div className="mb-4">
        <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
        {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
      </div>
      {children}
    </section>
  );
}

