import { Link, NavLink } from "react-router-dom";

type Props = {
  children: React.ReactNode;
};

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/reports", label: "Reports" },
];

export function Layout({ children }: Props) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(15,118,110,0.15),_transparent_35%),linear-gradient(180deg,#f7f3ea_0%,#fefcf7_100%)] text-ink">
      <header className="border-b border-black/5 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-2xl font-semibold tracking-tight">
            Paper2Lab
          </Link>
          <nav className="flex items-center gap-5 text-sm font-medium">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  isActive ? "text-accent underline decoration-2 underline-offset-8" : "text-slate-600"
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
    </div>
  );
}

