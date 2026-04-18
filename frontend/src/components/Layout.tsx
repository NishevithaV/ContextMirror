import { NavLink, Outlet } from "react-router-dom";

const nav = [
  { to: "/", label: "Dashboard" },
  { to: "/profile", label: "Profile" },
];

export function Layout() {
  return (
    <div className="min-h-screen bg-base text-white flex">
      <aside className="hidden md:flex md:w-60 lg:w-64 flex-col border-r border-elevated px-5 py-8 sticky top-0 h-screen">
        <div className="flex items-center gap-2.5 mb-10">
          <div className="w-7 h-7 rounded-md bg-elevated border border-white/10" />
          <div className="font-medium tracking-tight text-[15px]">ContextMirror</div>
        </div>

        <nav className="flex flex-col gap-0.5">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive
                    ? "bg-elevated text-white"
                    : "text-text-muted hover:text-white"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto pt-6 border-t border-elevated">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-elevated flex items-center justify-center text-xs font-medium">
              J
            </div>
            <div className="leading-tight">
              <div className="text-sm">Julia</div>
              <div className="text-xs text-text-muted">Demo account</div>
            </div>
          </div>
        </div>
      </aside>

      <header className="md:hidden fixed top-0 left-0 right-0 bg-base/90 backdrop-blur border-b border-elevated z-10">
        <div className="flex items-center justify-between px-5 py-3">
          <div className="font-medium">ContextMirror</div>
          <div className="flex gap-2">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end
                className={({ isActive }) =>
                  `text-xs px-3 py-1.5 rounded-full ${
                    isActive ? "bg-elevated text-white" : "text-text-muted"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>
      </header>

      <main className="flex-1 px-8 md:px-12 pt-20 md:pt-12 pb-16 max-w-5xl mx-auto w-full">
        <Outlet />
      </main>
    </div>
  );
}
