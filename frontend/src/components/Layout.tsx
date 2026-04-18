import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

type NavItem = { to: string; label: string; icon: React.ReactNode };

const nav: NavItem[] = [
  { to: "/", label: "Dashboard", icon: <IconDashboard /> },
  { to: "/timeline", label: "Timeline", icon: <IconTimeline /> },
  { to: "/profile", label: "Profile", icon: <IconProfile /> },
];

const COLLAPSE_KEY = "contextmirror.sidebar.collapsed";

export function Layout() {
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem(COLLAPSE_KEY) === "1";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    localStorage.setItem(COLLAPSE_KEY, collapsed ? "1" : "0");
  }, [collapsed]);

  return (
    <div className="min-h-screen bg-base text-white flex">
      <aside
        className={`hidden md:flex flex-col border-r border-elevated py-8 sticky top-0 h-screen transition-[width] duration-200 ${
          collapsed ? "w-16 px-2" : "w-60 lg:w-64 px-5"
        }`}
      >
        <div
          className={`flex items-center mb-10 ${
            collapsed ? "justify-center" : "justify-between"
          }`}
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-md bg-elevated border border-white/10 shrink-0" />
            {!collapsed && (
              <div className="font-medium tracking-tight text-[15px] truncate">
                ContextMirror
              </div>
            )}
          </div>
          {!collapsed && (
            <button
              onClick={() => setCollapsed(true)}
              className="text-text-muted hover:text-white p-1 rounded"
              title="Collapse sidebar"
            >
              <IconChevronLeft />
            </button>
          )}
        </div>

        {collapsed && (
          <button
            onClick={() => setCollapsed(false)}
            className="text-text-muted hover:text-white self-center mb-4 p-1 rounded"
            title="Expand sidebar"
          >
            <IconChevronRight />
          </button>
        )}

        <nav className="flex flex-col gap-0.5">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end
              title={collapsed ? item.label : undefined}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md text-sm transition-colors ${
                  collapsed ? "justify-center px-0 py-2" : "px-3 py-2"
                } ${
                  isActive
                    ? "bg-elevated text-white"
                    : "text-text-muted hover:text-white"
                }`
              }
            >
              <span className="shrink-0">{item.icon}</span>
              {!collapsed && <span className="truncate">{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div
          className={`mt-auto pt-6 border-t border-elevated ${
            collapsed ? "flex justify-center" : ""
          }`}
        >
          <UserMenu collapsed={collapsed} />
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

function UserMenu({ collapsed }: { collapsed: boolean }) {
  const { user, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const nav = useNavigate();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  if (!user) return null;
  const initial = user.name.charAt(0).toUpperCase();

  return (
    <div className="relative w-full" ref={ref}>
      {open && (
        <div
          className={`absolute bottom-full mb-2 rounded-md border border-elevated bg-card shadow-lg overflow-hidden ${
            collapsed ? "left-full ml-2 w-44" : "left-0 right-0"
          }`}
        >
          {collapsed && (
            <div className="px-3 py-2 border-b border-elevated">
              <div className="text-sm text-white truncate">{user.name}</div>
              <div className="text-xs text-text-muted truncate">
                {user.email}
              </div>
            </div>
          )}
          <button
            onClick={() => {
              setOpen(false);
              nav("/profile");
            }}
            className="w-full text-left px-3 py-2 text-sm text-text-muted hover:bg-elevated hover:text-white transition-colors"
          >
            View profile
          </button>
          <button
            onClick={() => {
              setOpen(false);
              signOut();
              nav("/signin");
            }}
            className="w-full text-left px-3 py-2 text-sm text-danger hover:bg-elevated transition-colors border-t border-elevated"
          >
            Sign out
          </button>
        </div>
      )}
      <button
        onClick={() => setOpen((v) => !v)}
        title={collapsed ? user.name : undefined}
        className={`flex items-center gap-3 rounded-md transition-colors w-full ${
          collapsed ? "justify-center p-1" : "px-1 py-1"
        } ${open ? "bg-elevated/60" : "hover:bg-elevated/40"}`}
      >
        <div className="w-8 h-8 rounded-full bg-elevated flex items-center justify-center text-xs font-medium shrink-0">
          {initial}
        </div>
        {!collapsed && (
          <>
            <div className="leading-tight text-left flex-1 min-w-0">
              <div className="text-sm truncate">{user.name}</div>
              <div className="text-xs text-text-muted truncate">
                {user.email}
              </div>
            </div>
            <span className="text-text-muted text-xs mr-1">⋯</span>
          </>
        )}
      </button>
    </div>
  );
}

function IconDashboard() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="9" rx="1.5" />
      <rect x="14" y="3" width="7" height="5" rx="1.5" />
      <rect x="14" y="12" width="7" height="9" rx="1.5" />
      <rect x="3" y="16" width="7" height="5" rx="1.5" />
    </svg>
  );
}

function IconTimeline() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 7h16M4 12h16M4 17h16" />
      <circle cx="8" cy="7" r="1.5" fill="currentColor" />
      <circle cx="14" cy="12" r="1.5" fill="currentColor" />
      <circle cx="10" cy="17" r="1.5" fill="currentColor" />
    </svg>
  );
}

function IconProfile() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21a8 8 0 0 1 16 0" />
    </svg>
  );
}

function IconChevronLeft() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 18l-6-6 6-6" />
    </svg>
  );
}

function IconChevronRight() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 6l6 6-6 6" />
    </svg>
  );
}
